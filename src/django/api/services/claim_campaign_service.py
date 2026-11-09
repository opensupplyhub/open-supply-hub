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
    FacilityListItem,
    Source,
)

SELF_SERVE_FLAG = 'claim_campaign_self_serve'
MAX_SUPPLIERS_PER_CAMPAIGN = 5000

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
        }
        for facility in facilities
    ]


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


def get_list_facilities(source):
    """
    The distinct matched production locations on one uploaded list, in
    upload order.
    """
    facilities = {}
    items = (
        FacilityListItem.objects.filter(
            source=source,
            facility__isnull=False,
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
