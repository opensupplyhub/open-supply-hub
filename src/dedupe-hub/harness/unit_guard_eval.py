#!/usr/bin/env python3
"""Evaluate the unit-suffix guard in its CORRECT form: per item, at the
arbitration layer -- not as a pairwise gate.

The first version of this guard was pairwise and fired on zero clean-label
pairs, because unit-suffix pairs live almost entirely in the pick-one bucket
that clean labels exclude. That was the wrong instrument. Production decides
per ITEM by taking the top candidate, so the guard belongs there.

Two rules, evaluated separately:

  PREFER  -- if the item's own name carries a unit designator and exactly one
             candidate's designator matches it, pick that candidate. Corrective:
             it can fix a wrong top-1, not just suppress it.
  DEMOTE  -- if the top candidates are unit-siblings (same stem, different
             designator) and the item's name does NOT disambiguate, send the
             item to the moderation queue instead of auto-matching. The data
             genuinely does not contain the answer; a human has to pick.

  python3 unit_guard_eval.py --sets .data/arbitration_sets.csv \
      --scores .data/arb_scores_retrained.csv --auto 0.356
"""
import argparse
import csv
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unit_guard import designators, base_name, _same_unit  # noqa: E402


def unit_siblings(a, b):
    da, db = designators(a), designators(b)
    return (bool(da) and bool(db) and not _same_unit(da, db)
            and base_name(a) == base_name(b) and bool(base_name(a)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", required=True)
    ap.add_argument("--scores", required=True)
    ap.add_argument("--auto", type=float, default=0.356)
    args = ap.parse_args()

    scores = {}
    with open(args.scores) as f:
        for r in csv.DictReader(f):
            scores.setdefault(r["match_id"], float(r["retrained_conf"]))

    sets = defaultdict(list)
    with open(args.sets) as f:
        for r in csv.DictReader(f):
            sets[r["item_id"]].append(r)

    base_ok = prefer_ok = demote_n = 0
    fixed, broke, demoted_sets = [], [], []
    n = 0

    for iid, cands in sets.items():
        scored = [(scores.get(c["match_id"]), c) for c in cands]
        scored = [(s, c) for s, c in scored if s is not None]
        if len(scored) < 2:
            continue
        if sum(1 for _, c in scored if c["status"] == "CONFIRMED") != 1:
            continue
        n += 1
        scored.sort(key=lambda x: -x[0])
        top_s, top_c = scored[0]
        correct = top_c["status"] == "CONFIRMED"
        base_ok += correct

        item_name = top_c.get("item_clean_name") or top_c.get("item_name") or ""
        item_d = designators(item_name)

        # --- PREFER ---
        pick_s, pick_c = top_s, top_c
        if item_d:
            matching = [(s, c) for s, c in scored
                        if s >= args.auto and _same_unit(item_d, designators(c["fac_name"]))]
            if len(matching) == 1:
                pick_s, pick_c = matching[0]
        now_correct = pick_c["status"] == "CONFIRMED"
        prefer_ok += now_correct
        if now_correct and not correct:
            fixed.append((item_name, top_c["fac_name"], pick_c["fac_name"]))
        elif correct and not now_correct:
            broke.append((item_name, top_c["fac_name"], pick_c["fac_name"]))

        # --- DEMOTE ---
        above = [c for s, c in scored if s >= args.auto]
        sibling_conflict = any(unit_siblings(above[i]["fac_name"], above[j]["fac_name"])
                               for i in range(len(above))
                               for j in range(i + 1, len(above)))
        if sibling_conflict and not item_d:
            demote_n += 1
            demoted_sets.append((item_name, [c["fac_name"] for c in above],
                                 now_correct))

    print(f"usable arbitration sets      : {n}")
    print(f"\ntop-1 agreement with moderator")
    print(f"  no guard                   : {base_ok / n:.2%}")
    print(f"  with PREFER rule           : {prefer_ok / n:.2%}  "
          f"({len(fixed)} fixed, {len(broke)} broken)")
    print(f"\nDEMOTE rule")
    print(f"  sets sent to queue         : {demote_n} ({demote_n / n:.2%} of sets)")
    wrong_demoted = sum(1 for _, _, ok in demoted_sets if not ok)
    if demote_n:
        print(f"  of those, model was WRONG  : {wrong_demoted}/{demote_n} "
              f"-- these are the saves")
        print(f"  cost: {demote_n - wrong_demoted} correct auto-matches "
              f"become queue items")

    if fixed:
        print(f"\n--- PREFER fixed these ---")
        for item, was, now in fixed[:6]:
            print(f"  item : {item[:62]}")
            print(f"    was: {was[:60]}")
            print(f"    now: {now[:60]}")
    if broke:
        print(f"\n--- PREFER broke these ---")
        for item, was, now in broke[:6]:
            print(f"  item : {item[:62]}")
            print(f"    was: {was[:60]}")
            print(f"    now: {now[:60]}")
    if demoted_sets:
        print(f"\n--- DEMOTE examples (item has no unit; candidates differ) ---")
        for item, facs, ok in demoted_sets[:6]:
            print(f"  item : {item[:62]}   (model was "
                  f"{'right' if ok else 'WRONG'})")
            for fn in facs[:3]:
                print(f"    cand: {fn[:60]}")


if __name__ == "__main__":
    main()
