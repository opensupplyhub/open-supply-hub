CREATE OR REPLACE
FUNCTION index_parent_company_id(af_id TEXT)
RETURNS TABLE (parent_company_id INTEGER)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
SELECT
	(aef.value -> 'contributor_id')::INTEGER
FROM
	api_extendedfield aef
WHERE
	aef.facility_id = af_id
	AND aef.field_name = 'parent_company'
	AND aef.value -> 'contributor_id' IS NOT NULL;
END;

$Body$;
