from rest_framework import viewsets, mixins
from rest_framework.response import Response
from waffle import switch_is_active

from api.models.facility.facility_index import FacilityIndex
from api.serializers.facility.facility_download_serializer import \
    FacilityDownloadSerializer
from api.serializers.facility.facility_download_serializer_embed_mode import \
    FacilityDownloadSerializerEmbedMode
from api.serializers.utils import get_embed_contributor_id_from_query_params
from api.services.facilities_download_service import FacilitiesDownloadService


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
        return FacilityDownloadSerializer(objs, many=True)

    def list(self, request):
        FacilitiesDownloadService.check_if_downloads_are_blocked()
        FacilitiesDownloadService.validate_query_params(request)
        FacilitiesDownloadService.log_request(request)

        base_qs = FacilitiesDownloadService.get_filtered_queryset(request)

        limit = None
        if (
            not switch_is_active('private_instance')
            and not self.__is_embed_mode()
        ):
            limit = FacilitiesDownloadService.get_download_limit(request)

        page = int(request.query_params.get('page', 1) or 1)
        page_size = int(request.query_params.get('pageSize', 250) or 250)
        is_first_page = (page == 1)

        FacilitiesDownloadService.enforce_limits(
            qs=base_qs, limit=limit, is_first_page=is_first_page
        )

        items, is_last_page = FacilitiesDownloadService.\
            fetch_page_and_cache(
                base_qs,
                request,
                page,
                page_size,
                block=50
            )
        next_link, prev_link = FacilitiesDownloadService.\
            build_page_links(
                request,
                page,
                page_size,
                is_last_page
            )

        list_serializer = self.get_serializer(items)
        rows = [f['row'] for f in list_serializer.data]
        headers = list_serializer.child.get_headers()
        data = {'rows': rows, 'headers': headers}

        payload = {
            'next': next_link,
            'previous': prev_link,
            'page': page,
            'pageSize': page_size,
            'results': data,
        }

        if is_first_page:
            payload['count'] = base_qs.count()

        if is_last_page and limit:
            total_records = (page - 1) * page_size + len(items)
            prev_free = getattr(limit, 'free_download_records', 0)
            prev_paid = getattr(limit, 'paid_download_records', 0)
            FacilitiesDownloadService.register_download_if_needed(
                limit,
                total_records
            )
            FacilitiesDownloadService.send_email_if_needed(
                request,
                limit,
                prev_free,
                prev_paid
            )

        return Response(payload)
