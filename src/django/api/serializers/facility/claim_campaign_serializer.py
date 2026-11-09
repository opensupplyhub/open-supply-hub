from rest_framework import serializers

from api.models.facility.claim_campaign import ClaimCampaign
from api.models.facility.facility_list_item import FacilityListItem
from api.services.claim_campaign_service import (
    MAX_SUPPLIERS_PER_CAMPAIGN,
    get_campaign_invites,
    get_contributor_list_sources,
    serialize_suppliers,
)


class ClaimCampaignSerializer(serializers.ModelSerializer):
    """
    Read-only representation of a claim campaign for the campaign
    owner's dashboard, including per-supplier claim statuses.

    A campaign's suppliers are its chosen roster when it has one;
    otherwise (v1) every facility on the contributor's active lists.
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
        invites = get_campaign_invites(campaign)
        return [
            {**supplier, 'last_invite': invites.get(supplier['os_id'])}
            for supplier in self.get_campaign_suppliers(campaign)
        ]

    def get_campaign_suppliers(self, campaign):
        roster = [entry.facility for entry in campaign.suppliers.all()]
        if roster:
            return serialize_suppliers(roster)

        # Every list-based campaign of a contributor shares the same
        # roster, so compute it once per request.
        cache = self.context.setdefault('suppliers_by_contributor', {})
        if campaign.contributor_id not in cache:
            cache[campaign.contributor_id] = self.build_list_suppliers(
                campaign.contributor_id
            )
        return cache[campaign.contributor_id]

    @staticmethod
    def build_list_suppliers(contributor_id):
        facilities = {
            item.facility.id: item.facility
            for item in FacilityListItem.objects.filter(
                source__contributor_id=contributor_id,
                source__is_active=True,
                facility__isnull=False,
            ).select_related('facility')
        }
        return serialize_suppliers(facilities.values())


class ClaimCampaignCreateSerializer(serializers.Serializer):
    """
    Validates a brand's request to create a campaign from suppliers on
    one of its own active lists (public or private).
    """

    name = serializers.CharField(max_length=200, allow_blank=False)
    list_id = serializers.IntegerField()
    os_ids = serializers.ListField(
        child=serializers.CharField(max_length=32),
        allow_empty=False,
        max_length=MAX_SUPPLIERS_PER_CAMPAIGN,
    )

    def validate(self, data):
        contributor = self.context['contributor']
        source = (
            get_contributor_list_sources(contributor)
            .filter(facility_list_id=data['list_id'])
            .first()
        )
        if source is None:
            raise serializers.ValidationError(
                {'list_id': 'Choose one of your active lists.'}
            )

        on_list = set(
            FacilityListItem.objects.filter(
                source=source,
                facility_id__in=data['os_ids'],
            ).values_list('facility_id', flat=True)
        )
        missing = [os_id for os_id in data['os_ids'] if os_id not in on_list]
        if missing:
            raise serializers.ValidationError(
                {
                    'os_ids': (
                        'These OS IDs are not on the chosen list: '
                        + ', '.join(missing[:10])
                    )
                }
            )

        data['name'] = data['name'].strip()
        return data
