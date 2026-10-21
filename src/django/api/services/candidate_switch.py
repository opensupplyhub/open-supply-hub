"""
The Earth Genome candidate pilot kill switch (OSDEV-3627).

One waffle switch, ``earth_genome_candidates``, created inactive by
migration 0251, turns the whole candidate pilot on or off per
environment without a deploy. While it is inactive:

* ``ingest_satellite_detections`` refuses to run;
* the candidate vote and retirement-request endpoints answer 404;
* a candidate OS ID answers 404 on both detail endpoints, exactly as
  before the pilot (a retired OS ID keeps answering 410);
* ``GET /api/v1/production-locations/candidates/`` answers 404, so the
  map never draws candidate footprints.

What the switch does **not** touch, on purpose: every candidate
exclusion (default manager, index trigger, logstash, downloads, reports,
admin) and the contributor guard (OSDEV-3248). Those are safety
behaviours that cost nothing when no candidates exist and must hold
whenever they do.

The React app reads the same switch from ``/api-feature-flags/``.
"""
from waffle import switch_is_active

SWITCH_NAME = 'earth_genome_candidates'


def candidates_enabled() -> bool:
    return switch_is_active(SWITCH_NAME)
