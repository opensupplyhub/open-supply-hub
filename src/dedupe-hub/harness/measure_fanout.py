#!/usr/bin/env python3
"""Measure candidate fan-out: how many candidates Gazetteer.match() returns per
item at a given threshold, against a real indexed facility corpus.

This is the one question the offline pair evaluation structurally cannot answer.
`evaluate.py` scores a FIXED set of pairs -- every one of which was already the
incumbent gazetteer's candidate -- so it can tell you how well a model ranks
candidates, but not how many candidates a lower GAZETTEER_THRESHOLD lets
through in the first place. OSDEV-3277 recalibrates that threshold from 0.5 to
~0.007, which is close to "return everything above the floor", so the fan-out
has to be measured before a shadow deploy, not after.

Trains the production field config (country/name/address) against a candidate
training.json, indexes a real facility corpus, and matches a sample of items.
Scores every candidate at the LOWEST threshold of interest and derives the
counts at higher thresholds from the same scored results -- `threshold` filters
dedupe's scored output, so the low-threshold run is a strict superset.

Runs inside the api-app image (dedupe 1.9.4, stdlib only):

  docker run --rm -v "$PWD/src/dedupe-hub":/dh --entrypoint python api-app:latest \
    /dh/harness/measure_fanout.py \
      --facilities /dh/harness/.data/bd_facilities.csv \
      --items /dh/harness/.data/bd_items.csv \
      --training /dh/api/app/data/training.json \
      --thresholds 0.007,0.1,0.356,0.5,0.8 \
      --out /dh/harness/.data/fanout_retrained.csv
"""
import argparse
import csv
import os
import resource
import sys
import time

# Same shim app/main.py applies at service startup: dedupe 1.9.4's blocking.py
# calls time.clock(), removed in Python 3.8. The service gets this via main.py;
# anything that drives dedupe outside the app (this harness) has to repeat it or
# Gazetteer.index() dies. Nothing else in dedupe's train/score path needs it,
# which is why the other harness scripts run without it.
if not hasattr(time, 'clock'):
    time.clock = time.perf_counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_training_json import record  # noqa: E402

FIELDS = [
    {"field": "country", "type": "Exact"},
    {"field": "name", "type": "String"},
    {"field": "address", "type": "String"},
]
SAMPLE_SIZE = 15000


def load(path, key):
    out = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            rec = record(r.get("name"), r.get("address"), r.get("country"))
            if rec["name"]:
                out[str(r[key])] = rec
    return out


def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def pct(values, p):
    if not values:
        return float("nan")
    s = sorted(values)
    k = min(len(s) - 1, max(0, int(round(p / 100.0 * (len(s) - 1)))))
    return s[k]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--facilities", required=True)
    ap.add_argument("--items", required=True)
    ap.add_argument("--training", required=True)
    ap.add_argument("--thresholds", default="0.007,0.1,0.356,0.5,0.8")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    thresholds = sorted(float(t) for t in args.thresholds.split(","))
    floor = thresholds[0]

    canonical = load(args.facilities, "fac_id")
    messy = load(args.items, "item_id")
    print(f"corpus {len(canonical)} facilities / {len(messy)} items", flush=True)

    from dedupe import Gazetteer

    gaz = Gazetteer(FIELDS)
    t0 = time.time()
    print("sampling...", flush=True)
    # sample() wants a messy/canonical pair; use the real corpora.
    gaz.sample(messy, canonical, SAMPLE_SIZE)
    with open(args.training) as f:
        gaz.readTraining(f)
    gaz.train()
    t_train = time.time() - t0
    print(f"trained in {t_train:.1f}s", flush=True)

    t1 = time.time()
    print(f"indexing {len(canonical)} facilities...", flush=True)
    gaz.index(canonical)
    t_index = time.time() - t1
    print(f"indexed in {t_index:.1f}s  (peak RSS {rss_mb():.0f} MB)", flush=True)

    t2 = time.time()
    results = gaz.match(messy, threshold=floor, n_matches=None, generator=True)
    counts = {t: [] for t in thresholds}
    per_item = []
    matched_items = 0
    for matches in results:
        # dedupe yields a numpy structured array per messy record, so test
        # emptiness with len() -- `if not matches` raises "truth value of an
        # array with more than one element is ambiguous".
        if len(matches) == 0:
            continue
        matched_items += 1
        scored = [(float(s), str(cid)) for (_, cid), s in matches]
        scores = [s for s, _ in scored]
        mid = str(matches[0][0][0])
        row = {"item_id": mid}
        for t in thresholds:
            n = sum(1 for s in scores if s >= t)
            counts[t].append(n)
            row[f"n@{t}"] = n
        best_score, best_id = max(scored)
        row["top"] = best_score
        row["top_fac_id"] = best_id      # so decisions can be eyeballed, not just counted
        per_item.append(row)
    t_match = time.time() - t2

    # items that returned nothing at the floor still count as zero fan-out
    zero = len(messy) - matched_items
    for t in thresholds:
        counts[t] += [0] * zero

    print(f"\nmatched in {t_match:.1f}s  "
          f"({t_match / max(1, len(messy)) * 1000:.1f} ms/item)")
    print(f"peak RSS {rss_mb():.0f} MB")
    print(f"\n{'threshold':>10s} {'mean':>8s} {'p50':>6s} {'p90':>6s} "
          f"{'p99':>6s} {'max':>6s} {'items w/ >=1':>13s}")
    for t in thresholds:
        c = counts[t]
        nonzero = sum(1 for x in c if x)
        print(f"{t:10.3f} {sum(c) / len(c):8.2f} {pct(c, 50):6.0f} "
              f"{pct(c, 90):6.0f} {pct(c, 99):6.0f} {max(c):6.0f} "
              f"{nonzero / len(c):12.1%}")

    with open(args.out, "w", newline="") as f:
        cols = ["item_id"] + [f"n@{t}" for t in thresholds] + ["top", "top_fac_id"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row in per_item:
            w.writerow(row)
    print(f"\nwrote {args.out}")
    print(f"TIMINGS train={t_train:.1f}s index={t_index:.1f}s match={t_match:.1f}s")


if __name__ == "__main__":
    main()
