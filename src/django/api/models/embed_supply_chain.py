from django.core.validators import URLValidator
from django.db import models

from .embed_config import hex_color_validator


class EmbedSupplyChain(models.Model):
    """
    A supply chain a contributor has put together from their own facilities,
    to show on their embedded map: which locations it runs through and which
    of them supplies which.
    """
    MAX_NODES = 60
    DEFAULT_COLOR = '#c0392b'

    class Meta:
        ordering = ('order', 'id')

    contributor = models.ForeignKey(
        'Contributor',
        null=False,
        on_delete=models.CASCADE,
        related_name='embed_supply_chains',
        help_text='The contributor who owns this supply chain.')
    name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        help_text='The name shown to visitors, such as a product line.')
    description = models.TextField(
        max_length=600,
        blank=True,
        default='',
        help_text='A short description shown to visitors.')
    product_url = models.CharField(
        max_length=500,
        blank=True,
        default='',
        validators=[URLValidator(schemes=['http', 'https'])],
        help_text='A link to the product this supply chain makes.')
    color = models.CharField(
        max_length=7,
        default=DEFAULT_COLOR,
        validators=[hex_color_validator],
        help_text='The color of this supply chain on the map.')
    is_published = models.BooleanField(
        default=False,
        help_text='Whether visitors to the embedded map can see this '
                  'supply chain.')
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text='The position of this supply chain among the '
                  'contributor\'s supply chains.')
    nodes = models.JSONField(
        default=list,
        blank=True,
        help_text='The locations in this supply chain, as '
                  '[{"os_id": ..., "stage": ...}].')
    links = models.JSONField(
        default=list,
        blank=True,
        help_text='Which location supplies which, as '
                  '[[supplier OS ID, customer OS ID]].')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'EmbedSupplyChain {id}: {name}'.format(**self.__dict__)
