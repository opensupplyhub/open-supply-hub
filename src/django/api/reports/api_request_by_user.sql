-- Count the number of successful API requests made by each user in each month up to the current date.
-- Count the number of unsuccessful API requests made by each user in each month up to the current date.
-- Exclude users with openapparel.org or azavea.com email addresses.

SELECT
  to_char(l.created_at, 'YYYY-MM') AS month,
  email,
  COUNT(l.response_code) filter (where l.response_code::text LIKE '2%') as successful_api_request_count,
  COUNT(l.response_code) filter (where l.response_code::text NOT LIKE '2%') as unsuccessful_api_request_count
FROM api_requestlog l
JOIN api_user u ON l.user_id = u.id
WHERE to_char(l.created_at, 'YYYY-MM-dd') < to_char(now(), 'YYYY-MM-dd')
AND NOT u.email LIKE '%openapparel.org%'
AND NOT u.email LIKE '%opensupplyhub.org%'
AND NOT u.email LIKE '%azavea.com%'
GROUP BY to_char(l.created_at, 'YYYY-MM'), email
ORDER BY to_char(l.created_at, 'YYYY-MM'), email;
