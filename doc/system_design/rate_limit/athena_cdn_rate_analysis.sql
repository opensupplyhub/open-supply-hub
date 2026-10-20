-- =====================================================================
-- OSDEV-2138: per-IP API traffic analysis from CloudFront logs (Athena)
--
-- Why CloudFront logs: WAF sits in front of CloudFront, so it counts
-- EVERY request per source IP, including cache hits that never reach
-- Django. These logs are the closest match to what a WAF rate rule sees.
--
-- Table: osh_<env>_cdn_logs  (deployment/terraform/athena.tf)
--   production -> osh_prd_cdn_logs, staging -> osh_stg_cdn_logs, ...
--
-- Limitations:
--   * The logs do not include the Authorization header (and cookies
--     are not logged), so token vs. anonymous/session traffic can't be
--     split exactly. The referrer is used as a proxy: requests from the
--     React app carry Referer https://opensupplyhub.org/..., while API
--     scripts usually send none ('-').
--   * Counts use a TRAILING 5-minute window evaluated every minute,
--     like a WAF rate rule with evaluation_window_sec = 300. WAF's own
--     counting is approximate, so leave headroom on top of these numbers.
--
-- COST WARNING: the cdn_logs table has no partitions and the logs
-- bucket has no lifecycle rule, so EVERY query against it scans the
-- whole CDN log history, whatever the date filter says. Check the size
-- of s3://<logs bucket>/CDN first. Then run step 0 ONCE to copy the
-- window you need into a small Parquet table, and run everything else
-- against that copy.
-- =====================================================================


-- ---------------------------------------------------------------------
-- 0. One-time snapshot: last 28 days of /api/ requests -> Parquet.
--    Written to the workgroup's query result location (add
--    external_location = 's3://.../' to WITH (...) to choose another).
--    DROP TABLE osh_prd_api_requests_28d when you're done.
-- ---------------------------------------------------------------------
CREATE TABLE osh_prd_api_requests_28d
WITH (format = 'PARQUET', parquet_compression = 'SNAPPY') AS
SELECT CAST(concat(CAST("date" AS varchar), ' ', "time") AS timestamp) AS ts,
       request_ip,
       method,
       uri,
       status,
       result_type,
       user_agent,
       referrer,
       (referrer LIKE 'https://opensupplyhub.org/%')                    AS is_web_app
FROM osh_prd_cdn_logs
WHERE "date" >= current_date - INTERVAL '28' DAY
  AND host_header = 'opensupplyhub.org'
  AND uri LIKE '/api/%';


-- ---------------------------------------------------------------------
-- 1. Distribution of per-IP peaks, for two candidate rule scopes:
--      all_api        -> the "ApiRateLimitPerIp" rule
--      web_app_ref    -> approximation of the "no Authorization header"
--                        rule (browser / session traffic)
--    Tells you what limit leaves (almost) every IP untouched.
-- ---------------------------------------------------------------------
WITH scoped AS (
    SELECT 'all_api' AS scope, request_ip, ts FROM osh_prd_api_requests_28d
    UNION ALL
    SELECT 'web_app_ref', request_ip, ts FROM osh_prd_api_requests_28d WHERE is_web_app
),
per_minute AS (
    SELECT scope, request_ip,
           CAST(floor(to_unixtime(ts) / 60) AS bigint) AS minute_idx,
           count(*)                                    AS n
    FROM scoped
    GROUP BY 1, 2, 3
),
-- each minute's count contributes to the 5 trailing windows ending at
-- minute_idx, minute_idx+1 ... minute_idx+4
rolling AS (
    SELECT scope, request_ip, minute_idx + k AS window_end, sum(n) AS n_5min
    FROM per_minute
    CROSS JOIN UNNEST(sequence(0, 4)) AS t (k)
    GROUP BY 1, 2, 3
),
per_ip AS (
    SELECT p.scope, p.request_ip, p.peak_1min, r.peak_5min
    FROM (SELECT scope, request_ip, max(n) AS peak_1min
          FROM per_minute GROUP BY 1, 2) p
    JOIN (SELECT scope, request_ip, max(n_5min) AS peak_5min
          FROM rolling GROUP BY 1, 2) r
      ON r.scope = p.scope AND r.request_ip = p.request_ip
)
SELECT scope,
       count(*)                               AS ips,
       approx_percentile(peak_5min, 0.50)     AS p50_5min,
       approx_percentile(peak_5min, 0.99)     AS p99_5min,
       approx_percentile(peak_5min, 0.999)    AS p999_5min,
       max(peak_5min)                         AS max_5min,
       max(peak_1min)                         AS max_1min,
       count_if(peak_5min > 500)              AS ips_over_500,
       count_if(peak_5min > 1000)             AS ips_over_1k,
       count_if(peak_5min > 2000)             AS ips_over_2k,
       count_if(peak_5min > 5000)             AS ips_over_5k,
       count_if(peak_5min > 10000)            AS ips_over_10k,
       count_if(peak_5min > 20000)            AS ips_over_20k,
       count_if(peak_5min > 50000)            AS ips_over_50k
