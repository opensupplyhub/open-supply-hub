CREATE OR REPLACE
FUNCTION index_facility_type(af_id TEXT)
RETURNS TABLE (facility_type TEXT)
LANGUAGE plpgsql
AS $Body$
DECLARE
	matched_values_key CONSTANT TEXT := 'matched_values';
	raw_values_key CONSTANT TEXT := 'raw_values';
	-- Placeholders contributors upload instead of leaving the field empty,
	-- plus legacy production types that are not part of the taxonomy. Kept in
	-- sync with the exclusions of the api_facility_processing_value table.
	excluded_values CONSTANT TEXT[] := ARRAY[
		'null', 'none', 'n/a', 'na', 'unknown', 'other', '-',
		'denim services', 'boarding'
	];
BEGIN
	RETURN QUERY
/*One pass over the ExtendedFields of the location. Every matched value
contributes either the standardized taxonomy value at index 2 or, when that
slot is null, the raw value the contributor submitted in its place. Reading
both from the same scan keeps this function on the write path of every
ExtendedField change: it runs from perform_extended_field_indexing for each
insert, update and delete.*/
SELECT DISTINCT
	raw1
FROM
	(
	SELECT
		CASE
			WHEN matched.matched->>2 IS NOT NULL THEN matched.matched->>2
			ELSE btrim(raw_values.raw_array[matched.idx])
		END AS raw1
	FROM
		(
		SELECT
			ae.value
		FROM
			api_extendedfield ae
		WHERE
			ae.facility_id = af_id
			AND ae.field_name = 'facility_type'
			AND ae.value -> matched_values_key IS NOT NULL
			-- Only ExtendedFields visible on the location profile, matching
			-- index_extended_fields().
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
						afm.facility_list_item_id
					FROM
						api_facilitymatch afm
					JOIN api_facilitylistitem afli
						ON afli.id = afm.facility_list_item_id
					JOIN api_source source
						ON source.id = afli.source_id
					WHERE
						afm.facility_id = af_id
						AND afm.status IN (
							'AUTOMATIC', 'CONFIRMED', 'MERGED'
						)
						AND afm.is_active = TRUE
						AND afli.facility_id = af_id
						AND source.is_active = TRUE
				)
			)
	) AS visible_fields
	/*Built once per ExtendedField rather than once per matched value, and
	subscripted below by ordinality. Expanding it into rows instead would pair
	the two arrays through a cartesian product filtered down to the positional
	matches. Mirrors the string vs array handling of process_raw_values(); an
	absent raw_values yields an empty array, whose every subscript is null.*/
	CROSS JOIN LATERAL (
		SELECT
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
							jsonb_array_elements_text(
								visible_fields.value -> raw_values_key
							)
					)
			END AS raw_array
	) AS raw_values
	CROSS JOIN LATERAL jsonb_array_elements(visible_fields.value -> matched_values_key)
		WITH ORDINALITY AS matched(matched, idx)
) AS value1
WHERE
	raw1 IS NOT NULL
	AND btrim(raw1) <> ''
	-- Placeholders reach the index through both branches: 'null' arrives as a
	-- standardized matched value, the rest mostly as unmatched raw values.
	AND lower(btrim(raw1)) <> ALL (excluded_values);
END;

$Body$;
