#!/usr/bin/env python3
"""Build dedupe's training.json from moderator-adjudicated labeled pairs.

OSDEV-3277 — label-only retrain. Emits the SAME three fields the production
Gazetteer uses (country / name / address). It deliberately does not add
features; the v4 feature work is a separate ticket.

Input: a labeled-pairs CSV with one row per FacilityMatch adjudication:
  match_id, status, confidence,
  item_name, item_clean_name, item_address, item_clean_address, item_country,
  fac_name, fac_address, fac_country
`status == CONFIRMED` is a positive; anything else is a negative.

Output: dedupe 1.9.4 training.json ({"match": [...], "distinct": [...]}),
written where gazetteer_train.py reads it: src/dedupe-hub/api/app/data/.

Two decisions are baked in and must not be "cleaned up" without rereading the
Aug 2026 matcher evaluation:

1. Pick-one rejects STAY in the negatives. ~90% of REJECTED rows mean "not
   this near-identical sibling", not "no match". Purging them (the v5
   experiment) collapsed the negative pool to ~1k pairs and made the hard
   lookalike class and within-set ranking worse on every metric. They are
   ranking signal. They are excluded from EVALUATION negatives instead --
   that split belongs to the eval harness, not here.

2. The draw is curated, not random: hard pairs (long shared name prefix but
   not identical -- the UNIT A vs UNIT B lookalike class -- plus pairs where
   the incumbent's score disagreed with the moderator) are oversampled 2:1
   over easy pairs. Mirrors what dedupe's own active learning would surface.

Deterministic: fixed seed, and the train half is selected by a stable hash of
match_id so the split is reproducible across files and runs. Never split on
row order -- pair_id-by-row-order silently misjoined 97.5% of rows once
already and still produced plausible AUCs.

Usage:
  python3 make_training_json.py --pairs <labeled_pairs.csv> [--out <path>]
                                [--per-class 3000] [--hard-share 0.67] [--dry-run]
"""
import argparse
import csv
import hashlib
import json
import os
import random
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(HERE, os.pardir, "api", "app", "data", "training.json")

SEED = 42
PREFIX_HARD = 12          # shared leading chars that make a pair a "lookalike"
SURPRISE_MARGIN = 0.5     # |prod score - label| above this = model/human disagreement


def stable_train_half(match_id: str) -> bool:
    """Deterministic 50/50 split keyed on match_id (never on row order)."""
    h = hashlib.md5(str(match_id).encode()).hexdigest()
    return int(h[:8], 16) % 2 == 0


EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")


def scrub(value: str) -> str:
    """Strip contact emails before they reach a file we commit.

    training.json lives in a PUBLIC repo. Facility names and addresses are
    public data on OS Hub, but contributor-entered address fields occasionally
    carry a personal contact email, which is not (3 of 160,000 fields in the
    2026-08 sample, one of them a person's name @ a company domain). The token
    carries no matching signal -- the two sides of a true match never agree on
    it -- so dropping it costs nothing.

    Phone numbers are deliberately NOT scrubbed. Every pattern loose enough to
    catch an international phone number also eats plot numbers, postcodes and
    street numbers: the obvious one matched 1.8% of all fields and mangled real
    address signal ("industrial plot no. 1, sector - 28 121008 faridabad" ->
    "industrial plot no. 1, sector - faridabad"). Address digits are matching
    signal, and these addresses are already public on the site.
    """
    return " ".join(EMAIL_RE.sub(" ", value).split())


try:
    from unidecode import unidecode
except ImportError:  # the api-app image always has it; a bare laptop may not
    unidecode = None
    print("WARNING: unidecode is not installed, so accents are folded with a "
          "fallback that can differ from production's clean()", file=sys.stderr)


def _fold_accents(text):
    """Fallback for unidecode: drop accents so cleaning can still run."""
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()


def clean(column):
    """Production's text cleaning, copied from app/utils/clean.py.

    dedupe-hub runs this on BOTH sides before matching: the uploaded item
    (Reader), every facility in the index (get_canonical_items) and the training
    sample. Keep it identical to production, or the model is trained and scored
    on text that looks different from what it sees at runtime. Returns None for
    an empty value, as production does.
    """
    column = (unidecode or _fold_accents)(column or "")
    column = re.sub('\n', ' ', column)
    column = re.sub('-', '', column)
    column = re.sub('/', ' ', column)
    column = re.sub("'", '', column)
    column = re.sub(",", '', column)
    column = re.sub(":", ' ', column)
    column = re.sub(' +', ' ', column)
    column = column.strip().strip('"').strip("'").lower().strip()
    if not column:
        column = None
    return column


