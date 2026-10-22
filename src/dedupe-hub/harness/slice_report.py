#!/usr/bin/env python3
"""Per-slice report on labeled pairs. OSDEV-3277 AC#2 / AC#3.

evaluate.py reports one set of numbers for the whole held-out half. This reports
the same kind of numbers for each named slice (see slices.py), so a regression
in one country cannot be averaged away by gains elsewhere.

For every model and slice, at one operating point (--auto, --floor), each
held-out pair lands in exactly one cell, so the shares add up to 100%:

  auto ok     score >= auto bar  and the human said match
  auto bad    score >= auto bar  and the human rejected it   (a wrong merge)
  review      floor <= score < auto bar                      (goes to a human)
  missed      score <  floor     and the human said match    (a duplicate)
  none ok     score <  floor     and the human rejected it

plus precision at the bar, recall at the bar, recall at the floor, and a 95%
margin (Wilson, in percentage points) on each rate so a thin slice is visibly
thin.

LIMITS, read before quoting a number:
  * Pairwise, not per upload. Every pair was the incumbent matcher's own
    candidate, so "missed" here means "scored below the floor", NOT "never
    retrieved". Retrieval misses and per-upload rates (auto-match, new-facility)
    need measure_fanout.py on sampled uploads.
  * Labels are moderator decisions, a proxy for truth. "auto bad" counts
    arbitration rejects as errors unless you use the CLEAN view; read both.
  * The margin covers sampling error on this held-out set only. It does not
    cover run-to-run model variation; measure that by running the model several
    times and comparing the CSV output.

Pure stdlib, like evaluate.py.

Usage:
  python3 slice_report.py --pairs pairs.csv --flags pick_one_flags.csv \
      --scores "retrain=candidate_scores.csv" [--scores "base112=...csv"] \
      [--auto 0.8] [--floor 0.5] [--min-n 200] [--csv out.csv]

`prod` (the `confidence` column in the pairs file) is always included. The
default operating point is production's, 0.8 / 0.5.
"""
import argparse
import csv
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from evaluate import (  # noqa: E402
    PROD_AUTO, PROD_GAZ, attach_flags, attach_scores, auc, load_pairs)
from slices import assign  # noqa: E402

NAN = float("nan")


def wilson_half(k, n, z=1.96):
    """Half-width of the Wilson 95% interval for k successes out of n."""
    if n <= 0:
        return NAN
    p = k / n
    denom = 1 + z * z / n
    return z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom


def measure(rows, col, auto, floor):
    sub = [r for r in rows if col in r]
    n = len(sub)
    if not n:
        return None
    pos = sum(r["label"] for r in sub)
    auto_ok = sum(1 for r in sub if r[col] >= auto and r["label"] == 1)
    auto_bad = sum(1 for r in sub if r[col] >= auto and r["label"] == 0)
    review = sum(1 for r in sub if floor <= r[col] < auto)
    missed = sum(1 for r in sub if r[col] < floor and r["label"] == 1)
    none_ok = sum(1 for r in sub if r[col] < floor and r["label"] == 0)
    at_floor = sum(1 for r in sub if r[col] >= floor and r["label"] == 1)
    n_auto = auto_ok + auto_bad
    return {
        "n": n,
        "n_pos": pos,
        "n_neg": n - pos,
        "auc": auc([(r["label"], r[col]) for r in sub]),
        "auto_ok": auto_ok,
        "auto_bad": auto_bad,
        "review": review,
        "missed": missed,
        "none_ok": none_ok,
        "precision_auto": auto_ok / n_auto if n_auto else NAN,
        "precision_auto_pm": wilson_half(auto_ok, n_auto),
        "recall_auto": auto_ok / pos if pos else NAN,
        "recall_auto_pm": wilson_half(auto_ok, pos),
        "recall_floor": at_floor / pos if pos else NAN,
        "recall_floor_pm": wilson_half(at_floor, pos),
    }


def pct(x, width=6):
    return f"{'n/a':>{width}s}" if x != x else f"{x * 100:{width}.1f}"


