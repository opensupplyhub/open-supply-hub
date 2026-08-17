from django.contrib.gis.db import models as gis_models
from django.db import models


class NamedPolygon(models.Model):
    """
    A reusable, named geographic boundary. Boundaries are arbitrary
    shapes (single polygons, disjoint multi-part polygons, and polygons
    with holes are all supported) and are not tied to country borders.

    This is a foundation for other tooling to build on: look up a
    boundary by name, call `facilities()` to get the OS Hub production
    locations within it, then do whatever that tooling needs to do with
    those locations.
    """

    name = models.CharField(
        max_length=200,
        help_text='A short, descriptive name for this boundary.'
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
        verbose_name = 'Named polygon'
        verbose_name_plural = 'Named polygons'

    def __str__(self):
        return self.name

    def facilities(self):
        """
        Return the FacilityIndex queryset of OS Hub production locations
        within this boundary.
        """
        from .facility.facility_index import FacilityIndex
        return FacilityIndex.objects.filter(location__within=self.geom)
