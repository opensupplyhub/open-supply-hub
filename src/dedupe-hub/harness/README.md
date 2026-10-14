# Dedupe matcher retrain harness

Rebuilds `src/dedupe-hub/api/app/data/training.json` — the file the production
Gazetteer trains from at cold start — out of moderator-adjudicated
`FacilityMatch` rows, then measures the candidate against the production
baseline before anything is deployed.

Written for [OSDEV-3277](https://opensupplyhub.atlassian.net/browse/OSDEV-3277)
(label-only retrain: new labels, **no** feature changes) and intended to be the
periodic-retrain runbook from here on.

Background: "Matcher Evaluation — Findings: Splink vs Retrained Dedupe, Aug
2026" (Confluence 1441103874), child of the Dedupe Hub project brief.

## Why this exists

The committed `training.json` held **112 pairs** from the OAR era — 47 match /
65 distinct, all apparel — while ~631k moderator adjudications accumulated
unused. Retraining on modern labels, changing nothing else, is worth most of
the quality gap measured in the evaluation (see Results below).

## Scripts

| script | does |
|---|---|
| `make_training_json.py` | labeled-pairs CSV → `training.json` in dedupe 1.9.4 format |
| `verify_retrain.py` | trains the **production field config** against a candidate `training.json`, times the cold start, scores a pair file |
| `evaluate.py` | candidate vs prod baseline: AUC, lookalike AUC, auto-approve share, and re-derived thresholds |

All three are stdlib-only — the `api-app` image carries neither pandas nor
scikit-learn, and the harness has to run inside it to use the same dedupe build
as production.

## Inputs

A labeled-pairs CSV, one row per adjudication:

```
match_id, status, confidence,
item_name, item_clean_name, item_address, item_clean_address, item_country,
fac_name, fac_address, fac_country
```

`status == CONFIRMED` is a positive; anything else is a negative. `match_id` is
the join key everywhere — **never** a row-order index (see "Join discipline").

`extract_labels.sql` now pulls these straight from `FacilityMatch`, with a
deterministic per-country draw:

```bash
psql -v per_country=4000 -f src/dedupe-hub/harness/extract_labels.sql > pairs.csv
```

Read that file's header before choosing `per_country`. Capping the *extraction*
is sensible; rebalancing the training *draw* by country was tested and made
every country worse. The two are not the same decision.

The 2026-08 sample this branch's results were measured on (`pairs_geo.csv`, 40k
curated pairs) and the DB-verified `pick_one_flags.csv` are held locally by
whoever ran the evaluation, not in the repo. To reproduce the published numbers
exactly you need those files; to run the procedure on fresh labels, the SQL is
enough. `arbitration_sets.csv` (4,000 sets, used by `arbitration_rank.py`) is
in the same local set.

**Pair CSVs are never committed.** They are facility data; `.data/` is
gitignored. Regenerate them from the local anonymized dump (or a prod snapshot,
run internally).

## Procedure

```bash
# 0. One-time: the cached api-app image may predate the BTrees==6.4 pin in
#    requirements.txt. If sampling dies with "Attempting to block with an index
#    predicate without indexing records", rebuild the image (or pin in a layer):
docker compose build api-app

# 1. Stage inputs (gitignored)
mkdir -p src/dedupe-hub/harness/.data
cp <labeled_pairs.csv> src/dedupe-hub/harness/.data/pairs.csv
cp <pick_one_flags.csv> src/dedupe-hub/harness/.data/

# 2. Build the candidate training.json (writes to api/app/data/training.json)
python3 src/dedupe-hub/harness/make_training_json.py \
    --pairs src/dedupe-hub/harness/.data/pairs.csv --dry-run   # inspect first
python3 src/dedupe-hub/harness/make_training_json.py \
    --pairs src/dedupe-hub/harness/.data/pairs.csv

# 3. Train it under the production config and score the pairs (~80s)
docker run --rm -v "$PWD/src/dedupe-hub":/dh --entrypoint python api-app:latest \
    /dh/harness/verify_retrain.py \
    --pairs /dh/harness/.data/pairs.csv \
    --training /dh/api/app/data/training.json \
    --out /dh/harness/.data/candidate_scores.csv

# 4. Compare against prod and re-derive the thresholds
python3 src/dedupe-hub/harness/evaluate.py \
    --pairs src/dedupe-hub/harness/.data/pairs.csv \
    --flags src/dedupe-hub/harness/.data/pick_one_flags.csv \
    --scores "candidate=src/dedupe-hub/harness/.data/candidate_scores.csv"

# 5. Compare against the committed operating point (0.8 / 0.3) in
#    gazetteer_match_defaults.py, then shadow-run on Test with
#    dedupe_hub_live=false before deploying. Read that file's docstring and the
#    Thresholds section below before changing either number.
```

