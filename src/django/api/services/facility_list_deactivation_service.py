from api.models.facility.facility_list import FacilityList


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
