#!/usr/bin/env python3
"""Score a candidate matcher against the production baseline and re-derive the
two production thresholds. OSDEV-3277 AC#1 and the queue-volume half of AC#2.

Pure stdlib (the api-app image has no pandas) so it runs in the container, on a
laptop, or in CI unchanged.

Two evaluation surfaces, because a single number hides the regression that
matters:
  * AUC over all labeled pairs -- overall gating quality.
  * "probe" AUC over the lookalike class (long shared name prefix, not
    identical: the UNIT A vs UNIT B pairs) -- the class the whole matcher
    evaluation was motivated by, and the one a label-only retrain degrades.

Labels are reported twice:
  * NOISY  -- every non-CONFIRMED row counts as a negative.
  * CLEAN  -- pick-one rejects dropped from the negatives. ~90% of REJECTED
    rows mean "not this near-identical sibling", not "no match"; scoring
    against them measures arbitration, not gating. CLEAN is the headline.

Thresholds are re-derived by matching the production OPERATING POINT rather
than the production number, because a retrained classifier's scores live on a
different scale entirely:
  * AUTOMATIC_THRESHOLD -> the lowest candidate score whose precision is still
    at least the precision prod achieves at its own threshold. Never auto-accept
    at a worse error rate than today.
  * GAZETTEER_THRESHOLD -> the score retaining the same recall over true matches
    that prod retains at its own threshold. Never drop a true match we surface
    today.

Usage:
  python3 evaluate.py --pairs pairs.csv --flags pick_one_flags.csv \
      --scores "retrained=osdev3277_scores.csv" [--scores "other=...csv"]
"""
import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_training_json import prefix_len, stable_train_half  # noqa: E402

PROD_AUTO = 0.8
PROD_GAZ = 0.5
PROBE_PREFIX = 12


def load_pairs(path):
    rows, seen = [], set()
    with open(path) as f:
        for r in csv.DictReader(f):
            mid = r["match_id"]
            if mid in seen:
                continue
            seen.add(mid)
            rows.append({
                "match_id": mid,
                "label": 1 if r["status"] == "CONFIRMED" else 0,
                "prod": float(r["confidence"]),
                "name_l": (r.get("item_clean_name") or r.get("item_name") or "").upper(),
                "name_r": (r.get("fac_name") or "").upper(),
                "train": stable_train_half(mid),
            })
    return rows


def attach_scores(rows, path, col):
    d = {}
    with open(path) as f:
        rd = csv.DictReader(f)
        score_col = "retrained_conf" if "retrained_conf" in rd.fieldnames \
            else rd.fieldnames[-1]
        for r in rd:
            d.setdefault(r["match_id"], float(r[score_col]))
    hit = sum(1 for r in rows if r["match_id"] in d)
    if hit == 0:
        sys.exit(f"{path}: joined 0 rows by match_id -- wrong file or key")
    for r in rows:
        if r["match_id"] in d:
            r[col] = d[r["match_id"]]
    print(f"  {col}: joined {hit}/{len(rows)} by match_id", file=sys.stderr)


def attach_flags(rows, path):
    d = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            d[r["match_id"]] = str(r["pick_one"]).lower() in ("true", "t", "1")
    for r in rows:
        r["pick_one"] = d.get(r["match_id"], False)


def auc(pairs):
    """Rank-based AUC with correct handling of tied scores."""
    pairs = sorted(pairs, key=lambda p: p[1])
    n = len(pairs)
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and pairs[j + 1][1] == pairs[i][1]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[k] = avg
        i = j + 1
    n1 = sum(1 for p in pairs if p[0] == 1)
    n0 = n - n1
    if not n1 or not n0:
        return float("nan")
    s = sum(ranks[k] for k in range(n) if pairs[k][0] == 1)
    return (s - n1 * (n1 + 1) / 2.0) / (n1 * n0)


def auto_share(pairs, precision=0.98):
    d = sorted(pairs, key=lambda p: -p[1])
    cum_fp, ok = 0, []
    for idx, (y, s) in enumerate(d, start=1):
        cum_fp += (1 - y)
        if cum_fp / idx <= 1 - precision:
            ok.append(s)
    thr = min(ok) if ok else 1.0
    return thr, sum(1 for y, s in d if s >= thr) / len(d)


def best_accuracy(pairs):
    cands = sorted({round(s, 3) for _, s in pairs})
    best = (0.0, 0.0)
    for t in cands:
        tp = sum(1 for y, s in pairs if s >= t and y == 1)
        tn = sum(1 for y, s in pairs if s < t and y == 0)
        acc = (tp + tn) / len(pairs)
        if acc > best[0]:
            best = (acc, t)
    return best


def precision_at(data, col, thr):
    sel = [r for r in data if r[col] >= thr]
    return (sum(r["label"] for r in sel) / len(sel) if sel else float("nan")), len(sel)


