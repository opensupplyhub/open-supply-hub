import uuid
from django.contrib.gis.db import models as gis_models
from django.db import models
from api.constants import OriginSource


class FacilityLocation(models.Model):
    """
    A record of a facility's location change, including the new lat/lng point
    and any notes regarding the change process.
    """
    uuid = models.UUIDField(
        null=False,
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique identifier for the facility location change.'
    )
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
        blank=True,
        null=True,
        max_length=200,
        help_text="The environment value where instance running"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
