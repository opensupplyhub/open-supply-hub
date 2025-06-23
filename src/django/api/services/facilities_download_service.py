import logging

from rest_framework.exceptions import ValidationError
from waffle import switch_is_active
from datetime import datetime
from django.utils.timezone import make_aware

from api.models.facility.facility_index import FacilityIndex
from api.models.facility_download_limit import FacilityDownloadLimit
from api.serializers.facility.facility_query_params_serializer import (
    FacilityQueryParamsSerializer)
from api.exceptions import ServiceUnavailableException
from api.constants import APIErrorMessages, FacilitiesDownloadSettings

logger = logging.getLogger(__name__)


class FacilitiesDownloadService:
    def _check_if_downloads_are_blocked(self):
        if switch_is_active('block_location_downloads'):
            raise ServiceUnavailableException(
                    APIErrorMessages.TEMPORARILY_UNAVAILABLE
                )

    def _validate_query_params(self, request):
        params = FacilityQueryParamsSerializer(data=request.query_params)

        if not params.is_valid():
            raise ValidationError(params.errors)

    def _log_request(self, request):
        logger.info(
            f'Facility downloads request for User ID: {request.user.id}'
        )

    def _get_filtered_queryset(self, request):
        return FacilityIndex.objects.filter_by_query_params(
            request.query_params
        ).order_by('name', 'address', 'id')

    def _get_download_limit(self, request):
        initial_release_date = make_aware(datetime(2025, 7, 12))

        return FacilityDownloadLimit.get_or_create_user_download_limit(
            request.user, initial_release_date
        )

    def _enforce_limits(self, request, total_records, limit):
        current_page = int(request.query_params.get("page", 1))

        has_exhausted_limit = (
            current_page == 1 and
            limit is not None and
            (
                limit.free_download_records +
                limit.paid_download_records
            ) == 0
        )

        if has_exhausted_limit:
            raise ValidationError(
                'You have reached your annual limit for facility record '
                'downloads, including both free and paid. Additional '
                'downloads will be available at the start of the next '
                'calendar year.'
            )

        has_download_limit = limit is not None
        max_allowed = FacilitiesDownloadSettings\
            .FACILITIES_DOWNLOAD_LIMIT

        is_blocked = has_download_limit and total_records > max_allowed

        if is_blocked:
            records_used = (
                limit.free_download_records +
                limit.paid_download_records
            )
            raise ValidationError(
                f'Downloads are only allowed for results containing '
                f'{records_used} facilities or fewer.'
            )

    def _check_pagination(self, page_queryset):
        if page_queryset is None:
            raise ValidationError("Invalid pageSize parameter")
        return page_queryset

    def _register_download_if_needed(self, limit, record_count):
        if limit:
            limit.register_download(record_count)
