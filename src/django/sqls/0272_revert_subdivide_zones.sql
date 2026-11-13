/*
OSDEV-3744 reverse. Merge the pieces of each feature back into one row,
so the one-row-per-feature unique constraint can be restored (by the
reverse of 0271, which runs after this in a transaction of its own).

ST_UnaryUnion of a feature's pieces removes the cut lines and gives
back the feature's coverage; the result can differ from the uploaded
geometry by floating-point noise along the former cut lines. Features
stored as a single piece are left untouched.

The table lock keeps a zone upload from committing between the copy and
the DELETE below, where its rows would be deleted and never re-inserted
(see 0272_subdivide_zones.sql). It blocks writers only; reads go on.
*/

LOCK TABLE api_zone IN SHARE ROW EXCLUSIVE MODE;

CREATE TEMP TABLE zone_merge_sources ON COMMIT DROP AS
SELECT
    zone_set_id,
    feature_index,
    ST_Multi(ST_UnaryUnion(ST_Collect(geom ORDER BY piece_index))) AS geom,
    (array_agg(value ORDER BY piece_index))[1] AS value,
    min(created_at) AS created_at
FROM api_zone
GROUP BY zone_set_id, feature_index
HAVING count(*) > 1;

DELETE FROM api_zone AS zone
USING zone_merge_sources AS merged
WHERE zone.zone_set_id = merged.zone_set_id
    AND zone.feature_index = merged.feature_index;

INSERT INTO api_zone
    (zone_set_id, feature_index, piece_index, geom, value, created_at)
SELECT zone_set_id, feature_index, 0, geom, value, created_at
FROM zone_merge_sources;
