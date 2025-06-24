from rest_framework import viewsets, mixins
from api.pagination import PageAndSizePagination
from api.models.facility.facility_index import FacilityIndex
from api.serializers.facility.facility_download_serializer \
    import FacilityDownloadSerializer
from api.serializers.facility.facility_download_serializer_embed_mode \
    import FacilityDownloadSerializerEmbedMode
from api.serializers.utils import get_embed_contributor_id_from_query_params
from api.services.facilities_download_service import FacilitiesDownloadService


class FacilitiesDownloadViewSet(mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    """
    Get facilities in array format, suitable for CSV/XLSX download.
    """
    queryset = FacilityIndex.objects.all()
    pagination_class = PageAndSizePagination

    def get_serializer(self, page_queryset):
        if self.request.query_params.get('embed') == '1':
            contributor_id = get_embed_contributor_id_from_query_params(
                self.request.query_params
            )
            return FacilityDownloadSerializerEmbedMode(
                page_queryset, many=True, contributor_id=contributor_id
            )

        return FacilityDownloadSerializer(page_queryset, many=True)

    def list(self, request):
        """
        Returns a list of facilities in array format for a given query.
        (Maximum of 250 facilities per page.)
        """
        FacilitiesDownloadService.check_if_downloads_are_blocked()
        FacilitiesDownloadService.validate_query_params(request)
        FacilitiesDownloadService.log_request(request)

        queryset = FacilitiesDownloadService.get_filtered_queryset(request)
        total_records = queryset.count()

        facility_download_limit = FacilitiesDownloadService \
            .get_download_limit(request)
        FacilitiesDownloadService.enforce_limits(
            request,
            total_records,
            facility_download_limit
        )

        page_queryset = FacilitiesDownloadService \
            .check_pagination(self.paginate_queryset(queryset))
        list_serializer = self.get_serializer(page_queryset)

        rows = [f['row'] for f in list_serializer.data]
        headers = list_serializer.child.get_headers()
        data = {'rows': rows, 'headers': headers}

        response = self.get_paginated_response(data)

        records_to_subtract = len(data['rows'])
        FacilitiesDownloadService.register_download_if_needed(
            facility_download_limit,
            records_to_subtract
        )

        return response
