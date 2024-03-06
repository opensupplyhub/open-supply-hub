CREATE OR REPLACE
FUNCTION index_activity_reports_info(af_id TEXT,
af_name TEXT)
RETURNS TABLE (activity_report_info json)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
SELECT
	raw
FROM
	(
	SELECT
		json_build_object(
        'facility',
		afar.facility_id,
		'reported_by_contributor',
		ac.name,
		'closure_state',
		afar.closure_state,
		'approved_at',
		afar.approved_at,
		'status_change_reason',
		afar.status_change_reason,
		'status',
		afar.status,
		'status_change_by',
		ac1.name,
		'status_change_date',
		afar.status_change_date,
		'created_at',
		afar.created_at,
		'updated_at',
		afar.updated_at,
		'id',
		afar.id,
		'reason_for_report',
		afar.reason_for_report,
		'facility_name',
		af_name
) AS raw
	FROM
		api_facilityactivityreport afar
	LEFT JOIN api_contributor ac ON
		ac.id = afar.reported_by_contributor_id
	LEFT JOIN api_contributor ac1 ON
		ac1.admin_id = afar.status_change_by_id
	WHERE
		afar.facility_id = af_id
		AND (afar.status = 'PENDING'
			OR afar.status = 'CONFIRMED')
	ORDER BY
		afar.created_at DESC) AS sqlresult;
END;

$Body$;