def print_table(model, mode, slices, col, auto, floor):
    print(f"\n=== {model} | {mode} labels | auto >= {auto}, floor {floor} ===")
    print(f"{'slice':24s} {'n':>6s} {'pos':>5s} {'AUC':>6s} | "
          f"{'autoOK%':>7s} {'autoBAD%':>8s} {'review%':>7s} {'missed%':>7s} "
          f"{'noneOK%':>7s} | {'prec%':>6s} {'+-':>4s} {'rec@auto%':>9s} "
          f"{'+-':>4s} {'rec@floor%':>10s} {'+-':>4s} | {'#bad':>5s}")
    for name, rows in slices.items():
        m = measure(rows, col, auto, floor)
        if m is None or m["n"] == 0:
            print(f"{name:24s} {0:6d}  (no pairs)")
            continue
        n = m["n"]
        print(f"{name:24s} {n:6d} {m['n_pos']:5d} "
              f"{('n/a' if m['auc'] != m['auc'] else format(m['auc'], '.3f')):>6s} | "
              f"{pct(m['auto_ok'] / n, 7)} {pct(m['auto_bad'] / n, 8)} "
              f"{pct(m['review'] / n, 7)} {pct(m['missed'] / n, 7)} "
              f"{pct(m['none_ok'] / n, 7)} | "
              f"{pct(m['precision_auto'])} {pct(m['precision_auto_pm'], 4)} "
              f"{pct(m['recall_auto'], 9)} {pct(m['recall_auto_pm'], 4)} "
              f"{pct(m['recall_floor'], 10)} {pct(m['recall_floor_pm'], 4)} | "
              f"{m['auto_bad']:5d}")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pairs", required=True)
    p.add_argument("--flags", help="pick_one_flags.csv; enables the CLEAN view")
    p.add_argument("--scores", action="append", default=[], metavar="NAME=PATH",
                   help="repeatable; scores from verify_retrain.py")
    p.add_argument("--auto", type=float, default=PROD_AUTO,
                   help=f"auto bar (default {PROD_AUTO}, production's)")
    p.add_argument("--floor", type=float, default=PROD_GAZ,
                   help=f"candidate floor (default {PROD_GAZ}, production's)")
    p.add_argument("--min-n", type=int, default=200,
                   help="also list every other country with at least this many "
                        "held-out pairs (default 200)")
    p.add_argument("--csv", help="write long-format results here (model, labels, "
                                 "slice, metric, value)")
    args = p.parse_args()

    rows = load_pairs(args.pairs)
    models = [("prod", "prod")]
    for spec in args.scores:
        name, _, path = spec.partition("=")
        attach_scores(rows, path, name)
        models.append((name, name))
    if args.flags:
        attach_flags(rows, args.flags)

    test = [r for r in rows if not r["train"]]
    print(f"held-out half (stable match_id hash): {len(test)} of {len(rows)} pairs")
    print("pairwise view: every pair was the incumbent's own candidate; see the "
          "LIMITS note in the docstring.")

    views = [("all", test)]
    if args.flags:
        clean = [r for r in test if not (r["label"] == 0 and r["pick_one"])]
        views = [("clean", clean)] + views
    else:
        print("no --flags given: reporting ALL labels only (raw REJECTED = "
              "negative, the conservative bound)")

    out_rows = []
    for mode, data in views:
        slices = assign(data, min_n=args.min_n)
        for model, col in models:
            print_table(model, mode, slices, col, args.auto, args.floor)
            for sname, srows in slices.items():
                m = measure(srows, col, args.auto, args.floor)
                if m is None:
                    continue
                for metric, value in m.items():
                    out_rows.append((model, mode, sname, metric, value))

    if args.csv:
        with open(args.csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["model", "labels", "slice", "metric", "value"])
            w.writerows(out_rows)
        print(f"\nwrote {len(out_rows)} rows to {args.csv}")


if __name__ == "__main__":
    main()
