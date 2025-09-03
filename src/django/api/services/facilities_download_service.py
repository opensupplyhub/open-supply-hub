import logging
import stripe

from django.conf import settings
from rest_framework.exceptions import ValidationError
from waffle import switch_is_active
from datetime import datetime
from django.utils.timezone import make_aware
from urllib.parse import urlencode

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

from api.services.keyset_pagination_service import (
    KeysetPaginationService
)

from api.pagination_keyset_helpers import (
    create_query_hash,
    set_page_bookmark,
    get_paginated_items_after_id
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
        ).order_by('id')

    @staticmethod
    def get_download_limit(request):
        initial_release_date = make_aware(datetime(2025, 7, 12))

        return FacilityDownloadLimit.get_or_create_user_download_limit(
            request.user, initial_release_date
        )

    @staticmethod
    def enforce_limits(qs, limit, is_first_page):
        if not limit or not is_first_page:
            return

        allowed = limit.free_download_records + limit.paid_download_records

        if allowed == 0:
            raise ValidationError(
                "You have reached your annual limit "
                "for facility record downloads..."
            )

        probe = list(
            qs.order_by("id").values_list("id", flat=True)[:allowed + 1]
        )
        if len(probe) > allowed:
            raise ValidationError(
                "Downloads are supported only for searches resulting in "
                f"{allowed} facilities or less."
            )

    @staticmethod
    def check_pagination(page_queryset):
        if page_queryset is None:
            raise ValidationError("Invalid pageSize parameter")
        return page_queryset

    @staticmethod
    def register_download_if_needed(
        limit: FacilityDownloadLimit,
        records_returned: int,
        is_same_contributor: bool = False
    ):
        if is_same_contributor or not limit:
            return
        try:
            count = int(records_returned)
        except (TypeError, ValueError):
            count = 0

        if count <= 0:
            return

        limit.register_download(count)

    @staticmethod
    def send_email_if_needed(
        request,
        limit: FacilityDownloadLimit,
        prev_free,
        prev_paid
    ):
        if not limit:
            return

        limit.refresh_from_db()

        nearing_annual_limit = (
            0 < limit.free_download_records <= 1000 and
            limit.paid_download_records == 0
        )
        reached_annual_limit = (
            limit.free_download_records == 0 and
            prev_free > 0 and
            prev_paid == 0
        )
        reached_paid_limit = (
            limit.paid_download_records == 0 and
            prev_paid > 0
        )

        if any([
            nearing_annual_limit,
            reached_annual_limit,
            reached_paid_limit
        ]):
            site_url = request.build_absolute_uri('/')
            redirect_path = site_url + 'facilities'
            url = FacilitiesDownloadService.get_checkout_url(
                limit.user.id,
                redirect_path
            )

        if nearing_annual_limit:
            send_ddl_near_annual_limit_email(
                limit.free_download_records,
                url,
                limit.user.email
            )
        elif reached_annual_limit:
            send_ddl_reach_annual_limit_email(
                url,
                limit.user.email
            )
        elif reached_paid_limit:
            send_ddl_reach_paid_limit_email(
                url,
                limit.user.email
            )

    @staticmethod
    def get_checkout_url(user_id, redirect_path):
        try:
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

        except stripe.error.StripeError as e:
            logger.error(
                f"Stripe checkout session creation failed: {str(e)}"
            )
            raise ServiceUnavailableException(
                "Payment service temporarily unavailable"
            )

    @staticmethod
    def fetch_page_and_cache(
        base_qs,
        request,
        page: int,
        page_size: int,
        block: int,
    ):
        keyset_pag_service = KeysetPaginationService(base_qs, block)
        prev_last_id = keyset_pag_service.get_page_cursor(
            request,
            page,
            page_size
        )

        if page > 1 and prev_last_id is None:
            return [], True

        items, last_id, is_last_page = get_paginated_items_after_id(
            base_qs,
            page_size,
            prev_last_id
        )

        if page >= 1:
            set_page_bookmark(
                create_query_hash(request, page_size),
                page,
                last_id
            )

        return items, is_last_page

    @staticmethod
    def build_page_links(
        request,
        page: int,
        page_size: int,
        is_last_page: bool
    ):
        base_qs_params = request.query_params.copy()

        def make_link(target_page):
            query = base_qs_params.copy()
            query['page'] = target_page
            query['pageSize'] = page_size
            return request.build_absolute_uri(
                '?' + urlencode(query, doseq=True)
            )

        next_link = None if is_last_page else make_link(page + 1)
        prev_link = make_link(page - 1) if page > 1 else None
        return next_link, prev_link
