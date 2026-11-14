import logging
import uuid

from django.contrib.gis.db import models as gis_models
from django.db import models, transaction
from django.db.models import Count, Q
from django.db.models.fields.json import KeyTransform

from api.helpers.geojson_zones import is_usable_zone_value
from api.helpers.location_filters import build_filters_q, has_filters

from api.facility_index_backfill.zone_set_ids_recompute import (
    schedule_zone_set_ids_recompute,
)
from api.models.polygon import variable_style_name_validator

logger = logging.getLogger(__name__)


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

    Filters: a set may limit itself to locations matching `filters`
    (sector, country, product type and the other polygon filter
    fields; see `api.helpers.location_filters`). The filled-in boxes
    combine with AND, and the values inside one box are alternatives.
    Richer rules, such as OR between boxes, are future work and are
    noted in that module. A location inside a zone that fails the
    filters gets no value, on the location page, in the v1 endpoint,
    in search and in the contributor-profile spotlight alike. The
    filters are not stored with the zones: they are applied to each
    location when it is served, so editing them needs no re-upload
    and no recompute of `zone_set_ids`.

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
    filters = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            'Optional: only show this dataset on locations that match, '
            'e.g. {"sector": ["Mining"]} or {"country": ["KH"], '
            '"product_type": ["sugarcane"]}. Allowed keys: country, '
            'sector, facility_type, processing_type, product_type, '
            'parent_company (the same ones polygon filters use). Within '
            'one key the values are alternatives; across keys a '
            'location must match all. Sector and the other names must '
            'be spelled exactly as they appear on locations; product '
            'types are not case sensitive. Leave empty to show the '
            'dataset on every location inside a zone.'
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

    @property
    def feature_count(self):
        """How many uploaded features the set stores (not pieces)."""
        return self.zones.aggregate(
            n=Count('feature_index', distinct=True)
        )['n']

    def features_lacking(self, keys):
        """
        For each feature property in `keys`, how many of the set's
        uploaded features have no usable stored value for it.

        "Usable" is decided by the same function the provider serves
        by and the upload check demands
        (`api.helpers.geojson_zones.is_usable_zone_value`), applied in
        Python to the stored values rather than re-stated in SQL, so
        the three can never disagree (a tab-only string, say, is blank
        to all of them). One row per feature is read, carrying just the
        requested properties, so pieces of the same feature are not
        counted twice and the numbers match the upload messages.

        Used by the partner field admin to refuse a schema change that
        makes a property required when the zones already stored were
        never read for it (OSDEV-3659).

        Args:
            keys: The property names to count.

        Returns:
            Dict of key to the number of features lacking it.
        """
        keys = list(keys)
        missing = dict.fromkeys(keys, 0)
        if not keys:
            return missing
        rows = (
            self.zones.order_by('feature_index')
            .distinct('feature_index')
            .values_list('feature_index', *[
                KeyTransform(key, KeyTransform('properties', 'value'))
                for key in keys
            ])
        )
        for row in rows:
            for key, value in zip(keys, row[1:]):
                if not is_usable_zone_value(value):
                    missing[key] += 1
        return missing

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

    def filters_condition(self):
        """
        The query condition for this set's `filters`, safe to serve with.

        Returns `None` when the set has no filters (callers treat that
        as "no restriction"). Returns the condition from
        `build_filters_q` otherwise.

        A stored value that is not usable (it can only get there outside
        the admin form, which refuses it, for example a hand edit in the
        database) must never break a location page or search, and must
        never widen what is shown. So the error is logged and the set is
        treated as matching nothing, the same "match nothing, never
        everything" rule the India Labour Line provider follows. The
        returned condition for that case, `Q(id__in=[])`, is the same
        empty match the partner search filter uses when a polygon is
        missing.
        """
        if not has_filters(self.filters):
            return None
        try:
            return build_filters_q(self.filters)
        except ValueError as exc:
            logger.error(
                'Zone set "%s" (id %s) has filters that cannot be used, '
                'so it matches no location until they are fixed in the '
                'admin: %s', self.name, self.pk, exc,
            )
            return Q(id__in=[])

    def passes_filters(self, production_location):
        """
        Whether a location matches this set's `filters`.

        A set with no filters passes every location. Otherwise the
        location is looked up in the search index by id and tested
        with the same condition search and the profile spotlight use
        (`filters_condition`), as one
        existence query. The index is used for both kinds of caller
        because the location page passes a `FacilityIndex` (which
        carries the filterable columns) while the v1 endpoint passes a
        `Facility` (which does not); the two share an id.

        The filters are applied to the location, not stored with the
        zones, so changing them takes effect at once with no upload
        and no recompute.

        Args:
            production_location: The Facility or FacilityIndex being
                rendered.
        """
        condition = self.filters_condition()
        if condition is None:
            return True
        from api.models.facility.facility_index import FacilityIndex
        return (
            FacilityIndex.objects
            .filter(id=production_location.id)
            .filter(condition)
            .exists()
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
