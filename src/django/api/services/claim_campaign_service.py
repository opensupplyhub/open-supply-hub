import re
import secrets

from django.db import IntegrityError, transaction
from django.db.models import Exists, OuterRef, Q
from rest_framework.exceptions import ValidationError
from waffle import switch_is_active

from api.constants import FacilityClaimStatuses
from api.models import (
    ClaimCampaign,
    ClaimCampaignSupplier,
    FacilityClaim,
    FacilityClaimInvite,
    FacilityList,
    FacilityListItem,
    Source,
)

SELF_SERVE_FLAG = 'claim_campaign_self_serve'
MAX_SUPPLIERS_PER_CAMPAIGN = 5000
# A supplier search returns at most this many facilities to choose from.
MAX_SEARCH_RESULTS = 500
# Search params that don't narrow the results, so a search made only of
# these would return the whole database.
NON_FILTER_SEARCH_PARAMS = frozenset({
    'sort_by',
    'page',
    'pageSize',
    'embed',
    'detail',
    'combine_contributors',
})

# Unambiguous characters for generated code suffixes (no 0/O, 1/I).
CODE_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'


def resolve_claim_campaign(facility, code):
    """
    Attribute a facility claim to an active claim campaign.

    A valid code for an ACTIVE campaign wins and marks the claim as
    submitted via a campaign link. Without a usable code, the claim is
    attributed only when exactly one ACTIVE campaign has the facility on
    its roster; an ambiguous match (two or more campaigns) attributes
    nothing. An invalid or unknown code never blocks the claim.

    A campaign's roster is its chosen suppliers when it has any;
    otherwise (v1 behaviour) it is every facility on the contributor's
    currently-active uploaded lists (replaced lists do not count).

    While the claim_campaigns switch is off no attribution happens at
    all, so existing claim behavior is fully unchanged.

    Returns a (campaign, via_link) tuple.
    """
    if not switch_is_active('claim_campaigns'):
        return None, False

    if code:
        campaign = ClaimCampaign.objects.filter(
            code=code.strip().upper(),
            status=ClaimCampaign.Status.ACTIVE,
        ).first()
        if campaign is not None:
            return campaign, True

    has_roster = ClaimCampaignSupplier.objects.filter(
        campaign=OuterRef('pk'),
    )
    on_roster = ClaimCampaignSupplier.objects.filter(
        campaign=OuterRef('pk'),
        facility=facility,
    )
    on_active_list = FacilityListItem.objects.filter(
        facility=facility,
        source__is_active=True,
    ).values('source__contributor')

    campaigns = list(
        ClaimCampaign.objects.filter(
            status=ClaimCampaign.Status.ACTIVE,
        ).filter(
            Q(Exists(on_roster))
            | (~Q(Exists(has_roster)) & Q(contributor__in=on_active_list))
        )[:2]
    )
    if len(campaigns) == 1:
        return campaigns[0], False
    return None, False


def campaign_includes_facility(campaign, facility):
    """
    Whether the facility is one of the campaign's suppliers: on its
    roster when it has one, otherwise (v1) on one of the contributor's
    active lists.
    """
    if campaign.suppliers.exists():
        return campaign.suppliers.filter(facility=facility).exists()
    return FacilityListItem.objects.filter(
        facility=facility,
        source__contributor_id=campaign.contributor_id,
        source__is_active=True,
    ).exists()


def get_campaign_for_invite(user, facility, code):
    """
    The sender's own active campaign with this code, for a claim invite
    sent from the campaign dashboard. Raises a ValidationError (shown to
    the sender) when the code isn't one of the sender's active campaigns
    or the facility isn't one of its suppliers.
    """
    contributor = getattr(user, 'contributor', None)
    campaign = None
    if contributor is not None and switch_is_active('claim_campaigns'):
        campaign = ClaimCampaign.objects.filter(
            code=code.strip().upper(),
            contributor=contributor,
            status=ClaimCampaign.Status.ACTIVE,
        ).first()
    if campaign is None:
        raise ValidationError(
            'This campaign is closed or isn\'t one of yours.'
        )
    if not campaign_includes_facility(campaign, facility):
        raise ValidationError(
            'This production location isn\'t part of this campaign.'
        )
    return campaign


