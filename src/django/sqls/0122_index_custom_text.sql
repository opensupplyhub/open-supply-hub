CREATE OR REPLACE FUNCTION index_custom_text(af_id text)
RETURNS TABLE (custom_text text)
LANGUAGE plpgsql
AS $Body$
BEGIN
    RETURN QUERY
    SELECT jsonb_array_elements_text(aflif.value)::text AS custom_text
	FROM api_facilitylistitemfield aflif
	LEFT JOIN api_facilitylistitem afli ON aflif.facility_list_item_id = afli.id
    WHERE afli.facility_id = af_id;
END;
$Body$;
