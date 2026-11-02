/*
OSDEV-3743. The zone sets whose zones cover a location, for the
zone_set_ids column of api_facilityindex.

index_facilities_by(ids) calls this for every row it writes (see
0264_index_facilities_zone_set_ids.sql), so the column is refreshed by
the api_facility triggers on every facility save, including a coordinate
correction. The backfill_facility_index "zone_set_ids" field group calls
it for every existing row after a set's zones are replaced, which changes
membership without touching any facility row.

The test is ST_Covers, the same one ZoneSet.resolve_zone runs for the
location page, so a point exactly on a zone edge is inside the dataset on
both surfaces. It is answered from the GiST index on api_zone.geom.

Every zone set is included, active or not: "active" is a presentation
flag the search filter applies when it resolves which set ids to look
for (get_active_zone_sets_for_fields), so toggling it takes effect at
once with no recompute. Ids are sorted so two computations of the same
membership compare equal, which the backfill relies on to skip rows that
have not changed. A location with no coordinates gets an empty array.
*/

CREATE OR REPLACE
FUNCTION index_zone_set_ids(location geometry)
RETURNS integer[]
LANGUAGE sql
STABLE
PARALLEL SAFE
AS $Body$
SELECT COALESCE(
	(
		SELECT array_agg(DISTINCT az.zone_set_id ORDER BY az.zone_set_id)
		FROM api_zone az
		WHERE ST_Covers(az.geom, location)
	),
	'{}'::integer[]
);
$Body$;
