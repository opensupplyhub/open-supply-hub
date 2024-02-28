-- Count the number of API requests made by each user in each month up to the current date.
-- Exclude users with openapparel.org or azavea.com email addresses.
-- Count only successful calls

SELECT
  to_char(l.created_at, 'YYYY-MM') AS month,
  email,
  COUNT(*) AS api_request_count
FROM api_requestlog l
JOIN api_user u ON l.user_id = u.id
WHERE to_char(l.created_at, 'YYYY-MM-dd') < to_char(now(), 'YYYY-MM-dd')
AND NOT u.email LIKE '%openapparel.org%'
AND NOT u.email LIKE '%opensupplyhub.org%'
AND NOT u.email LIKE '%azavea.com%'
AND l.response_code = 200
OR l.response_code = 299
GROUP BY to_char(l.created_at, 'YYYY-MM'), email
ORDER BY to_char(l.created_at, 'YYYY-MM'), email;
