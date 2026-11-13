/*
Organization level: re-creates index_contributors() so that a contribution recorded
against an organization (organization_id on its source or claim) is
named after the organization instead of the member's contributor.
The contributor's id, type and admin id are kept, and organization_id
marks the entry so that no link to the member's profile is published.
*/

CREATE OR REPLACE
FUNCTION index_contributors(af_id TEXT)
RETURNS TABLE (contributor json)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
	SELECT
	json_build_object(
	'id',
	ac.id,
	'admin_id',
	ac.admin_id,
	'fl_id',
	afl.id,
	'name',
	CASE
		WHEN afl.id IS NOT NULL THEN concat(COALESCE(ao."name", ac."name"),
		' (',
		afl."name" ,
		')')
		ELSE COALESCE(ao."name", ac."name")
	END,
	'contributor_name',
	COALESCE(ao."name", ac."name"),
	'organization_id',
	ao.id,
	'contrib_type',
	ac.contrib_type,
	'should_display_associations',
	afm.is_active
	AND as1.is_active
	AND as1.is_public
	AND NOT as1.is_anonymized,
	'is_verified',
	ac.is_verified,
	'list_name',
	afl."name",
	'list_uploaded_at',
	afl.created_at,
	'last_contributed_at',
	afli.updated_at)
FROM
	api_facilitymatch afm
LEFT JOIN api_facilitylistitem afli ON
	afli.id = afm.facility_list_item_id
LEFT JOIN api_source as1 ON
	as1.id = afli.source_id
LEFT JOIN api_contributor ac ON
	ac.id = as1.contributor_id
LEFT JOIN api_organization ao ON
	ao.id = as1.organization_id
LEFT JOIN api_facilitylist afl ON
	afl.id = as1.facility_list_id
WHERE
	afm.facility_id = af_id
	AND (afm.status = 'AUTOMATIC'
		OR afm.status = 'CONFIRMED'
		OR afm.status = 'MERGED');
END;

$Body$;
