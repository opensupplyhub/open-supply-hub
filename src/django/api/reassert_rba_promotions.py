import logging

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from api.constants import OriginSource, ProcessingAction
from api.models import Facility, FacilityListItem, FacilityMatch

logger = logging.getLogger(__name__)

PROMOTABLE_ITEM_STATUSES = (
    FacilityListItem.MATCHED,
    FacilityListItem.CONFIRMED_MATCH,
)

PROMOTABLE_MATCH_STATUSES = (
    FacilityMatch.AUTOMATIC,
    FacilityMatch.CONFIRMED,
)

# The promote endpoint records 'Promoted <new> over <previous>' as the
# facility's change reason, and this command records the same wording with
# a suffix. The facility delete flow writes 'Deleted X and promoted Y' -
# lowercase, and never as a facility change reason - so it does not match.
PROMOTION_REASON_PREFIX = 'Promoted '

# Fields promote copies from the list item onto the facility. Saving only
# these leaves a concurrent write to anything else (is_closed, new_os_id,
# has_inexact_coordinates, a sync overwrite) intact instead of reverting
# it from a stale in-memory copy.
PROMOTED_FACILITY_FIELDS = (
    'name',
    'address',
    'country_code',
    'location',
    'created_from',
)


def is_rba_instance():
    return getattr(
        settings, 'INSTANCE_SOURCE', OriginSource.OSHUB
    ) == OriginSource.RBA


def _promotable_rba_matches():
    """
    RBA-origin matches that could be promoted, ignoring current state.

    Narrows the facility set before touching history, which is much larger
    than the set of facilities carrying an RBA contribution.
    """
    return FacilityMatch.objects.filter(
        origin_source=OriginSource.RBA,
        is_active=True,
        status__in=PROMOTABLE_MATCH_STATUSES,
        facility_list_item__status__in=PROMOTABLE_ITEM_STATUSES,
    ).exclude(facility_list_item__geocoded_point__isnull=True)


def latest_promoted_item_ids(facility_ids):
    """
    The list item each facility was most recently *deliberately* promoted
    to, read from facility history.

    History is the right source rather than a PROMOTE_MATCH processing
    result on the item, for two reasons.

    First, that marker does not mean "this item was promoted": the
    facility delete flow appends it to every other matched item as well
    (see facilities_view_set, the other_matches loop), so a contribution
    nobody promoted can carry it.

    Second, only history orders promotions against everything else that
    has happened to the facility. Taking the most recent promotion means a
    moderator who promotes a different contribution later - including a
    public one, which is how a promotion gets undone - is authoritative,
    and this command leaves that facility alone instead of reversing the
    decision on the next run.
    """
    rows = (
        Facility.history.model.objects
        .filter(
            id__in=list(facility_ids),
            history_change_reason__startswith=PROMOTION_REASON_PREFIX,
        )
        .order_by('id', '-history_date', '-history_id')
        .values_list('id', 'created_from_id')
    )

    latest = {}
    for facility_id, created_from_id in rows.iterator():
        # Ordered newest-first per facility, so the first row wins.
        latest.setdefault(facility_id, created_from_id)
    return latest


def find_reverted_promotions():
    '''
    Return the matches whose promotion has been undone.

    The daily sync from OS Hub overwrites every synced field of a shared
    facility, including created_from, so a promotion made on this instance
    is reverted whenever the public row changes. The contribution itself
    survives: its source, list item and match are rows created here, which
    the sync never touches. That makes the reverted set derivable rather
    than something we have to journal - the facility's own history records
    what it was last promoted to, and that record outlives the overwrite.

    A facility is out of date when its current created_from is not the
    item its most recent promotion set. Restoring is then a matter of
    promoting that item's match again.
    '''
    candidates = _promotable_rba_matches()
    facility_ids = set(candidates.values_list('facility_id', flat=True))
    if not facility_ids:
        return []

    promoted = latest_promoted_item_ids(facility_ids)
    if not promoted:
        return []

    current = dict(
        Facility.objects
        .filter(id__in=list(promoted))
        .values_list('id', 'created_from_id')
    )

    # Only where the promotion is no longer in force.
    wanted = {
        facility_id: item_id
        for facility_id, item_id in promoted.items()
        if item_id is not None and current.get(facility_id) != item_id
    }
    if not wanted:
        return []

    matches = (
        candidates
        .filter(
            facility_id__in=list(wanted),
            facility_list_item_id__in=list(wanted.values()),
        )
        .select_related(
            'facility',
            'facility__created_from',
            'facility__created_from__source',
            'facility__created_from__source__facility_list',
            'facility_list_item',
            'facility_list_item__source',
            'facility_list_item__source__facility_list',
        )
        .order_by('id')
    )

    # The two id__in filters cross-join, so keep only the pairs that
    # actually belong together.
    return [
        match for match in matches
        if wanted.get(match.facility_id) == match.facility_list_item_id
    ]


def _describe(item):
    if item.source.facility_list:
        return f'item {item.id} in list {item.source.facility_list.id}'
    return f'item {item.id}'


class PromotionConflict(RuntimeError):
    """Raised when the item cannot be promoted onto the facility."""


