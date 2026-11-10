"""
Cut zone geometry into small pieces before it is saved (OSDEV-3744).

PostGIS answers "does this zone cover this point" in two steps: the
GiST index finds the zones whose bounding box contains the point, then
an exact test walks each candidate's vertices. That exact test is what
makes a dissolved layer slow. Merging every basin with the same value
into one multipolygon per value leaves a handful of features with
hundreds of thousands of vertices each and bounding boxes that span
continents, so every point hits several candidates and each exact test
walks an enormous ring: about 1.2 ms per point against about 10 µs for
a layer of small features. That cost lands on every facility save
(`index_zone_set_ids` runs in the indexing trigger) and on the
full-table `zone_set_ids` recompute after an upload, which is why it
is paid once here instead.

`ST_Subdivide` tiles each feature into pieces of at most
`ZONE_PIECE_MAX_VERTICES` vertices, cutting along axis-aligned lines.
The pieces partition the feature exactly, so the covered area is the
same; each piece carries the source feature's value and its position
in the file, so `ZoneSet.resolve_zone` returns the same label as it did
for the undivided feature and overlap precedence still follows file
order. A point on a cut line is covered by two pieces of the same
feature, which both carry the same value.
"""

from django.contrib.gis.geos import GEOSGeometry
from django.db import connection

# Vertices per piece. Chosen by timing the `ST_Covers` probe for 20,000
# facility points against the real Aqueduct 4.0 layer (68,506 basins,
# 13.3M vertices) stored three ways: raw, dissolved per country and
# value (890 features, up to 1.28M vertices) and dissolved per value
# (7 features, up to 1.52M vertices). Undivided, the country bands took
# 340 s and the global dissolve exhausted the database server's memory;
# every subdivided variant took 0.43-0.64 s whatever the source shape,
# against 1.2 s for the raw basins. 32, 64, 128 and 256 were within
# noise of each other, with 64 slightly ahead on the raw basins, so the
# smallest budget that showed no penalty is used. PostGIS's default is
# 256; `ST_Subdivide` refuses anything under 5.
ZONE_PIECE_MAX_VERTICES = 64

# One statement for the whole upload: the validated feature geometries
# go in as an ordered array and every piece comes back tagged with its
# source feature's position and its own position within that feature.
# Doing it in PostGIS rather than in GEOS keeps the result identical to
# what the migration that subdivided pre-existing zones produced.
SUBDIVIDE_SQL = """
SELECT
    source.ordinality - 1 AS feature_index,
    piece.ordinality - 1 AS piece_index,
    ST_AsEWKB(ST_Multi(piece.geom)) AS geom
FROM unnest(%s::bytea[]) WITH ORDINALITY AS source(ewkb, ordinality),
    LATERAL ST_Subdivide(ST_GeomFromEWKB(source.ewkb), %s)
        WITH ORDINALITY AS piece(geom, ordinality)
ORDER BY 1, 2
"""


def subdivide_zone_records(zone_records, max_vertices=ZONE_PIECE_MAX_VERTICES):
    """
    Split each zone record's geometry into pieces of at most
    `max_vertices` vertices.

    Args:
        zone_records: Dicts with `geom`, `label` and `properties` keys,
            in file order (the output of `parse_zone_features`).
        max_vertices: The vertex budget per piece.

    Returns:
        A list of dicts in (feature, piece) order, each with:
            - `feature_index`: the position of the source record
            - `piece_index`: the position of the piece within it
            - `geom`: a WGS 84 MultiPolygon of at most `max_vertices`
              vertices
            - `label` and `properties`: copied from the source record
        A record whose geometry already fits the budget comes back as
        its single piece 0, unchanged.
    """
    if not zone_records:
        return []
    with connection.cursor() as cursor:
        cursor.execute(
            SUBDIVIDE_SQL,
            [
                [bytes(record['geom'].ewkb) for record in zone_records],
                max_vertices,
            ],
        )
        rows = cursor.fetchall()
    pieces = []
    for feature_index, piece_index, ewkb in rows:
        record = zone_records[feature_index]
        pieces.append({
            'feature_index': feature_index,
            'piece_index': piece_index,
            # GEOSGeometry reads WKB from a buffer, not from bytes.
            'geom': GEOSGeometry(memoryview(ewkb)),
            'label': record['label'],
            'properties': record['properties'],
        })
    return pieces
