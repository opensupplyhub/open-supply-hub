/*
OSDEV-3744. Store every existing zone as pieces of at most 64 vertices,
exactly as ZoneSet.replace_zones now does for new uploads (see
api/helpers/zone_subdivision.py for why, and for the budget).

Every row is re-cut, not only the ones over the budget, so the result is
identical to re-uploading the same file: ST_Subdivide returns a geometry
that already fits as a single piece. The rows are removed before the
pieces are inserted so piece 0 can take the (zone_set, feature_index, 0)
slot of the row it replaces. Each piece keeps its feature's value,
feature_index and created_at, so the location page and the search
column see the same coverage and labels as before; only row ids change.
*/

-- Django declares the zone_set foreign key DEFERRABLE INITIALLY
-- DEFERRED, so the inserts below would leave pending constraint
-- triggers and the ALTER TABLEs that run next in the same migration
-- transaction would fail with "pending trigger events". Check them
-- as they happen instead.
SET CONSTRAINTS ALL IMMEDIATE;

CREATE TEMP TABLE zone_subdivide_sources ON COMMIT DROP AS
SELECT id, zone_set_id, feature_index, geom, value, created_at
FROM api_zone;

DELETE FROM api_zone
WHERE id IN (SELECT id FROM zone_subdivide_sources);

INSERT INTO api_zone
    (zone_set_id, feature_index, piece_index, geom, value, created_at)
SELECT
    source.zone_set_id,
    source.feature_index,
    piece.ordinality - 1,
    ST_Multi(piece.geom),
    source.value,
    source.created_at
FROM zone_subdivide_sources AS source,
    LATERAL ST_Subdivide(source.geom, 64)
        WITH ORDINALITY AS piece(geom, ordinality);
