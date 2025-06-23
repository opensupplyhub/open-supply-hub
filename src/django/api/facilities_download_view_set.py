import logging

from rest_framework.exceptions import ValidationError
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from waffle import switch_is_active
from datetime import datetime
from django.utils.timezone import make_aware

from api.pagination import PageAndSizePagination
from api.models.facility.facility_index import FacilityIndex
from api.models.facility_download_limit import FacilityDownloadLimit
from api.serializers.facility.facility_query_params_serializer import (
    FacilityQueryParamsSerializer)
from api.serializers.facility.facility_download_serializer \
    import FacilityDownloadSerializer
from api.serializers.facility.facility_download_serializer_embed_mode \
    import FacilityDownloadSerializerEmbedMode
from api.serializers.utils import get_embed_contributor_id_from_query_params
from api.exceptions import ServiceUnavailableException
from api.constants import APIErrorMessages, FacilitiesDownloadSettings

logger = logging.getLogger(__name__)


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
        if switch_is_active('block_location_downloads'):
            raise ServiceUnavailableException(
                APIErrorMessages.TEMPORARILY_UNAVAILABLE
            )

        params = FacilityQueryParamsSerializer(data=request.query_params)

        if not params.is_valid():
            raise ValidationError(params.errors)

        logger.info(
            f'Facility downloads request for User ID: {request.user.id}'
        )

        queryset = FacilityIndex \
            .objects \
            .filter_by_query_params(request.query_params) \
            .order_by('name', 'address', 'id')

        total_records = queryset.count()

        initial_release_date = make_aware(datetime(2025, 6, 20))
        facility_download_limit = None

        if not switch_is_active('private_instance') and not switch_is_active('allow_large_downloads'):
            facility_download_limit = FacilityDownloadLimit \
                .get_or_create_user_download_limit(
                    request.user,
                    initial_release_date
                )

        current_page = int(request.query_params.get("page", 1))

        if (
            current_page == 1 and
            facility_download_limit
            and (facility_download_limit.free_download_records + facility_download_limit.paid_download_records) == 0  # noqa: E501
        ):
            raise ValidationError('You have reached the maximum number of '
                                  'facility downloads permitted for this year'
                                  ', both free and paid. Please wait until '
                                  'the start of the next calendar year to '
                                  'access additional data or to order new '
                                  'records for download.')

        is_large_download_allowed = (
            not facility_download_limit or
            total_records <= FacilitiesDownloadSettings.FACILITIES_DOWNLOAD_LIMIT  # noqa: E501
        )

        if (not is_large_download_allowed):
            records_sum = (
                facility_download_limit.free_download_records +
                facility_download_limit.paid_download_records
            )
            raise ValidationError(
                ('Downloads are supported only for searches resulting in '
                 f'{records_sum} '
                 'facilities or less.'))

        page_queryset = self.paginate_queryset(queryset)

        if page_queryset is None:
            raise ValidationError("Invalid pageSize parameter")

        list_serializer = self.get_serializer(page_queryset)
        rows = [f['row'] for f in list_serializer.data]
        headers = list_serializer.child.get_headers()
        data = {'rows': rows, 'headers': headers}
        response = self.get_paginated_response(data)

        records_to_subtract = len(data['rows'])

        if facility_download_limit:
            facility_download_limit.register_download(records_to_subtract)

        return response

    @action(
        detail=False,
        methods=['post'],
        url_path='upgrade',
        permission_classes=[IsAuthenticated]
    )
    def upgrade_download_limit(self, request):
        upgrade_number = request.data.get('upgrade_number')

        if upgrade_number is None:
            raise ValidationError("'upgrade_number' is required.")

        try:
            upgrade_number = int(upgrade_number)
        except ValueError:
            raise ValidationError("'upgrade_number' must be an integer.")
        
        try:
            download_limit = FacilityDownloadLimit.objects.get(user=request.user)
        except FacilityDownloadLimit.DoesNotExist:
            raise ValidationError(f"FacilityDownloadLimit with ID {request.user.id} does not exist.")

        download_limit = FacilityDownloadLimit.upgrade_user_download_limit(
            download_limit,
            upgrade_number
        )

        return Response({
            "allowed_records_number": download_limit.free_download_records + download_limit.paid_download_records
        })
