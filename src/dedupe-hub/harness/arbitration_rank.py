#!/usr/bin/env python3
"""Within-set ranking on real arbitration sets, overall and for the
unit-suffix class specifically.

Pairwise gating and within-set ranking are different questions. A pick-one
reject sitting in the auto band is NOT automatically a bad write: production
takes the top candidate per item, so what matters is whether the model ranks
the sibling the moderator actually chose above the ones they rejected. That is
unmeasurable pairwise and is exactly where the Unit 2 / Unit 4 risk lives.

Each set is one item with its candidates: status == CONFIRMED is the
moderator's pick, the rest were rejected.

  python3 arbitration_rank.py --sets .data/arbitration_sets.csv \
      --scores "retrained=.data/arb_scores_retrained.csv" \
      --scores "prod=.data/arb_scores_baseline.csv"
"""
import argparse
import csv
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unit_guard import designators, base_name, _same_unit  # noqa: E402


def load_scores(path):
    d = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            d.setdefault(r["match_id"], float(r["retrained_conf"]))
    return d


def is_unit_set(cands):
    """True when the set contains two candidates that are the same business
    distinguished only by a unit designator -- the class the retrain regresses
    on and the one a moderator must not have decided for them."""
    for i in range(len(cands)):
        for j in range(i + 1, len(cands)):
            a, b = cands[i]["fac_name"], cands[j]["fac_name"]
            da, db = designators(a), designators(b)
            if da and db and not _same_unit(da, db) \
                    and base_name(a) == base_name(b) and base_name(a):
                return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", required=True)
    ap.add_argument("--scores", action="append", required=True,
                    metavar="NAME=PATH")
    ap.add_argument("--show", type=int, default=8)
    args = ap.parse_args()

    sets = defaultdict(list)
    with open(args.sets) as f:
        for r in csv.DictReader(f):
            sets[r["item_id"]].append(r)

    models = []
    for spec in args.scores:
        name, _, path = spec.partition("=")
        models.append((name, load_scores(path)))

    usable, unit_sets = [], []
    for iid, cands in sets.items():
        if len(cands) < 2:
            continue
        if sum(1 for c in cands if c["status"] == "CONFIRMED") != 1:
            continue
        usable.append((iid, cands))
        if is_unit_set(cands):
            unit_sets.append((iid, cands))

    print(f"arbitration sets         : {len(sets)}")
    print(f"usable (>=2 cands, 1 pick): {len(usable)}")
    print(f"unit-suffix sets          : {len(unit_sets)} "
          f"({len(unit_sets) / len(usable):.1%} of usable)")

    def top1(subset, scores):
        ok = n = 0
        misses = []
        for iid, cands in subset:
            scored = [(scores.get(c["match_id"]), c) for c in cands]
            scored = [(s, c) for s, c in scored if s is not None]
            if len(scored) < 2:
                continue
            n += 1
            best = max(scored, key=lambda x: x[0])
            if best[1]["status"] == "CONFIRMED":
                ok += 1
            else:
                truth = [c for _, c in scored if c["status"] == "CONFIRMED"]
                misses.append((best, truth[0] if truth else None, scores))
        return (ok / n if n else float("nan")), n, misses

    print(f"\n{'model':12s} {'top-1 all sets':>16s} {'top-1 unit sets':>18s}")
    all_misses = {}
    for name, scores in models:
        a, na, _ = top1(usable, scores)
        u, nu, miss = top1(unit_sets, scores)
        all_misses[name] = miss
        print(f"{name:12s} {a:15.1%} ({na:5d}) {u:14.1%} ({nu:4d})")

    for name, _ in models:
        miss = all_misses[name]
        if not miss:
            continue
        print(f"\n--- {name}: unit-suffix sets where the model picks the "
              f"WRONG unit ({len(miss)}) ---")
        for (bs, bc), truth, sc in miss[:args.show]:
            print(f"  item: {(bc.get('item_clean_name') or bc.get('item_name'))[:62]}")
            print(f"    model picked : {bs:.3f}  {bc['fac_name'][:58]}")
            if truth is not None:
                print(f"    human picked : {sc.get(truth['match_id']):.3f}  "
                      f"{truth['fac_name'][:58]}")


if __name__ == "__main__":
    main()