@transaction.atomic
def reassert_promotion(match):
    '''
    Re-apply a single promotion, mirroring the promote endpoint.

    The change reason keeps the "Promoted ... over ..." wording the
    facility history parser matches on, with a suffix recording that this
    was a re-assertion rather than a moderator action. Keeping the prefix
    also means the re-assertion is itself the facility's most recent
    promotion, so a later run reads it and does nothing.
    '''
    # Lock both rows and re-read them, so the values written are based on
    # the facility and item as they are now rather than as they were when
    # the set was built. Always the facility first and the item second, so
    # two concurrent runs cannot take them in opposite orders and deadlock.
    facility = Facility.objects.select_for_update().get(id=match.facility_id)

    # The item lock is what makes appending to processing_results safe.
    # That append is a read-modify-write here, while aws_batch appends with
    # raw SQL - processing_results = processing_results || '<json>' - across
    # every item of a source. Holding the row lock makes such an append wait
    # for this transaction and apply on top of the value written here,
    # instead of this save overwriting it from a stale in-memory list.
    # No select_related here: facility_list is nullable, so joining it
    # makes Postgres refuse the lock ("FOR UPDATE cannot be applied to the
    # nullable side of an outer join"). _describe loads it lazily instead.
    item = (
        FacilityListItem.objects
        .select_for_update()
        .get(id=match.facility_list_item_id)
    )
    previous_created_from_id = facility.created_from_id

    if item.geocoded_point is None:
        # The selection query excludes ungeocoded items, so this means the
        # point was cleared between then and now. Facility.location is not
        # nullable, so saving would raise IntegrityError and be swallowed
        # as a generic error - name the real problem instead.
        raise PromotionConflict(
            f'{item.id} no longer has a geocoded point, so it cannot be '
            f'promoted on {facility.id}.'
        )

    if previous_created_from_id == item.id:
        # Restored by an earlier iteration or a concurrent write.
        return None

    conflict = (
        Facility.objects
        .filter(created_from_id=item.id)
        .exclude(id=facility.id)
        .values_list('id', flat=True)
        .first()
    )
    if conflict:
        # created_from is a OneToOneField. Saving would raise IntegrityError
        # and be swallowed as a generic error, so name the real problem.
        raise PromotionConflict(
            f'{item.id} is already the created_from of {conflict}, so it '
            f'cannot also be promoted on {facility.id}. The item was most '
            'likely moved by a facility delete or merge.'
        )

    reason = (
        f'Promoted {_describe(item)} '
        f'over {_describe(facility.created_from)} '
        '(re-asserted after sync)'
    )

    facility.name = item.name
    facility.address = item.address
    facility.country_code = item.country_code
    facility.location = item.geocoded_point
    facility.created_from = item
    facility._change_reason = reason
    facility.save(update_fields=list(PROMOTED_FACILITY_FIELDS))

    now = str(timezone.now())
    item.processing_results.append({
        'action': ProcessingAction.PROMOTE_MATCH,
        'started_at': now,
        'error': False,
        'finished_at': now,
        'previous_created_from_id': previous_created_from_id,
    })
    item.save(update_fields=['processing_results'])

    return {
        'os_id': facility.id,
        'match_id': match.id,
        'item_id': item.id,
        'previous_created_from_id': previous_created_from_id,
    }


def reassert_rba_promotions(dry_run=False, limit=None):
    '''
    Restore RBA promotions that have been undone. Returns a summary dict.

    Safe to run repeatedly: a facility already created from the item its
    latest promotion names is not selected, so a run with nothing to do
    makes no writes.
    '''
    if limit is not None and limit < 1:
        raise ValueError('limit must be 1 or greater, got {}'.format(limit))

    matches = find_reverted_promotions()
    if limit is not None:
        matches = matches[:limit]

    summary = {
        'found': 0,
        'reasserted': 0,
        'skipped': 0,
        'errors': 0,
        'dry_run': dry_run,
    }

    for match in matches:
        summary['found'] += 1

        if dry_run:
            logger.info(
                'Would re-assert promotion of match %s on %s (created_from '
                'is %s)',
                match.id,
                match.facility_id,
                match.facility.created_from_id,
            )
            continue

        try:
            result = reassert_promotion(match)
            if result is None:
                summary['skipped'] += 1
                logger.info(
                    'Skipped %s: already created from item %s',
                    match.facility_id,
                    match.facility_list_item_id,
                )
                continue
            summary['reasserted'] += 1
            logger.info(
                'Re-asserted promotion of match %s on %s (was created_from '
                '%s)',
                result['match_id'],
                result['os_id'],
                result['previous_created_from_id'],
            )
        except PromotionConflict as err:
            summary['errors'] += 1
            logger.error(
                'Cannot re-assert promotion of match %s on %s: %s',
                match.id, match.facility_id, err,
            )
        except Exception:
            summary['errors'] += 1
            logger.exception(
                'Failed to re-assert promotion of match %s on %s',
                match.id,
                match.facility_id,
            )

    logger.info(
        'Re-assert finished: found=%s reasserted=%s skipped=%s errors=%s '
        'dry_run=%s',
        summary['found'],
        summary['reasserted'],
        summary['skipped'],
        summary['errors'],
        summary['dry_run'],
    )

    return summary
