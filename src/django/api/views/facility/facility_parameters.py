from drf_yasg.openapi import (
  Parameter,
  IN_QUERY,
  TYPE_BOOLEAN,
  TYPE_STRING,
  TYPE_INTEGER
)

from api.constants import FacilitiesListSettings

facility_parameters = [
    Parameter(
        'created_at_of_data_points',
        IN_QUERY,
        type=TYPE_BOOLEAN,
        required=False,
        description=(
            'If created_at_of_data_points is true, the created_at '
            'property will be included in the objects of the '
            'sector property and the objects of the child '
            'properties within the extended_fields property.'),
    ),
    Parameter(
        'pending_claim_info',
        IN_QUERY,
        type=TYPE_BOOLEAN,
        required=False,
        description=(
            'If pending_claim_info is true, the value of the '
            'claim_info property will be {"status": "PENDING"} '
            'when a facility has a pending claim.'),
    )
]

facilities_list_parameters = [
    Parameter(
        'page',
        IN_QUERY,
        type=TYPE_INTEGER,
        required=False,
        description=(
            'A page number within the paginated result set. As of now, the '
            'last page that can be accessed is '
            f'{FacilitiesListSettings.DEFAULT_PAGE_LIMIT}. To access more '
            'data, please contact support@opensupplyhub.org.'),
    ),
    Parameter(
        'q',
        IN_QUERY,
        type=TYPE_STRING,
        required=False,
        description='Facility Name or OS ID',
    ),
    Parameter(
        'name',
        IN_QUERY,
        type=TYPE_STRING,
        required=False,
        description='Facility Name (DEPRECATED; use `q` instead)'
    ),
    Parameter(
        'contributors',
        IN_QUERY,
        type=TYPE_INTEGER,
        required=False,
        description='Contributor ID',
    ),
    Parameter(
        'lists',
        IN_QUERY,
        type=TYPE_INTEGER,
        required=False,
        description='List ID',
    ),
    Parameter(
        'contributor_types',
        IN_QUERY,
        type=TYPE_STRING,
        required=False,
        description='Contributor Type',
    ),
    Parameter(
        'countries',
        IN_QUERY,
        type=TYPE_STRING,
        required=False,
        description='Country Code',
    ),
    Parameter(
        'combine_contributors',
        IN_QUERY,
        type=TYPE_STRING,
        required=False,
        description=(
            'Set this to "AND" if the results should contain '
            'facilities associated with ALL the specified '
            'contributors.')
    ),
    Parameter(
        'boundary',
        IN_QUERY,
        type=TYPE_STRING,
        required=False,
        description=(
            'Pass a GeoJSON geometry to filter by '
            'facilities within the boundaries of that geometry.')
    ),
    Parameter(
        'parent_company',
        IN_QUERY,
        type=TYPE_STRING,
        required=False,
        description=(
            'Pass a Contributor ID or Contributor name to filter '
            'by facilities with that Parent Company.')
    ),
    Parameter(
        'facility_type',
        IN_QUERY,
        type=TYPE_STRING,
        required=False,
        description='Facility type',
    ),
    Parameter(
        'processing_type',
        IN_QUERY,
        type=TYPE_STRING,
        required=False,
        description='Processing type',
    ),
    Parameter(
        'product_type',
        IN_QUERY,
        type=TYPE_STRING,
        required=False,
        description='Product type',
    ),
    Parameter(
        'number_of_workers',
        IN_QUERY,
        type=TYPE_STRING,
        required=False,
        description=(
            'Submit one of several standardized ranges to filter '
            'by facilities with a number_of_workers matching '
            'those values. Options are: "Less than 1000", '
            '"1001-5000", "5001-10000", or "More than 10000".'
        ),
    ),
    Parameter(
        'native_language_name',
        IN_QUERY,
        type=TYPE_STRING,
        required=False,
        description='The native language name of the facility',
    ),
    Parameter(
        'detail',
        IN_QUERY,
        type=TYPE_BOOLEAN,
        required=False,
        description=(
            'Set this to true to return additional detail about '
            'contributors and extended fields with each result. '
            'setting this to true will make the response '
            'significantly slower to return.'),
    ),
    Parameter(
        'number_of_public_contributors',
        IN_QUERY,
        type=TYPE_BOOLEAN,
        required=False,
        description=(
            'Set this to true to return number of public '
            'contributors of each facility.'),
    ),
    Parameter(
        'sectors',
        IN_QUERY,
        type=TYPE_STRING,
        required=False,
        description=(
            'The sectors that this facility belongs to. '
            'Values must match those returned from the '
            '`GET /api/sectors` endpoint'
            )
    ),

    Parameter(
        'sort_by',
        IN_QUERY,
        type=TYPE_STRING,
        required=False,
        description=(
            'The sort_by parameter submits type of sorting order for '
            'facilities. Parameter value must be equal to name. Default '
            'sorting will be primary by public '
            'contributors count descending and secondary by name '
            'ascending/descending and contributors count ascending. '
            )
    )
]

facilities_create_parameters = [
    Parameter(
        'create',
        IN_QUERY,
        type=TYPE_BOOLEAN,
        required=False,
        description=(
            'If false, match results will be returned, but a new '
            'facility or facility match will not be saved'),
    ),
    Parameter(
        'public',
        IN_QUERY,
        type=TYPE_BOOLEAN,
        required=False,
        description=(
            'If false and a new facility or facility match is '
            'created, the contributor will not be publicly '
            'associated with the facility'),
    ),
    Parameter(
        'textonlyfallback',
        IN_QUERY,
        type=TYPE_BOOLEAN,
        required=False,
        description=(
            'If true and no confident matches were made then '
            'attempt to make a text-only match of the facility '
            'name. If more than 5 text matches are made only the '
            '5 highest confidence results are returned'),
    ),
]
