#!/usr/bin/env python3
"""Train the production Gazetteer config against a candidate training.json and
score a labeled pair file with it. OSDEV-3277 AC#1 and AC#3.

Deliberately mirrors gazetteer_train.py exactly -- same three fields, same
sample size, same call order -- so a green run here is evidence the service
will cold-start on this training.json with no code change. Times the train so
the startup-cost half of AC#3 is measured rather than asserted.

Optionally (--retrieval-out) also runs a RETRIEVAL CHECK. Scoring a pair tells
you what the model thinks of it, but not whether the learned search rules would
ever have compared the two records in the first place. The check indexes the
facility side of the evaluation pairs, runs every upload side against that
index with the score cutoff at zero, and records whether each pair's own
facility came back as a candidate. A human-approved pair that does not come back
is one the model would never have considered: a duplicate. It is an
approximation of the real thing, because the index holds the evaluation
facilities rather than the whole registry; whether two records share a search
key mostly does not depend on the other facilities, but the fuzzy word-weight
rules use corpus statistics and can shift a little.

Randomness: the 15,000-pair sample and the record samples that decide which
search rules are learned are drawn at random. --seed (default 42) fixes Python's
and numpy's generators so a run can be repeated. For full repeatability also pass
`-e PYTHONHASHSEED=0` to docker run, which fixes the order dedupe iterates its
string sets in. This changes only this harness, never the service.

Runs inside the api-app image (dedupe 1.9.4, no pandas/sklearn):

  docker run --rm -e PYTHONHASHSEED=0 -e PYTHONWARNINGS=ignore::FutureWarning \
    -v "$PWD/src/dedupe-hub":/dh -v "$HOME/osdev-3277/data":/data \
    --entrypoint python api-app:latest \
    /dh/harness/verify_retrain.py --pairs /data/pairs.csv \
      --training /dh/api/app/data/training.json --out /data/scores.csv \
      [--eval-set /data/eval_set.csv --retrieval-out /data/retrieval.csv \
       --retrieval-limit 3000 | --retrieval-all]
"""
import argparse
import csv
import json
import os
import resource
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_training_json import (can_score, only_countries, parse_countries, record,  # noqa: E402
                                stable_train_half)

# The production field config. Do not edit here -- OSDEV-3277 is label-only;
# if these drift from gazetteer_train.py the verification is meaningless.
FIELDS = [
    {"field": "country", "type": "Exact"},
    {"field": "name", "type": "String"},
    {"field": "address", "type": "String"},
]
SAMPLE_SIZE = 15000
MESSY_PREFIX = "ev-m-"      # ids for upload records in the retrieval check
CANON_PREFIX = "ev-c-"      # ids for facility records in the retrieval check


def load(path):
    """Read the labeled pairs CSV into scoreable rows, skipping any pair that
    make_training_json.can_score() rejects (a name is empty, or both sides are
    empty in the same field).

    The email scrub in record() can empty a cell that held only a contact
    email, and dedupe's affine-gap distance raises ZeroDivisionError when asked
    to compare two empty strings. The skipped count is printed so the loss is
    visible rather than silent.
    """
    rows = []
    seen = set()
    skipped = 0
    with open(path) as f:
        for r in csv.DictReader(f):
            mid = r["match_id"]
            if mid in seen:
                continue
            seen.add(mid)
            left = record(r.get("item_clean_name") or r.get("item_name"),
                          r.get("item_clean_address") or r.get("item_address"),
                          r.get("item_country"))
            right = record(r.get("fac_name"), r.get("fac_address"),
                           r.get("fac_country"))
            if not can_score(left, right):
                skipped += 1
                continue
            rows.append({"match_id": mid,
                         "label": 1 if r["status"] == "CONFIRMED" else 0,
                         "left": left, "right": right,
                         "country": (r.get("item_country") or r.get("fac_country") or "").strip().lower(),
                         "train": stable_train_half(mid)})
    if skipped:
        print(f"skipped {skipped} pair(s) that cannot be scored (a name is empty, "
              f"or both sides are empty in a field after cleaning)", flush=True)
    return rows


