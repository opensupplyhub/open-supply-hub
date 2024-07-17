CREATE OR REPLACE
FUNCTION index_number_of_workers(af_id TEXT)
RETURNS TABLE (number TEXT)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
SELECT
    now_result
FROM
    (
        SELECT
            UNNEST(format_numbers_of_workers(
                (elem->'value'->>'max')::int,
                (elem->'value'->>'min')::int
            )) AS now_result
        FROM
            (
                SELECT 
                    UNNEST(COALESCE(array_agg(extended_field), '{}')) AS elem
                FROM 
                    index_extended_fields(af_id)
                WHERE
                    extended_field->>'field_name' = 'number_of_workers'
            ) AS x
    ) AS y;

END;

$Body$;
