import uuid

from django.contrib.gis.db import models as gis_models
from django.db import models, transaction

from api.facility_index_backfill.zone_set_ids_recompute import (
    schedule_zone_set_ids_recompute,
)
from api.models.polygon import variable_style_name_validator


class ZoneSet(models.Model):
    """
    A zoned geospatial dataset: a collection of polygons ("zones") that
    each carry a value, such as water-stress basins or landslide-
    susceptibility bands.

    A zone set feeds one Spotlight partner field. When a production
    location's coordinates fall inside one of the set's zones, that
    zone's value is shown on the location page under the linked
    field, resolved at request time with a point-in-polygon query.
    A string field gets one value per zone, read from the feature
    property named by `value_property`. An object field gets one
    value per key of its JSON schema, each read from the feature
    property of the same name, so one upload serves several data
    points per zone as one block on the page (OSDEV-3659); see
    `feeds_object_field` and `schema_keys`.
    Search is served differently: `FacilityIndex.zone_set_ids` holds
    the ids of the sets covering each location, refreshed on every
    facility save and recomputed for the whole table after
    `replace_zones` (OSDEV-3743). The field's title,
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

    Storage: each uploaded feature is cut into pieces of a bounded
    vertex count before it is saved (`api.helpers.zone_subdivision`,
    run by the admin form while it validates the file), so a
    dissolved layer of a few enormous multipolygons costs the
    point-in-polygon test no more than a layer of many small ones.
    Every piece carries the feature's value and `feature_index`, so
    nothing above this paragraph changes; `Zone.piece_index` only
    tells the pieces of one feature apart.
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
        blank=True,
        null=True,
        help_text=(
            'For a "string" partner field: the GeoJSON feature property '
            'that supplies each zone\'s displayed value (e.g. '
            '"bws_label"). Every feature in an upload must carry it. '
            'Leave empty for an "object" field, which reads one feature '
            'property per key of its JSON schema instead.'
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

    @property
    def feeds_object_field(self):
        """
        Whether the linked partner field is object-typed.

        Decides the shape of what each zone carries and what the
        provider serves: a single label read from `value_property` for
        a string field, or one value per top-level key of the field's
        JSON schema for an object field (OSDEV-3659). A set with no
        field linked counts as a string set.
        """
        field = self.partner_field
        return field is not None and field.type == field.OBJECT

    @property
    def schema_keys(self):
        """
        The top-level keys of the linked object field's JSON schema, in
        schema order: the feature properties an upload is read by and
        the only ones the provider serves. Empty for a string field, a
        set with no field, or an object field without a usable schema
        (which the admin form refuses to link).
        """
        field = self.partner_field
        if field is None:
            return []
        return list(field.object_schema_properties().keys())

    def resolve_zone(self, point):
        """
        Return the zone of this set that covers the point, or None.

        Coverage is evaluated by PostGIS using the zones' spatial
        index. `covers` rather than `contains` so a point exactly on a
        zone's edge still resolves: raster-derived datasets have
        grid-aligned edges at round coordinates, and a location
        geocoded onto one of them is inside the dataset, not outside
        it. When several zones cover the point (overlap, or a shared
        edge), the one that came first in the uploaded file wins
        (lowest `feature_index`) — see the class docstring for why
        that rule and how to steer it.

        Args:
            point: A GEOS Point in WGS 84 (a facility's `location`).
        """
        return (
            self.zones.filter(geom__covers=point)
            .order_by('feature_index', 'piece_index')
            .first()
        )

    @transaction.atomic
    def replace_zones(self, pieces):
        """
        Replace every zone in this set with the given pieces, in one
        transaction.

        Callers validate and cut the whole upload BEFORE calling this
        (`api.helpers.geojson_zones.parse_zone_features`, then
        `api.helpers.zone_subdivision.subdivide_zone_records`; the
        admin form runs both in `clean`), so by the time any row is
        touched the new data is known to be good and a feature that
        could not be cut has already been refused as a form error. The
        delete and the inserts commit together: readers either see the
        complete old set or the complete new set, never a mix or a gap.

        Each piece becomes one `Zone` row carrying its source feature's
        label, properties and position in the file.

        New zones change which locations the set covers without
        touching any facility row, so once the transaction commits a
        recompute of `FacilityIndex.zone_set_ids` for the whole table
        is started (see
        `api.facility_index_backfill.zone_set_ids_recompute`). Until it
        finishes, search results for the set reflect the previous
        zones; the location page, which resolves zones live, reflects
        the new ones at once.

        Args:
            pieces: Dicts as returned by `subdivide_zone_records`, in
                (feature, piece) order: `feature_index`, `piece_index`,
                `geom`, `label` and `properties`.
        """
        self.zones.all().delete()
        Zone.objects.bulk_create(
            [
                Zone(
                    zone_set=self,
                    feature_index=piece['feature_index'],
                    piece_index=piece['piece_index'],
                    geom=piece['geom'],
                    value={
                        'label': piece['label'],
                        'properties': piece['properties'],
                    },
                )
                for piece in pieces
            ],
            batch_size=500,
        )
        schedule_zone_set_ids_recompute()


class Zone(models.Model):
    """
    One piece of one feature of a `ZoneSet`, carrying the value shown
    for locations inside it. A feature whose geometry fits the vertex
    budget is a single piece; a larger one is several rows that share
    its `feature_index` and value and differ in `piece_index` (see
    `api.helpers.zone_subdivision`). Rows are created only by
    `ZoneSet.replace_zones`; they are not edited individually.

    Every piece of a feature stores a copy of the feature's `value`
    (label plus all source properties), so a feature cut into N pieces
    stores its JSON N times. That is deliberate for now: the admin and
    the migration that re-cut existing zones stay one-table changes,
    and the cost is bounded (the upload cap is 10 MB and a piece's
    JSON is small next to its geometry). If per-feature data grows or
    needs editing, the value belongs on a ZoneFeature row that the
    pieces point at, with uniqueness of `feature_index` falling out of
    that key.
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
    piece_index = models.PositiveIntegerField(
        default=0,
        help_text=(
            'Position of this piece within its source feature '
            '(0-based). Large features are cut into pieces of a '
            'bounded vertex count at upload; every piece carries the '
            "feature's value."
        ),
    )
    geom = gis_models.MultiPolygonField(
        srid=4326,
        help_text='The zone geometry in WGS 84 (EPSG:4326).',
    )
    value = models.JSONField(
        help_text=(
            'The zone\'s value: {"label": <displayed value>, '
            '"properties": {<every property of the source feature>}}. '
            'For a set feeding an object field the label is the first '
            'required schema property (or empty) and the served values '
            'are read from "properties" by schema key.'
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Zone'
        verbose_name_plural = 'Zones'
        ordering = ('zone_set', 'feature_index', 'piece_index')
        constraints = [
            models.UniqueConstraint(
                fields=('zone_set', 'feature_index', 'piece_index'),
                name='zone_unique_piece_per_feature_per_set',
            ),
        ]

    def __str__(self):
        """A zone is identified by its set, feature, piece and label."""
        return (
            f'{self.zone_set.name} #{self.feature_index}.{self.piece_index}: '
            f'{self.label}'
        )

    @property
    def label(self):
        """The displayed value for locations inside this zone."""
        return (self.value or {}).get('label', '')
