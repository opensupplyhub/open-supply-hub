from waffle import switch_is_active
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
        facility_download_limit = None

        if not switch_is_active('private_instance'):
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

    # @action(
    #     detail=False,
    #     methods=['post'],
    #     url_path='upgrade',
    #     permission_classes=[IsAuthenticated]
    # )
    # def upgrade_download_limit(self, request):
    #     upgrade_number = request.data.get('upgrade_number')

    #     if upgrade_number is None:
    #         raise ValidationError("'upgrade_number' is required.")

    #     try:
    #         upgrade_number = int(upgrade_number)
    #     except ValueError:
    #         raise ValidationError("'upgrade_number' must be an integer.")
        
    #     try:
    #         download_limit = FacilityDownloadLimit.objects.get(user=request.user)
    #     except FacilityDownloadLimit.DoesNotExist:
    #         raise ValidationError(f"FacilityDownloadLimit with ID {request.user.id} does not exist.")

    #     download_limit = FacilityDownloadLimit.upgrade_user_download_limit(
    #         download_limit,
    #         upgrade_number
    #     )

    #     return Response({
    #         "allowed_records_number": download_limit.free_download_records + download_limit.paid_download_records
    #     })
