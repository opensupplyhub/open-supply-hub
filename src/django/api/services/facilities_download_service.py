import logging
import stripe

from django.conf import settings

from rest_framework.exceptions import ValidationError
from waffle import switch_is_active
from datetime import datetime
from django.utils.timezone import make_aware

from api.models.facility.facility_index import FacilityIndex
from api.models.facility_download_limit import FacilityDownloadLimit
from api.serializers.facility.facility_query_params_serializer import (
    FacilityQueryParamsSerializer)
from api.exceptions import ServiceUnavailableException
from api.constants import APIErrorMessages

from api.mail import (
    send_ddl_near_annual_limit_email,
    send_ddl_reach_annual_limit_email,
    send_ddl_reach_paid_limit_email
)

stripe.api_key = settings.STRIPE_SECRET_KEY
STRIPE_PRICE_ID = settings.STRIPE_PRICE_ID

logger = logging.getLogger(__name__)


class FacilitiesDownloadService:
    @staticmethod
    def check_if_downloads_are_blocked():
        if switch_is_active('block_location_downloads'):
            raise ServiceUnavailableException(
                    APIErrorMessages.TEMPORARILY_UNAVAILABLE
                )

    @staticmethod
    def validate_query_params(request):
        params = FacilityQueryParamsSerializer(data=request.query_params)

        if not params.is_valid():
            raise ValidationError(params.errors)

    @staticmethod
    def log_request(request):
        logger.info(
            f'Facility downloads request for User ID: {request.user.id}'
        )

    @staticmethod
    def get_filtered_queryset(request):
        return FacilityIndex.objects.filter_by_query_params(
            request.query_params
        ).order_by('name', 'address', 'id')

    @staticmethod
    def get_download_limit(request):
        initial_release_date = make_aware(datetime(2025, 7, 12))

        return FacilityDownloadLimit.get_or_create_user_download_limit(
            request.user, initial_release_date
        )

    @staticmethod
    def enforce_limits(request, total_records, limit):
        current_page = int(request.query_params.get("page", 1))

        if limit is None:
            return

        allowed_records = (
            limit.free_download_records +
            limit.paid_download_records
        )

        has_exhausted_limit = (
            current_page == 1 and
            allowed_records == 0
        )

        if has_exhausted_limit:
            raise ValidationError(
                'You have reached your annual limit for facility record '
                'downloads, including both free and paid. Additional '
                'downloads will be available at the start of the next '
                'calendar year.'
            )

        is_blocked = (
            current_page == 1
            and total_records > allowed_records
        )

        if is_blocked:
            raise ValidationError(
                f'Downloads are supported only for searches '
                f'resulting in {allowed_records} facilities or less.'
            )

    @staticmethod
    def check_pagination(page_queryset):
        if page_queryset is None:
            raise ValidationError("Invalid pageSize parameter")
        return page_queryset

    @staticmethod
    def register_download_if_needed(limit, record_count):
        if limit:
            limit.register_download(record_count)

    @staticmethod
    def send_email_if_needed(
        request,
        limit: FacilityDownloadLimit,
        prev_free = 0,
        prev_paid = 0
    ):
        if limit:
            limit.refresh_from_db()

            site_url = request.build_absolute_uri('/')
            redirect_path = site_url + 'facilities'
            url = FacilitiesDownloadService.get_checkout_url(
                limit.user.id,
                redirect_path
            )

            if (0 < limit.free_download_records <= 1000
                and limit.paid_download_records == 0
            ):
                send_ddl_near_annual_limit_email(
                    limit.free_download_records,
                    url,
                    limit.user.email
                )
            elif (limit.free_download_records == 0
                and prev_free > 0
                and prev_paid == 0
            ):
                send_ddl_reach_annual_limit_email(
                    url,
                    limit.user.email
                )
            elif (limit.paid_download_records == 0
                and prev_paid > 0
            ):
                send_ddl_reach_paid_limit_email(
                    url,
                    limit.user.email
                )

    @staticmethod
    def get_checkout_url(user_id, redirect_path):
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': STRIPE_PRICE_ID,
                    'quantity': 1,
                    'adjustable_quantity': {
                        'enabled': True,
                        'minimum': 1,
                    },
                },
            ],
            payment_method_types=['card'],
            mode='payment',
            metadata={
                'user_id': user_id,
            },
            allow_promotion_codes=True,
            success_url=redirect_path,
            cancel_url=redirect_path,
        )

        return checkout_session.url
