#!/usr/bin/env python3
"""Translate the lookalike AUC regression into operational harm.

AUC on the probe class is a poor instrument for deciding anything: on clean
labels that subset is ~98% positive, so the number rests on ~70 negatives. And
for THIS class the pick-one rejects that clean labels drop are the signal --
they are the wrong-sibling cases. So measure the thing we actually care about:
at each model's OWN operating point, how many lookalike pairs get auto-matched
when they should not have been?

Also measures exposure: production decides per item by taking the top
candidate, so a ranking error is recoverable only when there is something to
rank against. An item whose ONLY retrieved candidate is the wrong sibling has
no ranking step at all -- gating decides alone. Fan-out p50 is 1, so that path
is common, and it is where a gating regression actually bites.
"""
import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_training_json import prefix_len, stable_train_half  # noqa: E402

PROBE_PREFIX = 12


def load_scores(path):
    d = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            d.setdefault(r["match_id"], float(r["retrained_conf"]))
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--flags", required=True)
    ap.add_argument("--retrained", required=True)
    ap.add_argument("--auto-retrained", type=float, default=0.356)
    ap.add_argument("--auto-prod", type=float, default=0.8)
    args = ap.parse_args()

    retr = load_scores(args.retrained)
    pick_one = {}
    with open(args.flags) as f:
        for r in csv.DictReader(f):
            pick_one[r["match_id"]] = str(r["pick_one"]).lower() in ("true", "t", "1")

    rows = []
    with open(args.pairs) as f:
        for r in csv.DictReader(f):
            mid = r["match_id"]
            if mid not in retr or stable_train_half(mid):
                continue
            nl = (r.get("item_clean_name") or r.get("item_name") or "").upper()
            nr = (r.get("fac_name") or "").upper()
            rows.append({
                "label": 1 if r["status"] == "CONFIRMED" else 0,
                "prod": float(r["confidence"]),
                "retr": retr[mid],
                "pick_one": pick_one.get(mid, False),
                "probe": prefix_len(nl, nr) >= PROBE_PREFIX and nl != nr,
            })

    probe = [r for r in rows if r["probe"]]

    def harm(subset, title):
        n = len(subset)
        neg = [r for r in subset if r["label"] == 0]
        pos = [r for r in subset if r["label"] == 1]
        if not neg:
            print(f"\n{title}: no negatives, skipping")
            return
        print(f"\n{title}")
        print(f"  pairs {n}   negatives {len(neg)} ({len(neg) / n:.1%})")
        print(f"  {'model':10s} {'bad auto-matches':>18s} {'per 1,000 pairs':>17s} "
              f"{'true matches held':>19s}")
        for name, col, thr in (("prod", "prod", args.auto_prod),
                               ("retrained", "retr", args.auto_retrained)):
            bad = sum(1 for r in neg if r[col] >= thr)
            held = sum(1 for r in pos if r[col] >= thr)
            print(f"  {name:10s} {bad:18d} {bad / n * 1000:17.1f} "
                  f"{held / len(pos):18.1%}")

    harm(probe, "LOOKALIKE CLASS -- clean labels (pick-one excluded)"
         if False else "LOOKALIKE CLASS -- all held-out labels (pick-one INCLUDED)")

    clean_probe = [r for r in probe if not (r["label"] == 0 and r["pick_one"])]
    harm(clean_probe, "LOOKALIKE CLASS -- clean labels (pick-one excluded)")

    nonprobe = [r for r in rows if not r["probe"]]
    harm(nonprobe, "EVERYTHING ELSE -- all held-out labels (for contrast)")

    # how much of the class is pick-one, i.e. wrong-sibling arbitration
    po = sum(1 for r in probe if r["label"] == 0 and r["pick_one"])
    neg = sum(1 for r in probe if r["label"] == 0)
    print(f"\nof {neg} lookalike negatives, {po} ({po / neg:.0%}) are pick-one "
          f"rejects -- the wrong-sibling cases clean labels discard")

    # ---- iso-recall: the only fair comparison ----
    # The two models sit at very different points on the curve (retrained holds
    # far more true matches), so raw bad-auto-match counts are not comparable.
    # Hold recall fixed and ask which model admits fewer bad lookalikes.
    print("\n" + "=" * 68)
    print("ISO-RECALL on the lookalike class (all labels) -- threshold set per")
    print("model so each holds the SAME share of true lookalike matches")
    print("=" * 68)
    pos = [r for r in probe if r["label"] == 1]
    negs = [r for r in probe if r["label"] == 0]

    def thr_for_recall(col, target):
        s = sorted((r[col] for r in pos), reverse=True)
        k = min(len(s) - 1, max(0, int(round(target * len(s))) - 1))
        return s[k]

    print(f"  {'recall held':>12s} {'prod bad':>10s} {'retrained bad':>15s} "
          f"{'change':>10s}")
    for target in (0.70, 0.74, 0.80, 0.85, 0.90, 0.93):
        tp = thr_for_recall("prod", target)
        tr = thr_for_recall("retr", target)
        bp = sum(1 for r in negs if r["prod"] >= tp)
        br = sum(1 for r in negs if r["retr"] >= tr)
        delta = (br - bp) / bp if bp else float("nan")
        print(f"  {target:11.0%} {bp:10d} {br:15d} {delta:9.0%}")


if __name__ == "__main__":
    main()
