CREATE OR REPLACE
FUNCTION index_processing_type(af_id TEXT)
RETURNS TABLE (processing_type TEXT)
LANGUAGE plpgsql
AS $Body$
DECLARE
	matched_values_key CONSTANT TEXT := 'matched_values';
	raw_values_key CONSTANT TEXT := 'raw_values';
BEGIN
	RETURN QUERY
SELECT
	raw1
FROM
	(
	SELECT
		(raw->>3) AS raw1
	FROM
		(
		SELECT
			jsonb_array_elements(aef.value -> matched_values_key) AS raw
		FROM
			api_extendedfield aef
		WHERE
			aef.facility_id = af_id
			AND aef.field_name = 'processing_type'
			AND aef.value -> matched_values_key IS NOT NULL
	) AS standardized
	WHERE
		(raw->>3) IS NOT NULL

	UNION

	SELECT
		btrim(raw_vals.raw_value) AS raw1
	FROM
		(
		SELECT
			ae.value
		FROM
			api_extendedfield ae
		WHERE
			ae.facility_id = af_id
			AND ae.field_name = 'processing_type'
			AND ae.value -> matched_values_key IS NOT NULL
			AND ae.value -> raw_values_key IS NOT NULL
			AND (
				EXISTS (
					SELECT
						1
					FROM
						api_facilityclaim af2
					WHERE
						af2.id = ae.facility_claim_id
						AND af2.status = 'APPROVED'
				)
				OR ae.facility_list_item_id IN (
					SELECT
						am.facility_list_item_id
					FROM
						(
						SELECT
							afm.facility_list_item_id
						FROM
							api_facilitymatch afm
						WHERE
							afm.facility_id = af_id
							AND afm.status IN ('AUTOMATIC', 'CONFIRMED', 'MERGED')
							AND afm.is_active = TRUE
					) AS am
					WHERE
						am.facility_list_item_id IN (
						SELECT
							afli.id
						FROM
							api_facilitylistitem afli
						WHERE
							afli.facility_id = af_id
							AND afli.source_id IN (
							SELECT
								as2.id
							FROM
								api_source as2
							WHERE
								as2.is_active = TRUE
						)
					)
				)
			)
	) AS visible_fields
	CROSS JOIN LATERAL jsonb_array_elements(visible_fields.value -> matched_values_key)
		WITH ORDINALITY AS matched(matched, idx)
	CROSS JOIN LATERAL unnest(
		CASE
			WHEN jsonb_typeof(visible_fields.value -> raw_values_key) = 'string' THEN
				CASE
					WHEN (visible_fields.value ->> raw_values_key) LIKE '%|%' THEN
						string_to_array(visible_fields.value ->> raw_values_key, '|')
					ELSE
						ARRAY[visible_fields.value ->> raw_values_key]
				END
			ELSE
				ARRAY(
					SELECT
						jsonb_array_elements_text(visible_fields.value -> raw_values_key)
				)
		END
	) WITH ORDINALITY AS raw_vals(raw_value, raw_idx)
	WHERE
		matched.idx = raw_vals.raw_idx
		AND matched.matched->>3 IS NULL
		AND raw_vals.raw_value IS NOT NULL
		AND btrim(raw_vals.raw_value) <> ''
		AND lower(btrim(raw_vals.raw_value)) NOT IN (
			'other', 'denim services', 'boarding'
		)
) AS value1
WHERE
	raw1 IS NOT NULL;
END;

$Body$;
