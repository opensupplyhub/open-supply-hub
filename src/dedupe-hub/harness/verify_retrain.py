#!/usr/bin/env python3
"""Train the production Gazetteer config against a candidate training.json and
score a labeled pair file with it. OSDEV-3277 AC#1 and AC#3.

Deliberately mirrors gazetteer_train.py exactly -- same three fields, same
sample size, same call order -- so a green run here is evidence the service
will cold-start on this training.json with no code change. Times the train so
the startup-cost half of AC#3 is measured rather than asserted.

Runs inside the api-app image (dedupe 1.9.4, no pandas/sklearn):

  docker run --rm \
    -v "$PWD/src/dedupe-hub":/dh -v "$HOME/splink-eval/slink":/eval \
    --entrypoint python api-app:latest \
    /dh/harness/verify_retrain.py --pairs /eval/pairs_geo.csv \
      --training /dh/api/app/data/training.json --out /eval/osdev3277_scores.csv
"""
import argparse
import csv
import json
import os
import resource
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_training_json import record, stable_train_half  # noqa: E402

# The production field config. Do not edit here -- OSDEV-3277 is label-only;
# if these drift from gazetteer_train.py the verification is meaningless.
FIELDS = [
    {"field": "country", "type": "Exact"},
    {"field": "name", "type": "String"},
    {"field": "address", "type": "String"},
]
SAMPLE_SIZE = 15000


def load(path):
    rows = []
    seen = set()
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
            if not left["name"] or not right["name"]:
                continue
            rows.append({"match_id": mid,
                         "label": 1 if r["status"] == "CONFIRMED" else 0,
                         "left": left, "right": right,
                         "train": stable_train_half(mid)})
    return rows


def rss_mb():
    # ru_maxrss is KB on Linux, bytes on macOS; container runs Linux.
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pairs", required=True)
    p.add_argument("--training", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    rows = load(args.pairs)
    train = [r for r in rows if r["train"]]
    print(f"pairs {len(rows)}  train-half {len(train)}", flush=True)

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
    print(f"wrote {args.out} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
