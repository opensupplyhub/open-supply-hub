SELECT
  COALESCE(ac.name, '-') AS "Contributor name",
  COALESCE(ac.contrib_type, '-') AS "Contributor type",
  COALESCE(ac.id, 0) AS "Contributor #",
  COALESCE(TO_CHAR(MIN(l.created_at), 'Month DD, YYYY'),(TO_CHAR(MIN(s.created_at), 'Month DD, YYYY'))) AS "Date of First Upload",
  COALESCE(CURRENT_DATE - MIN(l.created_at)::date,CURRENT_DATE - MIN(s.created_at)::date) AS "Time Since First Upload (Days)",
  COALESCE(TO_CHAR(MAX(l.created_at), 'Month DD, YYYY'),TO_CHAR(MAX(s.created_at), 'Month DD, YYYY')) AS "Date of Last Upload",
  COALESCE(CURRENT_DATE - MAX(l.created_at)::date,CURRENT_DATE - MAX(s.created_at)::date) AS "Time Since Last Upload (Days)",
  COUNT(*) AS "Lifetime Uploads",
  COALESCE(
  ROUND(
        CASE
        WHEN EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM COALESCE(MIN(l.created_at), MIN(s.created_at))) = 0
        THEN COUNT(*)::numeric
        ELSE COUNT(*)::numeric / NULLIF(EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM COALESCE(MIN(l.created_at), MIN(s.created_at))), 0)::numeric
      END,
    2),
    0
  ) AS "Uploads per Year"
FROM api_contributor ac
LEFT JOIN api_source s ON s.contributor_id = ac.id
LEFT JOIN api_facilitylist l ON l.id = s.facility_list_id
LEFT JOIN api_user u ON ac.admin_id = u.id
WHERE s.create = TRUE
GROUP BY ac.id, ac.name, ac.contrib_type
ORDER BY COALESCE(MAX(l.created_at), MAX(s.created_at)) DESC;
