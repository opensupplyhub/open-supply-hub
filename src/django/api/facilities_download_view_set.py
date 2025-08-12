# api/views/facilities_download.py
from urllib.parse import urlencode
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from waffle import switch_is_active

from api.models.facility.facility_index import FacilityIndex
from api.serializers.facility.facility_download_serializer import FacilityDownloadSerializer
from api.serializers.facility.facility_download_serializer_embed_mode import FacilityDownloadSerializerEmbedMode
from api.serializers.utils import get_embed_contributor_id_from_query_params
from api.services.facilities_download_service import FacilitiesDownloadService
from api.pagination_keyset_helpers import (
    qhash, get_bm, set_bm, keyset_page_id, advance_blocks_id
)

class FacilitiesDownloadViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Keyset pagination by id, API stays page/pageSize. No OFFSET, no COUNT(*).
    """
    queryset = FacilityIndex.objects.all()
    pagination_class = None  # important: manual pagination

    def __is_embed_mode(self):
        return self.request.query_params.get('embed') == '1'

    def get_serializer(self, objs):
        if self.__is_embed_mode():
            contributor_id = get_embed_contributor_id_from_query_params(
                self.request.query_params
            )
            return FacilityDownloadSerializerEmbedMode(objs, many=True, contributor_id=contributor_id)
        return FacilityDownloadSerializer(objs, many=True)

    def list(self, request):
        FacilitiesDownloadService.check_if_downloads_are_blocked()
        FacilitiesDownloadService.validate_query_params(request)
        FacilitiesDownloadService.log_request(request)

        base_qs = FacilitiesDownloadService.get_filtered_queryset(request).order_by("id")

        limit = None
        if not switch_is_active('private_instance') and not self.__is_embed_mode():
            limit = FacilitiesDownloadService.get_download_limit(request)

        page = int(request.query_params.get('page', 1) or 1)
        page_size = int(request.query_params.get('pageSize', 250) or 250)
        is_first_page = (page == 1)

        # Enforce limits w/o COUNT(*)
        FacilitiesDownloadService.enforce_limits(
            qs=base_qs, limit=limit, is_first_page=is_first_page
        )

        # Locate page start via cached bookmarks; no OFFSET
        if page == 1:
            prev_last_id = None
        else:
            qh = qhash(request, page_size)
            prev_last_id = get_bm(qh, page - 1)
            if prev_last_id is None:
                nearest = page - 1
                while nearest > 1 and get_bm(qh, nearest) is None:
                    nearest -= 1
                start_after = get_bm(qh, nearest) if nearest > 1 else None
                steps = (page - 1) - (nearest if nearest > 1 else 0)
                if start_after is None and nearest == 1:
                    first_items, first_last = keyset_page_id(base_qs, page_size, None)
                    set_bm(qh, 1, first_last)
                    start_after, steps = first_last, steps - 1
                if steps > 0 and start_after is not None:
                    start_after = advance_blocks_id(base_qs, page_size, start_after, steps, block=10)
                prev_last_id = start_after

        items, last_id = keyset_page_id(base_qs, page_size, prev_last_id)

        # Cache bookmark for this page
        if page >= 1:
            set_bm(qhash(request, page_size), page, last_id)

        # Serialize
        ser = self.get_serializer(items)
        rows = [f['row'] for f in ser.data]
        headers = ser.child.get_headers()
        data = {'rows': rows, 'headers': headers}

        # Build minimal paginated response (page links only)
        base_qs_params = request.query_params.copy()
        base_qs_params.pop('cursor', None)  # ensure no cursor ever leaks

        def make_link(p):
            q = base_qs_params.copy()
            q['page'] = p
            q['pageSize'] = page_size
            return request.build_absolute_uri('?' + urlencode(q, doseq=True))

        is_last_page = len(items) < page_size
        next_link = make_link(page + 1) if not is_last_page else None
        prev_link = make_link(page - 1) if page > 1 else None

        payload = {
            'next': next_link,
            'previous': prev_link,
            'page': page,
            'pageSize': page_size,
            'results': data,
        }

        if is_first_page:
            payload['count'] = base_qs.count()

        # Register download & emails ONLY on last page (derive total without COUNT)
        if is_last_page and limit:
            total_records = (page - 1) * page_size + len(items)
            prev_free = getattr(limit, 'free_download_records', 0)
            prev_paid = getattr(limit, 'paid_download_records', 0)
            FacilitiesDownloadService.register_download_if_needed(limit, total_records)
            FacilitiesDownloadService.send_email_if_needed(request, limit, prev_free, prev_paid)

        return Response(payload)