def record(name, address, country):
    """Exactly the three fields gazetteer_train.py declares, cleaned the way
    production cleans them (see clean()), then email-scrubbed for the public
    repo. The scrub is the one step production does not do, and it only ever
    touches the rare cell that holds a contact email."""
    return {
        "name": scrub(clean(name) or ""),
        "address": scrub(clean(address) or ""),
        "country": clean(country) or "",
    }


def can_score(left, right):
    """True if dedupe can compute distances for this pair of records.

    Both sides need a name. And for name and for address, at least one side must
    be non-empty: dedupe's affine-gap distance raises ZeroDivisionError when it
    is asked to compare two empty strings. This happens when the email scrub
    empties a cell that held only a contact email. Every script that scores
    pairs uses this one rule, so they all keep and skip exactly the same rows.
    """
    if not left["name"] or not right["name"]:
        return False
    return not any(not left[f] and not right[f] for f in ("name", "address"))


def prefix_len(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def load_pairs(path):
    rows = []
    seen = set()
    with open(path) as f:
        for r in csv.DictReader(f):
            mid = r["match_id"]
            if mid in seen:
                continue          # join discipline: match_id is the key, keep it unique
            seen.add(mid)
            left = record(r.get("item_clean_name") or r.get("item_name"),
                          r.get("item_clean_address") or r.get("item_address"),
                          r.get("item_country"))
            right = record(r.get("fac_name"), r.get("fac_address"),
                           r.get("fac_country"))
            if not left["name"] or not right["name"]:
                continue
            try:
                conf = float(r.get("confidence") or 0.0)
            except ValueError:
                conf = 0.0
            rows.append({
                "match_id": mid,
                "label": 1 if r["status"] == "CONFIRMED" else 0,
                "left": left,
                "right": right,
                "confidence": conf,
                "country": (r.get("item_country") or r.get("fac_country") or "").strip().lower(),
                "train": stable_train_half(mid),
            })
    return rows


def parse_countries(text):
    """Turn "cn,tw, HK" into {"cn", "tw", "hk"} (lowercase ISO codes), or None for no filter."""
    if not text:
        return None
    return {c.strip().lower() for c in text.split(",") if c.strip()}


def only_countries(rows, codes):
    """Keep the rows whose country is in `codes`; with no codes, keep them all. Used to train
    and test a model on one region's pairs only."""
    if not codes:
        return rows
    return [r for r in rows if r.get("country") in codes]


def curate(rows, per_class, hard_share, per_match=None, per_distinct=None, use_surprise=True):
    """Oversample the hard classes; return the selected training pairs.

    per_class is how many pairs to take of each class. per_match and per_distinct override it
    for one class, which changes the mix of matches to non-matches (None keeps per_class).
    use_surprise=False picks the hard pairs by lookalike names alone, without looking at the recorded
    production score (a pair is otherwise also "hard" when that score and the human decision disagree)."""
    rng = random.Random(SEED)
    train = [r for r in rows if r["train"]]
    for r in train:
        r["probe"] = (prefix_len(r["left"]["name"], r["right"]["name"]) >= PREFIX_HARD
                      and r["left"]["name"] != r["right"]["name"])
        r["surprise"] = abs(r["confidence"] - r["label"]) > SURPRISE_MARGIN

    want = {1: per_class if per_match is None else per_match,
            0: per_class if per_distinct is None else per_distinct}

    selected = []
    for label in (0, 1):
        per_class = want[label]            # this class's target size
        n_hard = int(round(per_class * hard_share))
        n_easy = per_class - n_hard
        lab = [r for r in train if r["label"] == label]
        is_hard = (lambda r: r["probe"] or r["surprise"]) if use_surprise else (lambda r: r["probe"])
        hard = [r for r in lab if is_hard(r)]
        easy = [r for r in lab if not is_hard(r)]
        rng.shuffle(hard)
        rng.shuffle(easy)
        # Backfill in BOTH directions. The negative class is almost all hard
        # (pick-one rejects are near-identical names, so nearly every one is a
        # lookalike), while the positive class is mostly easy -- a one-way
        # backfill silently returns a short class for whichever pool runs dry.
        take_hard = hard[:n_hard]
        take_easy = easy[:n_easy]
        short = per_class - len(take_hard) - len(take_easy)
        if short > 0:
            take_hard += hard[len(take_hard):len(take_hard) + short]
            short = per_class - len(take_hard) - len(take_easy)
        if short > 0:
            take_easy += easy[len(take_easy):len(take_easy) + short]
        selected += take_hard + take_easy
    return train, selected


def eval_overlap(selected, eval_set_path):
    """How many of the selected training pairs are also in the frozen evaluation set.

    Training on a pair and then scoring it makes a model look better than it is, so this
    should be 0. The training half and the evaluation half come from opposite sides of the
    same hash of match_id, so it is 0 by construction; this reads the real evaluation file
    to show that rather than assume it."""
    with open(eval_set_path, newline="") as f:
        evaluated = {row["match_id"] for row in csv.DictReader(f)}
    return sum(1 for r in selected if r["match_id"] in evaluated)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pairs", required=True, help="labeled pairs CSV")
    p.add_argument("--out", default=DEFAULT_OUT, help="training.json path")
    p.add_argument("--per-class", type=int, default=3000,
                   help="training pairs per class (default 3000)")
    p.add_argument("--per-match", type=int,
                   help="matches to take, instead of --per-class (changes the match to non-match mix)")
    p.add_argument("--per-distinct", type=int,
                   help="non-matches to take, instead of --per-class (changes the match to non-match mix)")
    p.add_argument("--hard-share", type=float, default=2.0 / 3.0,
                   help="share of each class drawn from the hard pool")
    p.add_argument("--eval-set", help="frozen eval_set.csv: print how many selected pairs are in it "
                                      "and refuse to write if any are")
    p.add_argument("--countries", help="comma-separated country codes: use only these countries' pairs "
                                       "(to train a regional model)")
    p.add_argument("--auto-size", action="store_true",
                   help="shrink --per-class to what the (filtered) pool can supply in BOTH classes, so a "
                        "small region still gets balanced classes")
    p.add_argument("--no-surprise", action="store_true",
                   help="pick hard pairs by lookalike names only, not by whether the recorded production score "
                        "disagreed with the human")
    p.add_argument("--ids-out", help="also write the match_id of every selected pair here, one per line, so uploads "
                                     "containing them can be left out of a comparison")
    p.add_argument("--dry-run", action="store_true",
                   help="report composition, write nothing")
    args = p.parse_args(argv)

    rows = load_pairs(args.pairs)
    if not rows:
        sys.exit(f"no usable rows in {args.pairs}")
    rows = only_countries(rows, parse_countries(args.countries))
    if not rows:
        sys.exit(f"no pairs for countries {args.countries}")
    per_class = args.per_class
    if args.auto_size:
        pool = [r for r in rows if r["train"]]
        per_class = min(per_class, sum(r["label"] == 1 for r in pool), sum(r["label"] == 0 for r in pool))
        print(f"auto size             : {per_class} per class")
    train, selected = curate(rows, per_class, args.hard_share, args.per_match, args.per_distinct,
                             use_surprise=not args.no_surprise)

    match = [r for r in selected if r["label"] == 1]
    distinct = [r for r in selected if r["label"] == 0]

    print(f"pairs read            : {len(rows)}")
    print(f"train half (by hash)  : {len(train)}")
    print(f"selected              : {len(match)} match / {len(distinct)} distinct")
    print(f"  lookalike (probe)   : {sum(1 for r in selected if r['probe'])}")
    print(f"  model/human dispute : {sum(1 for r in selected if r['surprise'])}")
    if args.eval_set:
        overlap = eval_overlap(selected, args.eval_set)
        print(f"overlap with eval set : {overlap} of {len(selected)} selected pairs")
        if overlap:
            sys.exit("refusing to write: training pairs are also in the evaluation set")
    if not match or not distinct:
        sys.exit("refusing to write: one class is empty")

    training = {
        "match": [{"__class__": "tuple", "__value__": [r["left"], r["right"]]}
                  for r in match],
        "distinct": [{"__class__": "tuple", "__value__": [r["left"], r["right"]]}
                     for r in distinct],
    }
    if args.dry_run:
        print("dry run: nothing written")
        return
    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(training, f)
    print(f"wrote {out} ({os.path.getsize(out) / 1024:.0f} KB)")
    if args.ids_out:
        with open(args.ids_out, "w") as f:
            f.write("\n".join(sorted(r["match_id"] for r in selected)) + "\n")
        print(f"wrote {len(selected)} match_ids to {args.ids_out}")


if __name__ == "__main__":
    main()
