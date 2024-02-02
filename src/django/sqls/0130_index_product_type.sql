CREATE OR REPLACE
FUNCTION index_product_type(af_id TEXT)
RETURNS TABLE (product_type TEXT)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
SELECT
	lower(REPLACE(raw, '"', ''))
FROM
	(
	SELECT
		jsonb_array_elements(aef.value -> 'raw_values')::varchar AS raw
	FROM
		api_extendedfield aef
	WHERE
		aef.facility_id = af_id
		AND aef.field_name = 'product_type'
		AND aef.value -> 'raw_values' IS NOT NULL
) AS value;
END;

$Body$;
