from api.models.facility.facility_index import FacilityIndex
from api.models.sector_group import SectorGroup
from rest_framework.decorators import (
    api_view,
    throttle_classes,
)
from rest_framework.response import Response
from django.db.models import F, Func

from ..models.facility.facility_claim import FacilityClaim
from ..models.facility.facility_list_item import FacilityListItem


@api_view(['GET'])
@throttle_classes([])
def sectors_new(request):
    """
    Returns a list of suggested sectors submitted by contributors,
    sorted alphabetically.


    ## Sample Response

        [
            "Agriculture",
            "Apparel",
            "Information",
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
                    status=FacilityClaim.APPROVED)
            .annotate(values=Func('sector', function='unnest'))
            .values_list('values', flat=True)
            .distinct()
        )

        submitted_sectors = item_sectors.union(claim_sectors)

    else:
        submitted_sectors = set(
            FacilityIndex
            .objects
            .annotate(all_sectors=Func(F('sector'), function='unnest'))
            .values_list('all_sectors', flat=True)
            .distinct()
        )

        print('submitted_sectors >>>', submitted_sectors)

    # Fetch all sector groups
    sector_groups = SectorGroup.objects.all()

    response_data = []

    for group in sector_groups:
        # Filter sectors that are part of the submitted_sectors
        group_sectors = group.sectors.filter(name__in=submitted_sectors)

        if group_sectors.exists():
            response_data.append({
                "id": group.id,
                "name": group.name,
                "sectors": list(group_sectors.values_list('name', flat=True))
            })

    print('response_data >>>', response_data)

    return Response(sorted(list(submitted_sectors)))
