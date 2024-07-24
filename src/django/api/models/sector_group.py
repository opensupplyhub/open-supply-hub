from django.db import models


class SectorGroup(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def related_sectors(self):
        return ", ".join([sector.name for sector in self.sectors.all()])

    def __str__(self):
        return self.name
