from api.constants import FacilityListQueryParams
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.source import Source
from api.pagination import PageAndSizePagination
from api.permissions import IsSuperuser
from api.serializers.facility.facility_list_query_params_serializer import \
    FacilityListQueryParamsSerializer
from api.serializers.facility.facility_list_serializer import \
    FacilityListSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView


class AdminFacilityListView(ListAPIView):
    """
    Upload and update facility lists for an authenticated Contributor.
    """
    queryset = FacilityList.objects.all()
    serializer_class = FacilityListSerializer
    permission_classes = [IsSuperuser]
    pagination_class = PageAndSizePagination
    swagger_schema = None
    throttle_classes = []

    def get_queryset(self):
        """
        Returns Facility Lists for an authenticated superusers.
        """
        params = FacilityListQueryParamsSerializer(
            data=self.request.query_params)
        if not params.is_valid():
            raise ValidationError(params.errors)

        ordering = params.validated_data.get(
            FacilityListQueryParams.ORDERING,
            'created_at',
        )

        facility_lists = FacilityList.objects.select_related(
            'replaced_by',
            'source',
            'source__contributor',
            'source__contributor__admin',
        ).order_by(ordering)

        contributor = params.data.get(FacilityListQueryParams.CONTRIBUTOR)
        if contributor:
            facility_lists = facility_lists.filter(
                source__contributor=contributor)

        responsibility = params.data.get(
            FacilityListQueryParams.MATCH_RESPONSIBILITY)
        if responsibility:
            facility_lists = facility_lists.filter(
                match_responsibility=responsibility)

        status = params.data.get(
            FacilityListQueryParams.STATUS)
        if status == FacilityList.MATCHED:
            sources = Source.objects.filter(
                facilitylistitem__status__in=[
                    FacilityListItem.MATCHED,
                    FacilityListItem.POTENTIAL_MATCH,
                    FacilityListItem.ERROR_MATCHING
                ])
            facility_lists = facility_lists.filter(source__in=sources)
        elif status == FacilityList.REPLACED:
            facility_lists = facility_lists.filter(replaced_by__isnull=False)
        elif status in (FacilityList.PENDING, FacilityList.APPROVED):
            facility_lists = facility_lists.filter(
                status=status,
                replaced_by__isnull=True,
                source__is_active=True,
            )
        elif status is not None:
            facility_lists = facility_lists.filter(status=status)

        id_gt = params.validated_data.get(FacilityListQueryParams.ID_GT)
        if id_gt is not None:
            facility_lists = facility_lists.filter(id__gt=id_gt)

        return facility_lists
