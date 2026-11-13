/*
OSDEV-3744. Store every existing zone as pieces of at most 64 vertices:
the value of ZONE_PIECE_MAX_VERTICES (api/helpers/zone_subdivision.py,
which says why and how the budget was chosen) when this migration was
written. The constant may move later; this file must not, so the number
is written out rather than read from the code.

Every row is re-cut, not only the ones over the budget, so the result is
identical to re-uploading the same file at that budget: ST_Subdivide
returns a geometry that already fits as a single piece. The rows are
removed before the pieces are inserted so piece 0 can take the
(zone_set, feature_index, 0) slot of the row it replaces. Each piece
keeps its feature's value, feature_index and created_at, so the location
page and the search column see the same coverage and labels as before;
only row ids change.

The temp table is a full copy of api_zone taken in this transaction and
the DELETE below removes exactly the rows it copied; readers on other
connections keep seeing the old rows until this transaction commits.

The copy and the DELETE are separate statements, and under READ
COMMITTED each sees what has committed by the time it runs: a zone
upload (ZoneSet.replace_zones) committing between the two would have its
rows deleted and never re-inserted. The table lock below closes that
window. SHARE ROW EXCLUSIVE blocks INSERT, UPDATE and DELETE from other
transactions until this one commits, and replace_zones is the only
writer, so at worst an admin upload waits a few seconds; it conflicts
with no read, so the facility indexing trigger, location pages and the
zone_set_ids recompute are not held up.

piece_index is numbered per (zone_set, feature_index) over every piece
of every source row, not from ST_Subdivide's ordinality alone, so the
file does not assume one row per feature: run against rows that are
already pieces it renumbers them and changes nothing else.
*/

LOCK TABLE api_zone IN SHARE ROW EXCLUSIVE MODE;

CREATE TEMP TABLE zone_subdivide_sources ON COMMIT DROP AS
SELECT id, zone_set_id, feature_index, piece_index, geom, value, created_at
FROM api_zone;

DELETE FROM api_zone
WHERE id IN (SELECT id FROM zone_subdivide_sources);

INSERT INTO api_zone
    (zone_set_id, feature_index, piece_index, geom, value, created_at)
SELECT
    source.zone_set_id,
    source.feature_index,
    row_number() OVER (
        PARTITION BY source.zone_set_id, source.feature_index
        ORDER BY source.piece_index, piece.ordinality
    ) - 1,
    ST_Multi(piece.geom),
    source.value,
    source.created_at
FROM zone_subdivide_sources AS source,
    LATERAL ST_Subdivide(source.geom, 64)
        WITH ORDINALITY AS piece(geom, ordinality);
