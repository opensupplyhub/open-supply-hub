class GazetteerMatchDefaults:
    '''
    Operating points for the Gazetteer, re-derived for the retrained
    training.json under OSDEV-3277. These are NOT free parameters: they belong
    to a specific model's score distribution and must be re-derived whenever
    data/training.json changes. See src/dedupe-hub/harness/README.md --
    `evaluate.py` prints both, `lookalike_harm.py` justifies the auto bar.

    AUTOMATIC_THRESHOLD stays at 0.8, unchanged from the 112-pair model.

    An earlier revision of this branch set it to 0.356, derived by matching
    production's precision on CLEAN labels (pick-one rejects excluded). That
    method has a blind spot: clean labels drop 95% of the lookalike class's
    negatives -- the "Unit 2 vs Unit 4" wrong-sibling cases -- so it tuned the
    auto bar on data with the hardest class removed, and 0.356 admitted 1,158
    bad lookalike auto-matches against production's 476.

    At 0.8 the retrained model is better than production on every axis
    measured, at the same threshold number:

      precision @0.8, clean labels   0.9982  vs prod 0.9929
      precision @0.8, all labels     0.9280  vs prod 0.8910
      bad lookalike auto-matches        368  vs prod 476
      bad auto-matches overall          630  vs prod 1019

    It costs 2.1pp of overall recall against production. Holding recall fixed,
    the two models are within ~5% of each other on lookalike errors across the
    operating region, so the AUC gap on that class is concentrated in the
    high-precision tail rather than anywhere we run.

    GAZETTEER_THRESHOLD drops to 0.3. This is the candidate floor, a separate
    question from the auto bar: it governs whether an item finds any match at
    all, and it is what delivers the duplicate reduction.

    0.3 is chosen on review cost per duplicate prevented, measured over 1,800
    uploads across three countries with deliberately different corpus profiles.
    Combined, at each candidate floor:

      floor   d decisions   duplicates avoided   cost each
      0.007         +825                  116        7.11
      0.050         +240                   97        2.47
      0.100         +114                   86        1.33
      0.200          +38                   76        0.50
      0.300           -9                   64        FREE
      0.500         -112                   19        FREE (but little benefit)

    At 0.3 the retrain prevents 64 duplicate records while slightly REDUCING
    the number of confirm/reject decisions moderators make. Going lower buys
    more duplicate reduction at rising cost; going higher gives most of the
    review saving up but loses the duplicate benefit.

    Per-country floors are NOT used, though the countries differ sharply.
    Measured delta-decisions at floor 0.3: Bangladesh -44, Vietnam +21,
    Mexico +14. Bangladesh is the duplicate-heavy case (27.3% of uploads become
    new facilities today) and gains most; Mexico already matches well (8.7%)
    and has highly formulaic addresses, so a low floor there produces enormous
    spurious fan-out -- 11 candidates per item at 0.007 -- for almost no gain.
    A single floor of 0.3 sits close to each country's own optimum, and
    per-country calibration would save roughly 21 decisions per 1,800 uploads:
    not worth 100+ per-country constants that must be re-derived on every
    retrain. Revisit only if an instance is reviewer-capacity-bound.

    An earlier revision of this branch used 0.007 (the recall-matched floor)
    and then 0.1. Both were set from Bangladesh data alone. Mexico breaks them:
    at 0.1 it costs 13.6 decisions per duplicate avoided, against Bangladesh's
    "free". Do not re-derive this threshold from one country.

    Item-level decisions at 0.8 / 0.3, Bangladesh:

      prod @ 0.8 / 0.5     auto 50.8%  queue 21.8%  new facility 27.3%
      this @ 0.8 / 0.3     auto 66.5%  queue 13.3%  new facility 20.2%

    PENDING SHADOW VALIDATION (OSDEV-3277 AC#2). Every pair in the offline
    evaluation was the incumbent gazetteer's own candidate, so these bands are
    conditional on candidacy. Run with dedupe_hub_live=false on Test and
    compare AB_Test_ results against live decisions before production.

    Mexico was measured on its Jalisco slice (40,101 facilities), not the full
    559,891 -- indexing all of Mexico exhausted a 7.75 GB Docker allocation.
    The slice keeps item-to-facility linkage intact because Mexican addresses
    carry the state name, but it excludes cross-state candidates, so true
    Mexican fan-out is HIGHER than measured and the case against a low floor is
    if anything understated.
    '''

    AUTOMATIC_THRESHOLD = 0.8
    GAZETTEER_THRESHOLD = 0.3
    RECALL_WEIGHT = 1.0
