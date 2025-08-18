from waffle import switch_is_active
from rest_framework import viewsets, mixins
from api.pagination import PageAndSizePagination
from api.models.facility.facility_index import FacilityIndex
from api.serializers.facility.facility_download_serializer \
    import FacilityDownloadSerializer
from api.serializers.facility.facility_download_serializer_embed_mode \
    import FacilityDownloadSerializerEmbedMode
from api.serializers.utils import get_embed_contributor_id_from_query_params
from api.services.facilities_download_service import FacilitiesDownloadService


class FacilitiesDownloadViewSet(mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    """
    Get facilities in array format, suitable for CSV/XLSX download.
    """
    queryset = FacilityIndex.objects.all()
    pagination_class = PageAndSizePagination

    def get_serializer(self, page_queryset):
        if self.__is_embed_mode():
            contributor_id = get_embed_contributor_id_from_query_params(
                self.request.query_params
            )
            return FacilityDownloadSerializerEmbedMode(
                page_queryset, many=True, contributor_id=contributor_id
            )

        return FacilityDownloadSerializer(page_queryset, many=True)

    def __is_embed_mode(self):
        return self.request.query_params.get('embed') == '1'

    def list(self, request):
        """
        Returns a list of facilities in array format for a given query.
        (Maximum of 250 facilities per page.)
        """
        FacilitiesDownloadService.check_if_downloads_are_blocked()
        FacilitiesDownloadService.validate_query_params(request)
        FacilitiesDownloadService.log_request(request)

        queryset = FacilitiesDownloadService.get_filtered_queryset(request)
        total_records = queryset.count()
        facility_download_limit = None

        if (
            not switch_is_active('private_instance')
            and not self.__is_embed_mode()
        ):
            facility_download_limit = FacilitiesDownloadService \
                .get_download_limit(request)
        FacilitiesDownloadService.enforce_limits(
            request,
            total_records,
            facility_download_limit
        )

        page_queryset = FacilitiesDownloadService \
            .check_pagination(self.paginate_queryset(queryset))
        list_serializer = self.get_serializer(page_queryset)

        rows = [facility_data['row'] for facility_data in list_serializer.data]
        headers = list_serializer.child.get_headers()

        is_same_contributor = self.__check_all_contributor_facilities(
            queryset, request
        )

        data = {
            'rows': rows,
            'headers': headers,
            'is_same_contributor': is_same_contributor
        }

        response = self.get_paginated_response(data)

        paginator = self.paginator
        if paginator.page.number == paginator.page.paginator.num_pages:
            prev_free_amount = getattr(
                facility_download_limit,
                'free_download_records',
                0
            )
            prev_paid_amount = getattr(
                facility_download_limit,
                'paid_download_records',
                0
            )

            FacilitiesDownloadService.register_download_if_needed(
                facility_download_limit,
                total_records,
                is_same_contributor
            )
            FacilitiesDownloadService.send_email_if_needed(
                request,
                facility_download_limit,
                prev_free_amount,
                prev_paid_amount
            )

        return response

    def __check_all_contributor_facilities(self, queryset, request):
        """
        Ensures the current user's contributor is involved in all
        facilities.
        """
        if not queryset or queryset.count() == 0:
            return False

        current_user_contributor_id = None
        if hasattr(request.user, 'contributor') and request.user.contributor:
            current_user_contributor_id = request.user.contributor.id
        else:
            return False

        for facility in queryset:
            facility_contributor_ids = [
                contributor.get('id') for contributor in facility.contributors
                if contributor.get('id') is not None
            ]
            if (
                current_user_contributor_id
                and current_user_contributor_id not in facility_contributor_ids
            ):
                return False

        return True
