from collections import namedtuple

from api.constants import FacilitiesQueryParams


FacilityProcessingQuery = namedtuple(
    'FacilityProcessingQuery',
    ['facility_types', 'processing_types', 'exact_processing_types'],
)


def _nonblank_values(params, key):
    return [
        value
        for value in params.getlist(key)
        if value is not None and value.strip()
    ]


def parse_facility_processing_query(params):
    facility_types = _nonblank_values(
        params,
        FacilitiesQueryParams.FACILITY_TYPE,
    )
    processing_types = _nonblank_values(
        params,
        FacilitiesQueryParams.PROCESSING_TYPE,
    )
    processing_type_identities = {
        value.lower() for value in processing_types
    }
    exact_processing_types = [
        value
        for value in _nonblank_values(
            params,
            FacilitiesQueryParams.PROCESSING_TYPE_EXACT,
        )
        if value.lower() in processing_type_identities
    ]

    return FacilityProcessingQuery(
        facility_types,
        processing_types,
        exact_processing_types,
    )
