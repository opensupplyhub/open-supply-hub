SELECT
  COALESCE(ac.name, '-') AS "Contributor name",
  COALESCE(ac.contrib_type, '-') AS "Contributor type",
  COALESCE(ac.id, 0) AS "Contributor #",
  COALESCE(TO_CHAR(min(l.created_at), 'Month DD, YYYY'),(TO_CHAR(min(s.created_at), 'Month DD, YYYY'))) AS "Date of First Upload",
  COALESCE(CURRENT_DATE - min(l.created_at)::date,CURRENT_DATE - min(s.created_at)::date) AS "Time Since First Upload (Days)",
  COALESCE(TO_CHAR(max(l.created_at), 'Month DD, YYYY'),TO_CHAR(max(s.created_at), 'Month DD, YYYY')) AS "Date of Last Upload",
  COALESCE(CURRENT_DATE - max(l.created_at)::date,CURRENT_DATE - max(s.created_at)::date) AS "Time Since Last Upload (Days)",
  COUNT(*) AS "Lifetime Uploads",
  COALESCE(ROUND(COUNT(*) / ROUND((CURRENT_DATE - min(l.created_at)::date) / 365.25, 2), 2),ROUND(COUNT(*) / ROUND((CURRENT_DATE - min(s.created_at)::date) / 365.25, 2), 2))  AS "Uploads per Year"
FROM api_contributor ac
LEFT JOIN api_source s ON s.contributor_id = ac.id
LEFT JOIN api_facilitylist l on l.id = s.facility_list_id
LEFT JOIN api_facilitylistitem i ON i.source_id = s.id
LEFT JOIN api_user u ON ac.admin_id = u.id
where ac.id = s.contributor_id
GROUP BY ac.id, ac.name, ac.contrib_type
ORDER BY COALESCE(max(l.created_at), max(s.created_at)) DESC;
