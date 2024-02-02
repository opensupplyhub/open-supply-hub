CREATE OR REPLACE
FUNCTION index_facility_list_items(af_id TEXT,
af_location geometry)
RETURNS TABLE (facility_list_item json)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
SELECT
	json_build_object(
'location_lat',
	ST_Y(afli.geocoded_point),
	'location_lng',
	ST_X(afli.geocoded_point),
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
	api_facilitymatch afm
LEFT JOIN api_facilitylistitem afli ON
	afli.id = afm.facility_list_item_id
LEFT JOIN api_source as1 ON
	as1.id = afli.source_id
LEFT JOIN api_contributor ac ON
	ac.id = as1.contributor_id
WHERE
	afm.facility_id = af_id
	AND (afm.status = 'CONFIRMED'
		OR afm.status = 'AUTOMATIC'
		OR afm.status = 'MERGED')
	AND afm.is_active
	AND as1.is_active
	AND as1.is_public
	AND afli.geocoded_point IS NOT NULL
	AND (ST_Y(afli.geocoded_point) != ST_Y(af_location)
		OR ST_X(afli.geocoded_point) != ST_X(af_location));
END;

$Body$;
