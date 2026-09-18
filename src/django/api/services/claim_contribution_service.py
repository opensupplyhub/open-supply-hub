'''
Records an approved claimant's name and address as a contribution to their
production location.

The claim fields themselves (facility_name_english, facility_address) drive
promotion on the production location page through the existing claim
indexing. What they lack is submission history: nothing shows *when* the
claimant asserted a name or address, or lists it alongside the other
contributions. This service fills that gap by creating a CLAIM-type
ModerationEvent linked to the claim and approving it on the spot through
the same UpdateProductionLocation template that approves an SLC
contribution, which yields the Source, FacilityListItem and FacilityMatch
the location page and the index read as history.

The event is created already approved, never pending: the claim is the
pending record (claimants edit it, moderators decide it), so a second
pending object would have to be kept in sync and would surface in the
moderation queue - and be picked up by the external auto-approval
automation - independently of the claim decision.
'''
import logging
from typing import Dict, Optional, Tuple

from django.contrib.gis.geos import Point
from waffle import switch_is_active

from api.models.facility.facility_claim import FacilityClaim
from api.models.moderation_event import ModerationEvent
from api.models.sector import Sector
from api.models.user import User
from api.moderation_event_actions.approval.update_production_location import (
    UpdateProductionLocation,
)
from api.moderation_event_actions.creation.claim_contribution \
    .claim_contribution import ClaimContribution
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.moderation_event_actions.creation.moderation_event_creator import (
    ModerationEventCreator,
)

log = logging.getLogger(__name__)

LOG_PREFIX = '[Claim Contribution]'

# The switch that makes the claim form's name and address editable
# (OSDEV-3404, created inactive by migration 0241). The backend records
# contributions only while it is on, so the whole feature ships dark
# together: without it, a claimed-details edit of an approved claim's
# name or address would already start producing history.
CLAIM_NAME_ADDRESS_EDIT_SWITCH = 'enable_claim_name_address_edit'


class ClaimContributionError(Exception):
    '''
    The claim's name or address could not be cleaned into a contribution.
    Both values are validated with the same rules at claim submission, so
    this should not happen; when it does the caller's transaction rolls
    back rather than approving a claim whose history is silently missing.
    '''

    def __init__(self, claim_id: int, errors: Dict) -> None:
        super().__init__(
            f'Could not record the contribution for claim {claim_id}: '
            f'{errors}'
        )
        self.errors = errors


def has_name_or_address(claim: FacilityClaim) -> bool:
    return bool(
        (claim.facility_name_english or '').strip()
        or (claim.facility_address or '').strip()
    )


def record_claim_contribution(
    claim: FacilityClaim, acting_user: User
) -> Optional[ModerationEvent]:
    '''
    Create and approve a CLAIM moderation event carrying the claim's
    current name and address. Returns the event, or None when the
    enable_claim_name_address_edit switch is off or the claim asserts
    neither value (a claim from before the fields were editable).

    Meant to run inside the caller's transaction, after the claim itself
    has been saved with its new status or values. The acting user is the
    moderator on approval and the claimant on a later claimed-details
    edit, mirroring who actually made the values live.

    A value the claim does not assert is backfilled from the production
    location, the way an SLC PATCH backfills, so the list item is always
    a complete name/address/country row; the backfilled field names are
    recorded on the event.
    '''
    if not switch_is_active(CLAIM_NAME_ADDRESS_EDIT_SWITCH):
        return None
    if not has_name_or_address(claim):
        return None

    facility = claim.facility
    point, geocode_result = _resolve_location(claim, acting_user)

    raw_data = {
        'name': (claim.facility_name_english or '').strip(),
        'address': (claim.facility_address or '').strip(),
        'country': facility.country_code,
        # As strings, the way list uploads deliver them: ContriCleaner's
        # coordinate check treats a falsy value as absent, so a numeric
        # 0.0 latitude or longitude would be dropped.
        'coordinates': {'lat': str(point.y), 'lng': str(point.x)},
    }
    backfilled_fields = []
    if not raw_data['name']:
        raw_data['name'] = facility.name
        backfilled_fields.append('name')
    if not raw_data['address']:
        raw_data['address'] = facility.address
        backfilled_fields.append('address')

    # Mirror the sectors the claim itself asserts, so the contribution
    # says the same thing as the claim. Only names the Sector table knows
    # are passed: ContriCleaner files anything it does not recognise as a
    # product type, which would attribute invented product types to the
    # claimant. With no known sectors ContriCleaner records 'Unspecified',
    # which the location page already sorts last.
    sectors = _known_sectors(claim.sector)
    if sectors:
        raw_data['sector'] = sectors

    event_dto = CreateModerationEventDTO(
        contributor=claim.contributor,
        os=facility,
        claim=claim,
        raw_data=raw_data,
        request_type=ModerationEvent.RequestType.CLAIM.value,
        geocode_result=geocode_result or {},
        backfilled_fields=backfilled_fields,
    )
    result = ModerationEventCreator(ClaimContribution()) \
        .perform_event_creation(event_dto)
    if result.errors:
        log.error(
            f'{LOG_PREFIX} Cleaning failed for claim {claim.id}: '
            f'{result.errors}'
        )
        raise ClaimContributionError(claim.id, result.errors)

    event = result.moderation_event
    UpdateProductionLocation(
        event, acting_user, facility.id
    ).process_moderation_event()
    log.info(
        f'{LOG_PREFIX} Recorded contribution for claim {claim.id} on '
        f'{facility.id} as moderation event {event.uuid}.'
    )
    return event


def _known_sectors(values) -> list:
    if not values:
        return []
    return list(
        Sector.objects.filter(name__in=values)
        .order_by('name')
        .values_list('name', flat=True)
    )


def _resolve_location(
    claim: FacilityClaim, acting_user: User
) -> Tuple[Point, Optional[Dict]]:
    '''
    Decide where the contribution's list item is placed. Returns the point
    and the geocode result to record on the item (None: nothing geocoded).

    The claimant's own pin wins when they have placed one (the
    claimed-details form geocodes on the client and the PUT propagates the
    point to the facility). Otherwise the item sits at the production
    location's current pin, recorded as skipped_geocoder: a claimed
    address is a correction of the same place, and a CONFIRMED_MATCH
    contribution never moves the pin. Moving the pin to follow a changed
    claimed address is OSDEV-3406.
    '''
    if claim.facility_location is not None:
        return claim.facility_location, None
    return claim.facility.location, None
