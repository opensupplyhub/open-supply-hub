class GazetteerMatchDefaults:
    '''
    Operating points for the Gazetteer, re-derived for the retrained
    training.json under OSDEV-3277. These are NOT free parameters: they belong
    to a specific model's score distribution, so they must be re-derived
    whenever data/training.json changes. See src/dedupe-hub/harness/README.md
    (`evaluate.py` prints both numbers) for the procedure.

    The previous values (0.8 / 0.5) were tuned to the 112-pair OAR-era model.
    Measured end-to-end against a real indexed corpus (49,470 BD facilities,
    600 items) the retrained model improves every band even with the old
    thresholds, so recalibration is an improvement rather than a guard against
    breakage:

      prod @ 0.8/0.5        auto 54.0%  queue 18.8%  new facility 27.2%
      retrained @ 0.356/0.007   auto 83.0%  queue  3.5%  new facility 13.5%
      retrained @ 0.8/0.5   auto 69.2%  queue 11.2%  new facility 19.7%

    The risk to watch is over-matching, not under-matching: auto-match rises
    from 54.0% to 83.0% of items, and an auto-match is unreviewed. 0.356 holds
    production's pair-level precision (0.9929 on clean labels), but over a
    larger auto-matched population. A more conservative AUTOMATIC_THRESHOLD is
    worth modelling if the shadow run shows false auto-matches rising.

    Derived on the held-out half of the 40k labeled-pair sample (2026-10-07) by
    matching the production operating point rather than the production number:

      AUTOMATIC_THRESHOLD -- the lowest score whose precision still matches the
        precision production achieves at 0.8 (0.9929 on clean labels). Never
        auto-accept at a worse error rate than today.
      GAZETTEER_THRESHOLD -- the score retaining the recall production retains
        at 0.5 (0.9965). Never drop a true match we surface today.

    Effect on the moderation queue: 24.0% -> 10.6% of candidate pairs.

    PENDING SHADOW VALIDATION (OSDEV-3277 AC#2). Every pair in the eval set was
    the incumbent gazetteer's own candidate, so these bands are conditional on
    candidacy. GAZETTEER_THRESHOLD in particular is now low enough to be close
    to "return everything", which cannot widen the candidate set in an offline
    eval but can live. Run with dedupe_hub_live=false on Test and compare
    AB_Test_ results against live decisions before this reaches production.
    '''

    AUTOMATIC_THRESHOLD = 0.356
    GAZETTEER_THRESHOLD = 0.007
    RECALL_WEIGHT = 1.0
