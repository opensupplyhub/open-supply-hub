from django.db import models
from ..constants import OriginSource


class Sector(models.Model):
    DEFAULT_SECTOR_NAME = 'Unspecified'

    name = models.CharField(max_length=200, primary_key=True)

    groups = models.ManyToManyField(
        'SectorGroup',
        blank=False,
        related_name='sectors',
        help_text='The sector groups to which this sector belongs.',
    )
    origin_source = models.CharField(
        choices=OriginSource.CHOICES,
        blank=True,
        null=True,
        max_length=200,
        help_text="The environment value where instance running"
    )

    def __str__(self):
        return self.name
