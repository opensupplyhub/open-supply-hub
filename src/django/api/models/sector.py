from django.db import models


class Sector(models.Model):
    DEFAULT_SECTOR_NAME = 'Unspecified'

    name = models.CharField(max_length=200, primary_key=True)

    def __str__(self):
        return self.name
