from rest_framework import serializers

from api.models.facility.claim_campaign import ClaimCampaign
from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem
from api.services.claim_campaign_service import (
    API_SOURCE_ID,
    MAX_SUPPLIERS_PER_CAMPAIGN,
    count_facilities,
    count_list_facilities,
    exclude_removed_list_items,
    get_claim_statuses,
    get_contributor_api_items,
    get_contributor_list_sources,
    get_item_facilities,
    is_too_large,
    serialize_suppliers,
    too_large_message,
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
        if campaign.uses_roster:
            # Exactly the chosen suppliers; an emptied roster stays empty.
            return serialize_suppliers(
                [entry.facility for entry in campaign.suppliers.all()]
            )

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
        return serialize_suppliers(
            get_item_facilities(
                exclude_removed_list_items(
                    FacilityListItem.objects.filter(
                        source__contributor_id=contributor_id,
                        source__is_active=True,
                        facility__isnull=False,
                    )
                )
            )
        )


# Fits about two lines of the campaign card title.
MAX_CAMPAIGN_NAME_LENGTH = 100


class ClaimCampaignCreateSerializer(serializers.Serializer):
    """
    Validates a brand's request to create a campaign. Suppliers come
    either from one of its own active lists (public or private), or its
    API submissions (`list_id` = "api"), when `list_id` is given, or from
    a search of OS Hub, when it isn't: then any facility can be chosen.
    Either way, facilities that are closed or already claimed are left
    out (and reported as `skipped`); pending claims are kept, since they
    may yet be denied.
    """

    # CharField trims surrounding whitespace before validating, so a
    # whitespace-only name is rejected as blank.
    name = serializers.CharField(max_length=MAX_CAMPAIGN_NAME_LENGTH)
    # A list ID, or `api` for the locations the brand added through the
    # API. Absent or null when the suppliers come from a search.
    list_id = serializers.CharField(required=False, allow_null=True)
    os_ids = serializers.ListField(
        child=serializers.CharField(max_length=32),
        allow_empty=False,
        max_length=MAX_SUPPLIERS_PER_CAMPAIGN,
    )

    def validate_name(self, value):
        # Collapse line breaks, tabs and runs of spaces into single spaces.
        name = ' '.join(value.split())
        if ClaimCampaign.objects.filter(
            contributor=self.context['contributor'],
            name__iexact=name,
        ).exists():
            raise serializers.ValidationError(
                'You already have a campaign with this name.'
            )
        return name

    def validate(self, data):
        data['os_ids'] = list(dict.fromkeys(data['os_ids']))
        if data.get('list_id') is None:
            self.validate_search_suppliers(data['os_ids'])
        elif data['list_id'] == API_SOURCE_ID:
            self.validate_api_suppliers(data['os_ids'])
        else:
            self.validate_list_suppliers(data['list_id'], data['os_ids'])
        data['os_ids'], data['skipped'] = self.leave_out_closed_and_claimed(
            data['os_ids']
        )
        return data

    def validate_api_suppliers(self, os_ids):
        self.refuse_too_large(
            count_facilities(
                get_contributor_api_items(self.context['contributor'])
            )
        )
        on_api = set(
            get_contributor_api_items(self.context['contributor'])
            .filter(facility_id__in=os_ids)
            .values_list('facility_id', flat=True)
        )
        missing = [os_id for os_id in os_ids if os_id not in on_api]
        if missing:
            raise serializers.ValidationError(
                {
                    'os_ids': (
                        'These OS IDs were not added through your API '
                        'submissions: '
                        + ', '.join(missing[:10])
                    )
                }
            )

    def validate_list_suppliers(self, list_id, os_ids):
        contributor = self.context['contributor']
        source = (
            get_contributor_list_sources(contributor)
            .filter(facility_list_id=list_id)
            .first()
            if str(list_id).isdigit()
            else None
        )
        if source is None:
            raise serializers.ValidationError(
                {'list_id': 'Choose one of your active lists.'}
            )
        self.refuse_too_large(count_list_facilities(source))

        on_list = set(
            exclude_removed_list_items(
                FacilityListItem.objects.filter(
                    source=source,
                    facility_id__in=os_ids,
                )
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
    def refuse_too_large(facility_count):
        if is_too_large(facility_count):
            raise serializers.ValidationError(
                {'list_id': too_large_message(facility_count)}
            )

    @staticmethod
    def validate_search_suppliers(os_ids):
        found = set(
            Facility.objects.filter(id__in=os_ids).values_list(
                'id', flat=True
            )
        )

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

    @staticmethod
    def leave_out_closed_and_claimed(os_ids):
        """
        The screen never offers closed or claimed facilities, but one can
        be closed or claimed between being chosen and the campaign being
        created. Leave those out and say which (`skipped`), rather than
        refusing the whole campaign. Pending claims stay in: they may yet
        be denied. Only when nothing is left is the request refused.
        """
        closed = set(
            Facility.objects.filter(id__in=os_ids, is_closed=True)
            .values_list('id', flat=True)
        )
        statuses = get_claim_statuses(os_ids)
        claimed = {
            os_id for os_id in os_ids
            if os_id not in closed and statuses[os_id] == 'claimed'
        }
        kept = [
            os_id for os_id in os_ids
            if os_id not in closed and os_id not in claimed
        ]
        if not kept:
            raise serializers.ValidationError(
                {
                    'os_ids': (
                        'None of the chosen production locations can be '
                        'invited: they have all been claimed or closed.'
                    )
                }
            )
        skipped = [
            {'os_id': os_id, 'reason': 'closed'}
            for os_id in os_ids if os_id in closed
        ] + [
            {'os_id': os_id, 'reason': 'claimed'}
            for os_id in os_ids if os_id in claimed
        ]
        return kept, skipped
