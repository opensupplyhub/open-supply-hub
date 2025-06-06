import uuid
from django.db import models


class SectorGroup(models.Model):
    name = models.CharField(max_length=200, unique=True)
    uuid = models.UUIDField(
        null=False,
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique identifier for the sector group.'
    )

    def related_sectors(self):
        return ", ".join([sector.name for sector in self.sectors.all()])

    def __str__(self):
        return self.name
