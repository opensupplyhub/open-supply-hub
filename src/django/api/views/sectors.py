from api.constants import FacilityClaimStatuses
from api.models.facility.facility_index import FacilityIndex
from api.models.sector_group import SectorGroup
from rest_framework.decorators import (
    api_view,
    throttle_classes,
)
from rest_framework.response import Response
from django.db.models import F, Func

from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Parameter, IN_QUERY, TYPE_INTEGER, TYPE_BOOLEAN

from ..models.facility.facility_claim import FacilityClaim
from ..models.facility.facility_list_item import FacilityListItem


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        Parameter(
            'embed',
            IN_QUERY,
            description="Set to true to enable embed mode.",
            type=TYPE_BOOLEAN,
        ),
        Parameter(
            'contributor',
            IN_QUERY,
            description="If `embed` is provided, this parameter must be "
            "included to filter sectors submitted by a specific contributor.",
            type=TYPE_INTEGER,
        ),
    ],
)
@api_view(['GET'])
@throttle_classes([])
def sectors(request):
    """
    Returns a list of suggested sectors submitted by contributors,
    sorted alphabetically.

    ## Query Parameters

    - `embed` (optional): If provided, the response will be a flat list
    of sectors.
    - `contributor` (optional): If `embed` is provided, this parameter must be
      included to filter sectors submitted by a specific contributor.

    ## Sample Response

    If `embed` is provided the response will be a flat list of sectors.:

        [
            "Agriculture",
            "Apparel",
            "Information",
        ]

    If `embed` is not provided the response will be grouped by sector groups:

        [
            {
                "group_name": "Agriculture, Food & Beverage",
                "sectors": [
                    "Agriculture",
                    "Animal Production",
                    "Aquaculture",
                    "Beverages",
                    "Biotechnology",
                ]
            },
            {
                "group_name": "Apparel, Footwear, Textiles",
                "sectors": [
                    "Apparel",
                    "Apparel Accessories",
                    "Footwear",
                    "Home Accessories",
                    "Home Textiles",
                ]
            }
        ]
    """

    submitted_sectors = set()

    embed = request.query_params.get('embed', None)
    if embed is not None:
        contributor = request.query_params.get('contributor', None)
        if contributor is None:
            return Response(submitted_sectors)

        item_sectors = set(
            FacilityListItem
            .objects
            .filter(
                status__in=[
                    FacilityListItem.MATCHED,
                    FacilityListItem.CONFIRMED_MATCH],
                source__contributor_id=contributor,
                source__is_active=True,
                source__is_public=True
            ).annotate(
                values=Func('sector', function='unnest')
            ).values_list('values', flat=True)
            .distinct()
        )

        claim_sectors = set(
            FacilityClaim
            .objects
            .filter(contributor_id=contributor,
                    status=FacilityClaimStatuses.APPROVED)
            .annotate(values=Func('sector', function='unnest'))
            .values_list('values', flat=True)
            .distinct()
        )

        submitted_sectors = item_sectors.union(claim_sectors)
        return Response(sorted(list(submitted_sectors)))

    else:
        submitted_sectors = set(
            FacilityIndex.objects.annotate(
                all_sectors=Func(F('sector'), function='unnest')
            )
            .values_list('all_sectors', flat=True)
            .distinct()
        )

        sector_groups = SectorGroup.objects.all()
        response_data = []

        for group in sector_groups:
            group_sectors = group.sectors.filter(name__in=submitted_sectors)

            if group_sectors.exists():
                response_data.append(
                    {
                        "group_name": group.name,
                        "sectors": list(
                            group_sectors.values_list('name', flat=True)
                        ),
                    }
                )

        response_data_sorted = sorted(
            response_data, key=lambda x: x['group_name']
        )

        return Response(response_data_sorted)
