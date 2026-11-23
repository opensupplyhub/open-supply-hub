-- =====================================================================
-- WAF API rate limit review (OSDEV-2138, OSDEV-3614).
-- Runbook: doc/ops/waf_rate_limit_runbook.md
--
-- Replays both rate rules against the CloudFront logs of the last 90 days
-- to see WHICH IPs go (or would go) over the limits, and how much. Used to
-- check a limit before changing it, and for the quarterly review together
-- with the WAF logs (which only contain blocked requests).
--
--   ApiRateLimitPerIp      all /api/ requests            limit 2,000 / 5 min
--   ApiRateLimitAnonPerIp  /api/ requests without token  limit   500 / 5 min
--
-- CloudFront logs don't include the Authorization header, so the anonymous
-- rule is approximated with requests that carry the website referrer
-- Query 1 compares the replay with CloudWatch Blocked/CountedRequests
-- per day, so we know how close it is.
--
-- Table: osh_prd_cdn_logs (osh_<env>_cdn_logs for other environments).
-- Each full scan of the CDN logs costs a few cents; step 0 runs it once.
-- =====================================================================


-- ---------------------------------------------------------------------
-- 0. One-time snapshot of the last 90 days (/api/ only) -> Parquet.
--    DROP TABLE osh_prd_api_requests_waf_review when done.
-- ---------------------------------------------------------------------
CREATE TABLE osh_prd_api_requests_waf_review
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
WHERE "date" >= current_date - INTERVAL '90' DAY
  AND host_header = 'opensupplyhub.org'
  AND lower(coalesce(try(url_decode(uri)), uri)) LIKE '/api/%';


-- ---------------------------------------------------------------------
-- 1. Daily requests each rule would have blocked (replay).
--    Compare with CloudWatch BlockedRequests (CountedRequests in Count
--    mode) per rule per day (scripts/waf_count_review_cli.sh).
--    Close numbers = the replay is
--    trustworthy for the per-IP lists below.
-- ---------------------------------------------------------------------
WITH params AS (
    SELECT 2000 AS all_limit, 500 AS anon_limit
),
scoped AS (
    SELECT 'ApiRateLimitPerIp' AS rule_name, request_ip, ts
    FROM osh_prd_api_requests_waf_review
    UNION ALL
    SELECT 'ApiRateLimitAnonPerIp', request_ip, ts
    FROM osh_prd_api_requests_waf_review WHERE is_web_app
),
per_minute AS (
    SELECT rule_name, request_ip,
           CAST(floor(to_unixtime(ts) / 60) AS bigint) AS minute_idx,
           count(*)                                    AS n
    FROM scoped
    GROUP BY 1, 2, 3
),
rolling AS (
    SELECT rule_name, request_ip, minute_idx + k AS window_end, sum(n) AS n_5min
    FROM per_minute
    CROSS JOIN UNNEST(sequence(0, 4)) AS t (k)
    GROUP BY 1, 2, 3
),
blocked AS (
    SELECT m.rule_name, m.request_ip, m.minute_idx,
           greatest(0, least(m.n, r.n_5min -
               CASE m.rule_name WHEN 'ApiRateLimitPerIp' THEN p.all_limit
                                ELSE p.anon_limit END)) AS would_block
    FROM per_minute m
    JOIN rolling r
      ON r.rule_name = m.rule_name AND r.request_ip = m.request_ip
     AND r.window_end = m.minute_idx
    CROSS JOIN params p
)
SELECT date(from_unixtime(minute_idx * 60))           AS day_utc,
       rule_name,
       sum(would_block)                               AS requests_would_block,
       count(DISTINCT CASE WHEN would_block > 0 THEN request_ip END) AS ips
FROM blocked
GROUP BY 1, 2
ORDER BY 1, 2;


