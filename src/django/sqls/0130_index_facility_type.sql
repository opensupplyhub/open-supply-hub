CREATE OR REPLACE
FUNCTION index_facility_type(af_id TEXT)
RETURNS TABLE (facility_type TEXT)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
SELECT
	raw1
FROM
	(
	SELECT
		(raw->>2) AS raw1
	FROM
		(
		SELECT
			jsonb_array_elements(aef.value -> 'matched_values') AS raw
		FROM
			api_extendedfield aef
		WHERE
			aef.facility_id = af_id
			AND aef.field_name = 'facility_type'
			AND aef.value -> 'matched_values' IS NOT NULL
	) AS value
	WHERE
		raw->>2 IS NOT NULL
) AS value1;
END;

$Body$;
