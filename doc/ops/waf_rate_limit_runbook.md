# WAF API rate limiting: denylist updates and quarterly review

The CloudFront web ACL (`deployment/terraform/waf.tf`) has two rate-based rules on `/api/` requests, counted per source IP over 5 minutes:

| Rule | Counts | Limit variable |
|---|---|---|
| `ApiRateLimitPerIp` | every `/api/` request | `waf_api_rate_limit_per_ip` |
| `ApiRateLimitAnonPerIp` | `/api/` requests without an `Authorization: Token` header and without a `sessionid` cookie (anonymous) | `waf_api_anon_rate_limit_per_ip` |

A blocked request gets `429` with `{"detail": "Request was throttled."}`. The action (`count` or `block`) is set per environment with `waf_rate_limit_action`.

There are two IP lists, both kept in Secrets Manager as JSON lists of CIDRs:
- **Denylist:** IPs that are always blocked.
- **Exemption list:** IPs the rate rules skip.

Background and decisions: [OSDEV-2138](https://opensupplyhub.atlassian.net/browse/OSDEV-2138) (rules) and [OSDEV-3614](https://opensupplyhub.atlassian.net/browse/OSDEV-3614) (Count-mode review, switch to Block).

## Where everything is (Production account)

| What | Where |
|---|---|
| WAF rules and IP sets, CloudWatch WAF metrics, WAF logs | **us-east-1** (CloudFront scope). Log group: `aws-waf-logs-opensupplyhub-production` (365-day retention; only counted or blocked requests are logged) |
| CloudFront access logs (Athena table `osh_prd_cdn_logs`), Secrets Manager | **eu-west-1** |
| Per-customer API usage | Django table `api_requestlog`, via the SSM tunnel to the production database (`deployment/ssm/ssm_tunnel.sh`) |
| Denylist secret | `oshub/production/ip-denylist` |
| Exemption secret | name set in `waf_rate_limit_exempt_ips_secret_name` (not set until the first exemption is needed) |
| Tools | `scripts/waf_count_review_cli.sh`, `doc/ops/waf_rate_limit/athena_waf_review.sql`, `doc/ops/waf_rate_limit/requestlog_rate_analysis.sql`, `scripts/waf_rate_limit_test.py` |

## Update the IP denylist

The WAF IP set is built from the secret **when Terraform applies**. So:
1. Update the secret **before** the Production infrastructure deploy.
2. If you update it after the deploy, re-run the Production infrastructure deploy so the IP set picks it up.

```bash
S=oshub/production/ip-denylist
R=eu-west-1

# 1. Download the current list
aws secretsmanager get-secret-value --secret-id "$S" --region "$R" \
  --query SecretString --output text > denylist.json

# 2a. Add entries (single IPv4 = /32, single IPv6 = /128, an IPv6 network = /64)
jq '. + ["203.0.113.10/32", "2001:db8:1:2::/64"] | unique' denylist.json > denylist.new.json
# 2b. Or remove entries
# jq '. - ["203.0.113.10/32"]' denylist.json > denylist.new.json

# 3. Check: only the intended lines changed, and every entry is a CIDR
diff denylist.json denylist.new.json
jq -e 'all(.[]; test("^([0-9]{1,3}\\.){3}[0-9]{1,3}/[0-9]{1,2}$") or test("^[0-9a-fA-F:]+/[0-9]{1,3}$"))' denylist.new.json

# 4. Upload, then clean up
aws secretsmanager put-secret-value --secret-id "$S" --region "$R" \
  --secret-string file://denylist.new.json
rm denylist.json denylist.new.json
```

After the deploy, check the IPs are in the IP set: AWS WAF → **IP sets** (region **Global (CloudFront)**) → `production-denylist-ipv4-ipset`. The first IPv6 entry also creates `production-denylist-ipv6-ipset` and a `BlockDenylistedIPv6` rule.

**Emergency block** (takes effect in seconds, no deploy): add the IP in the console to the same IP set. **Also add it to the secret**, or the next Terraform apply removes it.

The exemption list works the same way with its own secret. Exempt IPs skip both rate rules but not the denylist.

## Quarterly review (every 3 months)

Scrapers change IPs and behaviour, so every quarter:
- check what the rate rules blocked,
- find new persistent scrapers that stay under the limits,
- clean stale denylist entries,
- confirm no customer is being blocked.

Open a Jira ticket for each review and record the results there, not in this repository. The IP addresses involved shouldn't be committed.

### Step 1: Totals per rule (CLI)

```bash
ENVIRONMENT=Production ./scripts/waf_count_review_cli.sh
```

This prints the web ACL's rules, then per day for the last 90 days (set `START=` for another window):
- `BlockedRequests` for both rate rules and the denylist rules,
- the IPs over a limit right now.

Note the totals and the spike days.

### Step 2: Who the rate rules blocked (WAF logs)

In CloudWatch → **Logs Insights** (us-east-1), choose log group `aws-waf-logs-opensupplyhub-production`, set the time range to the last 90 days, and run:

```
fields httpRequest.clientIp as ip, terminatingRuleId as rule
| filter terminatingRuleId like /ApiRateLimit/
| stats count(*) as blocked, earliest(@timestamp) as first_seen, latest(@timestamp) as last_seen by ip, rule
| sort blocked desc
| limit 100
```

**Blocked requests that carried an API token**, i.e. possible customers. Any result here needs a closer look. The token value is redacted in the logs, but the header name is kept.

```
fields httpRequest.clientIp as ip
| filter terminatingRuleId like /ApiRateLimit/
| filter @message like /(?i)"name":"authorization"/
| stats count(*) as blocked by ip
| sort blocked desc
```

**Profile one IP** (paths, user agent in the headers):

```
fields @timestamp, terminatingRuleId, httpRequest.uri, httpRequest.headers
| filter httpRequest.clientIp = "203.0.113.10"
| sort @timestamp desc
| limit 50
```

### Step 3: Persistent scrapers that stay under the limits (Athena)

The WAF logs only contain blocked requests, so clients that stay just under the limits only show up in the CloudFront logs. In Athena (eu-west-1, database `default`), run `doc/ops/waf_rate_limit/athena_waf_review.sql`:
1. **Step 0:** copies the last 90 days of `/api/` traffic into a small Parquet table. Each full scan of the CloudFront logs costs a few cents.
2. **Query 3:** lists the **denylist candidates**: at least 10,000 requests over at least 5 days, and either mostly Django 429s or 1,000+ requests a day.
3. **Status codes per IP** (below), to tell an API customer apart from a scraper. Mostly 200s with no website referrer means an API-token client.
4. **Optional, queries 1 and 2:** replay both rules over the same days. Use them to check how a new limit would behave before changing it.
5. **Finish with** `DROP TABLE osh_prd_api_requests_waf_review;`.

```sql
SELECT request_ip, status, count(*) AS requests
FROM osh_prd_api_requests_waf_review
WHERE request_ip IN ('203.0.113.10', '203.0.113.11')
GROUP BY 1, 2
ORDER BY 1, 3 DESC;
```

### Step 4: Clean stale denylist entries (WAF logs)

```
fields httpRequest.clientIp as ip
| filter terminatingRuleId like /BlockDenylisted/
| stats count(*) as blocked, latest(@timestamp) as last_seen by ip
| sort blocked desc
```

Compare with the secret. An entry with **no blocks in 90 days** has gone quiet, or the IP has been reassigned (common for cloud IPs). Remove it as described in "Update the IP denylist".

### Step 5: Customer check (production database, read-only)

Run query 1 of `doc/ops/waf_rate_limit/requestlog_rate_analysis.sql` (last 90 days). It gives each token customer's peak requests per 5 minutes next to their Django limits. If a customer comes near `waf_api_rate_limit_per_ip`, find its IPs and add them to the exemption secret before it gets blocked.

### Step 6: Classify, decide, apply

Look up who owns each IP with `whois <ip>` (for RIPE addresses: `whois -h whois.ripe.net <ip>`).

| Pattern | Action |
|---|---|
| Automation that keeps coming back or stays under the limits: cloud/hosting IP, scripted or headless user agent, many user agents, high % Django 429s | **Denylist** |
| One-off bursts | Leave to the rate rules |
| Declared crawler that follows robots.txt (e.g. `ShapBot`) | `Crawl-delay` or `Disallow` in `src/react/public/robots.txt` |
| Customer or partner being blocked | **Exemption secret**, or raise the limit |
| Real users being blocked | Revisit the rule conditions in `waf.tf` |

Then:
1. Apply the secret changes and re-run the Production infrastructure deploy.
2. Record in the review ticket:
   - totals per rule,
   - IPs added to or removed from the denylist and why,
   - exemptions,
   - any limit changes.

## Testing a rule

`scripts/waf_rate_limit_test.py` sends a chosen number of requests to one URL and separates WAF 429s from Django 429s. Use a non-production environment, ideally Development with a temporarily low limit.

## Rollback

If real users get blocked:
1. In the WAF console, set the rate rule's action to **Count**. This takes effect immediately.
2. Set `waf_rate_limit_action = "count"` in the environment's tfvars, so the next Terraform apply doesn't switch it back to Block.
