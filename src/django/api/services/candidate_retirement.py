"""
Retire a candidate OS ID that the community decided is not a facility
(OSDEV-3246, design decisions D3 and D5).

Retirement is a hard delete of the candidate ``Facility`` row plus a
terminal ``FacilityAlias`` tombstone (``reason=NOT_A_FACILITY``,
``facility=None``) that keeps what must outlive the row: the detection
key ``(source, external_id)`` so ingest can refuse to re-create the
detection, and the final vote tally for audit and the feedback export.

The vote model that decides *when* to retire is OSDEV-3245; it calls
``retire_candidate`` with the tally it computed. Ingest (OSDEV-3244)
calls ``is_retired_detection`` before ``update_or_create``.
"""
from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone

from api.constants import ProcessingAction
from api.models.extended_field import ExtendedField
from api.models.facility.facility_alias import FacilityAlias
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_match import FacilityMatch
from api.models.source import Source
from api.models.version import Version

RETIRED_DETAIL = (
    'This OS ID was retired: the community determined it is not a facility.'
)


class NotACandidateError(ValueError):
    """Raised when retirement is requested for a non-candidate facility."""


def is_retired_detection(source, external_id):
    """
    True when a detection ``(source, external_id)`` was retired as
    NOT_A_FACILITY, so ingest must not create a candidate for it again.
    """
    if not source or not external_id:
        return False
    return FacilityAlias.objects.filter(
        reason=FacilityAlias.NOT_A_FACILITY,
        retired_source=source,
        retired_external_id=external_id,
    ).exists()


def get_tombstone(os_id):
    """The NOT_A_FACILITY tombstone for ``os_id``, or None."""
    return FacilityAlias.objects.filter(
        os_id=os_id,
        reason=FacilityAlias.NOT_A_FACILITY,
        facility__isnull=True,
    ).first()


def tombstone_payload(alias):
    """The 410 Gone response body for a retired OS ID."""
    tally = alias.retirement_tally or {}
    return {
        'detail': RETIRED_DETAIL,
        'os_id': alias.os_id,
        'retired_at': tally.get('retired_at'),
    }


def _build_tally(tally, retired_by):
    stored = dict(tally or {})
    stored.setdefault('confirmed', 0)
    stored.setdefault('not_a_facility', 0)
    stored.setdefault('retired_at', timezone.now().isoformat())
    stored['retired_by'] = (
        retired_by.id if retired_by is not None else None
    )
    return stored


def _detach_list_item(item, os_id, now):
    """Mirror of FacilitiesViewSet.destroy()'s list-item handling."""
    item.status = FacilityListItem.DELETED
    item.processing_results.append({
        'action': ProcessingAction.DELETE_FACILITY,
        'started_at': now,
        'error': False,
        'finished_at': now,
        'deleted_os_id': os_id,
    })
    item.facility = None
    item.save()


@transaction.atomic
def retire_candidate(facility, tally, retired_by=None):
    """
    Hard-delete candidate ``facility`` and leave a NOT_A_FACILITY tombstone.

    ``tally`` is the final vote tally as a dict (``confirmed``,
    ``not_a_facility`` counts; anything else the caller wants kept).
    ``retired_at`` is stamped if absent and ``retired_by`` is recorded as
    the user's id. Returns the tombstone ``FacilityAlias``.

    Raises ``NotACandidateError`` before touching anything if
    ``facility.is_candidate`` is False: confirmed facilities leave through
    merge or superuser delete, never through here.

    Deletion order is dictated by the PROTECT graph around a candidate's
    synthetic Source -> FacilityListItem -> FacilityMatch records:

    1. FacilityMatch rows go first: ``FacilityMatch.facility`` and
       ``FacilityMatch.facility_list_item`` are both PROTECT.
    2. ExtendedFields of the list item go next:
       ``ExtendedField.facility_list_item`` is PROTECT (the facility side
       would CASCADE, but the item side would not).
    3. Every list item pointing at the facility is detached
       (``facility=None``): ``FacilityListItem.facility`` is PROTECT, so
       the facility row cannot be deleted while an item points at it.
    4. The tombstone is created, then the Facility row is deleted. The
       index trigger drops the ``api_facilityindex`` row and the
       ``post_delete`` signal removes the OpenSearch document (tolerant
       of a document that never existed).
    5. Only now can the ``created_from`` list item be deleted:
       ``Facility.created_from`` is a OneToOne PROTECT *from* the
       facility *to* the item, so the item is protected until the
       facility is gone.
    6. The Source is deleted last (``FacilityListItem.source`` is
       PROTECT) and only if no other item still uses it, which keeps a
       shared ingest-batch Source intact.
    """
    if not facility.is_candidate:
        raise NotACandidateError(
            f'{facility.id} is not a candidate and cannot be retired as '
            'NOT_A_FACILITY. Confirmed facilities are removed through '
            'merge or superuser deletion.'
        )

    os_id = facility.id
    created_from = facility.created_from
    source = created_from.source
    now = str(timezone.now())
    change_reason = f'Retired {os_id}: not a facility'

    # 1. Matches (PROTECT on both facility and facility_list_item).
    matches = FacilityMatch.objects.filter(
        Q(facility=facility) | Q(facility_list_item=created_from)
    )
    for match in matches:
        match._change_reason = change_reason
        match.delete()

    # 2. Extended fields of the created_from item (PROTECT on the item).
    ExtendedField.objects.filter(facility_list_item=created_from).delete()

    # 3. Detach every list item still pointing at the facility (PROTECT).
    for item in FacilityListItem.objects.filter(facility=facility):
        if item.id == created_from.id:
            item.facility = None
            item.save(update_fields=['facility'])
        else:
            _detach_list_item(item, os_id, now)

    # Redirect aliases that pointed at the candidate (PROTECT) would now
    # dangle; a candidate is never a merge target, but be safe.
    for alias in FacilityAlias.objects.filter(facility=facility):
        alias._change_reason = change_reason
        alias.delete()

    # 4. Tombstone first, then the facility row. Both are in the same
    # transaction, so a failure here leaves nothing half-retired.
    tombstone = FacilityAlias.objects.create(
        os_id=os_id,
        facility=None,
        reason=FacilityAlias.NOT_A_FACILITY,
        retired_source=facility.source or None,
        retired_external_id=facility.external_id,
        retirement_tally=_build_tally(tally, retired_by),
    )

    facility._change_reason = change_reason
    facility.delete()

    # 5. The created_from item is no longer protected by the facility.
    created_from.delete()

    # 6. The synthetic source, unless other items still hang off it.
    if not FacilityListItem.objects.filter(source=source).exists():
        Source.objects.filter(id=source.id).delete()

    try:
        tile_version = Version.objects.get(name='tile_version')
        tile_version.version = F('version') + 1
        tile_version.save()
    except Version.DoesNotExist:
        pass

    return tombstone
