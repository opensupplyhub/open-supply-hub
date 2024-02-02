CREATE OR REPLACE
FUNCTION index_native_language_name(af_id TEXT)
RETURNS TABLE (native_language_name TEXT)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
SELECT
	trim(BOTH '"' FROM aef.value::TEXT)
FROM
	api_extendedfield aef
WHERE
	aef.facility_id = af_id
	AND aef.field_name = 'native_language_name';
END;

$Body$;
