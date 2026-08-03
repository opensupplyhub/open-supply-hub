/*
    Receives facility_id as text.

    Returns table:

    | sector  |
    | ------- |
    | varchar |

    Mirrors the sector data shown on the location profile. The profile
    (regroup_items_for_sector_field / regroup_claims_for_sector_field in
    api/serializers/facility/utils.py) displays, for each contributor, the
    sectors of a single list item - preferring items from active sources,
    then ordering by facility match activity and recency - plus the sectors
    of the latest approved claim per contributor. Only those sectors may be
    searchable. See OSDEV-992.
*/

CREATE OR REPLACE
FUNCTION index_sector(af_id TEXT)
RETURNS TABLE (sector varchar)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
	SELECT
		UNNEST(items.sector)
	FROM
		(
		SELECT DISTINCT ON (ac.id)
			afli.sector
		FROM
			api_facilitylistitem afli
		LEFT JOIN api_source as2 ON as2.id = afli.source_id
		LEFT JOIN api_facilitymatch afm ON afm.facility_list_item_id = afli.id
		LEFT JOIN api_contributor ac ON as2.contributor_id = ac.id
		WHERE
			afli.facility_id = af_id
			AND (afli.status = 'MATCHED'
				OR afli.status = 'CONFIRMED_MATCH')
		ORDER BY
			ac.id,
			COALESCE(as2.is_active, FALSE) DESC,
			COALESCE(afm.is_active, FALSE) ASC,
			afli.updated_at DESC
	) AS items
UNION ALL
	SELECT
		UNNEST(claims.sector)
	FROM
		(
		SELECT DISTINCT ON (afc.contributor_id)
			afc.sector
		FROM
			api_facilityclaim afc
		WHERE
			afc.facility_id = af_id
			AND afc.status = 'APPROVED'
			AND afc.sector IS NOT NULL
		ORDER BY
			afc.contributor_id,
			afc.updated_at DESC
	) AS claims;
END;

$Body$;