Step 5 is not optional — see "Thresholds" below.

## Results, 2026-10-07 (held-out half, clean labels)

| model | AUC | lookalike AUC | auto-approve @98% precision | best accuracy |
|---|---|---|---|---|
| prod (112-pair training) | 0.9443 | **0.8903** | 84.6% | 91.7% |
| **this retrain (labels only)** | **0.9808** | 0.8759 | **90.4%** | **96.1%** |
| v4 (labels + LatLong + token asymmetry) | 0.9832 | 0.8779 | 91.5% | 97.0% |

Labels alone carry ~94% of the AUC gap to the full v4 feature model, which is
what OSDEV-3277 set out to establish.

**Benchmark caveat, and it matters.** This pool is 43.8% Mexico and 0.1% Korea,
while production upload volume is 6.6% Mexico and 22.8% Korea. The AUC figure is
real but it is not a volume-weighted statement about production, and it should
not be the sole basis for a ship decision. The per-country tables under
"Thresholds" are the better guide to production behavior.

**The lookalike class regresses** (0.8903 → 0.8759). This is expected and was
predicted by the evaluation: three affine-gap string features cannot rank
*within* the near-identical UNIT A / UNIT B class, so better labels sharpen
overall gating while slightly blunting that class. Only the v4 features recover
it, and even v4 does not fully reach prod. Carry this into the shadow run.