FROM per_ip
GROUP BY scope
ORDER BY scope;


-- ---------------------------------------------------------------------
-- 2. Impact simulation: if the rule were in Block mode at each
--    threshold, how many IPs, minutes and requests would have been
--    blocked over the period? (A request is counted as blocked when its
--    IP's trailing 5-minute count, including that minute, is over the
--    threshold; within that minute only the overflow is counted. That's
--    roughly how WAF behaves, which itself reacts with a short delay.)
--    Edit the ARRAY[...] to try other thresholds.
-- ---------------------------------------------------------------------
WITH scoped AS (
    SELECT 'all_api' AS scope, request_ip, ts FROM osh_prd_api_requests_28d
    UNION ALL
    SELECT 'web_app_ref', request_ip, ts FROM osh_prd_api_requests_28d WHERE is_web_app
),
per_minute AS (
    SELECT scope, request_ip,
           CAST(floor(to_unixtime(ts) / 60) AS bigint) AS minute_idx,
           count(*)                                    AS n
    FROM scoped
    GROUP BY 1, 2, 3
),
rolling AS (
    SELECT scope, request_ip, minute_idx + k AS window_end, sum(n) AS n_5min
    FROM per_minute
    CROSS JOIN UNNEST(sequence(0, 4)) AS t (k)
    GROUP BY 1, 2, 3
),
minute_with_window AS (
    SELECT m.scope, m.request_ip, m.minute_idx, m.n, r.n_5min
    FROM per_minute m
    JOIN rolling r
      ON r.scope = m.scope AND r.request_ip = m.request_ip
     AND r.window_end = m.minute_idx
),
totals AS (
    SELECT scope, sum(n) AS total_requests FROM per_minute GROUP BY 1
)
SELECT w.scope,
       th.threshold,
       count(DISTINCT CASE WHEN w.n_5min > th.threshold THEN w.request_ip END) AS ips_blocked,
       count_if(w.n_5min > th.threshold)                                       AS minutes_blocked,
       sum(greatest(0, least(w.n, w.n_5min - th.threshold)))                  AS requests_blocked,
       round(100.0 * sum(greatest(0, least(w.n, w.n_5min - th.threshold)))
             / max(t.total_requests), 3)                                       AS pct_of_requests
FROM minute_with_window w
CROSS JOIN UNNEST(ARRAY[500, 1000, 2000, 5000, 10000, 20000, 50000]) AS th (threshold)
JOIN totals t ON t.scope = w.scope
GROUP BY 1, 2
ORDER BY 1, 2;


-- ---------------------------------------------------------------------
-- 3. Top 50 IPs by 5-minute peak: who would a limit actually hit?
--    Use this to build the rate_limit_exempt_ips list (known customers
--    / partners) and to spot scrapers.
--    pct_web_app ~100%  -> browser / session traffic (or a script
--                          faking the referrer)
--    pct_web_app ~0%    -> API client (token or scripted)
-- ---------------------------------------------------------------------
WITH per_minute AS (
    SELECT request_ip,
           CAST(floor(to_unixtime(ts) / 60) AS bigint) AS minute_idx,
           count(*)                                    AS n
    FROM osh_prd_api_requests_28d
    GROUP BY 1, 2
),
rolling AS (
    SELECT request_ip, minute_idx + k AS window_end, sum(n) AS n_5min
    FROM per_minute
    CROSS JOIN UNNEST(sequence(0, 4)) AS t (k)
    GROUP BY 1, 2
),
peaks AS (
    SELECT request_ip,
           max(n_5min)                                        AS peak_5min,
           from_unixtime(max_by(window_end, n_5min) * 60)     AS peak_window_last_minute_utc
    FROM rolling
    GROUP BY 1
),
profile AS (
    SELECT request_ip,
           count(*)                                           AS total_requests,
           count(DISTINCT date_trunc('day', ts))              AS active_days,
           round(100.0 * count_if(is_web_app) / count(*), 1)  AS pct_web_app,
           round(100.0 * count_if(result_type IN ('Hit', 'RefreshHit')) / count(*), 1)
                                                              AS pct_cache_hit,
           count_if(status = 429)                             AS django_429s,
           count_if(status = 403)                             AS waf_or_django_403s,
           count(DISTINCT user_agent)                         AS distinct_user_agents,
           arbitrary(user_agent)                              AS sample_user_agent
    FROM osh_prd_api_requests_28d
    GROUP BY 1
)
SELECT pk.request_ip,
       pk.peak_5min,
       pk.peak_window_last_minute_utc,
       pr.total_requests,
       pr.active_days,
       pr.pct_web_app,
       pr.pct_cache_hit,
       pr.django_429s,
       pr.waf_or_django_403s,
       pr.distinct_user_agents,
       url_decode(pr.sample_user_agent)                       AS sample_user_agent
