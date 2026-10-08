class GazetteerMatchDefaults:
    '''
    Operating points for the Gazetteer, re-derived for the retrained
    training.json under OSDEV-3277. These are NOT free parameters: they belong
    to a specific model's score distribution, so they must be re-derived
    whenever data/training.json changes. See src/dedupe-hub/harness/README.md
    (`evaluate.py` prints both numbers) for the procedure.

    The previous values (0.8 / 0.5) were tuned to the 112-pair OAR-era model.
    Carrying them onto the retrained classifier would push the share of
    candidate pairs scoring below GAZETTEER_THRESHOLD from 0.3% to 16.5% --
    pairs that Gazetteer.match() then stops returning at all, so they become
    silently created duplicate facilities rather than moderation-queue items.

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
