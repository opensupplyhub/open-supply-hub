from waffle import switch_is_active

from api.models import ClaimCampaign, FacilityListItem


def resolve_claim_campaign(facility, code):
    """
    Attribute a facility claim to an active claim campaign.

    A valid code for an ACTIVE campaign wins and marks the claim as
    submitted via a campaign link. Without a usable code, the claim is
    attributed only when exactly one ACTIVE campaign belongs to a
    contributor that has the facility on a currently-active uploaded
    list (replaced lists do not count); an ambiguous match (two or more
    campaigns) attributes nothing. An invalid or unknown code never
    blocks the claim.

    While the claim_campaigns switch is off no attribution happens at
    all, so existing claim behavior is fully unchanged.

    Returns a (campaign, via_link) tuple.
    """
    if not switch_is_active('claim_campaigns'):
        return None, False

    if code:
        campaign = ClaimCampaign.objects.filter(
            code=code,
            status=ClaimCampaign.Status.ACTIVE,
        ).first()
        if campaign is not None:
            return campaign, True

    campaigns = list(
        ClaimCampaign.objects.filter(
            status=ClaimCampaign.Status.ACTIVE,
            contributor__in=FacilityListItem.objects.filter(
                facility=facility,
                source__is_active=True,
            ).values('source__contributor'),
        )[:2]
    )
    if len(campaigns) == 1:
        return campaigns[0], False
    return None, False