def rss_mb():
    """Peak memory of this process in MB (ru_maxrss is KB on Linux, bytes on
    macOS; the container runs Linux)."""
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def eval_rows_for(rows, eval_set_path, all_pairs=False):
    """The rows the retrieval check runs on: every pair if all_pairs is set (the
    per-upload page needs this), else the pairs in the frozen eval set if one is
    given, otherwise the held-out half chosen by the match_id hash."""
    if all_pairs:
        return list(rows)
    if eval_set_path:
        with open(eval_set_path, newline="") as f:
            ids = {r["match_id"] for r in csv.DictReader(f)}
        return [r for r in rows if r["match_id"] in ids]
    return [r for r in rows if not r["train"]]


def retrieval_results(gaz, messy, canonical, progress=5000):
    """Run a trained gazetteer's search over an indexed corpus.

    Indexes `canonical`, matches every record in `messy` with the score cutoff at
    zero (so every candidate the learned search rules retrieve comes back, not
    only high-scoring ones) and returns {messy id: {canonical id: score}}.
    An upload that retrieves nothing is simply absent from the result.
    """
    gaz.index(canonical)
    found = {}
    results = gaz.match(messy, threshold=0.0, n_matches=None, generator=True)
    for n, matches in enumerate(results, 1):
        # dedupe yields a numpy structured array per upload, so test emptiness
        # with len() (see measure_fanout.py).
        if len(matches) == 0:
            continue
        mid = str(matches[0][0][0])
        found[mid] = {str(cid): float(s) for (_, cid), s in matches}
        if n % progress == 0:
            print(f"  retrieval: {n} uploads matched", flush=True)
    return found


def retrieval_rows(eval_rows, found):
    """One (match_id, retrieved 0/1, score) row per evaluation pair: did the
    pair's own facility come back among the candidates, and with what score."""
    out = []
    for r in eval_rows:
        score = found.get(MESSY_PREFIX + r["match_id"], {}).get(CANON_PREFIX + r["match_id"])
        out.append((r["match_id"], int(score is not None),
                    "" if score is None else "%.6f" % score))
    return out


def read_extra_pairs(path):
    """Read a CSV of pairs to score after training (columns: row, label, country_left, name_left, address_left,
    country_right, name_right, address_right), cleaned the way training pairs are. Pairs that cannot be scored
    (an empty name, say) are skipped. Returns a list of dicts with row, label, left and right."""
    out = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            left = record(r["name_left"], r["address_left"], r["country_left"])
            right = record(r["name_right"], r["address_right"], r["country_right"])
            if can_score(left, right):
                out.append({"row": r["row"], "label": r["label"], "left": left, "right": right})
    return out


def cross_country_rows(ev_rows, found, floor=0.5, bar=0.8):
    """For each upload in the retrieval check, how many candidates came from a DIFFERENT country than the upload.

    Production's search is not filtered by country, so whether another country's facilities are offered depends on
    the learned search rules and on how the model scores them. Returns (match_id, cross_retrieved, cross_at_floor,
    cross_at_bar, top_cross_score, same_country_retrieved) per upload: counts of other-country candidates returned
    at all, scoring at or above `floor`, and scoring above `bar`, the best such score (blank if none), and the
    number of same-country candidates returned, for scale."""
    canon_country = {CANON_PREFIX + r["match_id"]: r["right"]["country"] for r in ev_rows}
    out = []
    for r in ev_rows:
        cands = found.get(MESSY_PREFIX + r["match_id"], {})
        cross = [sc for cid, sc in cands.items() if canon_country.get(cid) != r["left"]["country"]]
        same = len(cands) - len(cross)
        out.append((r["match_id"], len(cross), sum(sc >= floor for sc in cross), sum(sc > bar for sc in cross),
                    "" if not cross else "%.6f" % max(cross), same))
    return out


