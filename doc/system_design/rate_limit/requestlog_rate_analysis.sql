-- =====================================================================
-- OSDEV-2138: API traffic analysis from Django's api_requestlog (Postgres)
--
-- What this table contains:
--   * One row per TOKEN-authenticated request that reached Django
--     (RequestLogMiddleware), including requests Django throttled (429).
--   * NOT included: web-app / session traffic, anonymous traffic, and
--     anything CloudFront served from cache. So these numbers are a
--     LOWER BOUND of what WAF would count for each customer.
--   * Keyed by user, not IP. WAF counts per IP, so one user spread over
--     several IPs looks smaller to WAF, and several users behind one IP
--     look bigger. Use the Athena queries for the per-IP view.
--
-- "peak_5min" is a TRAILING 5-minute window evaluated every minute,
-- which is how a WAF rate rule with evaluation_window_sec = 300 sees
-- traffic (fixed 5-minute buckets would under-count bursts that cross
-- a bucket edge).
--
-- Run on a read replica if possible. created_at is indexed, so keep the
-- date filter; widen or narrow '28 days' as needed.
-- =====================================================================


-- ---------------------------------------------------------------------
-- Q1. Per-user observed peaks vs configured Django limits
--     One row per user with token traffic in the window.
--     *_per_5min columns convert the configured rate into WAF terms.
-- ---------------------------------------------------------------------
WITH per_minute AS (
    SELECT user_id,
           date_trunc('minute', created_at)                  AS minute,
           count(*)                                          AS n,
           count(*) FILTER (WHERE response_code = 429)       AS n_429
    FROM api_requestlog
    WHERE created_at >= now() - interval '28 days'
    GROUP BY 1, 2
),
-- each minute's count contributes to the 5 trailing windows that end at
-- minute, minute+1 ... minute+4
rolling AS (
    SELECT user_id,
           minute + make_interval(mins => k) AS window_end,
           sum(n)                            AS n_5min
    FROM per_minute
    CROSS JOIN generate_series(0, 4) AS k
    GROUP BY 1, 2
),
per_day AS (
    SELECT user_id, date_trunc('day', minute) AS day, sum(n) AS n
    FROM per_minute
    GROUP BY 1, 2
),
minute_stats AS (
    SELECT user_id, sum(n) AS total_requests, sum(n_429) AS total_429,
           max(n) AS peak_1min
    FROM per_minute GROUP BY 1
),
window_stats AS (
    SELECT user_id, max(n_5min) AS peak_5min FROM rolling GROUP BY 1
),
day_stats AS (
    SELECT user_id, max(n) AS peak_day, count(*) AS active_days
    FROM per_day GROUP BY 1
),
stats AS (
    SELECT m.user_id, m.total_requests, m.total_429, m.peak_1min,
           w.peak_5min, d.peak_day, d.active_days
    FROM minute_stats m
    JOIN window_stats w USING (user_id)
    JOIN day_stats d    USING (user_id)
)
SELECT u.id                                   AS user_id,
       u.email,
       c.name                                 AS contributor,
       u.burst_rate,
       u.sustained_rate,
       u.data_upload_rate,
       round(split_part(u.burst_rate, '/', 1)::numeric * 300 /
             CASE split_part(u.burst_rate, '/', 2)
                  WHEN 'second' THEN 1 WHEN 'minute' THEN 60
                  WHEN 'hour' THEN 3600 WHEN 'day' THEN 86400 END)
                                              AS burst_limit_per_5min,
       round(split_part(u.sustained_rate, '/', 1)::numeric * 300 /
             CASE split_part(u.sustained_rate, '/', 2)
                  WHEN 'second' THEN 1 WHEN 'minute' THEN 60
                  WHEN 'hour' THEN 3600 WHEN 'day' THEN 86400 END, 1)
                                              AS sustained_avg_per_5min,
       s.total_requests,
       s.active_days,
       s.peak_1min,
       s.peak_5min,
       s.peak_day,
       s.total_429                            AS throttled_by_django
FROM stats s
JOIN api_user u             ON u.id = s.user_id
LEFT JOIN api_contributor c ON c.admin_id = u.id
ORDER BY s.peak_5min DESC;