def get_campaign_invites(campaign):
    """
    The most recent invite sent from the campaign to each supplier, as
    {facility_id: {recipient_email, created_at}}.
    """
    latest = {}
    for invite in campaign.invites.order_by('created_at'):
        latest[invite.facility_id] = {
            'recipient_email': invite.recipient_email,
            'created_at': invite.created_at,
        }
    return latest


def get_claim_statuses(facility_ids):
    """
    Map each facility ID to its public claim status: 'claimed' (approved
    claim), 'pending' (pending claim) or 'unclaimed'. Denied and revoked
    claims read as 'unclaimed', matching the public v1 API.

    Always read live from the claims table (nothing is cached), so a
    supplier that claims after the campaign was created shows as such on
    the next page load.
    """
    statuses = {}
    claims = FacilityClaim.objects.filter(
        facility_id__in=facility_ids,
        status__in=[
            FacilityClaimStatuses.APPROVED,
            FacilityClaimStatuses.PENDING,
        ],
    ).values_list('facility_id', 'status')
    for facility_id, status in claims:
        # An approved claim outranks a pending one.
        if statuses.get(facility_id) != 'claimed':
            statuses[facility_id] = (
                'claimed'
                if status == FacilityClaimStatuses.APPROVED
                else 'pending'
            )
    return {
        facility_id: statuses.get(facility_id, 'unclaimed')
        for facility_id in facility_ids
    }


def serialize_suppliers(facilities):
    """Supplier rows (with claim status) for an iterable of facilities."""
    facilities = list(facilities)
    statuses = get_claim_statuses([facility.id for facility in facilities])
    return [
        {
            'os_id': facility.id,
            'name': facility.name,
            'country_code': facility.country_code,
            'claim_status': statuses[facility.id],
            # Closed facilities can't be added to a campaign; one already
            # on a roster stays, shown as closed.
            'is_closed': bool(getattr(facility, 'is_closed', False)),
        }
        for facility in facilities
    ]


def search_campaign_candidates(query_params):
    """
    Facilities matching the public search filters, for a brand choosing
    campaign suppliers from a search. Closed facilities are left out
    because they can't be added to a campaign. Returns (total count,
    the first MAX_SEARCH_RESULTS facilities by name).
    """
    from api.models.facility.facility_index import FacilityIndex

    queryset = (
        FacilityIndex.objects.filter_by_query_params(query_params)
        .exclude(is_closed=True)
        .order_by('name', 'id')
    )
    return queryset.count(), list(queryset[:MAX_SEARCH_RESULTS])


def has_search_filter(query_params):
    return any(
        value.strip()
        for key in query_params.keys()
        if key not in NON_FILTER_SEARCH_PARAMS
        for value in query_params.getlist(key)
    )


def get_contributor_list_sources(contributor):
    """The contributor's active uploaded lists, newest first."""
    return (
        Source.objects.filter(
            contributor=contributor,
            source_type=Source.LIST,
            is_active=True,
            facility_list__isnull=False,
        )
        .select_related('facility_list')
        .order_by('-created_at')
    )


# The candidate "list" standing for everything the brand added through
# the API (one SINGLE source per submission) rather than by uploading a
# list file, so API-only contributors can pick suppliers too.
API_SOURCE_ID = 'api'
API_SOURCE_NAME = 'Locations added through the API'

# Item statuses still on their way to a match. A list with items in
# these states is still being processed.
PROCESSING_ITEM_STATUSES = (
    FacilityListItem.UPLOADED,
    FacilityListItem.PARSED,
    FacilityListItem.GEOCODED,
)


def get_contributor_api_items(contributor):
    """Matched items the contributor submitted through the API."""
    return exclude_removed_list_items(
        FacilityListItem.objects.filter(
            source__contributor=contributor,
            source__source_type=Source.SINGLE,
            source__is_active=True,
            facility__isnull=False,
        )
    )


def count_facilities(items):
    return items.values('facility_id').distinct().count()


def describe_list_source(source):
    """
    One entry of the step 1 list picker. A list is `pending` while OS
    Hub staff are still moderating it or its rows are still being
    processed; until then it may have no matched suppliers yet.
    """
    items = FacilityListItem.objects.filter(source=source)
    pending = (
        source.facility_list.status == FacilityList.PENDING
        or items.filter(status__in=PROCESSING_ITEM_STATUSES).exists()
    )
    return {
        'id': source.facility_list.id,
        'name': source.facility_list.name,
        'kind': 'list',
        'is_public': source.is_public,
        'created_at': source.created_at,
        'pending': pending,
        'supplier_count': count_facilities(
            exclude_removed_list_items(items.filter(facility__isnull=False))
        ),
    }


