CREATE OR REPLACE
FUNCTION index_claim_sectors(af_id TEXT)
RETURNS TABLE (claim_sector json)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
SELECT
	json_build_object(
	'sector',
	afc.sector,
	'created_at',
	afc.created_at,
	'updated_at',
	afc.updated_at,
	'contributor',
	json_build_object(
		'id',
	ac.id,
		'name',
	ac.name,
		'admin_id',
	ac.admin_id,
		'contrib_type',
	ac.contrib_type
	)
)
FROM
	api_facilityclaim afc
LEFT JOIN api_contributor ac ON
	afc.contributor_id = ac.id
WHERE
	afc.facility_id = af_id
	AND afc.status = 'APPROVED'
	AND afc.sector IS NOT NULL;
END;

$Body$;
