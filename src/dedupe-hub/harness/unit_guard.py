#!/usr/bin/env python3
"""Unit-suffix guard: refuse to AUTO-match two facilities whose names are the
same except for a unit designator ("UNIT 2" vs "UNIT 4", "Unit A" vs "Unit B").

Why this exists. OS Hub moderation policy treats a processing distinction as a
SEPARATE facility -- Unit A and Unit B at one industrial address are two
records, not one. The label-only retrain (OSDEV-3277) measurably regresses on
exactly this class (lookalike-probe AUC 0.8903 -> 0.8759) while simultaneously
raising the auto-match rate, so unit-suffix pairs start landing in the
unreviewed auto band. A blanket-higher AUTOMATIC_THRESHOLD would fix this by
throwing away the retrain's real recall wins; this guard targets only the
failing class.

The guard DEMOTES rather than rejects: a blocked pair is not discarded, it
drops from auto-match to potential-match so a moderator sees it. The cost of a
false block is therefore one queue item, not a lost match.

Deliberately conservative -- it fires only when BOTH sides carry a unit
designator and the designators differ. "Acme Ltd" vs "Acme Ltd (Unit 2)" does
NOT fire: a contributor omitting the unit on an otherwise identical name is
usually the same record, and that case belongs to the moderator.

Run the measurement:
  python3 unit_guard.py --pairs .data/pairs_geo.csv \
      --scores .data/osdev3277_scores.csv --auto 0.356
"""
import argparse
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_training_json import stable_train_half  # noqa: E402

# "unit 2", "unit-b", "unit no 3", "unit#4" -- the explicit forms.
UNIT_RE = re.compile(r"\bunit\s*(?:no\.?|#|-)?\s*([0-9]{1,3}|[a-z])\b")
# Trailing bare designator in brackets: "(2)", "(b)", "[unit 2]" handled above.
PAREN_RE = re.compile(r"\(\s*([0-9]{1,3}|[a-z])\s*\)\s*$")
PUNCT_RE = re.compile(r"[^a-z0-9\s]+")
WS_RE = re.compile(r"\s+")


def normalize(name: str) -> str:
    return WS_RE.sub(" ", PUNCT_RE.sub(" ", (name or "").lower())).strip()


ROMAN = {"i": 1, "v": 5, "x": 10, "ii": 2, "iii": 3, "iv": 4,
         "vi": 6, "vii": 7, "viii": 8, "ix": 9}


def canonical_designator(tok: str):
    """All readings of one designator token.

    "04" and "4" are the same unit written differently; so are "i" and "1".
    But "i" might equally be the letter I, and "v" the letter V, so a token
    keeps BOTH readings and two designators count as equal when their readings
    overlap. Without this the guard fires on Unit 04 vs Unit 4 -- which was 6
    of its first 6 false positives, every one a notation variant.
    """
    tok = tok.strip().lower()
    readings = {tok}
    if tok.isdigit():
        readings.add(int(tok))        # "04" -> 4
    elif tok in ROMAN:
        readings.add(ROMAN[tok])      # "i" -> 1, keeping "i" as a letter too
    return readings


def designators(name: str):
    """Unit designators in a name, as a list of reading-sets."""
    raw = (name or "").lower()
    found = set(UNIT_RE.findall(raw))
    m = PAREN_RE.search(raw.strip())
    if m:
        found.add(m.group(1))
    return [canonical_designator(t) for t in found]


def _same_unit(da, db) -> bool:
    """True if any designator on one side can be read as one on the other."""
    return any(a & b for a in da for b in db)


def base_name(name: str) -> str:
    """The name with unit designators stripped, for comparing the stems."""
    raw = (name or "").lower()
    raw = UNIT_RE.sub(" ", raw)
    raw = PAREN_RE.sub(" ", raw.strip())
    raw = re.sub(r"\bunit\b", " ", raw)
    return normalize(raw)


