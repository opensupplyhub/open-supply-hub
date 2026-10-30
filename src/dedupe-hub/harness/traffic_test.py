#!/usr/bin/env python3
"""Run one trained model over a random sample of real uploads. OSDEV-3277 traffic test.

Trains the production Gazetteer config on --training exactly the way verify_retrain.py does (same three fields,
same 15,000-pair sample, same call order), indexes the facility records from traffic_pull.sql, matches every
sampled upload against that index, and writes what the system would do with each one at the given thresholds:
auto-match it, send it to review, or create a new facility.

Run it once per model (for example the 112-pair file at 0.5/0.8 and the 6k file at 0.3/0.75), then compare the
two decision files with traffic_compare.py.

The decision rules are the ones outcomes.decide() copies from production. Production's exact matcher runs first:
an upload whose cleaned country, name and address equal exactly one facility's record is auto-matched to it. That
is a simplification of the real exact matcher, but it is applied identically to every model.

Besides the decision, every upload keeps its best candidates and their scores, so the thresholds can be changed
afterwards without re-running the model.

  docker run --rm -e PYTHONHASHSEED=0 -e PYTHONWARNINGS=ignore::FutureWarning \
    -v "$PWD/src/dedupe-hub":/dh -v "$HOME/osdev-3277/data":/data \
    --entrypoint python api-app:latest /dh/harness/traffic_test.py \
    --pairs /data/pairs.csv --training /data/training_6000_clean.json \
    --sample /data/traffic_sample.csv --index /data/traffic_index.csv \
    --floor 0.3 --auto 0.75 --seed 0 --out /data/traffic_6k_seed0.csv
"""
import argparse
import csv
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_training_json import record  # noqa: E402
from outcomes import decide  # noqa: E402
from verify_retrain import FIELDS, SAMPLE_SIZE, load, rss_mb  # noqa: E402

MATCH_MARK = "_MATCH-"        # dedupe-hub's synthetic id for a confirmed spelling: <facility>_MATCH-<match id>
KEEP_CANDIDATES = 8           # candidates written per upload, best first
OUT_COLUMNS = ["item_id", "country", "decision", "chosen", "cause", "n_above_floor", "n_above_bar", "candidates"]


def facility_of(index_id):
    """The facility an index record belongs to: its own id, or the part before the _MATCH- marker."""
    return index_id.split(MATCH_MARK)[0]


def read_index(path):
    """Read traffic_index.csv into ({index id: record}, {(country, name, address): set of facilities}).

    Each record is cleaned the way training records are. Rows with no usable name are dropped, because dedupe
    cannot compare two empty strings. The second dictionary is the exact-match lookup."""
    canonical, exact = {}, {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            rec = record(r["name"], r["address"], r["country"])
            if not rec["name"]:
                continue
            key = r["facility_id"] if r["kind"] == "facility" else r["facility_id"] + MATCH_MARK + r["match_id"]
            canonical[key] = rec
            exact.setdefault((rec["country"], rec["name"], rec["address"]), set()).add(r["facility_id"])
    return canonical, exact


def read_sample(path):
    """Read traffic_sample.csv into a list of dicts, each with its cleaned record under 'rec'. Uploads with an
    empty name after cleaning are kept out (they could not be scored)."""
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            rec = record(r["name"], r["address"], r["country"])
            if rec["name"]:
                rows.append(dict(r, rec=rec))
    return rows


def decide_upload(upload, found, canonical, exact, floor, auto):
    """What happens to one upload. `found` is {index id: score} from the search (empty if it retrieved nothing).

    Returns a dict shaped like OUT_COLUMNS. An exact match to exactly one facility is auto-matched before the
    gazetteer is consulted. Otherwise the candidates go through outcomes.decide()."""
    rec = upload["rec"]
    same = exact.get((rec["country"], rec["name"], rec["address"]), set())
    base = {"item_id": upload["item_id"], "country": upload["country"]}
    if len(same) == 1:
        return dict(base, decision="auto_match", chosen=next(iter(same)), cause="exact_matcher",
                    n_above_floor=1, n_above_bar=1, candidates="")
    cands = [{"facility": facility_of(i), "score": s,
              "exact": (canonical[i]["country"], canonical[i]["name"], canonical[i]["address"]) ==
                       (rec["country"], rec["name"], rec["address"])}
             for i, s in found.items()]
    action, chosen, above_floor, above_bar = decide(cands, floor, auto)
    best = {}
    for c in cands:
        best[c["facility"]] = max(best.get(c["facility"], 0.0), c["score"])
    top = sorted(best.items(), key=lambda kv: -kv[1])[:KEEP_CANDIDATES]
    return dict(base, decision=action, chosen=chosen or "", cause="gazetteer",
                n_above_floor=len(above_floor), n_above_bar=len(above_bar),
                candidates=";".join("%s:%.4f" % (fac, s) for fac, s in top))


def train(rows, training_path, seed):
    """Train a Gazetteer the way verify_retrain.py does and return it with the seconds it took."""
    import numpy
    from dedupe import Gazetteer
    random.seed(seed)
    numpy.random.seed(seed)
    train_rows = [r for r in rows if r["train"]]
    messy = {str(i): r["left"] for i, r in enumerate(train_rows)}
    canonical = {"c" + str(i): r["right"] for i, r in enumerate(train_rows)}
    t0 = time.time()
    gaz = Gazetteer(FIELDS)
    gaz.sample(messy, canonical, SAMPLE_SIZE)
    with open(training_path) as f:
        gaz.readTraining(f)
    gaz.train()
    return gaz, time.time() - t0


def main():
    """Train, index the real facility records, match the sampled uploads and write one decision per upload."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pairs", required=True, help="labeled pairs CSV (only used to sample the 15,000 pairs dedupe needs)")
    p.add_argument("--training", required=True)
    p.add_argument("--sample", required=True, help="traffic_sample.csv")
    p.add_argument("--index", required=True, help="traffic_index.csv")
    p.add_argument("--floor", type=float, required=True, help="candidate floor (GAZETTEER_THRESHOLD)")
    p.add_argument("--auto", type=float, required=True, help="auto-match bar (AUTOMATIC_THRESHOLD)")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    rows = load(args.pairs)
    gaz, secs = train(rows, args.training, args.seed)
    print(f"trained in {secs:.0f}s, peak RSS {rss_mb():.0f} MB, {len(gaz.predicates)} search rules", flush=True)

    canonical, exact = read_index(args.index)
    sample = read_sample(args.sample)
    print(f"index {len(canonical)} records; sample {len(sample)} uploads", flush=True)

    t0 = time.time()
    gaz.index(canonical)
    print(f"indexed in {time.time() - t0:.0f}s, peak RSS {rss_mb():.0f} MB", flush=True)

    messy = {u["item_id"]: u["rec"] for u in sample}
    found = {}
    t0 = time.time()
    for n, matches in enumerate(gaz.match(messy, threshold=0.0, n_matches=None, generator=True), 1):
        if len(matches) == 0:
            continue
        found[str(matches[0][0][0])] = {str(cid): float(s) for (_, cid), s in matches}
        if n % 500 == 0:
            print(f"  matched {n} uploads ({time.time() - t0:.0f}s)", flush=True)

    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=OUT_COLUMNS)
        w.writeheader()
        for u in sample:
            w.writerow(decide_upload(u, found.get(u["item_id"], {}), canonical, exact, args.floor, args.auto))
    print(f"wrote {args.out} ({len(sample)} uploads); matching took {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
