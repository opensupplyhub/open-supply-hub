from rest_framework.serializers import (
    SerializerMethodField,
    ModelSerializer,
)
from django.db.models import Count
from django.urls import reverse

from ...models import (
    FacilityList,
    FacilityListItem,
    Source,
)


class FacilityListSerializer(ModelSerializer):
    is_active = SerializerMethodField()
    is_public = SerializerMethodField()
    item_count = SerializerMethodField()
    items_url = SerializerMethodField()
    status = SerializerMethodField()
    statuses = SerializerMethodField()
    status_counts = SerializerMethodField()
    contributor_id = SerializerMethodField()

    class Meta:
        model = FacilityList
        fields = ('id', 'name', 'description', 'file_name', 'is_active',
                  'is_public', 'item_count', 'items_url', 'statuses',
                  'status_counts', 'contributor_id', 'created_at',
                  'match_responsibility', 'status', 'status_change_reason',
                  'file', 'parsing_errors')
        read_only_fields = ('created_at', 'match_responsibility')

    def get_is_active(self, facility_list):
        try:
            return facility_list.source.is_active
        except Source.DoesNotExist:
            return False

    def get_is_public(self, facility_list):
        try:
            return facility_list.source.is_public
        except Source.DoesNotExist:
            return False

    def get_item_count(self, facility_list):
        try:
            return facility_list.source.facilitylistitem_set.count()
        except Source.DoesNotExist:
            return 0

    def get_items_url(self, facility_list):
        return reverse('facility-list-items',
                       kwargs={'pk': facility_list.pk})

    def get_status(self, facility_list):
        if hasattr(facility_list, 'replaced_by'):
            return FacilityList.REPLACED

        return facility_list.status

    def get_statuses(self, facility_list):
        try:
            return (facility_list.source.facilitylistitem_set
                    .values_list('status', flat=True)
                    .distinct())
        except Source.DoesNotExist:
            return []

    def get_status_counts(self, facility_list):
        try:
            statuses = FacilityListItem \
                .objects \
                .filter(source=facility_list.source) \
                .values('status') \
                .annotate(status_count=Count('status'))
        except Source.DoesNotExist:
            statuses = []

        status_counts_dictionary = {
            status_dict.get('status'): status_dict.get('status_count')
            for status_dict
            in statuses
        }

        uploaded = status_counts_dictionary.get(
            FacilityListItem.UPLOADED,
            0
        )

        parsed = status_counts_dictionary.get(
            FacilityListItem.PARSED,
            0
        )

        geocoded = status_counts_dictionary.get(
            FacilityListItem.GEOCODED,
            0
        )

        geocoded_no_results = status_counts_dictionary.get(
            FacilityListItem.GEOCODED_NO_RESULTS,
            0
        )

        matched = status_counts_dictionary.get(
            FacilityListItem.MATCHED,
            0
        )

        potential_match = status_counts_dictionary.get(
            FacilityListItem.POTENTIAL_MATCH,
            0
        )

        confirmed_match = status_counts_dictionary.get(
            FacilityListItem.CONFIRMED_MATCH,
            0
        )

        error = status_counts_dictionary.get(
            FacilityListItem.ERROR,
            0
        )

        error_parsing = status_counts_dictionary.get(
            FacilityListItem.ERROR_PARSING,
            0
        )

        error_geocoding = status_counts_dictionary.get(
            FacilityListItem.ERROR_GEOCODING,
            0
        )

        error_matching = status_counts_dictionary.get(
            FacilityListItem.ERROR_MATCHING,
            0
        )

        duplicate = status_counts_dictionary.get(
            FacilityListItem.DUPLICATE,
            0
        )

        deleted = status_counts_dictionary.get(
            FacilityListItem.DELETED,
            0
        )

        item_removed = status_counts_dictionary.get(
            FacilityListItem.ITEM_REMOVED,
            0
        )

        return {
            FacilityListItem.UPLOADED: uploaded,
            FacilityListItem.PARSED: parsed,
            FacilityListItem.GEOCODED: geocoded,
            FacilityListItem.GEOCODED_NO_RESULTS: geocoded_no_results,
            FacilityListItem.MATCHED: matched,
            FacilityListItem.POTENTIAL_MATCH: potential_match,
            FacilityListItem.CONFIRMED_MATCH: confirmed_match,
            FacilityListItem.ERROR: error,
            FacilityListItem.ERROR_PARSING: error_parsing,
            FacilityListItem.ERROR_GEOCODING: error_geocoding,
            FacilityListItem.ERROR_MATCHING: error_matching,
            FacilityListItem.DUPLICATE: duplicate,
            FacilityListItem.DELETED: deleted,
            FacilityListItem.ITEM_REMOVED: item_removed,
        }

    def get_contributor_id(self, facility_list):
        try:
            return facility_list.source.contributor.id \
                if facility_list.source.contributor else None
        except Source.DoesNotExist:
            return None
