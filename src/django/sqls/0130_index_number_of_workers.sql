CREATE OR REPLACE
FUNCTION index_number_of_workers(af_id TEXT)
RETURNS TABLE (number TEXT)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
SELECT
	sss
FROM
	(
	SELECT
		UNNEST(format_numbers_of_workers((aef.value->'max')::int,
		(aef.value->'min')::int)) AS sss
	FROM
		api_extendedfield aef
	WHERE
		aef.facility_id = af_id
		AND aef.field_name = 'number_of_workers') AS x;
END;

$Body$;
