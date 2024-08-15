from drf_yasg.openapi import (
    Parameter,
    IN_QUERY,
    TYPE_BOOLEAN,
    TYPE_INTEGER,
)

sectors_manual_parameters = [
    Parameter(
        'embed',
        IN_QUERY,
        description="If present, returns a flat list of sectors submitted "
        "by a specific contributor.",
        type=TYPE_BOOLEAN,
    ),
    Parameter(
        'contributor',
        IN_QUERY,
        description="Contributor ID, required when 'embed' is present.",
        type=TYPE_INTEGER,
    ),
    Parameter(
        'grouped',
        IN_QUERY,
        description="If present, returns a grouped list of sectors by "
        "their sector groups.",
        type=TYPE_BOOLEAN,
    ),
]

sectors_operation_description = """
Returns a list of sectors or sectors grouped by their sector groups.

## Parameters:
- `embed` (optional): If present, returns a flat list of sectors submitted
by a specific contributor.
- `contributor` (optional): If `embed` is provided, this parameter must be
included to filter sectors submitted by a specific contributor.
- `grouped` (optional): If present, returns a grouped list of sectors by
their sector groups.

Note: If both `embed` and `grouped` are provided, the `embed` parameter
will take precedence.

## Sample Responses:

### Flat List (with or without 'embed'):
    [
        "Agriculture",
        "Apparel",
        "Information",
    ]

### Grouped List:
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
