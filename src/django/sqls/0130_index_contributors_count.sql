CREATE OR REPLACE
FUNCTION index_contributors_count(af_id TEXT)
RETURNS TABLE (contributor integer)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
	SELECT
	ac.id
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
			fli.source_id
		FROM
			api_facilitylistitem fli
		LEFT JOIN api_facilitymatch afm ON
			afm.facility_list_item_id = fli.id
		WHERE
			fli.facility_id = af_id
			AND afm.is_active
			AND (afm.status = 'AUTOMATIC'
				OR afm.status = 'CONFIRMED'
				OR afm.status = 'MERGED'))
		AND as1.is_active
		AND as1.is_public));
END;

$Body$;
