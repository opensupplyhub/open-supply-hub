from drf_yasg.openapi import Parameter, IN_QUERY, TYPE_INTEGER
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from ...models.facility.facility_list import FacilityList
from ...serializers import ContributorListQueryParamsSerializer


class ContributorFacilityListSortedViewSet(ReadOnlyModelViewSet):
    """
    View Facility Lists that are both active and approved filtered by
    Contributor and sorted by creation date.
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
    )], responses={200: ''})
    @method_decorator(
        cache_page(
            settings.MEMCACHED_VIEW_CACHE_TIMEOUT_SECONDS,
            cache="view_cache",
        )
    )
    def list(self, request):
        params = ContributorListQueryParamsSerializer(
            data=request.query_params)

        if not params.is_valid():
            raise ValidationError(params.errors)

        contributors = params.data.get('contributors', [])
        response_data = []

        for list in self.queryset.filter(
                source__contributor__id__in=contributors
                ).order_by('-created_at'):
            dict = {
                "id": list.id,
                "name": list.name,
            }
            response_data.append(dict)

        return Response(response_data)
