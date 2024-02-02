CREATE OR REPLACE
FUNCTION index_facility_names(af_id TEXT)
RETURNS TABLE (facility_name json)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
SELECT
	json_build_object(
	'name',
	af2.name,
	'updated_at',
	af2.updated_at,
	'created_at',
	af2.created_at,
	'contributor',
	json_build_object(
		'id',
	ac.id,
		'name',
	ac.name,
		'contrib_type',
	ac.contrib_type,
		'admin_id',
	ac.admin_id
	)
)
FROM
	api_facilitymatch fm_item
LEFT JOIN api_facilitylistitem af2 ON
	af2.id = fm_item.facility_list_item_id
LEFT JOIN api_source as2 ON
	as2.id = af2.source_id
LEFT JOIN api_contributor ac ON
	ac.id = as2.contributor_id
WHERE
	(fm_item.status = 'AUTOMATIC'
		OR fm_item.status = 'CONFIRMED'
		OR fm_item.status = 'MERGED')
	AND fm_item.facility_id = af_id
	AND fm_item.is_active
	AND as2.is_active
	AND as2.is_public;
END;

$Body$;
