import uuid

from django.contrib.gis.db import models as gis_models
from django.db import models, transaction

from api.models.polygon import variable_style_name_validator


class ZoneSet(models.Model):
    """
    A zoned geospatial dataset: a collection of polygons ("zones") that
    each carry a value, such as water-stress basins or landslide-
    susceptibility bands.

    A zone set feeds one Spotlight partner field. When a production
    location's coordinates fall inside one of the set's zones, that
    zone's value is shown on the location page under the linked
    field, resolved at request time with a point-in-polygon query —
    there is no backfill and no reindex. The field's title,
    attribution text and source link are the linked partner field's
    `label`, `source_by` and `base_url`/`display_text`, so they are
    edited where every other Spotlight field's presentation lives.

    Zones are uploaded in the Django admin from a GeoJSON
    FeatureCollection (see `api.models.zone_set_admin`). Re-uploading
    replaces the set's zones atomically: the old zones keep serving
    until the new file has fully validated, then they are swapped in
    one transaction (see `replace_zones`).

    Overlapping zones: if a location falls inside more than one zone
    of the same set, the zone that appeared FIRST in the uploaded
    file wins (lowest `Zone.feature_index`). This is deterministic
    and under the uploader's control — sort the features by severity
    before export to get "most severe wins". See `resolve_zone`.
    """

    uuid = models.UUIDField(
        null=False,
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique identifier for the zone set.',
    )
    name = models.CharField(
        max_length=200,
        unique=True,
        validators=[variable_style_name_validator],
        help_text=(
            'A short machine-friendly identifier for this dataset '
            '(e.g. "aqueduct_baseline_water_stress"). Letters, digits, '
            'and underscores only.'
        ),
    )
    description = models.TextField(
        help_text=(
            'Details about what this dataset represents, where it came '
            'from, and how the file was prepared.'
        ),
    )
    partner_field = models.OneToOneField(
        'PartnerField',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='zone_set',
        help_text=(
            'The Spotlight partner field this dataset feeds. The '
            "field's label is the displayed title, its source_by text "
            'is the attribution line, and its base URL / display text '
            'is the source link. The dataset serves nothing until a '
            'field is linked and a contributor holds that field. '
            'Deleting a field that a zone set points at is blocked.'
        ),
    )
    value_property = models.CharField(
        max_length=200,
        help_text=(
            'The GeoJSON feature property that supplies each zone\'s '
            'displayed value (e.g. "bws_label"). Every feature in an '
            'upload must carry it.'
        ),
    )
    active = models.BooleanField(
        default=True,
        help_text=(
            'Inactive zone sets serve no values. Use this to retire a '
            'dataset without deleting its zones.'
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Zone set'
        verbose_name_plural = 'Zone sets'

    def __str__(self):
        """A zone set is identified by its name."""
        return self.name

    def resolve_zone(self, point):
        """
        Return the zone of this set that contains the point, or None.

        Containment is evaluated by PostGIS using the zones' spatial
        index. When several zones contain the point, the one that came
        first in the uploaded file wins (lowest `feature_index`) — see
        the class docstring for why that rule and how to steer it.

        Args:
            point: A GEOS Point in WGS 84 (a facility's `location`).
        """
        return (
            self.zones.filter(geom__contains=point)
            .order_by('feature_index')
            .first()
        )

    @transaction.atomic
    def replace_zones(self, zone_records):
        """
        Replace every zone in this set with the given records, in one
        transaction.

        Callers validate the whole upload BEFORE calling this (see
        `api.helpers.geojson_zones.parse_zone_features`), so by the
        time any row is touched the new data is known to be good. The
        delete and the inserts commit together: readers either see the
        complete old set or the complete new set, never a mix or a gap.

        Args:
            zone_records: Dicts with `geom`, `label` and `properties`
                keys, in file order (the order defines
                `feature_index`).
        """
        self.zones.all().delete()
        Zone.objects.bulk_create(
            [
                Zone(
                    zone_set=self,
                    feature_index=index,
                    geom=record['geom'],
                    value={
                        'label': record['label'],
                        'properties': record['properties'],
                    },
                )
                for index, record in enumerate(zone_records)
            ],
            batch_size=500,
        )


class Zone(models.Model):
    """
    One polygon in a `ZoneSet`, carrying the value shown for locations
    inside it. Rows are created only by `ZoneSet.replace_zones`; they
    are not edited individually.
    """

    zone_set = models.ForeignKey(
        ZoneSet,
        on_delete=models.CASCADE,
        related_name='zones',
    )
    feature_index = models.PositiveIntegerField(
        help_text=(
            'Position of the source feature in the uploaded file '
            '(0-based). When zones in a set overlap, the lowest index '
            'wins.'
        ),
    )
    geom = gis_models.MultiPolygonField(
        srid=4326,
        help_text='The zone geometry in WGS 84 (EPSG:4326).',
    )
    value = models.JSONField(
        help_text=(
            'The zone\'s value: {"label": <displayed value>, '
            '"properties": {<every property of the source feature>}}.'
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Zone'
        verbose_name_plural = 'Zones'
        ordering = ('zone_set', 'feature_index')
        constraints = [
            models.UniqueConstraint(
                fields=('zone_set', 'feature_index'),
                name='zone_unique_feature_index_per_set',
            ),
        ]

    def __str__(self):
        """A zone is identified by its set and displayed label."""
        return f'{self.zone_set.name} #{self.feature_index}: {self.label}'

    @property
    def label(self):
        """The displayed value for locations inside this zone."""
        return (self.value or {}).get('label', '')