Cold start, same config, 40k-pair corpus (AC#3):

| training.json | sample | readTraining | train | total | peak RSS |
|---|---|---|---|---|---|
| 112 pairs (current) | 18.6s | 1.0s | 0.1s | **19.8s** | 542 MB |
| 6,000 pairs (this) | 19.3s | 51.4s | 4.8s | **75.5s** | 754 MB |

Cost is `readTraining`, and it scales with training-set size — `--per-class` is
the dial if +56s of cold start is judged too expensive. Indexing the real
canonical corpus is excluded here and dominates both numbers in production.

## Thresholds

**Committed on this branch: `AUTOMATIC_THRESHOLD = 0.8`, `GAZETTEER_THRESHOLD = 0.3`.**

The full derivation, the measurements behind each number and the two earlier
values that were withdrawn all live in the docstring of
`api/app/matching/matcher/gazeteer/gazetteer_match_defaults.py`. That docstring
is the authoritative record. Read it before changing either number.

The short version:

| | value | why |
|---|---|---|
| `AUTOMATIC_THRESHOLD` | 0.8 | Unchanged from the 112-pair model. At the same threshold number the retrain beats production on precision, on bad lookalike auto-matches and on bad auto-matches overall. |
| `GAZETTEER_THRESHOLD` | 0.3 | The candidate floor, chosen on review cost per duplicate prevented across three countries. At 0.3 the retrain prevents duplicates while slightly *reducing* moderator decisions. |

**Two earlier recommendations from this branch were withdrawn. Do not
reintroduce them.**

- `AUTOMATIC_THRESHOLD = 0.356` was derived by matching production's precision
  on *clean* labels. Clean labels drop ~95% of the lookalike class's negatives,
  so that method tuned the auto bar with the hardest class removed. At 0.356 the
  model admitted 1,158 bad lookalike auto-matches against production's 476.
- `GAZETTEER_THRESHOLD = 0.007`, and later `0.1`, were both set from Bangladesh
  alone. Mexico breaks them: at 0.1 it costs 13.6 decisions per duplicate
  avoided where Bangladesh is free. Never re-derive this floor from one country.

`evaluate.py` still re-derives both by matching production's *operating point*
rather than its threshold number, and that method is still the right one. The
mistake both times was the data it was pointed at, not the method.

### The open threshold question: 0.75

0.8 is the committed value and it is defensible, but it is probably too
conservative in the countries carrying production volume. Matching auto-match
*rate* rather than threshold number:

| country | production | 0.80 | **0.75** | 0.70 |
|---|---|---|---|---|
| Korea | 96.0% | 89.7% | **96.2%** | 98.0% |
| China | 74.8% | 80.5% | **82.7%** | 83.5% |
| Mexico | 90.3% | 89.3% | **89.7%** | 90.0% |
| Bangladesh | 50.8% | 66.5% | **70.2%** | 72.2% |
| Vietnam | 66.0% | 68.8% | **73.2%** | 76.2% |

At 0.75 every country is at or above production except Mexico, which is 0.6pp
short, and Bangladesh gains roughly 20pp. **0.75 is the configuration to shadow
test.** Only the auto-match and new-facility rates above are exact at 0.75;
decision counts need a re-run, and that is the immediate next measurement.

Korea is the cautionary tale here. It looked like a model regression at 0.8 and
is not one: at equal auto-match rate the two models agree on 98.6% of items and
pick a different facility on **zero**. A fixed threshold is not a fixed
operating point.

### Calibration

One threshold does not mean the same thing in every country, which is why the
table above exists at all. Calibrating the retrained scores (Platt or isotonic)
is what would make a single number portable, and it has been promoted from
nice-to-have to the central recommendation for the next round of work.

## Open work

In rough order. Items 1 and 2 are the gate; 3 needs a human ruling rather than
a measurement.

1. **Shadow run on Test** with `dedupe_hub_live=false`, comparing `AB_Test_`
   results against live decisions. This is AC#2 of OSDEV-3277 and it has not
   happened. It needs a deploy. No bound on acceptable queue-volume change has
   been agreed either, which is part of the same conversation.
2. **Verify 0.75** on decision counts and duplicates, then set it.
3. **Two human calls:** whether +56s of cold start is acceptable, and what
   queue-volume change counts as passing AC#2.
4. **Seed `dedupe.sample()`.** It is unseeded, so band figures move a few points
   between runs. Fix this before anyone quotes decimals from them.
5. **Score calibration**, as above.
6. **Release notes and PR**, held until the shadow numbers land.

Out of scope for this ticket and carried to the v4 feature work: the
IDF-weighted address comparator in `experiment_idf.py`. Addresses are 35.4%
boilerplate in Jalisco against 7.4% in Bangladesh, which is why Mexico produces
11 candidates per item at a low floor. It must be computed per country; global
IDF inverts the effect, since "jalisco" is rare globally.

## Join discipline

Every join is on `match_id`, and `evaluate.py` fails loudly on a zero-row join.
The train/test split is a stable MD5 hash of `match_id`, not row order.

This is not fussiness. During the August evaluation, `pair_id` assigned by row
order silently misjoined ~97.5% of rows across two files holding the same
sample in different orders — and because both were stratified by confidence
decile, the corrupted column still reported AUC ≈ 0.95 instead of collapsing to
0.5. The bug was survivable-looking for days. Never let a row-order id cross a
file boundary.

## Two things that look like bugs and are not

**Pick-one rejects stay in the training negatives.** ~90% of REJECTED rows mean
"not this near-identical sibling", not "no match" — the moderator was
arbitrating between duplicate facility records. The v5 experiment purged them;
the negative pool collapsed to ~1k pairs and *every* hard metric got worse
(lookalike AUC 0.878 → 0.855, within-set top-1 96.5% → 94.8%). They are ranking
signal. They are excluded from **evaluation** negatives instead — that is what
`--flags` does, and why `evaluate.py` reports clean and noisy labels separately.

**The draw is curated, not random.** Hard pairs — long shared name prefix but
not identical, plus pairs where the incumbent's score disagreed with the
moderator — are oversampled 2:1, mirroring what dedupe's own active learning
would surface.

## Scope

In: labels, thresholds, and the procedure. Out: model fields, the Reader, data
fetchers, service topology — `verify_retrain.py` hardcodes the production field
config precisely so a feature change cannot sneak in under a label-only
retrain. The v4 feature work (LatLong + token asymmetry) is a separate ticket
and builds on this.
