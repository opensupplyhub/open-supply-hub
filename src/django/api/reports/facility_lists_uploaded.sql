-- Total # of list uploads in a given month (these are uploads that come from external contributors, NOT OS Hub team members)
-- # of public list uploads in a given month (these are uploads that come from OS Hub team members AND have “[Public List]” in the contributor name)
-- Total facility listItems uploaded in a given month
-- # of Facilities from Public Lists
-- Total Facilities w/ status = new facility
-- # Public List Facilities w/ status = new facility
-- Data is ordered from most recent to oldest
SELECT
  to_char(l.created_at, 'YYYY-MM') AS month,
  COUNT(*) AS total_lists_uploaded,
  COUNT(u.email) filter (where u.email::text LIKE '%openapparel.org%'
             OR u.email::text LIKE '%opensupplyhub.org%') as "# Public Lists"
FROM api_facilitylist l
JOIN api_source s ON s.facility_list_id = l.id
JOIN api_contributor c ON s.contributor_id = c.id
JOIN api_user u ON u.id = c.admin_id
WHERE to_char(l.created_at, 'YYYY-MM-DD') != to_char(now(), 'YYYY-MM-DD')
GROUP BY to_char(l.created_at, 'YYYY-MM')
ORDER BY to_char(l.created_at, 'YYYY-MM') DESC;

-- Count the number of facility list CSV rows uploaded each month.

-- SELECT
--   to_char(i.created_at, 'YYYY-MM') AS month,
--   CASE WHEN (u.email LIKE '%openapparel.org%'
--              OR u.email LIKE '%opensupplyhub.org%')
--        THEN 'y' ELSE 'n' END AS is_public_list,
--   COUNT(*) AS item_count
--   FROM api_facilitylistitem i
--          JOIN api_source s on i.source_id = s.id
--          JOIN api_contributor c ON s.contributor_id = c.id
--          JOIN api_user u ON u.id = c.admin_id
--  WHERE to_char(i.created_at, 'YYYY-MM') != to_char(now(), 'YYYY-MM')
--  AND s.create = true
--  GROUP BY to_char(i.created_at, 'YYYY-MM'), is_public_list
--  ORDER BY to_char(i.created_at, 'YYYY-MM'), is_public_list;
