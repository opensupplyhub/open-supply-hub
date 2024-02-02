CREATE OR REPLACE
FUNCTION index_contrib_types(af_id TEXT)
RETURNS TABLE (contrib_type varchar)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
	SELECT
	ac.contrib_type
FROM
	api_contributor ac
WHERE
	(ac.id IN 
		(
	SELECT
		as1.contributor_id
	FROM
		api_source as1
	WHERE
		as1.id IN 
			(
		SELECT
			afli.source_id
		FROM
			api_facilitylistitem afli
		WHERE
			afli.id IN 
				(
			SELECT
				afm.facility_list_item_id
			FROM
				api_facilitymatch afm
			WHERE
				afm.is_active)
			AND afli.facility_id = af_id)
		AND as1.is_active));
END;

$Body$;
