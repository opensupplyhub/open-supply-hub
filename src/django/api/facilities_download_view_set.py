from typing import Union

from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets, mixins
from django.utils import timezone

from api.pagination import PageAndSizePagination
from api.models.facility.facility_index import FacilityIndex
from api.models.user import User
from api.models.facility_download_limit import FacilityDownloadLimit
from api.serializers.facility.facility_query_params_serializer import (
    FacilityQueryParamsSerializer)
from api.serializers.facility.facility_download_serializer \
    import FacilityDownloadSerializer
from api.serializers.facility.facility_download_serializer_embed_mode \
    import FacilityDownloadSerializerEmbedMode
from api.serializers.utils import get_embed_contributor_id_from_query_params
from api.constants import FacilitiesDownloadSettings
from django.core.exceptions import ObjectDoesNotExist


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
        facilityDownloadLimit, created = FacilityDownloadLimit.objects.get_or_create(
            user=request.user,
            defaults={
                "last_download_time": timezone.now(),
                "download_count": 1,
            }
        )
        # if not created:
        #     facilityDownloadLimit.last_download_time = timezone.now()
        #     facilityDownloadLimit.download_count += 1
        #     facilityDownloadLimit.save()

        self.last_download_time = facilityDownloadLimit.last_download_time
        self.allowed_downloads = facilityDownloadLimit.allowed_downloads
        self.download_count = facilityDownloadLimit.download_count
        self.allowed_records_number = facilityDownloadLimit.allowed_records_number
        print('!!!!!', self.last_download_time)
        print('!!!!!', self.allowed_downloads)
        print('!!!!!', self.download_count)
        print('!!!!!', self.download_count)
        # try:
        #     facilityDownloadLimit = FacilityDownloadLimit.objects.get(user=request.user)
        #     if facilityDownloadLimit is None:
        #         new_record = FacilityDownloadLimit(
        #             user=request.user,
        #             last_download_time=timezone.now(),
        #             allowed_downloads=10,
        #             download_count=1,
        #         )
        #         new_record.save()
        #     else:
        #         self.last_download_time = apiFacilityDownloadLimit.last_download_time
        #         self.allowed_downloads = apiFacilityDownloadLimit.allowed_downloads
        #         self.download_count = apiFacilityDownloadLimit.download_count
        # except ObjectDoesNotExist:
        #     raise ValidationError("ObjectDoesNotExist")

        params = FacilityQueryParamsSerializer(data=request.query_params)

        if not params.is_valid():
            raise ValidationError(params.errors)

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
