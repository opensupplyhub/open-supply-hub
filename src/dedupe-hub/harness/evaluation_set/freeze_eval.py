#!/usr/bin/env python3
"""Freeze the evaluation set so every model is graded on exactly the same pairs.
OSDEV-3277.

The held-out half of the labeled pairs is chosen by a stable hash of match_id,
so it is already repeatable for one pairs file. This script makes that explicit
and tamper-evident: it writes the exact list of held-out match_ids, plus tags
for each pair, plus a manifest holding checksums of the source pairs file and of
the eval set. slice_report.py --eval-set refuses to run if either checksum no
longer matches, so a re-pulled or edited pairs.csv can never silently change
what a model is graded on.

Pairs the harness cannot score (make_training_json.can_score) are left out, so
every model has a score for every pair in the frozen set.

Tags written per pair (1 or 0):
  pick_one    a REJECTED pair where the moderator confirmed a different facility
              for the same upload (from pick_one_flags.csv)
  exact_text  the cleaned name, address and country are identical on both sides.
              In production the exact-match step runs before the model, so a
              pair like this is not decided by it.
The recorded production confidence is deliberately NOT used anywhere: a score of
1.00 does not reliably mean an exact text match (about half of those pairs
differ in text), so it is not a safe marker.
The tag lets slice_report.py drop exact matches (--exclude-exact) as a VIEW of
the same frozen set, not as a different dataset.

Usage:
  python3 evaluation_set/freeze_eval.py --pairs pairs.csv --flags pick_one_flags.csv \
      --out eval_set.csv
Writes eval_set.csv and eval_set.csv.manifest.json. Freeze once; do not
regenerate it between runs you intend to compare.
"""
import argparse
import csv
import datetime
import hashlib
import json
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # the harness folder
sys.path[:0] = [_ROOT] + [os.path.join(_ROOT, d) for d in sorted(os.listdir(_ROOT))
                          if os.path.isdir(os.path.join(_ROOT, d)) and not d.startswith(("_", "."))]
from make_training_json import can_score, record, stable_train_half  # noqa: E402


def sha256_of(path):
    """Hex SHA-256 of a file, read in chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    """Select the held-out pairs, tag them, and write the eval set and manifest."""
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pairs", required=True)
    p.add_argument("--flags", required=True, help="pick_one_flags.csv")
    p.add_argument("--out", required=True, help="eval_set.csv to write")
    args = p.parse_args()

    with open(args.flags, newline="", encoding="utf-8-sig") as f:
        flagged = {r["match_id"] for r in csv.DictReader(f)}

    seen, read, skipped, train_half = set(), 0, 0, 0
    held = []
    with open(args.pairs, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            mid = r["match_id"]
            if mid in seen:
                continue
            seen.add(mid)
            read += 1
            left = record(r.get("item_clean_name") or r.get("item_name"),
                          r.get("item_clean_address") or r.get("item_address"),
                          r.get("item_country"))
            right = record(r.get("fac_name"), r.get("fac_address"),
                           r.get("fac_country"))
            if not can_score(left, right):
                skipped += 1
                continue
            if stable_train_half(mid):
                train_half += 1
                continue
            rejected = r["status"] != "CONFIRMED"
            held.append((
                mid,
                (r.get("item_country") or r.get("fac_country") or "").strip().lower(),
                int(rejected and mid in flagged),
                int(left == right),
            ))

    held.sort(key=lambda t: (len(t[0]), t[0]))
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["match_id", "country", "pick_one", "exact_text"])
        w.writerows(held)

    manifest = {
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "pairs_file": os.path.basename(args.pairs),
        "pairs_sha256": sha256_of(args.pairs),
        "eval_set_sha256": sha256_of(args.out),
        "pairs_read": read,
        "skipped_cannot_score": skipped,
        "train_half": train_half,
        "eval_rows": len(held),
        "exact_text_rows": sum(t[3] for t in held),
        "split_rule": "held out when int(md5(match_id)[:8], 16) is odd "
                      "(make_training_json.stable_train_half)",
    }
    with open(args.out + ".manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    print(f"pairs read {read}; cannot score {skipped}; train half {train_half}")
    print(f"FROZEN evaluation set: {len(held)} pairs -> {args.out}")
    print(f"  pairs with identical text on both sides: {manifest['exact_text_rows']}")
    print(f"  eval set sha256 {manifest['eval_set_sha256'][:16]}...  "
          f"pairs sha256 {manifest['pairs_sha256'][:16]}...")
    print(f"wrote {args.out}.manifest.json. Do not regenerate between runs "
          f"you intend to compare.")


if __name__ == "__main__":
    main()
