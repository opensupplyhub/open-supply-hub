SELECT
  c.name,
  s.source_type,
  COUNT(*) AS source_count
FROM api_source s
JOIN api_contributor c ON s.contributor_id = c.id
JOIN api_user u ON u.id = c.admin_id
WHERE s.create = 't'
AND NOT EXISTS (
  SELECT 1
  FROM api_facilitylistitem ci
  JOIN api_facility cf ON cf.id = ci.facility_id
  WHERE ci.source_id = s.id
  AND cf.is_candidate = true
)
GROUP BY c.name, s.source_type
ORDER BY COUNT(*) DESC;