FROM peaks pk
JOIN profile pr ON pr.request_ip = pk.request_ip
ORDER BY pk.peak_5min DESC
LIMIT 50;


-- ---------------------------------------------------------------------
-- 4. Gap between what WAF counts and what Django sees: cache hit ratio
--    per endpoint. High hit ratios mean a WAF limit "spends" budget on
--    requests that cost the backend nothing.
-- ---------------------------------------------------------------------
SELECT regexp_extract(uri, '^/api/(v1/)?[^/]+')                AS endpoint,
       count(*)                                                       AS requests,
       round(100.0 * count_if(result_type IN ('Hit', 'RefreshHit')) / count(*), 1)
                                                                      AS pct_cache_hit,
       round(100.0 * count_if(is_web_app) / count(*), 1)              AS pct_web_app,
       count_if(status = 429)                                         AS django_429s
FROM osh_prd_api_requests_28d
GROUP BY 1
ORDER BY requests DESC
LIMIT 40;


-- ---------------------------------------------------------------------
-- 5. Drill-down for one IP (replace the address): busiest minutes and
--    the endpoints behind them.
-- ---------------------------------------------------------------------
-- 5a. Requests per minute, busiest first
SELECT date_trunc('minute', ts) AS minute_utc,
       count(*)                 AS requests,
       count_if(status = 429)   AS django_429s
FROM osh_prd_api_requests_28d
WHERE request_ip = '203.0.113.10'
GROUP BY 1
ORDER BY requests DESC
LIMIT 30;

-- 5b. Endpoints (numeric IDs and OS IDs collapsed)
SELECT method,
       regexp_replace(
           regexp_replace(uri, '/[A-Z]{2}[0-9]{7}[A-Z0-9]{6}(/|$)', '/{os_id}$1'),
           '/[0-9]+(/|$)', '/{id}$1')                                  AS endpoint,
       count(*)                                                       AS requests,
       round(100.0 * count_if(result_type IN ('Hit', 'RefreshHit')) / count(*), 1)
                                                                      AS pct_cache_hit
FROM osh_prd_api_requests_28d
WHERE request_ip = '203.0.113.10'
GROUP BY 1, 2
ORDER BY requests DESC
LIMIT 30;


-- ---------------------------------------------------------------------
-- 6. Why do some heavy IPs get no Django 429s?
--    Splits each IP's traffic into endpoints Django does NOT throttle
--    (throttle_classes = [] in the views) and everything else.
--    * mostly 'unthrottled'           -> expected, Django never limits them
--    * 'throttled' with max_per_minute well over 100 and ~0 429s
--                                     -> Django's per-IP limit isn't
--                                        catching them (logged-in session
--                                        with a high limit, or the throttle
--                                        key being split across CloudFront
--                                        servers)
-- ---------------------------------------------------------------------
WITH classified AS (
    SELECT request_ip,
           ts,
           status,
           CASE WHEN regexp_like(uri,
                  '^/api/(contributors(/active_count)?|contributor-types|countries(/active_count)?'
                  || '|workers-ranges|claim-statuses|facility-processing-types'
                  || '|processing-type-suggestions|parent-companies|product-types|sectors'
                  || '|info/[^/]+)/?$')
                THEN 'unthrottled' ELSE 'throttled' END AS django_throttle
    FROM osh_prd_api_requests_28d
    WHERE request_ip IN ('18.185.51.40', '38.79.112.114', '216.22.11.132',
                         '120.48.174.206', '120.48.16.247', '180.76.186.7',
                         '2605:6440:d000:408:7ec2:55ff:fe96:97d6',
                         '82.222.123.25')   -- control: gets lots of 429s
),
per_minute AS (
    SELECT request_ip, django_throttle, date_trunc('minute', ts) AS minute,
           count(*) AS n
    FROM classified
    GROUP BY 1, 2, 3
)
SELECT c.request_ip,
       c.django_throttle,
       count(*)                       AS requests,
       count_if(c.status = 429)       AS django_429s,
       max(m.max_per_minute)          AS max_per_minute
FROM classified c
JOIN (SELECT request_ip, django_throttle, max(n) AS max_per_minute
      FROM per_minute GROUP BY 1, 2) m
  ON m.request_ip = c.request_ip AND m.django_throttle = c.django_throttle
GROUP BY 1, 2
ORDER BY 1, 2;
