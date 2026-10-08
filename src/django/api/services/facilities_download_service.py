import logging
import uuid
import stripe

from django.conf import settings
from django.core.cache import caches
from django.db import transaction
from rest_framework.exceptions import NotAuthenticated, ValidationError
from waffle import switch_is_active
from datetime import datetime
from django.utils.timezone import make_aware
from urllib.parse import urlencode

from api.models.contributor.contributor import Contributor
from api.models.facility.facility_index import FacilityIndex
from api.models.facility_download_limit import FacilityDownloadLimit
from api.serializers.facility.facility_query_params_serializer import (
    FacilityQueryParamsSerializer)
from api.exceptions import ServiceUnavailableException
from api.constants import (
    APIErrorMessages,
    FacilitiesDownloadErrorMessages,
    FacilitiesDownloadSettings,
    FacilitiesQueryParams,
    PaginationConfig,
)

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
    def parse_page_params(request):
        """
        Returns (page, page_size). page must be >= 1. page_size is clamped
        to 1..PaginationConfig.MAX_PAGE_SIZE so a single request can't pull
        an arbitrarily large result set.
        """
        params = request.query_params

        try:
            page = int(params.get('page') or 1)
        except (TypeError, ValueError):
            raise ValidationError(FacilitiesDownloadErrorMessages.INVALID_PAGE)
        if page < 1:
            raise ValidationError(FacilitiesDownloadErrorMessages.INVALID_PAGE)

        try:
            page_size = int(
                params.get('pageSize') or PaginationConfig.MAX_PAGE_SIZE
            )
        except (TypeError, ValueError):
            raise ValidationError(
                FacilitiesDownloadErrorMessages.INVALID_PAGE_SIZE
            )
        page_size = max(1, min(page_size, PaginationConfig.MAX_PAGE_SIZE))

        return page, page_size

    @staticmethod
    def resolve_embed_contributor_id(request):
        """
        Validates an embed-mode request and returns the embed contributor id.

        Embed mode skips download limits, so it is only honoured when the
        request targets exactly one contributor that has an embedded map
        enabled. The caller must also restrict the queryset to that
        contributor (see restrict_to_contributor) so embed downloads can
        only return what that contributor's public embedded map shows.
        """
        params = request.query_params
        contributors = params.getlist(FacilitiesQueryParams.CONTRIBUTORS)

        if len(contributors) != 1:
            raise ValidationError(
                FacilitiesDownloadErrorMessages.EMBED_SINGLE_CONTRIBUTOR
            )

        try:
            contributor_id = int(contributors[0])
        except (TypeError, ValueError):
            raise ValidationError(
                FacilitiesDownloadErrorMessages.EMBED_SINGLE_CONTRIBUTOR
            )

        # The embed serializer also reads a singular `contributor` param.
        # It must not point to a different contributor than the filter.
        singular = params.get('contributor')
        if singular is not None and str(singular) != str(contributor_id):
            raise ValidationError(
                FacilitiesDownloadErrorMessages.EMBED_SINGLE_CONTRIBUTOR
            )

        is_embed_enabled = Contributor.objects.filter(
            id=contributor_id,
            embed_level__isnull=False,
        ).exists()
        if not is_embed_enabled:
            raise ValidationError(
                FacilitiesDownloadErrorMessages.EMBED_NOT_ENABLED
            )

        return contributor_id

    @staticmethod
    def restrict_to_contributor(base_qs, contributor_id):
        return base_qs.filter(contributors_id__contains=[contributor_id])

    @staticmethod
    def ensure_authenticated(request):
        if not request.user or request.user.is_anonymous:
            raise NotAuthenticated(
                FacilitiesDownloadErrorMessages.LOGIN_REQUIRED
            )

    # Download sessions
    #
    # Page 1 opens (and, if needed, charges) a download session stored in a
    # cache shared by all Django processes. Every later page must carry the
    # session's download_id and the exact same query, so the limit check
    # and the charge can't be skipped by requesting pages out of order.

    @staticmethod
    def _session_cache():
        return caches[FacilitiesDownloadSettings.SESSION_CACHE_ALIAS]

    @staticmethod
    def _session_key(download_id):
        return f'session:{download_id}'

    @staticmethod
    def create_download_session(request, query_hash, count, charged):
        download_id = uuid.uuid4().hex
        session = {
            'user_id': getattr(request.user, 'id', None),
            'query_hash': query_hash,
            'count': count,
            'charged': charged,
        }

        try:
            # add() returns False when memcached can't store the key; a
            # fresh uuid never collides, so False means the cache is down.
            stored = FacilitiesDownloadService._session_cache().add(
                FacilitiesDownloadService._session_key(download_id),
                session,
                FacilitiesDownloadSettings.SESSION_TTL_SECONDS,
            )
        except Exception:
            logger.exception('Unable to store facility download session')
            stored = False

        if not stored:
            raise ServiceUnavailableException(
                FacilitiesDownloadErrorMessages.SESSION_UNAVAILABLE
            )

        return download_id, session

    @staticmethod
    def delete_download_session(download_id):
        try:
            FacilitiesDownloadService._session_cache().delete(
                FacilitiesDownloadService._session_key(download_id)
            )
        except Exception:
            logger.exception('Unable to delete facility download session')

    @staticmethod
    def get_valid_download_session(request, download_id, query_hash):
        try:
            download_id = uuid.UUID(str(download_id)).hex
        except (TypeError, ValueError):
            raise ValidationError(
                FacilitiesDownloadErrorMessages.SESSION_INVALID
            )

        key = FacilitiesDownloadService._session_key(download_id)
        cache = FacilitiesDownloadService._session_cache()

        try:
            session = cache.get(key)
        except Exception:
            logger.exception('Unable to read facility download session')
            raise ServiceUnavailableException(
                FacilitiesDownloadErrorMessages.SESSION_UNAVAILABLE
            )

        if (
            not session
            or session.get('user_id') != getattr(request.user, 'id', None)
            or session.get('query_hash') != query_hash
        ):
            raise ValidationError(
                FacilitiesDownloadErrorMessages.SESSION_INVALID
            )

        try:
            # Sliding expiry so long paid downloads don't expire mid-way.
            cache.touch(key, FacilitiesDownloadSettings.SESSION_TTL_SECONDS)
        except Exception:
            logger.exception('Unable to refresh facility download session')

        return download_id, session

    @staticmethod
    def charge_download(limit: FacilityDownloadLimit, count: int):
        """
        Re-checks the limit and charges `count` records in one transaction,
        holding a row lock so concurrent downloads can't both pass the
        check against the same balance.

        Returns (locked_limit, prev_free, prev_paid).
        """
        with transaction.atomic():
            locked = FacilityDownloadLimit.objects \
                .select_for_update() \
                .get(pk=limit.pk)
            prev_free = locked.free_download_records
            prev_paid = locked.paid_download_records

            FacilitiesDownloadService.enforce_limits(count, locked)
            FacilitiesDownloadService.register_download_if_needed(
                locked,
                count,
            )

        return locked, prev_free, prev_paid

    @staticmethod
    def get_download_limit(request):
        has_api_token = request.auth is not None

        # This is needed to figure out if the user is an API user or not.
        # The main reason is that API users should be counted against their
        # API limit when using the API, not the data download limit.
        if has_api_token:
            return None

        initial_release_date = make_aware(datetime(2025, 7, 12))

        return FacilityDownloadLimit.get_or_create_user_download_limit(
            request.user, initial_release_date
        )

    @staticmethod
    def enforce_limits(count, limit):
        if not limit:
            return

        allowed = limit.free_download_records + limit.paid_download_records

        if allowed == 0:
            raise ValidationError(
                "You have reached your annual limit "
                "for facility record downloads..."
            )

        if count > allowed:
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
        is_last_page: bool,
        download_id: str = None,
    ):

        def make_link(target_page):
            query_dict = dict(request.query_params.lists())
            query_dict['page'] = [str(target_page)]
            query_dict['pageSize'] = [str(page_size)]
            if download_id:
                query_dict[FacilitiesDownloadSettings.DOWNLOAD_ID_PARAM] = [
                    download_id
                ]

            return request.build_absolute_uri(
                '?' + urlencode(query_dict, doseq=True)
            )

        next_link = None if is_last_page else make_link(page + 1)
        prev_link = make_link(page - 1) if page > 1 else None
        return next_link, prev_link
