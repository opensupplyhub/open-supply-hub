CREATE OR REPLACE
FUNCTION index_parent_company_name(af_id TEXT)
RETURNS TABLE (parent_company_name TEXT)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
SELECT
	REPLACE(COALESCE(aef.value -> 'contributor_name',
	aef.value -> 'name')::varchar,
	'"',
	'')
FROM
	api_extendedfield aef
WHERE
	aef.facility_id = af_id
	AND aef.field_name = 'parent_company'
	AND (aef.value -> 'contributor_name' IS NOT NULL
		OR aef.value -> 'name' IS NOT NULL);
END;

$Body$;