-- ---------------------------------------------------------------------
-- 2. MAIN LIST: every IP that went over a limit, with a profile to
--    classify it (automation vs. real user / customer).
--
--    How to read it:
--      pct_web_app ~100      browser / website path (or a script faking it)
--      pct_web_app ~0        API client (token or scripted)
--      pct_django_429 high   Django was already rejecting it
--      many sample UAs, bare "Mozilla/5.0", curl, python, Headless...
--                            automation
--    Look up the owner of unclear IPs (whois / ASN): cloud provider
--    ranges are almost always automation; a company or university
--    network may be a customer or partner -> exemption candidate.
-- ---------------------------------------------------------------------
WITH params AS (
    SELECT 2000 AS all_limit, 500 AS anon_limit
),
scoped AS (
    SELECT 'ApiRateLimitPerIp' AS rule_name, request_ip, ts
    FROM osh_prd_api_requests_waf_review
    UNION ALL
    SELECT 'ApiRateLimitAnonPerIp', request_ip, ts
    FROM osh_prd_api_requests_waf_review WHERE is_web_app
),
per_minute AS (
    SELECT rule_name, request_ip,
           CAST(floor(to_unixtime(ts) / 60) AS bigint) AS minute_idx,
           count(*)                                    AS n
    FROM scoped
    GROUP BY 1, 2, 3
),
rolling AS (
    SELECT rule_name, request_ip, minute_idx + k AS window_end, sum(n) AS n_5min
    FROM per_minute
    CROSS JOIN UNNEST(sequence(0, 4)) AS t (k)
    GROUP BY 1, 2, 3
),
blocked AS (
    SELECT m.rule_name, m.request_ip, m.minute_idx, r.n_5min,
           greatest(0, least(m.n, r.n_5min -
               CASE m.rule_name WHEN 'ApiRateLimitPerIp' THEN p.all_limit
                                ELSE p.anon_limit END)) AS would_block
    FROM per_minute m
    JOIN rolling r
      ON r.rule_name = m.rule_name AND r.request_ip = m.request_ip
     AND r.window_end = m.minute_idx
    CROSS JOIN params p
),
offenders AS (
    SELECT request_ip,
           array_join(array_sort(array_agg(DISTINCT
               CASE WHEN would_block > 0 THEN rule_name END)), ', ') AS rules_hit,
           sum(would_block)                                          AS requests_would_block,
           count_if(would_block > 0)                                 AS minutes_over,
           count(DISTINCT CASE WHEN would_block > 0
                 THEN date(from_unixtime(minute_idx * 60)) END)      AS days_over,
           max(n_5min)                                               AS peak_5min,
           from_unixtime(min(CASE WHEN would_block > 0 THEN minute_idx END) * 60) AS first_over_utc,
           from_unixtime(max(CASE WHEN would_block > 0 THEN minute_idx END) * 60) AS last_over_utc
    FROM blocked
    GROUP BY 1
    HAVING sum(would_block) > 0
),
profile AS (
    SELECT request_ip,
           count(*)                                                AS total_requests,
           count(DISTINCT date(ts))                                AS active_days,
           round(100.0 * count_if(is_web_app) / count(*), 1)       AS pct_web_app,
           round(100.0 * count_if(result_type IN ('Hit', 'RefreshHit')) / count(*), 1)
                                                                   AS pct_cache_hit,
           round(100.0 * count_if(status = 429) / count(*), 1)     AS pct_django_429,
           count(DISTINCT user_agent)                              AS distinct_user_agents,
           arbitrary(coalesce(try(url_decode(user_agent)), user_agent))                       AS sample_user_agent,
           approx_most_frequent(3, regexp_extract(uri, '^/api/(v1/)?[^/]+'), 1000)
                                                                   AS top_endpoints
    FROM osh_prd_api_requests_waf_review
    WHERE request_ip IN (SELECT request_ip FROM offenders)
    GROUP BY 1
)
SELECT o.request_ip,
       o.rules_hit,
       o.requests_would_block,
       o.minutes_over,
       o.days_over,
       o.peak_5min,
       o.first_over_utc,
       o.last_over_utc,
       p.total_requests,
       p.active_days,
       p.pct_web_app,
       p.pct_cache_hit,
       p.pct_django_429,
       p.distinct_user_agents,
       p.sample_user_agent,
       p.top_endpoints
FROM offenders o
JOIN profile p ON p.request_ip = o.request_ip
ORDER BY o.requests_would_block DESC;


-- ---------------------------------------------------------------------
-- 3. DENYLIST CANDIDATES: heavy, persistent clients, whether or not they
--    go over the rate limits (steady scrapers stay just under them).
--    Starting criteria (tune as needed):
--      * at least 10,000 /api/ requests in the period, AND
--      * active on at least 5 days, AND
--      * either >= 50% of its requests already rejected by Django (429)
--        or an average of >= 1,000 requests per active day
--    These still need a human decision before going on the denylist.
-- ---------------------------------------------------------------------
SELECT request_ip,
       count(*)                                                AS total_requests,
       count(DISTINCT date(ts))                                AS active_days,
       round(1.0 * count(*) / count(DISTINCT date(ts)))        AS avg_per_active_day,
       round(100.0 * count_if(status = 429) / count(*), 1)     AS pct_django_429,
       round(100.0 * count_if(is_web_app) / count(*), 1)       AS pct_web_app,
       count(DISTINCT user_agent)                              AS distinct_user_agents,
       arbitrary(coalesce(try(url_decode(user_agent)), user_agent))                       AS sample_user_agent,
       approx_most_frequent(3, regexp_extract(uri, '^/api/(v1/)?[^/]+'), 1000)
                                                               AS top_endpoints
FROM osh_prd_api_requests_waf_review
GROUP BY 1
HAVING count(*) >= 10000
   AND count(DISTINCT date(ts)) >= 5
   AND (count_if(status = 429) >= 0.5 * count(*)
        OR count(*) >= 1000 * count(DISTINCT date(ts)))
ORDER BY total_requests DESC
LIMIT 100;


-- ---------------------------------------------------------------------
-- 4. Drill-down for one IP (replace the address): busiest minutes and
--    the endpoints behind them.
-- ---------------------------------------------------------------------
-- 4a. Requests per minute, busiest first
SELECT date_trunc('minute', ts) AS minute_utc,
       count(*)                 AS requests,
       count_if(status = 429)   AS django_429s,
       count_if(is_web_app)     AS web_app_requests
FROM osh_prd_api_requests_waf_review
WHERE request_ip = '203.0.113.10'
GROUP BY 1
ORDER BY requests DESC
LIMIT 30;

-- 4b. Endpoints (numeric IDs and OS IDs collapsed)
SELECT method,
       regexp_replace(
           regexp_replace(uri, '/[A-Z]{2}[0-9]{7}[A-Z0-9]{6}(/|$)', '/{os_id}$1'),
           '/[0-9]+(/|$)', '/{id}$1')                                  AS endpoint,
       count(*)                                                       AS requests,
       count_if(status = 429)                                         AS django_429s
FROM osh_prd_api_requests_waf_review
WHERE request_ip = '203.0.113.10'
GROUP BY 1, 2
ORDER BY requests DESC
LIMIT 30;
