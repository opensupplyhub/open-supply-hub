import logging

from django.conf import settings
from django.db import transaction
from django.db.models import F, Max
from django.utils import timezone

from api.constants import OriginSource, ProcessingAction
from api.models import FacilityListItem, FacilityMatch

logger = logging.getLogger(__name__)

PROMOTABLE_ITEM_STATUSES = (
    FacilityListItem.MATCHED,
    FacilityListItem.CONFIRMED_MATCH,
)

PROMOTABLE_MATCH_STATUSES = (
    FacilityMatch.AUTOMATIC,
    FacilityMatch.CONFIRMED,
)


def is_rba_instance():
    return getattr(
        settings, 'INSTANCE_SOURCE', OriginSource.OSHUB
    ) == OriginSource.RBA


def find_reverted_promotions():
    '''
    Return the matches whose promotion the sync has undone.

    The daily sync from OS Hub overwrites every synced field of a shared
    facility, including created_from, so a promotion made on this instance
    is reverted whenever the public row changes. The contribution itself
    survives: its source, list item and match are rows created here, which
    the sync never touches. That makes the reverted set derivable rather
    than something we have to journal - a facility is out of date when its
    newest promotable RBA match is not the one it is created from.

    Only the newest match per facility is considered, so re-asserting can
    never demote a facility to an older contribution.
    '''
    promotable = FacilityMatch.objects.filter(
        origin_source=OriginSource.RBA,
        is_active=True,
        status__in=PROMOTABLE_MATCH_STATUSES,
        facility_list_item__status__in=PROMOTABLE_ITEM_STATUSES,
    )

    newest_per_facility = (
        promotable
        .values('facility_id')
        .annotate(newest=Max('id'))
        .values_list('newest', flat=True)
    )

    return (
        FacilityMatch.objects
        .filter(id__in=list(newest_per_facility))
        .exclude(facility__created_from_id=F('facility_list_item_id'))
        .select_related(
            'facility',
            'facility__created_from',
            'facility__created_from__source',
            'facility_list_item',
            'facility_list_item__source',
        )
        .order_by('id')
    )


def _describe(item):
    if item.source.facility_list:
        return f'item {item.id} in list {item.source.facility_list.id}'
    return f'item {item.id}'


@transaction.atomic
def reassert_promotion(match):
    '''
    Re-apply a single promotion, mirroring the promote endpoint.

    The change reason keeps the "Promoted ... over ..." wording the
    facility history parser matches on, with a suffix recording that this
    was a re-assertion rather than a moderator action.
    '''
    facility = match.facility
    item = match.facility_list_item
    previous_created_from_id = facility.created_from_id

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
    facility.save()

    now = str(timezone.now())
    item.processing_results.append({
        'action': ProcessingAction.PROMOTE_MATCH,
        'started_at': now,
        'error': False,
        'finished_at': now,
        'previous_created_from_id': previous_created_from_id,
    })
    item.save()

    return {
        'os_id': facility.id,
        'match_id': match.id,
        'item_id': item.id,
        'previous_created_from_id': previous_created_from_id,
    }


def reassert_rba_promotions(dry_run=False, limit=None):
    '''
    Restore RBA promotions the sync reverted. Returns a summary dict.

    Safe to run repeatedly: a facility already created from its newest RBA
    match is not selected, so a run with nothing to do makes no writes.
    '''
    matches = find_reverted_promotions()
    if limit is not None:
        matches = matches[:limit]

    summary = {
        'found': 0,
        'reasserted': 0,
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
            summary['reasserted'] += 1
            logger.info(
                'Re-asserted promotion of match %s on %s (was created_from '
                '%s)',
                result['match_id'],
                result['os_id'],
                result['previous_created_from_id'],
            )
        except Exception:
            summary['errors'] += 1
            logger.exception(
                'Failed to re-assert promotion of match %s on %s',
                match.id,
                match.facility_id,
            )

    logger.info(
        'Re-assert finished: found=%s reasserted=%s errors=%s dry_run=%s',
        summary['found'],
        summary['reasserted'],
        summary['errors'],
        summary['dry_run'],
    )

    return summary
