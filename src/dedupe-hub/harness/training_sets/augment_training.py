#!/usr/bin/env python3
"""Add a handful of labeled pairs from chosen countries to an existing training file. OSDEV-3277.

Production's training file has 112 pairs and none from most of the countries the matcher is used in. This
takes that file (or any dedupe training.json) and appends N matches and N non-matches for each country asked
for, drawn at random from that country's pairs in the TRAINING half of the labeled data. Nothing is chosen by
whether the recorded production score agreed with the human (the disagreement rule is not used).

The draw is seeded, so the same seed gives the same pairs and different seeds give different draws. Every
added pair comes from the training half, which never overlaps the frozen evaluation set; the script checks
that against eval_set.csv anyway and refuses to write if any added pair is in it. It also writes the ids of
the added pairs, so a comparison can leave out uploads that contain them.

Usage:
  python3 training_sets/augment_training.py --base training_112.json --pairs pairs.csv --eval-set eval_set.csv \
      --add cn:10 --add us:10 --seed 0 --out training_aug10_s0.json --ids-out ids_aug10_s0.txt
"""
import argparse
import csv
import json
import os
import random
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # the harness folder
sys.path[:0] = [_ROOT] + [os.path.join(_ROOT, d) for d in sorted(os.listdir(_ROOT))
                          if os.path.isdir(os.path.join(_ROOT, d)) and not d.startswith(("_", "."))]
from make_training_json import load_pairs  # noqa: E402


def parse_add(specs):
    """Turn ["cn:10", "us:5"] into {"cn": 10, "us": 5} (lowercase country code to pairs per class)."""
    out = {}
    for spec in specs:
        code, _, n = spec.partition(":")
        if not code or not n.isdigit():
            raise ValueError(f"--add wants country:count, got {spec!r}")
        out[code.strip().lower()] = int(n)
    return out


def sample_pairs(rows, country, per_class, rng):
    """Pick `per_class` matches and `per_class` non-matches for one country from the training-half rows.

    Returns (matches, non_matches) as lists of rows. Raises ValueError if the country does not have enough
    pairs of either kind in the training half."""
    picked = []
    for label in (1, 0):
        pool = [r for r in rows if r["train"] and r["country"] == country and r["label"] == label]
        if len(pool) < per_class:
            raise ValueError(f"{country}: only {len(pool)} training-half pairs with label {label}, wanted {per_class}")
        picked.append(rng.sample(pool, per_class))
    return picked[0], picked[1]


def as_example(row):
    """One pair in the format dedupe's training file uses: a tuple of the two records."""
    return {"__class__": "tuple", "__value__": [row["left"], row["right"]]}


def main(argv=None):
    """Read the base file, add the sampled pairs, check them against the evaluation set, and write the result."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--base", required=True, help="the training.json to start from")
    p.add_argument("--pairs", required=True, help="labeled pairs CSV")
    p.add_argument("--eval-set", required=True, help="frozen eval_set.csv; no added pair may be in it")
    p.add_argument("--add", action="append", required=True, metavar="COUNTRY:N",
                   help="add N matches and N non-matches from this country (repeat for more countries)")
    p.add_argument("--seed", type=int, default=0, help="seed for the random draw")
    p.add_argument("--out", required=True)
    p.add_argument("--ids-out", help="write the match_ids of the added pairs here, one per line")
    args = p.parse_args(argv)

    rows = load_pairs(args.pairs)
    rng = random.Random(args.seed)
    with open(args.base) as f:
        training = json.load(f)
    base_counts = (len(training["match"]), len(training["distinct"]))
    added = []
    for country, n in parse_add(args.add).items():
        try:
            matches, non_matches = sample_pairs(rows, country, n, rng)
        except ValueError as e:
            sys.exit(str(e))
        training["match"] += [as_example(r) for r in matches]
        training["distinct"] += [as_example(r) for r in non_matches]
        added += matches + non_matches
        print(f"added {country}: {n} matches + {n} non-matches")
    with open(args.eval_set, newline="") as f:
        evaluated = {r["match_id"] for r in csv.DictReader(f)}
    overlap = sum(1 for r in added if r["match_id"] in evaluated)
    print(f"base {base_counts[0]} match / {base_counts[1]} distinct -> now {len(training['match'])} match / "
          f"{len(training['distinct'])} distinct; overlap with eval set: {overlap} of {len(added)} added")
    if overlap:
        sys.exit("refusing to write: an added pair is in the evaluation set")
    with open(args.out, "w") as f:
        json.dump(training, f)
    if args.ids_out:
        with open(args.ids_out, "w") as f:
            f.write("\n".join(sorted(r["match_id"] for r in added)) + "\n")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
