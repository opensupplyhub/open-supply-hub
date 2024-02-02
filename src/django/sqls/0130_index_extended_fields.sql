CREATE OR REPLACE
FUNCTION index_extended_fields(af_id TEXT)
RETURNS TABLE (extended_field json)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
SELECT
	json_build_object(
	'id',
	base_query.id,
	'is_verified',
	base_query.is_verified,
	'value',
	base_query.value,
	'created_at',
	base_query.created_at,
	'updated_at',
	base_query.updated_at,
	'facility_list_item_id',
	base_query.facility_list_item_id,
	'contributor',
	(
	SELECT
		json_build_object(
		'id',
		ac.id,
		'name',
		ac.name,
		'contrib_type',
		ac.contrib_type,
		'admin_id',
		ac.admin_id,
		'is_verified',
		ac.is_verified
		)
	FROM
		api_contributor ac
	WHERE
		ac.id = base_query.contributor_id),
	'value_count',
	(
	SELECT
		count(ae.id)
	FROM
		api_extendedfield ae
	LEFT JOIN api_facilitylistitem af4 ON
		af4.id = ae.facility_list_item_id
	LEFT JOIN api_source as3 ON
		as3.id = af4.source_id
	WHERE
		ae.facility_id = base_query.facility_id
		AND ae.field_name = base_query.field_name
		AND ae.value = base_query.value
		AND (
			ae.facility_list_item_id IS NULL
			OR
			as3.is_active
		)
	),
	'field_name',
	base_query.field_name,
	'should_display_association',
	(CASE
		WHEN base_query.facility_list_item_id IS NOT NULL
		THEN EXISTS(
		SELECT
			1
		FROM
			api_facilitymatch af3
		LEFT JOIN api_facilitylistitem af5 ON
			af3.facility_list_item_id = af5.id
		LEFT JOIN api_source as4 ON
			af5.source_id = as4.id
		WHERE
			af3.facility_list_item_id = base_query.facility_list_item_id
			AND af3.is_active = TRUE
			AND as4.is_active = TRUE
			AND as4.is_public = TRUE
		)
		ELSE TRUE
	END)
	
)
FROM
	(
	SELECT
		*,
		EXISTS
    (
		SELECT
			af2.status
		FROM
			api_facilityclaim af2
		WHERE
			af2.id = ae.facility_claim_id
			AND af2.status = 'APPROVED'
    ) AS has_active_claim,
		(ae.facility_list_item_id IN (
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
    )) AS is_active
	FROM
		api_extendedfield ae
	WHERE
		ae.facility_id = af_id
) AS base_query
WHERE
	has_active_claim = TRUE
	OR is_active = TRUE;
END;

$Body$;
