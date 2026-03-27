from django.db.models import Func

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response

from api.constants import FacilityClaimStatuses
from api.models.sector import Sector
from api.models.sector_group import SectorGroup
from api.views.sectors_swagger_schema import (
    sectors_manual_parameters,
    sectors_operation_description,
)
from ..models.facility.facility_claim import FacilityClaim
from ..models.facility.facility_list_item import FacilityListItem


@swagger_auto_schema(
    method='GET',
    manual_parameters=sectors_manual_parameters,
    operation_description=sectors_operation_description,
)
@api_view(['GET'])
@throttle_classes([])
def sectors(request):

    embed = request.query_params.get('embed')
    grouped = request.query_params.get('grouped')

    if embed:
        contributor = request.query_params.get('contributor')
        if not contributor:
            return Response([])

        submitted_sectors = get_sectors_for_contributor(contributor)

        return Response(sorted(list(submitted_sectors)))

    else:
        submitted_sectors = get_all_submitted_sectors()

        if grouped:
            grouped_sectors = group_sectors_by_group_name(submitted_sectors)

            return Response(grouped_sectors)

        else:
            return Response(sorted(list(submitted_sectors)))


def get_sectors_for_contributor(contributor):
    item_sectors = get_item_sectors(contributor)
    claim_sectors = get_claim_sectors(contributor)
    return item_sectors.union(claim_sectors)


def get_item_sectors(contributor):
    return set(
        FacilityListItem.objects.filter(
            status__in=[
                FacilityListItem.MATCHED,
                FacilityListItem.CONFIRMED_MATCH,
            ],
            source__contributor_id=contributor,
            source__is_active=True,
            source__is_public=True,
        )
        .annotate(values=Func('sector', function='unnest'))
        .values_list('values', flat=True)
        .distinct()
    )


def get_claim_sectors(contributor):
    return set(
        FacilityClaim.objects.filter(
            contributor_id=contributor,
            status=FacilityClaimStatuses.APPROVED,
        )
        .annotate(values=Func('sector', function='unnest'))
        .values_list('values', flat=True)
        .distinct()
    )


def get_all_submitted_sectors():
    """
    Get all valid sectors from the Sector model.
    This ensures only admin-managed, validated sectors are returned.
    """
    return set(
        Sector.objects.values_list('name', flat=True)
    )


def group_sectors_by_group_name(sectors):
    sector_groups = SectorGroup.objects.prefetch_related('sectors').all()
    grouped_data = []

    for group in sector_groups:
        group_sectors = group.sectors.filter(name__in=sectors)
        if group_sectors.exists():
            grouped_data.append(
                {
                    "group_name": group.name,
                    "sectors": sorted(
                        group_sectors.values_list('name', flat=True)
                    ),
                }
            )

    return sorted(grouped_data, key=lambda x: x['group_name'])
