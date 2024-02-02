from drf_yasg.openapi import Parameter, IN_QUERY, TYPE_INTEGER
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from ...models.facility.facility_list import FacilityList
from ...serializers import ContributorListQueryParamsSerializer


class ContributorFacilityListViewSet(ReadOnlyModelViewSet):
    """
    View Facility Lists that are both active and approved filtered by
    Contributor.
    """
    queryset = FacilityList.objects.filter(
        source__is_active=True,
        status=FacilityList.APPROVED
    )

    @swagger_auto_schema(manual_parameters=[Parameter(
        'contributors',
        IN_QUERY,
        description='The contributor ID.',
        type=TYPE_INTEGER,
        required=False
    )], responses={200: ''}, deprecated=True)
    def list(self, request):
        params = ContributorListQueryParamsSerializer(
            data=request.query_params)

        if not params.is_valid():
            raise ValidationError(params.errors)

        contributors = params.data.get('contributors', [])

        response_data = [
            (list.id, list.name)
            for list
            in self.queryset.filter(
                source__contributor__id__in=contributors).order_by('name')
        ]

        return Response(response_data)
