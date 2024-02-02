CREATE OR REPLACE
FUNCTION index_sector(af_id TEXT)
RETURNS TABLE (sector varchar)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
	SELECT
	ttt
FROM
	(
	SELECT
		UNNEST(afli.sector) AS ttt
	FROM
		api_facilitylistitem afli
	WHERE
		afli.facility_id = af_id
		AND (afli.status = 'MATCHED'
			OR afli.status = 'CONFIRMED_MATCH')
UNION ALL
	SELECT
		UNNEST(afc.sector) AS ttt
	FROM
		api_facilityclaim afc
	WHERE
		afc.facility_id = af_id
		AND afc.status = 'APPROVED'
) AS x;
END;

$Body$;
