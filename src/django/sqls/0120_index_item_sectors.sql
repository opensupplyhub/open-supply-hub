/*
    Receives facility_id as text.

    Returns table:

    | item_sectors                |
    | --------------------------- |
    | json_with_item_sectors_info |
    | json_with_item_sectors_info |
*/

CREATE OR REPLACE FUNCTION index_item_sectors(af_id text)
RETURNS TABLE (item_sectors jsonb)
LANGUAGE plpgsql
AS $Body$
BEGIN
    RETURN QUERY
    SELECT jsonb_build_object(
		'sector', afli.sector,
		'created_at', afli.created_at,
		'updated_at', afli.updated_at,
		'contributor',json_build_object(
			'id', ac.id,
			'name', ac.name,
			'admin_id', ac.admin_id,
			'contrib_type', ac.contrib_type
		),
		'source', json_build_object(
			'is_active', as2.is_active,
			'is_public', as2.is_public
		),
		'facilitymatch', json_build_object(
			'is_active', CASE 
				WHEN afm.is_active IS NULL THEN false
				ELSE afm.is_active
			END
		),
		'has_active_complete_match',  (select count(*) > 0
			FROM api_facilitymatch afm2
			WHERE afm2.facility_list_item_id = afli.id
			AND afm2.is_active
			AND afm2.status IN ('AUTOMATIC', 'CONFIRMED', 'MERGED')
		)
	)::jsonb as item_sectors
	FROM api_facilitylistitem afli
	LEFT JOIN api_source as2 ON as2.id = afli.source_id
	LEFT JOIN api_facilitymatch afm ON afm.facility_list_item_id = afli.id
	LEFT JOIN api_contributor ac ON as2.contributor_id = ac.id
	WHERE (
        afli.facility_id = af_id
	    AND (
            afli.status = 'MATCHED' 
            OR afli.status = 'CONFIRMED_MATCH'
        )
    );
END;
$Body$;
