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

Extraction SQL against `FacilityMatch` is not yet in-repo; the 2026-08 sample
(`pairs_geo.csv`, 40k stratified pairs) plus the DB-verified `pick_one_flags.csv`
live in Danielle's scratch copy. Porting the extraction to a management command
is the natural next piece of this harness.

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

# 5. Apply the recalibrated thresholds to gazetteer_match_defaults.py,
#    then shadow-run on Test with dedupe_hub_live=false before deploying.
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

`AUTOMATIC_THRESHOLD = 0.8` and `GAZETTEER_THRESHOLD = 0.5` are tuned to the
*current* model's score distribution. A retrained classifier scores on a
different scale, so **the numbers must move or the deploy silently breaks**:

> Leaving 0.8 / 0.5 in place sends the share of candidate pairs falling below
> `GAZETTEER_THRESHOLD` from **0.3% to 16.5%** (clean labels; 0.6% → 47.7% on
> noisy). Those are candidates `Gazetteer.match()` would stop returning at all —
> so they do not become queue items, they become **silently created duplicate
> facilities**. The moderation queue would *shrink*, which looks like a win in a
> dashboard and is the opposite of one.

`evaluate.py` re-derives both by matching the production *operating point*
rather than the production number:

- `AUTOMATIC_THRESHOLD` → lowest score whose precision still matches prod's
  precision at 0.8 (never auto-accept at a worse error rate than today).
- `GAZETTEER_THRESHOLD` → score retaining the recall prod retains at 0.5 (never
  drop a true match we surface today).

For the 2026-10-07 candidate that gives **AUTOMATIC_THRESHOLD ≈ 0.356** and
**GAZETTEER_THRESHOLD ≈ 0.007**, moving the moderation queue from 24.0% to 10.6%
of candidate pairs (−13.4 pp). On noisy labels — the conservative bound — the
same method gives 0.590 / 0.007 and a 53.2% → 41.9% queue.

Two caveats before anyone treats those as final:

1. Every pair in the eval set was the incumbent gazetteer's *own* candidate, so
   the "below threshold" band is conditional on candidacy and understates true
   new-facility volume.
2. A `GAZETTEER_THRESHOLD` near 0.007 is effectively "return everything above the
   floor". In the eval that is harmless because the candidate set is fixed, but
   live it widens how many candidates `match()` returns per item — unmeasurable
   here. **This is the single most important thing for the shadow run to
   settle**, and it is a strong argument for calibrating the retrained scores
   (Platt/isotonic) so the thresholds keep a stable meaning across retrains
   instead of being re-derived from scratch each time.

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
