/*
Organization level: re-creates index_contributors_count() so that
contributors whose contributions were recorded against the same
organization count once. The production location is shown as contributed
by the organization, so its members are not counted separately.

Returns one row per public contributor, as before, except that all the
contributors of one organization are represented by a single row.
*/

CREATE OR REPLACE
FUNCTION index_contributors_count(af_id TEXT)
RETURNS TABLE (contributor integer)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
	SELECT
	min(as1.contributor_id)
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
	AND as1.is_public
	AND as1.contributor_id IS NOT NULL
GROUP BY
	CASE
		WHEN as1.organization_id IS NOT NULL
		THEN 'organization-' || as1.organization_id
		ELSE 'contributor-' || as1.contributor_id
	END;
END;

$Body$;
