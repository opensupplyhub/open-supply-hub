from django.db import models
from ..constants import OriginSource


class SectorGroup(models.Model):
    name = models.CharField(max_length=200, unique=True)
    origin_source = models.CharField(
        choices=OriginSource.CHOICES,
        blank=True,
        null=True,
        max_length=200,
        help_text="The environment value where instance running"
    )

    def related_sectors(self):
        return ", ".join([sector.name for sector in self.sectors.all()])

    def __str__(self):
        return self.name
