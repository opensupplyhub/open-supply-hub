-- List the ISO country codes where facilities are located sorted by the year
-- and month that the country first appeared.

SELECT
  country_code,
  to_char(min(created_at), 'YYYY-MM') AS created_at
  FROM api_facility
 WHERE is_candidate = false
GROUP BY country_code
ORDER BY created_at DESC;
