from django.contrib.gis.db import models as gis_models
from django.db.models import Model, DateTimeField, CharField


class USCountyTigerline(Model):
    '''
    Stores US County Tigerline data with geometry.
    '''

    geoid = CharField(
        max_length=50,
        primary_key=True,
        help_text='The Geo ID of the county (US)'
    )
    name = CharField(
        max_length=255,
        help_text='The name of the county'
    )
    geometry = gis_models.MultiPolygonField(
        srid=5070,
        help_text='The MultiPolygon geometry of the county in EPSG:5070'
    )
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'US County Tigerline'
        verbose_name_plural = 'US County Tigerline'

    def __str__(self):
        return f'US County Tigerline: {self.name} ({self.geoid})'

