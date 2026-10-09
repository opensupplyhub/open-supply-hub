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

    GAZETTEER_THRESHOLD drops to 0.007, the score retaining the recall
    production retains at 0.5. This is the candidate floor, a separate question
    from the auto bar: it governs whether an item finds any match at all. It is
    what delivers the duplicate reduction (new-facility rate 27.3% -> 18.3% on
    600 items against 49,470 indexed facilities), and that gain is unaffected
    by where the auto bar sits.

    Item-level decisions, same corpus:

      prod @ 0.8 / 0.5        auto 50.8%  queue 21.8%  new facility 27.3%
      this @ 0.8 / 0.007      auto 64.7%  queue 17.0%  new facility 18.3%

    More auto-matched, a smaller queue, and fewer duplicate records than today.

    PENDING SHADOW VALIDATION (OSDEV-3277 AC#2). Every pair in the offline
    evaluation was the incumbent gazetteer's own candidate, so these bands are
    conditional on candidacy. Run with dedupe_hub_live=false on Test and
    compare AB_Test_ results against live decisions before production.
    '''

    AUTOMATIC_THRESHOLD = 0.8
    GAZETTEER_THRESHOLD = 0.007
    RECALL_WEIGHT = 1.0
