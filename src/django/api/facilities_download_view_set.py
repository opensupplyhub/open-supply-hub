from typing import Union
import logging

from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets, mixins
from waffle import switch_is_active

from api.pagination import PageAndSizePagination
from api.models.facility.facility_index import FacilityIndex
from api.models.user import User
from api.serializers.facility.facility_query_params_serializer import (
    FacilityQueryParamsSerializer)
from api.serializers.facility.facility_download_serializer \
    import FacilityDownloadSerializer
from api.serializers.facility.facility_download_serializer_embed_mode \
    import FacilityDownloadSerializerEmbedMode
from api.serializers.utils import get_embed_contributor_id_from_query_params
from api.constants import FacilitiesDownloadSettings
from api.exceptions import ServiceUnavailableException
from api.constants import APIErrorMessages

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

        is_large_download_allowed = self.__can_user_download_over_limit(
            queryset.count(), request.user
        )
        if (not is_large_download_allowed):
            raise ValidationError(
                ('Downloads are supported only for searches resulting in '
                 f'{FacilitiesDownloadSettings.DEFAULT_LIMIT} '
                 'facilities or less.'))

        page_queryset = self.paginate_queryset(queryset)

        if page_queryset is None:
            raise ValidationError("Invalid pageSize parameter")

        list_serializer = self.get_serializer(page_queryset)
        rows = [f['row'] for f in list_serializer.data]
        headers = list_serializer.child.get_headers()
        data = {'rows': rows, 'headers': headers}
        response = self.get_paginated_response(data)
        return response

    @staticmethod
    def __can_user_download_over_limit(
            number: int,
            user: Union[AnonymousUser, User]) -> bool:
        is_over_limit = number > FacilitiesDownloadSettings.DEFAULT_LIMIT
        is_api_user = not user.is_anonymous and user.has_groups

        if not is_api_user and is_over_limit:
            return False

        return True
