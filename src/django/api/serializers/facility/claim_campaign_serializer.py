from rest_framework import serializers

from api.constants import FacilityClaimStatuses
from api.models.facility.claim_campaign import ClaimCampaign
from api.models.facility.facility_claim import FacilityClaim
from api.models.facility.facility_list_item import FacilityListItem


class ClaimCampaignSerializer(serializers.ModelSerializer):
    """
    Read-only representation of a claim campaign for the campaign
    owner's dashboard, including per-supplier claim statuses for the
    facilities on the contributor's uploaded lists.
    """

    suppliers = serializers.SerializerMethodField()

    class Meta:
        model = ClaimCampaign
        fields = (
            'id',
            'name',
            'code',
            'status',
            'created_at',
            'suppliers',
        )

    def get_suppliers(self, campaign):
        # Every campaign of a contributor shares the same roster, so
        # compute it once per request instead of once per campaign.
        cache = self.context.setdefault('suppliers_by_contributor', {})
        if campaign.contributor_id not in cache:
            cache[campaign.contributor_id] = self.build_suppliers(
                campaign.contributor_id
            )
        return cache[campaign.contributor_id]

    @staticmethod
    def build_suppliers(contributor_id):
        facilities = {
            item.facility.id: item.facility
            for item in FacilityListItem.objects.filter(
                source__contributor_id=contributor_id,
                source__is_active=True,
                facility__isnull=False,
            ).select_related('facility')
        }

        claim_statuses = {}
        claims = FacilityClaim.objects.filter(
            facility_id__in=facilities.keys(),
            status__in=[
                FacilityClaimStatuses.APPROVED,
                FacilityClaimStatuses.PENDING,
            ],
        ).values_list('facility_id', 'status')
        for facility_id, status in claims:
            # An approved claim outranks a pending one.
            if claim_statuses.get(facility_id) != 'claimed':
                claim_statuses[facility_id] = (
                    'claimed'
                    if status == FacilityClaimStatuses.APPROVED
                    else 'pending'
                )

        return [
            {
                'os_id': facility.id,
                'name': facility.name,
                'country_code': facility.country_code,
                'claim_status': claim_statuses.get(facility.id, 'unclaimed'),
            }
            for facility in facilities.values()
        ]
