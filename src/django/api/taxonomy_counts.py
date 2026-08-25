from django.db.models import Count, F, Func

from api.isic import ISIC4_LEVEL_FIELDS
from api.models.facility.facility_index import FacilityIndex


def searchable_facility_index_queryset():
    """Facilities included in GET /api/facilities/ search results."""
    return FacilityIndex.objects.all()


def _aggregate_array_field_counts(queryset, field_name):
    rows = (
        queryset
        .annotate(value=Func(F(field_name), function='unnest'))
        .values('value')
        .annotate(count=Count('id', distinct=True))
    )
    return [
        row for row in rows
        if row['value'] not in (None, '')
    ]


def compute_isic4_counts():
    queryset = searchable_facility_index_queryset()
    counts = {}

    for level, field_name in ISIC4_LEVEL_FIELDS.items():
        for row in _aggregate_array_field_counts(queryset, field_name):
            counts[f'{level}:{row["value"]}'] = row['count']

    return counts
