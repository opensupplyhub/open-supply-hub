#!/bin/sh
# Build two small training files, to ask whether 6,000 pairs is too many and 112 too few:
#   600        300 matches + 300 non-matches, drawn the same way as the 6,000 file (two-thirds from the hard pool)
#   600_112    the original 112 pairs PLUS those 600 (712 pairs)
# Each file refuses to write if any pair is in the frozen evaluation set. The ids of the 600 pairs go to
# ids_600.txt so a comparison can leave out uploads that contain them.
# Usage: sh build_size_variants.sh
HARNESS="$(cd "$(dirname "$0")" && pwd)"
DATA="$HOME/osdev-3277/data"
python3 "$HARNESS/make_training_json.py" --pairs "$DATA/pairs.csv" --eval-set "$DATA/eval_set.csv" --per-class 300 \
  --out "$DATA/training_600.json" --ids-out "$DATA/ids_600.txt" | grep -E 'selected|lookalike|overlap|refusing|wrote'
python3 "$HARNESS/merge_training.py" --base "$DATA/training_112.json" --add "$DATA/training_600.json" \
  --out "$DATA/training_600_plus112.json"
