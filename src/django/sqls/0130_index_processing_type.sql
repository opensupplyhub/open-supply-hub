CREATE OR REPLACE
FUNCTION index_processing_type(af_id TEXT)
RETURNS TABLE (processing_type TEXT)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
SELECT
	raw1
FROM
	(
	SELECT
		(raw->>-1) AS raw1
	FROM
		(
		SELECT
			jsonb_array_elements(aef.value -> 'matched_values') AS raw
		FROM
			api_extendedfield aef
		WHERE
			aef.facility_id = af_id
			AND aef.field_name = 'processing_type'
			AND aef.value -> 'matched_values' IS NOT NULL
	) AS value
	WHERE
		raw ? 'PROCESSING_TYPE'
) AS value1;
END;

$Body$;