def main():
    """Train the model on --training, score every pair, and optionally run the
    retrieval check on the evaluation pairs."""
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pairs", required=True)
    p.add_argument("--training", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--seed", type=int, default=42,
                   help="seed for Python's and numpy's random generators (default 42)")
    p.add_argument("--alpha", type=float,
                   help="force the scoring model's regularization to this value and skip the "
                        "cross-validation that normally picks it (one of 0.00001, 0.0001, "
                        "0.001, 0.01, 0.1, 1). Shows each possible scoring model in turn")
    p.add_argument("--model-out", help="write the fitted scoring model (regularization, "
                                       "bias, weights) and the learned search rules here, "
                                       "so two runs can be compared with diff")
    p.add_argument("--eval-set", help="frozen eval_set.csv: run the retrieval check "
                                      "on exactly these pairs (default: held-out half)")
    p.add_argument("--countries", help="comma-separated country codes: train, score and test on only "
                                       "these countries' pairs (a regional model)")
    p.add_argument("--retrieval-all", action="store_true",
                   help="run the retrieval check on EVERY pair in --pairs instead of the "
                        "evaluation pairs (needed by upload_page.py, which uses all uploads)")
    p.add_argument("--retrieval-out", help="write the retrieval check here "
                                           "(match_id, retrieved, score)")
    p.add_argument("--extra-pairs-csv", help="a CSV of extra pairs to score with the trained model (see read_extra_pairs)")
    p.add_argument("--extra-out", help="where to write the extra pairs' scores (row, label, score)")
    p.add_argument("--cross-country-out", help="with --retrieval-out: also write, per upload, how many candidates "
                                               "came from another country (and how high they scored)")
    p.add_argument("--retrieval-limit", type=int, default=0,
                   help="check only this many pairs, chosen by a fixed hash of "
                        "match_id (0 = all). For a quick trial; the report only "
                        "uses a retrieval file that covers every evaluation pair")
    args = p.parse_args()

    import random
    import numpy
    random.seed(args.seed)
    numpy.random.seed(args.seed)
    if os.environ.get("PYTHONHASHSEED") is None:
        print("note: PYTHONHASHSEED is not set; pass -e PYTHONHASHSEED=0 to docker run "
              "for fully repeatable rule learning", flush=True)

    rows = only_countries(load(args.pairs), parse_countries(args.countries))
    if not rows:
        sys.exit(f"no pairs for countries {args.countries}")
    train = [r for r in rows if r["train"]]
    print(f"pairs {len(rows)}  train-half {len(train)}  seed {args.seed}", flush=True)

    with open(args.training) as f:
        t = json.load(f)
    print(f"training.json: {len(t['match'])} match / {len(t['distinct'])} distinct",
          flush=True)

    from dedupe import Gazetteer

    messy = {str(i): r["left"] for i, r in enumerate(train)}
    canonical = {"c" + str(i): r["right"] for i, r in enumerate(train)}

    t0 = time.time()
    gaz = Gazetteer(FIELDS)
    print("sampling...", flush=True)
    gaz.sample(messy, canonical, SAMPLE_SIZE)
    t_sample = time.time() - t0

    print("reading training...", flush=True)
    with open(args.training) as f:
        gaz.readTraining(f)
    t_read = time.time() - t0 - t_sample

    print("training...", flush=True)
    gaz.train()
    t_train = time.time() - t0 - t_sample - t_read

    print(f"\n== AC#3 cold-start cost (train only, excludes indexing) ==")
    print(f"  sample({SAMPLE_SIZE}) : {t_sample:7.1f}s")
    print(f"  readTraining    : {t_read:7.1f}s")
    print(f"  train()         : {t_train:7.1f}s")
    print(f"  TOTAL           : {t_sample + t_read + t_train:7.1f}s")
    print(f"  peak RSS        : {rss_mb():7.0f} MB", flush=True)

    if args.alpha is not None:
        from dedupe.api import flatten_training
        examples, labels = flatten_training(gaz.training_pairs)
        gaz.classifier.alpha = args.alpha
        gaz.classifier.fit(gaz.data_model.distances(examples), numpy.array(labels), cv=False)
        print(f"\n  scoring model refit with alpha forced to {args.alpha} "
              f"(cross-validation skipped)", flush=True)

    clf = gaz.classifier
    summary = [
        f"regularization alpha (picked by cross-validation): {clf.alpha}",
        f"bias: {float(clf.bias):.8f}",
        "weights: " + ", ".join("%.8f" % float(w) for w in clf.weights),
        f"search rules learned: {len(gaz.predicates)}",
    ]
    print("\n== fitted scoring model ==")
    for line in summary:
        print("  " + line)
    if args.model_out:
        with open(args.model_out, "w") as f:
            f.write("\n".join(summary) + "\n")
            for pred in gaz.predicates:
                f.write(str(pred) + "\n")
        print(f"  wrote model and rules to {args.model_out}", flush=True)

    dists = gaz.data_model.distances([(r["left"], r["right"]) for r in rows])
    probs = gaz.classifier.predict_proba(dists)
    try:
        probs = probs[:, -1]
    except (IndexError, TypeError):
        pass

    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["match_id", "retrained_conf"])
        for r, s in zip(rows, probs):
            w.writerow([r["match_id"], float(s)])
    print(f"wrote {args.out} ({len(rows)} rows)", flush=True)

    if args.extra_pairs_csv and args.extra_out:
        extra = read_extra_pairs(args.extra_pairs_csv)
        eprobs = gaz.classifier.predict_proba(gaz.data_model.distances([(e["left"], e["right"]) for e in extra]))
        try:
            eprobs = eprobs[:, -1]
        except (IndexError, TypeError):
            pass
        with open(args.extra_out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["row", "label", "score"])
            for e, sc in zip(extra, eprobs):
                w.writerow([e["row"], e["label"], "%.6f" % float(sc)])
        print(f"wrote {args.extra_out} ({len(extra)} extra pairs scored)", flush=True)

    if args.retrieval_out:
        ev = eval_rows_for(rows, args.eval_set, args.retrieval_all)
        if args.retrieval_limit:
            # A seeded random sample. Do NOT take the smallest md5 hashes: the
            # pairs file was itself pulled by keeping the smallest md5 per
            # country, so low hashes over-represent the big, capped countries.
            ev = sorted(ev, key=lambda r: int(r["match_id"]) if r["match_id"].isdigit()
                        else r["match_id"])
            ev = random.Random(args.seed).sample(ev, min(args.retrieval_limit, len(ev)))
        print(f"\nretrieval check on {len(ev)} evaluation pairs...", flush=True)
        t1 = time.time()
        found = retrieval_results(
            gaz,
            {MESSY_PREFIX + r["match_id"]: r["left"] for r in ev},
            {CANON_PREFIX + r["match_id"]: r["right"] for r in ev})
        if args.cross_country_out:
            cc = cross_country_rows(ev, found)
            with open(args.cross_country_out, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["match_id", "cross_retrieved", "cross_at_floor", "cross_above_bar", "top_cross_score", "same_retrieved"])
                w.writerows(cc)
            up = len(cc)
            print(f"  uploads offered a candidate from another country: {sum(1 for r in cc if r[1])} of {up} "
                  f"({sum(1 for r in cc if r[1]) / up:.1%}); scoring >= 0.5: {sum(1 for r in cc if r[2])}; > 0.8: {sum(1 for r in cc if r[3])}",
                  flush=True)
        out_rows = retrieval_rows(ev, found)
        with open(args.retrieval_out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["match_id", "retrieved", "score"])
            w.writerows(out_rows)
        got = {mid: flag for mid, flag, _ in out_rows}
        pos = [r for r in ev if r["label"] == 1]
        pos_got = sum(got[r["match_id"]] for r in pos)
        print(f"  confirmed pairs retrieved: {pos_got} of {len(pos)} "
              f"({pos_got / len(pos):.1%})" if pos else "  no confirmed pairs checked")
        neg = [r for r in ev if r["label"] == 0]
        neg_got = sum(got[r["match_id"]] for r in neg)
        print(f"  rejected pairs retrieved:  {neg_got} of {len(neg)} "
              f"({neg_got / len(neg):.1%})" if neg else "  no rejected pairs checked")
        print(f"  all pairs retrieved:       {sum(got.values())} of {len(ev)} "
              f"({sum(got.values()) / len(ev):.1%})")
        print(f"  took {time.time() - t1:.0f}s; wrote {args.retrieval_out}", flush=True)


if __name__ == "__main__":
    main()
