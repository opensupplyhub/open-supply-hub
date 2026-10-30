#!/usr/bin/env python3
"""Put two dedupe training files together. OSDEV-3277.

Used to test "the original 112 pairs PLUS a few hundred labeled pairs": the base file is kept whole and every match and
non-match from the added file is appended. Nothing is dropped or reordered, so the result is the base followed by the
additions. Pairs whose two records have the same text as a pair already present are skipped (and counted), so a pair
that is in both files is not trained on twice.

Usage:
  python3 merge_training.py --base training_112.json --add training_600.json --out training_600_plus112.json
"""
import argparse
import json


def pair_key(example):
    """What makes two training examples the same pair: the (country, name, address) of both records, ignoring ids."""
    return tuple((r["country"], r["name"], r["address"]) for r in example["__value__"])


def merge(base, extra):
    """Append `extra`'s matches and non-matches to `base`'s. Returns (merged, skipped), where skipped is how many extra
    pairs were left out because the same pair, in the same class, was already there."""
    merged = {"match": list(base["match"]), "distinct": list(base["distinct"])}
    skipped = 0
    for cls in ("match", "distinct"):
        seen = {pair_key(e) for e in merged[cls]}
        for e in extra[cls]:
            k = pair_key(e)
            if k in seen:
                skipped += 1
                continue
            seen.add(k)
            merged[cls].append(e)
    return merged, skipped


def main(argv=None):
    """Read both files, merge them and write the result."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--base", required=True, help="the training.json kept whole, e.g. production's 112 pairs")
    p.add_argument("--add", required=True, help="the training.json whose pairs are appended")
    p.add_argument("--out", required=True)
    args = p.parse_args(argv)
    with open(args.base) as f:
        base = json.load(f)
    with open(args.add) as f:
        extra = json.load(f)
    merged, skipped = merge(base, extra)
    with open(args.out, "w") as f:
        json.dump(merged, f)
    print(f"base {len(base['match'])} match / {len(base['distinct'])} distinct; added {len(extra['match'])} / "
          f"{len(extra['distinct'])} ({skipped} skipped as already present); wrote {len(merged['match'])} match / "
          f"{len(merged['distinct'])} distinct to {args.out}")


if __name__ == "__main__":
    main()