def describe_api_source(contributor):
    """
    The step 1 entry for the contributor's API submissions, or None if
    it has no matched ones.
    """
    items = get_contributor_api_items(contributor)
    supplier_count = count_facilities(items)
    if not supplier_count:
        return None
    return {
        'id': API_SOURCE_ID,
        'name': API_SOURCE_NAME,
        'kind': 'api',
        # Each API submission has its own public/private setting; the
        # entry is private if any of them is.
        'is_public': not items.filter(source__is_public=False).exists(),
        'created_at': None,
        'pending': False,
        'supplier_count': supplier_count,
    }


def get_api_facilities(contributor):
    """
    The distinct matched production locations the contributor added
    through the API, oldest submission first.
    """
    facilities = {}
    items = (
        get_contributor_api_items(contributor)
        .select_related('facility')
        .order_by('source__created_at', 'id')
    )
    for item in items:
        facilities.setdefault(item.facility.id, item.facility)
    return list(facilities.values())


def close_campaign(campaign):
    """
    Close a campaign. It stops collecting: new claims are no longer
    attributed to it and no more invites can be sent from it. Claims
    already attributed keep their campaign. Closing twice is a no-op.
    """
    if campaign.status != ClaimCampaign.Status.CLOSED:
        campaign.status = ClaimCampaign.Status.CLOSED
        campaign.save(update_fields=['status', 'updated_at'])
    return campaign


def exclude_removed_list_items(items):
    """
    Drop list items the contributor has since removed from the list:
    either the item itself was removed, or its match to a production
    location was dissociated (the facility link stays on the item).
    Mirrors the REMOVED filter on the facility list items endpoint.
    """
    return items.exclude(status=FacilityListItem.ITEM_REMOVED).exclude(
        facilitymatch__is_active=False
    )


def get_list_facilities(source):
    """
    The distinct matched production locations still on one uploaded
    list, in upload order.
    """
    facilities = {}
    items = (
        exclude_removed_list_items(
            FacilityListItem.objects.filter(
                source=source,
                facility__isnull=False,
            )
        )
        .select_related('facility')
        .order_by('row_index')
    )
    for item in items:
        facilities.setdefault(item.facility.id, item.facility)
    return list(facilities.values())


def make_code_prefix(contributor_name):
    words = re.findall(r'[A-Za-z0-9]+', contributor_name or '')
    return (words[0] if words else 'CAMPAIGN').upper()[:12]


def generate_campaign_code(contributor_name):
    prefix = make_code_prefix(contributor_name)
    suffix = ''.join(secrets.choice(CODE_ALPHABET) for _ in range(6))
    return f'{prefix}-{suffix}'


def create_campaign_with_suppliers(contributor, name, facility_ids):
    """
    Create an ACTIVE campaign for the contributor with an explicit
    supplier roster. Retries code generation in the (unlikely) event of
    a collision.
    """
    for _ in range(5):
        try:
            with transaction.atomic():
                campaign = ClaimCampaign.objects.create(
                    contributor=contributor,
                    name=name,
                    code=generate_campaign_code(contributor.name),
                )
                ClaimCampaignSupplier.objects.bulk_create(
                    [
                        ClaimCampaignSupplier(
                            campaign=campaign,
                            facility_id=facility_id,
                        )
                        for facility_id in dict.fromkeys(facility_ids)
                    ]
                )
                return campaign
        except IntegrityError:
            continue
    raise IntegrityError('Could not generate a unique campaign code.')


def move_campaign_suppliers(from_facility, to_facility):
    """
    Carry campaign rosters and sent invites over when a production
    location is merged into (or replaced by) another, so the campaign
    keeps the supplier under its surviving OS ID. Without this the
    roster rows would be cascade-deleted with the old facility, and a
    campaign that lost its whole roster would fall back to the v1
    every-list-facility roster.
    """
    already_on = set(
        ClaimCampaignSupplier.objects.filter(
            facility=to_facility,
        ).values_list('campaign_id', flat=True)
    )
    entries = ClaimCampaignSupplier.objects.filter(facility=from_facility)
    entries.filter(campaign_id__in=already_on).delete()
    entries.update(facility=to_facility)

    FacilityClaimInvite.objects.filter(facility=from_facility).update(
        facility=to_facility
    )
