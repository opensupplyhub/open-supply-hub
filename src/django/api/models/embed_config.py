from django.db import models


class EmbedConfig(models.Model):
    """
    Configuration data for an embedded map
    """

    width = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        default='600',
        help_text='The width of the embedded map.')
    height = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        default='400',
        help_text='The height of the embedded map.')
    color = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text='The color of the embedded map.')
    font = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text='The font of the embedded map.')
    prefer_contributor_name = models.BooleanField(
        null=True,
        blank=True,
        help_text='Whether to use the contributor\'s facility name ' +
                  'before other names.'
    )
    text_search_label = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        default='Facility name or OS ID',
        help_text='The label for the search box.')
    map_style = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        default='default',
        help_text='The map style for the embedded map')
    hide_sector_data = models.BooleanField(
        null=True,
        blank=True,
        help_text='Whether to hide sector data in the embedded map.'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return ('EmbedConfig {id}, '
                'Size: {width} x {height} '
                ).format(**self.__dict__)
