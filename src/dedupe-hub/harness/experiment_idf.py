#!/usr/bin/env python3
"""EXPERIMENT: add an IDF-weighted address comparator and measure what it does
to spurious candidate fan-out.

NOT part of OSDEV-3277, which is explicitly label-only. This is a feature
change and belongs to the v4 "productionize the matcher" ticket. It lives in
the harness so the evidence travels with the decision; gazetteer_train.py is
untouched.

Motivation, measured. Share of an average address made of tokens appearing in
more than 20% of that country's records:

    Mexico / Jalisco   35.4%   ->  11.01 candidates per item at floor 0.007
    Bangladesh          7.4%   ->   2.14
    Vietnam            21.9%   ->   1.52

In Jalisco "jalisco" appears in 100% of addresses, "c.p." in 90%, "colonia" in
88%, "calle" in 76%. dedupe's String type is affine-gap distance with no
term weighting, so CALLE and COLONIA count for as much as the street name, and
two unrelated Guadalajara workshops look similar. At comparable corpus size
Bangladesh's 7.4% boilerplate yields 2.1 candidates per item where Mexico's
35.4% yields 11.

The August matcher evaluation called corpus-level term frequency Splink's
"remaining untried lever ... moot given v4's margin". That was a global-average
judgement; it is not moot in Mexico.

The comparator returns an IDF-weighted cosine DISTANCE in [0,1] over address
tokens, so shared boilerplate contributes almost nothing and a shared rare
token (the actual street or colonia name) contributes a lot.

  docker run --rm -v "$PWD/src/dedupe-hub":/dh --entrypoint python \
    api-app:latest /dh/harness/experiment_idf.py \
      --facilities /dh/harness/.data/MXJAL_facilities.csv \
      --items /dh/harness/.data/MXJAL_items.csv \
      --training /dh/api/app/data/training.json \
      --out /dh/harness/.data/fanout_MXJAL_idf.csv
"""
import argparse
import csv
import math
import os
import resource
import sys
import time

if not hasattr(time, 'clock'):          # dedupe 1.9.4 calls the removed time.clock
    time.clock = time.perf_counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_training_json import record  # noqa: E402

SAMPLE_SIZE = 15000

# Module-level so the comparator stays picklable for dedupe's internals.
IDF = {}
DEFAULT_IDF = 1.0


def build_idf(records):
    """Document frequency over address tokens of the canonical corpus."""
    df = {}
    n = 0
    for r in records:
        toks = set(r["address"].split())
        if not toks:
            continue
        n += 1
        for t in toks:
            df[t] = df.get(t, 0) + 1
    global IDF, DEFAULT_IDF
    # smoothed idf; a token in every record contributes ~0, a rare one ~log(n)
    IDF = {t: math.log(n / (1.0 + c)) for t, c in df.items()}
    DEFAULT_IDF = math.log(n / 1.0)     # unseen token = maximally informative
    return n, len(IDF)


def idf_distance(a, b):
    """IDF-weighted cosine distance over address tokens, in [0, 1].

    0 = identical informative content, 1 = nothing informative in common.
    Boilerplate ("calle", "colonia", "c.p.", the state name) has near-zero
    weight, so it can no longer carry a match on its own.
    """
    ta = set((a or "").split())
    tb = set((b or "").split())
    if not ta or not tb:
        return 1.0
    wa = {t: IDF.get(t, DEFAULT_IDF) for t in ta}
    wb = {t: IDF.get(t, DEFAULT_IDF) for t in tb}
    num = sum(wa[t] * wb[t] for t in ta & tb)
    da = math.sqrt(sum(v * v for v in wa.values()))
    db = math.sqrt(sum(v * v for v in wb.values()))
    if da == 0 or db == 0:
        return 1.0
    return 1.0 - max(0.0, min(1.0, num / (da * db)))


def load(path, key):
    out = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            rec = record(r.get("name"), r.get("address"), r.get("country"))
            if rec["name"]:
                out[str(r[key])] = rec
    return out


def pct(values, p):
    s = sorted(values)
    k = min(len(s) - 1, max(0, int(round(p / 100.0 * (len(s) - 1)))))
    return s[k]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--facilities", required=True)
    ap.add_argument("--items", required=True)
    ap.add_argument("--training", required=True)
    ap.add_argument("--thresholds", default="0.007,0.05,0.1,0.2,0.3,0.5,0.8")
    ap.add_argument("--out", required=True)
    ap.add_argument("--baseline", action="store_true",
                    help="omit the IDF field (production config) for control")
    args = ap.parse_args()

    thresholds = sorted(float(t) for t in args.thresholds.split(","))
    floor = thresholds[0]

    canonical = load(args.facilities, "fac_id")
    messy = load(args.items, "item_id")
    n, vocab = build_idf(canonical.values())
    print(f"corpus {len(canonical)} facilities / {len(messy)} items", flush=True)
    print(f"IDF built over {n} addresses, {vocab} distinct tokens", flush=True)

    fields = [
        {"field": "country", "type": "Exact"},
        {"field": "name", "type": "String"},
        {"field": "address", "type": "String"},
    ]
    if not args.baseline:
        fields.append({"field": "address", "type": "Custom",
                       "comparator": idf_distance})
    print(f"fields: {len(fields)} "
          f"({'production config' if args.baseline else '+ IDF address'})",
          flush=True)

    from dedupe import Gazetteer

    gaz = Gazetteer(fields)
    t0 = time.time()
    gaz.sample(messy, canonical, SAMPLE_SIZE)
    with open(args.training) as f:
        gaz.readTraining(f)
    gaz.train()
    print(f"trained in {time.time() - t0:.1f}s", flush=True)

    t1 = time.time()
    gaz.index(canonical)
    print(f"indexed in {time.time() - t1:.1f}s "
          f"(peak RSS {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024:.0f} MB)",
          flush=True)

    t2 = time.time()
    results = gaz.match(messy, threshold=floor, n_matches=None, generator=True)
    counts = {t: [] for t in thresholds}
    per_item = []
    matched = 0
    for m in results:
        if len(m) == 0:
            continue
        matched += 1
        scored = [(float(s), str(cid)) for (_, cid), s in m]
        scores = [s for s, _ in scored]
        row = {"item_id": str(m[0][0][0])}
        for t in thresholds:
            c = sum(1 for s in scores if s >= t)
            counts[t].append(c)
            row[f"n@{t}"] = c
        best = max(scored)
        row["top"], row["top_fac_id"] = best
        per_item.append(row)
    for t in thresholds:
        counts[t] += [0] * (len(messy) - matched)
    print(f"matched in {time.time() - t2:.1f}s", flush=True)

    print(f"\n{'threshold':>10s} {'mean':>8s} {'p50':>6s} {'p90':>6s} "
          f"{'p99':>6s} {'max':>6s} {'items w/ >=1':>13s}")
    for t in thresholds:
        c = counts[t]
        print(f"{t:10.3f} {sum(c)/len(c):8.2f} {pct(c,50):6.0f} {pct(c,90):6.0f} "
              f"{pct(c,99):6.0f} {max(c):6.0f} "
              f"{sum(1 for x in c if x)/len(c):12.1%}")

    with open(args.out, "w", newline="") as f:
        cols = ["item_id"] + [f"n@{t}" for t in thresholds] + ["top", "top_fac_id"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in per_item:
            w.writerow(r)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
