from django.db import models


class Sector(models.Model):
    DEFAULT_SECTOR_NAME = 'Unspecified'

    name = models.CharField(max_length=200, primary_key=True)

    groups = models.ManyToManyField(
        'SectorGroup',
        blank=False,
        related_name='sectors',
        help_text='The sector groups to which this sector belongs.',
    )

    def __str__(self):
        return self.name
