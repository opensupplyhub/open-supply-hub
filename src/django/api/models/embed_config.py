from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, RegexValidator
from django.db import models

MAX_CORNER_RADIUS = 16

MAX_COLOR_BY_VALUES = 20


def validate_color_by_colors(colors):
    """`colors` maps a field value to the hex color of its map markers."""
    if not isinstance(colors, dict):
        raise ValidationError('Colors must be given per value.')
    if len(colors) > MAX_COLOR_BY_VALUES:
        raise ValidationError(
            'At most {} values can have a color.'.format(MAX_COLOR_BY_VALUES)
        )
    for value, color in colors.items():
        if not isinstance(value, str) or len(value) > 200:
            raise ValidationError('Each value must be text.')
        if not isinstance(color, str):
            raise ValidationError('Each color must be a hex value.')
        hex_color_validator(color)


hex_color_validator = RegexValidator(
    regex=r'^#[0-9a-fA-F]{6}$',
    message='Enter a color as a six-digit hex value, for example #1386c6.',
)


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
    accent_color = models.CharField(
        max_length=7,
        null=True,
        blank=True,
        validators=[hex_color_validator],
        help_text='The accent color of the embedded map. The primary '
                  'color is used when this is not set.')
    heading_font = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text='The font for headings in the embedded map. The body '
                  'font is used when this is not set.')
    corner_radius = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(MAX_CORNER_RADIUS)],
        help_text='The corner radius, in pixels, of buttons and inputs '
                  'in the embedded map. Each element keeps its own '
                  'corner style when this is not set.')
    marker_color = models.CharField(
        max_length=7,
        null=True,
        blank=True,
        validators=[hex_color_validator],
        help_text='The color of the facility markers on the embedded map '
                  'when they are not colored by a field. The primary color '
                  'is used when this is not set.')
    color_by_field = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text='The column name of the embed field whose value colors '
                  'each facility marker on the embedded map, for example a '
                  'tier. Markers share one color when this is not set.')
    color_by_colors = models.JSONField(
        default=dict,
        blank=True,
        validators=[validate_color_by_colors],
        help_text='The marker color for each value of color_by_field, as '
                  '{value: hex color}.')
    default_sort = models.CharField(
        max_length=220,
        null=True,
        blank=True,
        validators=[RegexValidator(
            regex=r'^(name_asc|name_desc|-?field:.+)$',
            message='Sort by name_asc, name_desc, field:<column> or '
                    '-field:<column>.',
        )],
        help_text='The order of the facility list on the embedded map: '
                  'name_asc, name_desc, field:<column name> or '
                  '-field:<column name> for descending. The list is sorted '
                  'by name when this is not set.')
    blurbs_first = models.BooleanField(
        default=False,
        help_text='Whether facilities that have a blurb are listed first '
                  'on the embedded map, ahead of the chosen list order.')
    show_spotlight = models.BooleanField(
        default=False,
        help_text='Whether the embedded map shows Spotlight data from '
                  'OS Hub data partners.')
    spotlight_highlight = models.BooleanField(
        default=False,
        help_text='Whether facilities that have Spotlight data are ringed '
                  'on the embedded map.')
    spotlight_filter = models.BooleanField(
        default=False,
        help_text='Whether visitors to the embedded map can filter by '
                  'Spotlight data.')
    spotlight_groups = models.JSONField(
        blank=True,
        default=list,
        help_text='The UUIDs of the partner field groups whose Spotlight '
                  'data the embedded map shows.')
    allow_visitor_sort = models.BooleanField(
        default=False,
        help_text='Whether visitors to the embedded map can change the '
                  'order of the facility list.')
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
