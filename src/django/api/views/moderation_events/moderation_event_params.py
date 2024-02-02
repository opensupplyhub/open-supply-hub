from drf_yasg.openapi import (
  Parameter,
  IN_QUERY,
  TYPE_BOOLEAN,
  TYPE_STRING,
  TYPE_INTEGER
)

merge_params = [
    Parameter(
        'detail',
        IN_QUERY,
        type=TYPE_BOOLEAN,
        required=False,
        description=(
            'Set this to true to return additional details about '
            'merge events, namely address and name of the '
            'original facility.'),
    ),
    Parameter(
        'date_greater_than_or_equal',
        IN_QUERY,
        type=TYPE_STRING,
        required=False,
        description=(
            'Specify the date in the YYYY-MM-DD format to retrieve '
            'merge events that occurred on or after the specified '
            'date.'),
    ),
    Parameter(
        'date_less_than',
        IN_QUERY,
        type=TYPE_STRING,
        required=False,
        description=(
            'Specify the date in the YYYY-MM-DD format to retrieve '
            'merge events that occurred before the specified date.'),
    ),
    Parameter(
        'all',
        IN_QUERY,
        type=TYPE_BOOLEAN,
        required=False,
        description=(
            'Set this to true to return all the merge events accross '
            'the whole system.'),
    ),
    Parameter(
        'contributors',
        IN_QUERY,
        type=TYPE_INTEGER,
        required=False,
        description=(
            'Specify the contributors as ids to retrieve the history of merge '
            'events applied to the facilities that the contributor ids are '
            'associated with.'),
    )
]
