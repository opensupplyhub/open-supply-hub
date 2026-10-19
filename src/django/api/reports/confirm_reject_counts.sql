-- Count the number of potential mand and confirmed/rejected list itemss created each month

SELECT
  to_char(li.created_at, 'YYYY-MM') AS month,
  SUM(CASE WHEN li.status = 'POTENTIAL_MATCH' THEN 1 ELSE 0 END) as open_count,
  SUM(CASE WHEN li.status = 'CONFIRMED_MATCH' THEN 1 ELSE 0 END) as confirmed_rejected_count
  FROM api_facilitylistitem li
 WHERE NOT EXISTS (
   SELECT 1
   FROM api_facility f
   WHERE f.id = li.facility_id
   AND f.is_candidate = true
 )
 GROUP BY to_char(li.created_at, 'YYYY-MM')
 ORDER BY to_char(li.created_at, 'YYYY-MM');
