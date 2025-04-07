from rest_framework import viewsets, mixins
from django.utils import timezone
from typing import Optional, Union

from django.contrib.auth.models import AnonymousUser
import math
from django.db import transaction
from django.db.models import F

from api.pagination import PageAndSizePagination
from api.models.facility.facility_index import FacilityIndex
from api.models.facility_download_limit import FacilityDownloadLimit
from api.models.user import User
from api.serializers.facility.facility_query_params_serializer import (
    FacilityQueryParamsSerializer)
from api.serializers.facility.facility_download_serializer \
    import FacilityDownloadSerializer
from api.serializers.facility.facility_download_serializer_embed_mode \
    import FacilityDownloadSerializerEmbedMode
from api.serializers.utils import get_embed_contributor_id_from_query_params
from rest_framework.exceptions import ValidationError


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
        params = FacilityQueryParamsSerializer(data=request.query_params)

        if not params.is_valid():
            raise ValidationError(params.errors)

        facility_download_limit = self.__get_user_download_limit(request.user)
        fdl = facility_download_limit

        if (
            fdl
            and fdl.download_count >= fdl.allowed_downloads
        ):
            raise ValidationError('You have reached the maximum number of '
                                  'facility downloads allowed this month. '
                                  'Please wait until next month to download '
                                  'more data.')

        queryset = FacilityIndex \
            .objects \
            .filter_by_query_params(request.query_params) \
            .order_by('name', 'address', 'id')

        total_records = queryset.count()

        is_large_download_allowed = not facility_download_limit or (
            total_records < facility_download_limit.allowed_records_number
        )

        if (not is_large_download_allowed):
            raise ValidationError(
                ('Downloads are supported only for searches resulting in '
                 f'{facility_download_limit.allowed_records_number} '
                 'facilities or less.'))

        page_queryset = self.paginate_queryset(queryset)

        if page_queryset is None:
            raise ValidationError("Invalid pageSize parameter")

        page_size = int(request.query_params.get("pageSize", 100))
        current_page = int(request.query_params.get("page", 1))
        total_pages = math.ceil(total_records / page_size)

        if facility_download_limit and current_page >= total_pages:
            self.__update_facility_download_limit(facility_download_limit)

        list_serializer = self.get_serializer(page_queryset)
        rows = [f['row'] for f in list_serializer.data]
        headers = list_serializer.child.get_headers()
        data = {'rows': rows, 'headers': headers}
        response = self.get_paginated_response(data)
        return response

    @staticmethod
    def __get_user_download_limit(
        user: Union[AnonymousUser, User]
    ) -> Optional[FacilityDownloadLimit]:
        is_api_user = not user.is_anonymous and user.has_groups

        # if user is an API user we don't want to impose limits
        if is_api_user or user.is_anonymous:
            return None

        facility_download_limit, _ = FacilityDownloadLimit.objects \
            .get_or_create(user=user)

        current_month = timezone.now().month
        last_download_month = facility_download_limit.last_download_time.month

        if current_month != last_download_month:
            facility_download_limit.download_count = 0
            facility_download_limit.last_download_time = timezone.now()
            facility_download_limit.save()

        return facility_download_limit

    @staticmethod
    def __update_facility_download_limit(
        facility_download_limit: FacilityDownloadLimit,
    ) -> None:
        with transaction.atomic():
            facility_download_limit.refresh_from_db()
            if (
                facility_download_limit.download_count >=
                facility_download_limit.allowed_downloads
            ):
                raise ValidationError("Concurrent limit exceeded.")

            facility_download_limit.last_download_time = timezone.now()
            facility_download_limit.download_count = F('download_count') + 1
            facility_download_limit.save()
