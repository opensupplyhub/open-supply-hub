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
		WHEN afl.id IS NOT NULL THEN concat(ac."name",
		' (',
		afl."name" ,
		')')
		ELSE ac."name"
	END,
	'contributor_name',
	ac."name",
	'contrib_type',
	ac.contrib_type,
	'should_display_associations',
	afm.is_active
	AND as1.is_active
	AND as1.is_public,
	'is_verified',
	ac.is_verified,
	'list_name',
	afl."name")
FROM
	api_facilitymatch afm
LEFT JOIN api_facilitylistitem afli ON
	afli.id = afm.facility_list_item_id
LEFT JOIN api_source as1 ON
	as1.id = afli.source_id
LEFT JOIN api_contributor ac ON
	ac.id = as1.contributor_id
LEFT JOIN api_facilitylist afl ON
	afl.id = as1.facility_list_id
WHERE
	afm.facility_id = af_id
	AND (afm.status = 'AUTOMATIC'
		OR afm.status = 'CONFIRMED'
		OR afm.status = 'MERGED');
END;

$Body$;
