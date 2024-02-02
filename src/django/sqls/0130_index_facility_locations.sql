CREATE OR REPLACE
FUNCTION index_facility_locations(af_id TEXT)
RETURNS TABLE (facility_location json)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
SELECT
	json_build_object(
'location_lat',
	ST_Y(aflo.location),
	'location_lng',
	ST_X(aflo.location),
	'location_notes',
	aflo.notes,
	'contributor',
	json_build_object(
	'admin_id',
	ac.admin_id,
	'name',
	ac.name,
	'contrib_type',
	ac.contrib_type
)
)
FROM
	api_facilitylocation aflo
LEFT JOIN api_contributor ac ON
	ac.id = aflo.contributor_id
WHERE
	aflo.facility_id = af_id;
END;

$Body$;
