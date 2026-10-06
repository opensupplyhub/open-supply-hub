SELECT
  month,
  source_type,
  COUNT(*) AS contributor_count
FROM (
  SELECT DISTINCT
    to_char(s.created_at, 'YYYY-MM') AS month,
    s.source_type,
    c.id
  FROM api_source s
  JOIN api_contributor c ON s.contributor_id = c.id
  JOIN api_user u ON u.id = c.admin_id
  WHERE to_char(s.created_at, 'YYYY-MM') != to_char(now(), 'YYYY-MM')
  AND s.create = true
  AND (u.email LIKE '%openapparel.org%' OR u.email LIKE '%opensupplyhub.org%')
  AND NOT EXISTS (
    SELECT 1
    FROM api_facilitylistitem ci
    JOIN api_facility cf ON cf.id = ci.facility_id
    WHERE ci.source_id = s.id
    AND cf.is_candidate = true
  )
  ORDER BY to_char(s.created_at, 'YYYY-MM'), c.id
) q
GROUP BY month, source_type
ORDER BY month, source_type;
