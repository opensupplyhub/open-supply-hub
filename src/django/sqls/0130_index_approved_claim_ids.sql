CREATE OR REPLACE
FUNCTION index_approved_claim_ids(af_id TEXT)
RETURNS TABLE (approved_claim_id integer)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
	SELECT
	afc.id
FROM
	api_facilityclaim afc
WHERE
	afc.facility_id = af_id
	AND afc.status = 'APPROVED';
END;

$Body$;