-- ---------------------------------------------------------------------
-- Q2. Distribution of per-user 5-minute peaks + how many API users a
--     per-IP limit at each threshold could touch (if each user used a
--     single IP). Pick a threshold that leaves almost everyone untouched
--     except the users you plan to exempt.
-- ---------------------------------------------------------------------
WITH per_minute AS (
    SELECT user_id, date_trunc('minute', created_at) AS minute, count(*) AS n
    FROM api_requestlog
    WHERE created_at >= now() - interval '28 days'
    GROUP BY 1, 2
),
rolling AS (
    SELECT user_id, minute + make_interval(mins => k) AS window_end, sum(n) AS n_5min
    FROM per_minute
    CROSS JOIN generate_series(0, 4) AS k
    GROUP BY 1, 2
),
per_user AS (
    SELECT user_id, max(n_5min) AS peak_5min FROM rolling GROUP BY 1
)
SELECT count(*)                                                  AS api_users,
       percentile_disc(0.50) WITHIN GROUP (ORDER BY peak_5min)   AS p50,
       percentile_disc(0.90) WITHIN GROUP (ORDER BY peak_5min)   AS p90,
       percentile_disc(0.99) WITHIN GROUP (ORDER BY peak_5min)   AS p99,
       max(peak_5min)                                            AS max,
       count(*) FILTER (WHERE peak_5min > 1000)                  AS over_1k,
       count(*) FILTER (WHERE peak_5min > 2000)                  AS over_2k,
       count(*) FILTER (WHERE peak_5min > 5000)                  AS over_5k,
       count(*) FILTER (WHERE peak_5min > 10000)                 AS over_10k,
       count(*) FILTER (WHERE peak_5min > 20000)                 AS over_20k,
       count(*) FILTER (WHERE peak_5min > 50000)                 AS over_50k
FROM per_user;


-- ---------------------------------------------------------------------
-- Q3. Limit tiers: who is configured with what, and do they use it?
--     Covers ALL users with non-default limits (also those with no
--     traffic in the window), so you can see e.g. whether the
--     10000/second account is actually active before exempting it.
--     Defaults from settings.py: burst 100/minute, sustained 10000/day,
--     data_upload 30/minute.
-- ---------------------------------------------------------------------
WITH per_minute AS (
    SELECT user_id, date_trunc('minute', created_at) AS minute, count(*) AS n
    FROM api_requestlog
    WHERE created_at >= now() - interval '28 days'
    GROUP BY 1, 2
),
rolling AS (
    SELECT user_id, minute + make_interval(mins => k) AS window_end, sum(n) AS n_5min
    FROM per_minute
    CROSS JOIN generate_series(0, 4) AS k
    GROUP BY 1, 2
),
per_user AS (
    SELECT user_id, max(n_5min) AS peak_5min FROM rolling GROUP BY 1
)
SELECT u.burst_rate,
       u.sustained_rate,
       count(*)                                     AS users,
       count(p.user_id)                             AS active_users_28d,
       max(p.peak_5min)                             AS max_peak_5min,
       string_agg(u.email, ', ' ORDER BY p.peak_5min DESC NULLS LAST)
                                                    AS users_by_peak
FROM api_user u
LEFT JOIN per_user p ON p.user_id = u.id
WHERE u.burst_rate      <> '100/minute'
   OR u.sustained_rate  <> '10000/day'
   OR u.data_upload_rate <> '30/minute'
   OR p.user_id IS NOT NULL
GROUP BY 1, 2
ORDER BY max_peak_5min DESC NULLS LAST;


-- ---------------------------------------------------------------------
-- Q4. Drill-down for one user: busiest 5-minute windows and the
--     endpoints behind them. Replace :user_id (psql: \set user_id 123).
-- ---------------------------------------------------------------------
-- 4a. Top 20 busiest trailing 5-minute windows
WITH per_minute AS (
    SELECT date_trunc('minute', created_at) AS minute, count(*) AS n
    FROM api_requestlog
    WHERE created_at >= now() - interval '28 days'
      AND user_id = :user_id
    GROUP BY 1
)
SELECT minute + make_interval(mins => k) AS window_last_minute,
       sum(n)                            AS n_5min
FROM per_minute
CROSS JOIN generate_series(0, 4) AS k
GROUP BY 1
ORDER BY n_5min DESC
LIMIT 20;

-- 4b. Endpoints (numeric IDs and OS IDs collapsed so they group together)
SELECT method,
       regexp_replace(
           regexp_replace(split_part(path, '?', 1),
                          '/[A-Z]{2}[0-9]{7}[A-Z0-9]{6}(/|$)', '/{os_id}\1', 'g'),
           '/[0-9]+(/|$)', '/{id}\1', 'g')      AS endpoint,
       count(*)                                 AS requests,
       count(*) FILTER (WHERE response_code = 429) AS throttled
FROM api_requestlog
WHERE created_at >= now() - interval '28 days'
  AND user_id = :user_id
GROUP BY 1, 2
ORDER BY requests DESC
LIMIT 30;
