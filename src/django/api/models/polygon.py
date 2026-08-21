import uuid

from django.contrib.gis.db import models as gis_models
from django.core.validators import RegexValidator
from django.db import models


# Polygon names are machine-friendly identifiers (other code looks
# polygons up by name), so they follow identifier rules: letters,
# digits, and underscores only, and the first character can't be a
# digit. The admin form shows this message when a name breaks the rule.
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

    uuid = models.UUIDField(
        null=False,
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique identifier for the polygon.',
    )
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
        """A polygon is identified by its name."""
        return self.name

    # The fields callers may pass as keys in the `filters` argument of
    # get_production_locations(), mapped to the FacilityIndex lookup
    # that implements each one. Two kinds of lookup appear here because
    # the underlying columns differ:
    #   - `__in` fields hold ONE value per location (a location has
    #     exactly one country), so the check is "is that value in the
    #     requested list".
    #   - `__overlap` fields are ARRAYS (a location can have several
    #     sectors), so the check is "does the location's list share at
    #     least one value with the requested list".
    # To make a new field filterable, add an entry here — anything not
    # in this whitelist is rejected with an error rather than silently
    # ignored.
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
        Return the OS Hub production locations inside this boundary.

        Containment is evaluated by PostGIS (the same `location__within`
        lookup used by the existing `boundary` facility-search query
        param). Any optional filters are combined into the same single
        database query, and PostgreSQL applies the cheap column checks
        before the more expensive point-in-polygon test on its own, so
        there is no separate pre-filtering step to manage.

        Args:
            filters: Optional dict narrowing the results by core
                location fields, e.g.
                `{'country': ['IN'], 'sector': ['Apparel']}`.
                Keys must appear in `FILTERABLE_FIELDS` (an unknown key
                raises `ValueError`, so typos can't silently return
                unfiltered results). Values may be a list or a single
                string. Within one key, values are OR'd ("US or IN");
                across keys, conditions are AND'd ("that country AND
                that sector"). Country codes are upper-cased before
                matching so `'in'` behaves the same as `'IN'`.

        Returns:
            A `FacilityIndex` queryset of the matching locations.
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
