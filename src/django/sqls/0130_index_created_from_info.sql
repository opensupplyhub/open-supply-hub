CREATE OR REPLACE
FUNCTION index_created_from_info(af_created_from_id integer)
RETURNS TABLE (info json)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
SELECT
	json_build_object(
'should_display_associations',
	as1.is_active
	AND as1.is_public,
	'created_at',
	afli.created_at,
	'contributor_name',
	ac.name,
	'contrib_type',
	ac.contrib_type
)
FROM
	api_facilitylistitem afli
LEFT JOIN api_source as1 ON
	as1.id = afli.source_id
LEFT JOIN api_contributor ac ON
	ac.id = as1.contributor_id
WHERE
	afli.id = af_created_from_id
LIMIT 1;
END;

$Body$;
