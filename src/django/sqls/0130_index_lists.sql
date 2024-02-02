CREATE OR REPLACE
FUNCTION index_lists(af_id TEXT)
RETURNS TABLE (list integer)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
	SELECT
	as2.facility_list_id
FROM
	api_facilitymatch afm
LEFT JOIN api_facilitylistitem af2 ON
	af2.id = afm.facility_list_item_id
LEFT JOIN api_source as2 ON
	as2.id = af2.source_id
	AND as2.is_active
	AND as2.is_public
WHERE
	afm.facility_id = af_id
	AND afm.is_active
	AND afm.status IN ('AUTOMATIC', 'CONFIRMED', 'MERGED')
	AND as2.facility_list_id IS NOT NULL;
END;

$Body$;
