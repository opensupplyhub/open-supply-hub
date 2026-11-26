"""Shared builders for FacilityClaim test rows.

FacilityClaim.objects.create is spelled out inline in ~30 test modules;
this is the start of consolidating that, and the one place that knows
how to build LEGACY-shaped rows: production carries decided claims from
before deciders were recorded (status_change_by NULL), claims with no
parent company, campaign, or invite, and facilities with country codes
that predate the current code list. Endpoints must serve those rows,
not 500 on them (the PR 1231 class).
"""
from api.constants import FacilityClaimStatuses
from api.models import FacilityClaim


def make_claim(facility, contributor, **overrides):
    """A PENDING claim with the minimal required fields; override at will.

    Legacy shapes worth testing (all default-off):
      status=<decided> with status_change_by left None - a decision from
      before deciders were recorded.
    """
    fields = {
        "facility": facility,
        "contributor": contributor,
        "contact_person": "Person",
        "job_title": "Title",
        "status": FacilityClaimStatuses.PENDING,
    }
    fields.update(overrides)
    return FacilityClaim.objects.create(**fields)
