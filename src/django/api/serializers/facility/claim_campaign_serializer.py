from rest_framework import serializers

from api.models.facility.claim_campaign import ClaimCampaign
from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem
from api.services.claim_campaign_service import (
    MAX_SUPPLIERS_PER_CAMPAIGN,
    exclude_removed_list_items,
    get_campaign_invites,
    get_claim_statuses,
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
            for item in exclude_removed_list_items(
                FacilityListItem.objects.filter(
                    source__contributor_id=contributor_id,
                    source__is_active=True,
                    facility__isnull=False,
                )
            ).select_related('facility')
        }
        return serialize_suppliers(facilities.values())


class ClaimCampaignCreateSerializer(serializers.Serializer):
    """
    Validates a brand's request to create a campaign. Suppliers come
    either from one of its own active lists (public or private), when
    `list_id` is given, or from a search of OS Hub, when it isn't: then
    any facility that isn't closed or already claimed can be chosen.
    """

    name = serializers.CharField(max_length=200, allow_blank=False)
    list_id = serializers.IntegerField(required=False, allow_null=True)
    os_ids = serializers.ListField(
        child=serializers.CharField(max_length=32),
        allow_empty=False,
        max_length=MAX_SUPPLIERS_PER_CAMPAIGN,
    )

    def validate(self, data):
        data['os_ids'] = list(dict.fromkeys(data['os_ids']))
        if data.get('list_id') is None:
            self.validate_search_suppliers(data['os_ids'])
        else:
            self.validate_list_suppliers(data['list_id'], data['os_ids'])

        data['name'] = data['name'].strip()
        return data

    def validate_list_suppliers(self, list_id, os_ids):
        contributor = self.context['contributor']
        source = (
            get_contributor_list_sources(contributor)
            .filter(facility_list_id=list_id)
            .first()
        )
        if source is None:
            raise serializers.ValidationError(
                {'list_id': 'Choose one of your active lists.'}
            )

        on_list = set(
            FacilityListItem.objects.filter(
                source=source,
                facility_id__in=os_ids,
            ).values_list('facility_id', flat=True)
        )
        missing = [os_id for os_id in os_ids if os_id not in on_list]
        if missing:
            raise serializers.ValidationError(
                {
                    'os_ids': (
                        'These OS IDs are not on the chosen list: '
                        + ', '.join(missing[:10])
                    )
                }
            )

    @staticmethod
    def validate_search_suppliers(os_ids):
        facilities = Facility.objects.filter(id__in=os_ids)
        found = {f.id: f for f in facilities}

        missing = [os_id for os_id in os_ids if os_id not in found]
        if missing:
            raise serializers.ValidationError(
                {
                    'os_ids': (
                        'These OS IDs were not found: '
                        + ', '.join(missing[:10])
                    )
                }
            )

        closed = [f.id for f in facilities if f.is_closed]
        if closed:
            raise serializers.ValidationError(
                {
                    'os_ids': (
                        'Closed production locations can\'t be added: '
                        + ', '.join(closed[:10])
                    )
                }
            )

        statuses = get_claim_statuses(os_ids)
        claimed = [
            os_id for os_id in os_ids if statuses[os_id] == 'claimed'
        ]
        if claimed:
            raise serializers.ValidationError(
                {
                    'os_ids': (
                        'These production locations are already claimed: '
                        + ', '.join(claimed[:10])
                    )
                }
            )
