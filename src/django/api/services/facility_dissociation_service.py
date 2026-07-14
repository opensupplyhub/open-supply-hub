from api.facility_history import create_dissociate_match_change_reason
from api.models.facility.facility import Facility
from api.models.facility.facility_match import FacilityMatch


def dissociate_contributor_matches(facility, contributor):
    """
    Deactivate every active match linking ``contributor`` to ``facility``.

    This is the shared core of contributor dissociation, used by both the
    legacy ``POST /api/facilities/{id}/dissociate/`` endpoint and the v1 API.
    It sets ``FacilityMatch.is_active = False`` (never deletes), records a
    django-simple-history change reason for each affected match, and bumps the
    facility's ``updated_at`` so downstream indexing (the Postgres
    ``api_facilityindex`` triggers and the Logstash ``production-locations``
    sync) picks up the change.

    Returns the number of matches that were deactivated.
    """
    matches = FacilityMatch.objects.filter(
        facility=facility,
        facility_list_item__source__contributor=contributor,
    )

    dissociated_count = 0

    # Call `save` in a loop rather than use `update` to make sure that
    # django-simple-history can log the changes.
    for match in matches:
        if match.is_active:
            match.is_active = False
            match._change_reason = create_dissociate_match_change_reason(
                match.facility_list_item,
                facility,
            )
            match.save()
            dissociated_count += 1

    Facility.update_facility_updated_at_field(facility.id)

    return dissociated_count
