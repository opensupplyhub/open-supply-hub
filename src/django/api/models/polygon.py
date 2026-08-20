from django.contrib.gis.db import models as gis_models
from django.core.validators import RegexValidator
from django.db import models


variable_style_name_validator = RegexValidator(
    regex=r'^[a-zA-Z_][a-zA-Z0-9_]*$',
    message=(
        'Name must contain only letters, digits, and underscores, and '
        'must not start with a digit '
        '(e.g. "national_capital_territory_of_delhi").'
    ),
)


class Polygon(models.Model):
    """
    A reusable, named geographic boundary. Boundaries are arbitrary
    shapes (single polygons, disjoint multi-part polygons, and polygons
    with holes are all supported) and are not tied to country borders.

    This is a foundation for other tooling to build on: look up a
    boundary by name, call `get_production_locations()` to get the
    OS Hub production locations within it, then do whatever that
    tooling needs to do with those locations.
    """

    name = models.CharField(
        max_length=200,
        unique=True,
        validators=[variable_style_name_validator],
        help_text=(
            'A short machine-friendly identifier for this boundary, '
            'used to reference it from code. Letters, digits, and '
            'underscores only.'
        )
    )
    display_name = models.CharField(
        max_length=200,
        blank=True,
        help_text=(
            'Optional human-friendly name, for use if this boundary '
            'is ever displayed on OS Hub.'
        )
    )
    description = models.TextField(
        blank=False,
        help_text=(
            'Details about what this boundary represents and where it '
            'came from.'
        )
    )
    geom = gis_models.MultiPolygonField(
        srid=4326,
        help_text='The boundary geometry in WGS 84 (EPSG:4326).'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Polygon'
        verbose_name_plural = 'Polygons'

    def __str__(self):
        return self.name

    # Fields callers may filter get_production_locations() by, mapped
    # to the FacilityIndex lookup that implements each. `__in` fields
    # hold one value per location; `__overlap` fields are arrays, so a
    # location matches if any of its values is in the requested list.
    FILTERABLE_FIELDS = {
        'country': 'country_code__in',
        'sector': 'sector__overlap',
        'facility_type': 'facility_type__overlap',
        'processing_type': 'processing_type__overlap',
        'product_type': 'product_type__overlap',
        'parent_company': 'parent_company_name__overlap',
    }

    def get_production_locations(self, filters=None):
        """
        Return the FacilityIndex queryset of OS Hub production locations
        within this boundary.

        `filters` optionally narrows the result by core location
        fields, e.g. {'country': ['IN'], 'sector': ['Apparel']}. Keys
        must be in FILTERABLE_FIELDS; values within a key are OR'd,
        separate keys are AND'd. Everything runs as a single query.
        """
        from .facility.facility_index import FacilityIndex
        queryset = FacilityIndex.objects.filter(location__within=self.geom)
        for field, values in (filters or {}).items():
            lookup = self.FILTERABLE_FIELDS.get(field)
            if lookup is None:
                raise ValueError(
                    f'Unknown filter field "{field}". Allowed fields: '
                    f'{", ".join(sorted(self.FILTERABLE_FIELDS))}.'
                )
            if isinstance(values, str):
                values = [values]
            if field == 'country':
                values = [value.upper() for value in values]
            queryset = queryset.filter(**{lookup: list(values)})
        return queryset
