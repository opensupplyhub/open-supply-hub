from datetime import datetime
from django.utils import timezone

from django.db import transaction

from api.models import (Facility, FacilityActivityReport, FacilityListItem,
                        Contributor, User)


# How many facility ids a dry run reports back. The count in 'to_close' is
# always complete; this only bounds the ids printed alongside it.
ID_SAMPLE_LIMIT = 2000


def _get_raw_value(list_item, field):
    raw = list_item.raw_json or {}
    for key, value in raw.items():
        if key.strip().lower() == field:
            return (value or '').strip().upper()
    return ''


def _facility_ids_by_status(list_id, status_field, status_values):
    """Partition the list's matched facilities by the raw status column.

    Returns (ids_to_close, ids_kept_open). A facility is closed only when
    at least one of its rows in this list carries a wanted status value
    and NONE of its rows carries any other status — so a facility that a
    row marks e.g. ACTIVE stays open even if another row of the same
    facility says INACTIVE.
    """
    field = status_field.strip().lower()
    wanted = {value.strip().upper() for value in status_values}
    close_ids = set()
    keep_open_ids = set()
    items = FacilityListItem.objects.filter(
        source__facility_list_id=list_id,
        facility__isnull=False).only('facility_id', 'raw_json')
    for item in items.iterator():
        if _get_raw_value(item, field) in wanted:
            close_ids.add(item.facility_id)
        else:
            keep_open_ids.add(item.facility_id)
    return close_ids - keep_open_ids, keep_open_ids


@transaction.atomic
def close_list(list_id, user_id, status_field=None, status_values=None,
               dry_run=False):
    """Close facilities belonging to a list.

    Without status_field, closes every facility in the list (original
    behavior). With status_field + status_values, closes only facilities
    whose uploaded rows carry one of the given values in that raw column
    (case-insensitive), skipping facilities that any row of the same list
    marks with a different status and facilities already closed.

    Returns a summary dict; with dry_run=True nothing is written.
    """
    user = User.objects.get(id=user_id)
    contributor = Contributor.objects.get(admin=user)
    now = datetime.now(tz=timezone.get_default_timezone())

    if status_field:
        target_ids, _ = _facility_ids_by_status(
            list_id, status_field, status_values or [])
        facilities = Facility.objects.filter(
            id__in=target_ids, is_closed=False)
        reason = ('Closed via bulk list closure ({0} in {1})'.format(
            status_field, ', '.join(sorted(
                v.strip().upper() for v in status_values or []))))
    else:
        facilities = Facility.objects.filter(
            facilitylistitem__source__facility_list_id=list_id).distinct()
        reason = "Closed via bulk list closure"

    summary = {
        'list_id': list_id,
        'to_close': facilities.count(),
        'closed': 0,
        'dry_run': dry_run,
        # Capped so a large list does not dump tens of thousands of ids into
        # the command output. Named a sample so the cap cannot be mistaken
        # for the full set - 'to_close' above is always the real count.
        'facility_ids_sample': list(
            facilities.values_list('id', flat=True)[:ID_SAMPLE_LIMIT]),
    }
    if dry_run:
        return summary

    for facility in facilities:
        facility.is_closed = True
        facility.save()
        FacilityActivityReport.objects.create(
            facility=facility,
            reported_by_user=user,
            reported_by_contributor=contributor,
            reason_for_report=reason,
            closure_state="CLOSED",
            approved_at=now,
            status=FacilityActivityReport.CONFIRMED,
            status_change_reason=reason,
            status_change_by=user,
            status_change_date=now,
        )
        summary['closed'] += 1
    return summary
