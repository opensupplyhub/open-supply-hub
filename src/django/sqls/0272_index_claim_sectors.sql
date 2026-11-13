/*
Organization level: re-creates index_claim_sectors() so that a contribution recorded
against an organization (organization_id on its source or claim) is
named after the organization instead of the member's contributor.
The contributor's id, type and admin id are kept, and organization_id
marks the entry so that no link to the member's profile is published.
*/

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
	COALESCE(ao.name, ac.name),
		'admin_id',
	ac.admin_id,
		'contrib_type',
	ac.contrib_type,
		'organization_id',
	ao.id
	)
)
FROM
	api_facilityclaim afc
LEFT JOIN api_contributor ac ON
	afc.contributor_id = ac.id
LEFT JOIN api_organization ao ON
	ao.id = afc.organization_id
WHERE
	afc.facility_id = af_id
	AND afc.status = 'APPROVED'
	AND afc.sector IS NOT NULL;
END;

$Body$;