def recall_at(data, col, thr):
    pos = [r for r in data if r["label"] == 1]
    return sum(1 for r in pos if r[col] >= thr) / len(pos)


def lowest_thr_meeting_precision(data, col, target):
    d = sorted(data, key=lambda r: -r[col])
    tp = n = 0
    best = None
    for r in d:
        n += 1
        tp += r["label"]
        if tp / n >= target:
            best = r[col]
    return best


def thr_meeting_recall(data, col, target):
    d = sorted(data, key=lambda r: -r[col])
    pos_total = sum(r["label"] for r in data)
    tp = 0
    for r in d:
        tp += r["label"]
        if tp / pos_total >= target:
            return r[col]
    return min(r[col] for r in data)


def bands(data, col, auto, gaz):
    t = len(data)
    a = sum(1 for r in data if r[col] >= auto)
    p = sum(1 for r in data if gaz <= r[col] < auto)
    return a / t, p / t, (t - a - p) / t


def report(rows, models, title):
    probe = [r for r in rows
             if prefix_len(r["name_l"], r["name_r"]) >= PROBE_PREFIX
             and r["name_l"] != r["name_r"]]
    pos = sum(r["label"] for r in rows) / len(rows)
    print(f"\n== {title}: {len(rows)} pairs ({pos:.0%} confirmed), probe {len(probe)}")
    print(f"{'model':34s} {'AUC':>7s} {'probeAUC':>9s} {'auto@98%':>9s} "
          f"{'bestAcc':>8s} {'n':>7s}")
    for name, col in models:
        sub = [(r["label"], r[col]) for r in rows if col in r]
        if not sub:
            continue
        psub = [(r["label"], r[col]) for r in probe if col in r]
        _, share = auto_share(sub)
        acc, _ = best_accuracy(sub)
        pa = auc(psub) if psub else float("nan")
        print(f"{name:34s} {auc(sub):7.4f} {pa:9.4f} {share:8.1%} "
              f"{acc:8.1%} {len(sub):7d}")


def recalibrate(data, col, title):
    p_auto, _ = precision_at(data, "prod", PROD_AUTO)
    p_rec = recall_at(data, "prod", PROD_GAZ)
    pa, pp, pn = bands(data, "prod", PROD_AUTO, PROD_GAZ)

    sub = [r for r in data if col in r]
    new_auto = lowest_thr_meeting_precision(sub, col, p_auto)
    new_gaz = thr_meeting_recall(sub, col, p_rec)
    va, vp, vn = bands(sub, col, new_auto, new_gaz)
    ua, up, un = bands(sub, col, PROD_AUTO, PROD_GAZ)

    print(f"\n-- threshold recalibration ({title}) --")
    print(f"  prod operating point: precision@{PROD_AUTO} = {p_auto:.4f}, "
          f"recall@{PROD_GAZ} = {p_rec:.4f}")
    print(f"  prod bands      auto/potential/none : {pa:.1%} / {pp:.1%} / {pn:.1%}")
    print(f"  RECALIBRATED    AUTOMATIC_THRESHOLD = {new_auto:.3f}   "
          f"GAZETTEER_THRESHOLD = {new_gaz:.3f}")
    print(f"  recalib bands   auto/potential/none : {va:.1%} / {vp:.1%} / {vn:.1%}")
    print(f"  moderation queue: {pp:.1%} -> {vp:.1%} ({(vp - pp) * 100:+.1f} pp)")
    print(f"  !! thresholds LEFT UNCHANGED (0.8/0.5) would give: "
          f"{ua:.1%} / {up:.1%} / {un:.1%}")
    print(f"     -> new-facility band {pn:.1%} -> {un:.1%}; these are candidates "
          f"dedupe would stop returning at all.")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pairs", required=True)
    p.add_argument("--flags", required=True)
    p.add_argument("--scores", action="append", required=True,
                   metavar="NAME=PATH", help="repeatable")
    args = p.parse_args()

    rows = load_pairs(args.pairs)
    models = [("prod gazetteer (112-pair)", "prod")]
    first_col = None
    for spec in args.scores:
        name, _, path = spec.partition("=")
        attach_scores(rows, path, name)
        models.append((name, name))
        first_col = first_col or name
    attach_flags(rows, args.flags)

    test = [r for r in rows if not r["train"]]
    print(f"\nheld-out half (stable match_id hash): {len(test)} of {len(rows)}")
    report(test, models, "NOISY labels (raw REJECTED = negative)")
    clean = [r for r in test if not (r["label"] == 0 and r["pick_one"])]
    report(clean, models, "CLEAN labels (pick-one rejects removed)")
    recalibrate(clean, first_col, "CLEAN labels -- headline")
    recalibrate(test, first_col, "NOISY labels -- conservative bound")


if __name__ == "__main__":
    main()
