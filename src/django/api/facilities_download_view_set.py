import logging

from rest_framework import viewsets, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from waffle import switch_is_active

from api.models.facility.facility_index import FacilityIndex
from api.serializers.facility.facility_download_serializer import \
    FacilityDownloadSerializer
from api.serializers.facility.facility_download_serializer_embed_mode import \
    FacilityDownloadSerializerEmbedMode
from api.serializers.utils import get_embed_contributor_id_from_query_params
from api.services.facilities_download_service import FacilitiesDownloadService
from api.serializers.facility.utils import is_same_contributor_from_url_param
from api.constants import (
    FacilitiesDownloadErrorMessages,
    FacilitiesDownloadSettings,
    PaginationConfig,
)
from api.pagination_keyset_helpers import create_query_hash
from api.services.contributor_masking_policy import ContributorMaskingPolicy

logger = logging.getLogger(__name__)


class FacilitiesDownloadViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    Get facilities in array format, suitable for CSV/XLSX download.
    """
    queryset = FacilityIndex.objects.all()
    pagination_class = None

    def __is_embed_mode(self):
        return self.request.query_params.get('embed') == '1'

    def get_serializer(self, objs):
        if self.__is_embed_mode():
            contributor_id = get_embed_contributor_id_from_query_params(
                self.request.query_params
            )
            return FacilityDownloadSerializerEmbedMode(
                objs,
                many=True,
                contributor_id=contributor_id
            )
        masked_contributors = ContributorMaskingPolicy.for_download()
        return FacilityDownloadSerializer(
            objs,
            many=True,
            masked_contributors=masked_contributors,
        )

    def __get_limit_for_new_download(self, request, is_same_contributor):
        """
        Decides, once per download (on page 1), whether the download is
        charged. Returns the user's limit when it is, or None when the
        download is exempt (private instance, embedded map, own data or
        API-token requests, which are counted against the API limit).
        """
        if (
            switch_is_active('private_instance')
            or self.__is_embed_mode()
            or is_same_contributor
        ):
            return None

        # The web client only lets logged-in users download outside of
        # embedded maps; anonymous requests would otherwise skip limits.
        FacilitiesDownloadService.ensure_authenticated(request)

        return FacilitiesDownloadService.get_download_limit(request)

    @staticmethod
    def __cap_to_count(items, is_last_page, page, page_size, count):
        """
        Never serve more rows than the session was opened (and charged)
        for, even if new facilities match the query after page 1.
        """
        remaining = count - (page - 1) * page_size
        if remaining <= 0:
            return [], True
        if len(items) >= remaining:
            return items[:remaining], True
        return items, is_last_page

    @staticmethod
    def __charge(request, limit, count, download_id):
        try:
            locked_limit, prev_free, prev_paid = \
                FacilitiesDownloadService.charge_download(limit, count)
        except Exception:
            # Nothing was charged, so the session must not be usable.
            FacilitiesDownloadService.delete_download_session(download_id)
            raise

        if not count:
            return

        try:
            FacilitiesDownloadService.send_email_if_needed(
                request,
                locked_limit,
                prev_free,
                prev_paid
            )
        except Exception:
            # The download is already charged; a notification failure
            # (e.g. Stripe being unavailable) must not fail the request.
            logger.exception(
                'Unable to send facility download limit email for '
                f'User ID: {request.user.id}'
            )

    def list(self, request):
        FacilitiesDownloadService.check_if_downloads_are_blocked()
        FacilitiesDownloadService.validate_query_params(request)
        FacilitiesDownloadService.log_request(request)

        page, page_size = FacilitiesDownloadService.parse_page_params(request)

        base_qs = FacilitiesDownloadService.get_filtered_queryset(request)
        if self.__is_embed_mode():
            embed_contributor_id = FacilitiesDownloadService.\
                resolve_embed_contributor_id(request)
            base_qs = FacilitiesDownloadService.restrict_to_contributor(
                base_qs,
                embed_contributor_id
            )

        is_same_contributor = is_same_contributor_from_url_param(request)
        query_hash = create_query_hash(request, page_size)
        download_id = request.query_params.get(
            FacilitiesDownloadSettings.DOWNLOAD_ID_PARAM
        )

        limit = None
        is_new_download = not download_id

        if not is_new_download:
            download_id, session = FacilitiesDownloadService.\
                get_valid_download_session(request, download_id, query_hash)
            count = session['count']
        elif page == 1:
            count = base_qs.count()
            limit = self.__get_limit_for_new_download(
                request,
                is_same_contributor
            )
            # Fail fast before doing the heavy work. The check is repeated
            # under a row lock when the download is charged.
            FacilitiesDownloadService.enforce_limits(count, limit)
        else:
            raise ValidationError(
                FacilitiesDownloadErrorMessages.SESSION_REQUIRED
            )

        items, is_last_page = FacilitiesDownloadService.\
            fetch_page_and_cache(
                base_qs,
                request,
                page,
                page_size,
                block=PaginationConfig.DEFAULT_BLOCK_SIZE
            )
        items, is_last_page = self.__cap_to_count(
            items,
            is_last_page,
            page,
            page_size,
            count
        )

        list_serializer = self.get_serializer(items)
        rows = [facility_data['row'] for facility_data in list_serializer.data]
        headers = list_serializer.child.get_headers()

        if is_new_download:
            download_id, _ = FacilitiesDownloadService.create_download_session(
                request,
                query_hash,
                count,
                charged=limit is not None
            )
            if limit is not None:
                self.__charge(request, limit, count, download_id)

        next_link, prev_link = FacilitiesDownloadService.\
            build_page_links(
                request,
                page,
                page_size,
                is_last_page,
                download_id
            )

        data = {
            'rows': rows,
            'headers': headers,
            'is_same_contributor': is_same_contributor
        }

        payload = {
            'next': next_link,
            'previous': prev_link,
            'page': page,
            'pageSize': page_size,
            'results': data,
        }

        if page == 1:
            payload['count'] = count

        return Response(payload)
