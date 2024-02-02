from django.db import models
from django.contrib.postgres import fields


class TileCache(models.Model):
    """
    This table serves as a cache for the generated tiles. Each unique key has
    a date to check whether it is a stale tile that needs to be regenerated.
    """
    path = models.TextField(
        primary_key=True,
        null=False,
        help_text='The requested tile URL.'
    )
    embed = models.BooleanField(
        default=False,
        help_text='Whether the tile is generated for an embedded map.'
    )
    contributors = fields.ArrayField(models.TextField(
        null=False,
        blank=False,
        help_text='The ID of the contributor passed via query param.'),
        default=list)
    value = models.BinaryField(
        null=False,
        help_text='The cached binary tile.'
    )
    counter = models.IntegerField(
        default=0,
        null=False,
        help_text='The count of the number of times the cached tile was used.')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Path - {self.path} embed - {self.embed}'
