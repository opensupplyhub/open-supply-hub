-- Count the number of API requests made by each user for all the time
-- Count the number of API requests for the previous month
-- Count the number of API requests for the current month
-- Exclude users with openapparel.org or azavea.com email addresses.
-- Count only successful calls

select email, count(*) as request_call_count,
  SUM(CASE WHEN to_char(l.created_at, 'YYYY-MM') >= to_char(date_trunc('month', now() - interval '1' month), 'YYYY-MM')
  and to_char(l.created_at, 'YYYY-MM') <  to_char(date_trunc('month', now()), 'YYYY-MM') THEN 1 ELSE 0 END) AS prev_month,
  SUM(CASE WHEN to_char(l.created_at, 'YYYY-MM-dd') >= to_char(date_trunc('month', now()), 'YYYY-MM-dd')
  and to_char(l.created_at, 'YYYY-MM-dd') <  to_char(now(), 'YYYY-MM-dd') THEN 1 ELSE 0 END) AS curr_month
from api_requestlog l
JOIN api_user u ON l.user_id = u.id
where NOT u.email LIKE '%openapparel.org%'
AND NOT u.email LIKE '%opensupplyhub.org%'
AND NOT u.email LIKE '%azavea.com%'
and l.response_code = 200 or l.response_code = 299
GROUP BY email
ORDER BY email;
