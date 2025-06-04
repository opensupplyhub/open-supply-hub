from django.contrib.gis.db import models as gis_models
from django.db import models
from ...constants import OriginSource


class FacilityLocation(models.Model):
    """
    """
    facility = models.ForeignKey(
        'Facility',
        null=False,
        on_delete=models.CASCADE,
        help_text='The Facility on which the location is changing'
    )
    location = gis_models.PointField(
        null=False,
        help_text='The corrected lat/lng point location of the facility')
    notes = models.TextField(
        null=False,
        blank=True,
        help_text='Details regarding the location change process')
    created_by = models.ForeignKey(
        'User',
        null=False,
        on_delete=models.PROTECT,
        help_text='The superuser that submitted the new location'
    )
    contributor = models.ForeignKey(
        'Contributor',
        null=True,
        on_delete=models.PROTECT,
        help_text=('An optional reference to the contributor who submitted '
                   'the new location')
    )
    origin_source = models.CharField(
        choices=OriginSource.CHOICES,
        default=OriginSource.OSHUB,
        max_length=200,
        help_text="The environment value where instance running"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
