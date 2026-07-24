from api.facility_history import create_dissociate_match_change_reason
from api.models.facility.facility import Facility
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_match import FacilityMatch


def dissociate_contributor_matches(
        facility, contributor, require_approved_list=False):
    """
    Deactivate every active match linking ``contributor`` to ``facility``.

    This is the shared core of contributor dissociation, used by both the
    legacy ``POST /api/facilities/{id}/dissociate/`` endpoint and the v1 API.
    The v1 endpoint sets ``require_approved_list=True`` so only contributions
    from lists approved by an admin can be dissociated. The legacy endpoint
    retains its existing behavior for contributor-responsibility lists.

    The service sets ``FacilityMatch.is_active = False`` (never deletes),
    records a django-simple-history change reason for each affected match, and
    bumps the facility's ``updated_at`` so downstream indexing (the Postgres
    ``api_facilityindex`` triggers and the Logstash ``production-locations``
    sync) picks up the change.

    The ``updated_at`` bump only happens when at least one match is actually
    deactivated, so callers can treat a return value of ``0`` as "nothing was
    changed".

    Returns the number of matches that were deactivated.
    """
    matches = FacilityMatch.objects.filter(
        facility=facility,
        facility_list_item__source__contributor=contributor,
    )

    if require_approved_list:
        matches = matches.filter(
            facility_list_item__source__facility_list__status=(
                FacilityList.APPROVED
            )
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

    if dissociated_count > 0:
        Facility.update_facility_updated_at_field(facility.id)

    return dissociated_count


def deactivate_contributor_source(facility_list, user):
    """
    Deactivate a contributor's list the same way the admin ``reject`` action
    does (minus the rejection email): mark the ``FacilityList`` as
    ``REJECTED``, which fires ``manual_list_reject_revert_trigger`` to force
    ``Source.is_active = False`` for the whole list.

    Setting the status - not just the source flag - is what makes the
    deactivation durable. That trigger re-syncs ``Source.is_active`` from the
    list status on every ``api_facilitylist`` update, so a source-only flip
    would be silently reverted by any later list update.

    Individual ``FacilityMatch`` rows are left untouched because
    ``FacilityMatch.should_display_association`` already requires the source to
    be active, so the whole list is anonymized through the source flag. The
    dissociation surfaces in facility history at read time (see
    ``create_dissociate_inactive_item_detail``).

    Returns True if the list was deactivated, False if its source was already
    inactive.
    """
    source = facility_list.source

    if not source.is_active:
        return False

    facility_list.status_change_reason = 'Deactivated by the contributor.'
    facility_list.status_change_by = user
    facility_list.status = FacilityList.REJECTED
    facility_list.save()

    if facility_list.replaces_id:
        facility_list.replaces = None
        facility_list.save()

    # The status change already deactivated the source via the trigger; set it
    # explicitly too, mirroring the admin reject path.
    source.is_active = False
    source.save()

    return True