def blocks(name_a: str, name_b: str) -> bool:
    """True when the pair must not be auto-matched.

    Fires only if both sides carry a unit designator, those designators are
    disjoint, and the remaining name stems are identical.
    """
    da, db = designators(name_a), designators(name_b)
    if not da or not db:
        return False
    if _same_unit(da, db):           # share a designator -> same unit
        return False
    ba, bb = base_name(name_a), base_name(name_b)
    if not ba or not bb:
        return False
    return ba == bb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--scores", required=True)
    ap.add_argument("--flags", help="pick_one_flags.csv; enables clean labels")
    ap.add_argument("--auto", type=float, default=0.356)
    ap.add_argument("--show", type=int, default=12)
    args = ap.parse_args()

    scores = {}
    with open(args.scores) as f:
        for r in csv.DictReader(f):
            scores.setdefault(r["match_id"], float(r["retrained_conf"]))

    pick_one = {}
    if args.flags:
        with open(args.flags) as f:
            for r in csv.DictReader(f):
                pick_one[r["match_id"]] = \
                    str(r["pick_one"]).lower() in ("true", "t", "1")

    rows = []
    with open(args.pairs) as f:
        for r in csv.DictReader(f):
            mid = r["match_id"]
            if mid not in scores or stable_train_half(mid):
                continue             # held-out half only
            label = 1 if r["status"] == "CONFIRMED" else 0
            # A pick-one reject is not a false match -- the moderator chose a
            # different near-identical sibling. Counting them as negatives
            # inflates the false auto-match rate roughly 20x.
            if args.flags and label == 0 and pick_one.get(mid, False):
                continue
            rows.append({
                "match_id": mid,
                "label": label,
                "score": scores[mid],
                "name_l": r.get("item_clean_name") or r.get("item_name") or "",
                "name_r": r.get("fac_name") or "",
            })

    kind = "CLEAN (pick-one rejects excluded)" if args.flags else "NOISY (raw)"
    print(f"labels                       : {kind}")
    auto = [r for r in rows if r["score"] >= args.auto]
    fired = [r for r in auto if blocks(r["name_l"], r["name_r"])]
    tp = [r for r in fired if r["label"] == 0]   # correctly stopped a bad auto-match
    fp = [r for r in fired if r["label"] == 1]   # wrongly demoted a true match

    # what the auto band looks like without the guard
    auto_bad = [r for r in auto if r["label"] == 0]

    print(f"held-out pairs               : {len(rows)}")
    print(f"auto band (score >= {args.auto}) : {len(auto)} "
          f"({len(auto) / len(rows):.1%} of held-out)")
    print(f"  of which NOT a true match  : {len(auto_bad)} "
          f"({len(auto_bad) / len(auto):.2%} false auto-match rate)")
    print()
    print(f"guard fires on               : {len(fired)} auto-band pairs "
          f"({len(fired) / len(auto):.2%} of the auto band)")
    print(f"  correctly blocked (label=0): {len(tp)}")
    print(f"  wrongly demoted  (label=1) : {len(fp)}")
    if fired:
        print(f"  guard precision            : {len(tp) / len(fired):.1%}")
    if auto_bad:
        print(f"  share of all false auto-matches caught: "
              f"{len(tp) / len(auto_bad):.1%}")
    if auto_bad:
        resid = (len(auto_bad) - len(tp)) / (len(auto) - len(fired))
        print(f"  false auto-match rate after guard     : {resid:.2%} "
              f"(from {len(auto_bad) / len(auto):.2%})")

    def show(label, rs):
        print(f"\n--- {label} ---")
        for r in rs[:args.show]:
            print(f"  {r['score']:.3f}  {r['name_l'][:58]}")
            print(f"         {r['name_r'][:58]}")

    show("CORRECTLY BLOCKED (would have been a bad auto-match)", tp)
    if fp:
        show("WRONGLY DEMOTED (true match sent to the queue)", fp)


if __name__ == "__main__":
    main()
