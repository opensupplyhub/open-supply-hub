from rest_framework.decorators import (
    api_view,
    throttle_classes,
)
from rest_framework.response import Response
from django.db.models import F, Func
import re

from ..models.contributor.contributor import Contributor
from ..models.facility.facility_index import FacilityIndex


def is_valid_parent_company_name(name):
    """
    Filter out invalid/dummy parent company names.
    Excludes names that are:
    - Empty or only whitespace
    - Only symbols/punctuation (like '.', '/', '-', etc.)
    - Too short (less than 2 characters after stripping)
    """
    if not name or not isinstance(name, str):
        return False

    stripped = name.strip()

    if len(stripped) < 2:
        return False

    if not re.search(r'[a-zA-Z0-9]', stripped):
        return False

    return True


@api_view(['GET'])
@throttle_classes([])
def parent_companies(_):
    """
    Returns list parent companies submitted by contributors, as a list of
    tuples of Key and contributor name (suitable for populating a choice list),
    sorted alphabetically.


    ## Sample Response

        [
            [1, "Brand A"],
            ["Non-Contributor", "Non-Contributor"],
            [2, "Contributor B"]
        ]

    """
    ids = (
        FacilityIndex
        .objects
        .annotate(
            parent_companies=Func(F('parent_company_id'), function='unnest')
        )
        .values_list('parent_companies', flat=True)
        .distinct()
    )
    contributors = (
        Contributor
        .objects
        .order_by_active_and_verified()
        .order_by('name', '-is_verified', '-has_active_sources')
        .filter(id__in=ids)
        .values('name')
        .values_list('id', 'name')
    )

    contrib_lookup = {name: id for (id, name) in contributors}

    names = (
        FacilityIndex
        .objects
        .annotate(
            parent_companies=Func(F('parent_company_name'), function='unnest')
        )
        .values_list('parent_companies', flat=True)
        .order_by('parent_companies')
        .distinct()
    )

    valid_names = [name for name in names if is_valid_parent_company_name(name)]

    return Response([
        (contrib_lookup[name] if name in contrib_lookup else name, name)
        for name in valid_names
    ])
