/*
    Receives facility_id as text.

    Returns table:

    | custom_field_info         |
    | ------------------------- |
    | json_with_extended_fields |
    | json_with_extended_fields |
*/

CREATE OR REPLACE FUNCTION index_custom_field_info(af_id text)
RETURNS TABLE (custom_field_info jsonb)
LANGUAGE plpgsql
AS $Body$
BEGIN
    RETURN QUERY
    SELECT jsonb_build_object(
        'contributor_id', ac.id,
        'raw_data', afli.raw_data,
        'source_type', as1.source_type,
        'list_header', afl.header,
        'embed_level', ac.embed_level,
        'embed_display_field', (
            SELECT array_agg(aef.display_name)
            FROM api_embedfield aef
            WHERE aef.embed_config_id = ac.embed_config_id AND aef.visible
        ),
        'embed_field', (
            SELECT array_agg(aef.column_name)
            FROM api_embedfield aef
            WHERE aef.embed_config_id = ac.embed_config_id AND aef.visible
        )
    )::jsonb AS custom_field_info
    FROM api_facilitylistitem afli
    LEFT JOIN api_source as1 ON as1.id = afli.source_id
    LEFT JOIN api_contributor ac ON ac.id = as1.contributor_id
    LEFT JOIN api_facilitylist afl ON afl.id = as1.facility_list_id
    LEFT JOIN api_facilitymatch afm ON afm.facility_list_item_id = afli.id
    WHERE as1.is_active AND afm.is_active AND afli.facility_id = af_id
    GROUP BY ac.id, afli.raw_data, as1.source_type, afli.created_at, afl.header
    ORDER BY afli.created_at DESC;
END;
$Body$;
