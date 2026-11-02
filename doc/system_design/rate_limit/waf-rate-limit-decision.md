# OSDEV-2138: WAF rate limiting for the API

Decision record for adding infrastructure-level rate limiting in front of Django (AWS WAF on CloudFront).

## Problem

API throttling only exists in Django (DRF), so abusive traffic still reaches the app before it is rejected. The concern was choosing WAF limits that stop abuse without hurting real users, given that Django limits are per user and some customers have very high custom rates.

## Why WAF can't copy the Django limits

- **Different key.** Django throttles per user (anonymous users per IP). WAF counts per source IP.
- **Different window.** WAF only counts over 1, 2, 5 or 10 minutes, approximately. It can't express "10000/day".
- **WAF sees cache hits.** WAF runs before the CloudFront cache, so it counts requests Django never sees.

**Decision:** WAF is a coarse per-IP safety net set above real traffic. Django stays the precise, per-user limit.

## Data analysed (28 days, production)

Queries are in `athena_cdn_rate_analysis.sql` (CloudFront logs, per IP) and `requestlog_rate_analysis.sql` (token requests in `api_requestlog`, per user).

### What "peak" means

An IP's or user's **5-minute peak** is the most requests it made in any 5-minute stretch during the 28 days. The query slides a 5-minute window across its traffic one minute at a time (12:00–12:05, 12:01–12:06, …), counts the requests in each window, and keeps the largest count.

Example:

| Minute | 12:00 | 12:01 | 12:02 | 12:03 | 12:04 | 12:05 |
|---|---|---|---|---|---|---|
| Requests | 10 | 200 | 300 | 250 | 150 | 5 |

The busiest window is 12:00–12:04, with 10 + 200 + 300 + 250 + 150 = **910**. So the peak is 910, even if the IP sent almost nothing the rest of the month.

We use the peak instead of an average because that's how WAF works. A limit of 500 per 5 minutes blocks an IP as soon as any 5-minute window goes over 500. So "99% of IPs peaked at 45 or fewer" means 99% of IPs never sent more than 45 requests in any 5 minutes, and a 500 limit would never have touched them.

### Per IP, from CloudFront logs

- 111,788 IPs. 99% peaked at **45 or fewer** requests per 5 min, and 99.9% at **345 or fewer**.
- IPs over each threshold: 52 over 500, 20 over 1k, 4 over 2k, 1 over 20k.
- Simulated blocking, as a share of all `/api/` requests: 15.4% at 500, 7.0% at 1k, 3.6% at 2k.
- Heavy IPs were almost all automation using the website's API path (site referrer): AI desktop apps, HeadlessChrome, curl, rotating user agents, and a cloud-IP cluster all peaking in the same minute.
- Some kept going after Django rejected them. One IP had 174k of 178k requests rejected with 429 over 19 days.
- Clients without a site referrer (API scripts) peaked at about 1,242.

### Per user, from RequestLog

- The busiest token user peaked at **1,242 per 5 min** (an internal account on 200/min). Every other account stayed at 554 or below.
- Every high-tier account (1000/min up to 10000/s) was **idle** in the window. They're mostly internal or import accounts.

### Django gaps found along the way

- **No `X-Forwarded-For` spoofing.** No heavy IP sent its own header, so that hypothesis was ruled out.
- **Some endpoints have no Django throttling at all** (`throttle_classes = []`): contributors, countries, sectors, parent-companies, product-types, workers-ranges, claim-statuses, processing types and suggestions, `info/*`.
- **Several IPs hit throttled endpoints at 150–545 per minute with ~0 429s**, against a 100/min anonymous limit. The cause isn't known yet: either logged-in sessions with high personal limits, or the anonymous throttle key being split by the CloudFront server IP. This is deferred to a separate Django ticket.

## Decisions

| Rule | Scope | Limit (per IP / 5 min) | Why |
|---|---|---|---|
| `ApiRateLimitPerIp` | all `/api/*` | **2,000** | ~60% headroom over the busiest token user (1,242). Would only have hit 4 IPs, all automation Django was already rejecting. |
| `ApiRateLimitAnonPerIp` | `/api/*` without an `Authorization: Token` header | **500** | Equals Django's intended anonymous limit (100/min), so real users are never restricted more than Django already intends. At 1,000, the low-and-steady scrapers (peaking 680–880) would get through. |

- **Exemptions.** There's an IP exempt list (a Secrets Manager secret, empty for now), for internal callers and occasional bulk-import jobs on high-tier accounts. It's implemented with a WAF label, so exempt IPs skip both rules.
- **Response.** A block returns `429` with `{"detail": "Request was throttled."}`, the same as Django, so existing clients keep working.
- **Rollout.** Enabled in all environments in **Count** mode. After 1–2 weeks of review, switch production to **Block** with `waf_rate_limit_action = "block"`. If real users show up in the counts, raise the anonymous limit to 1,000 first.

## Known limits

- Steady low-rate scrapers under the limit, and IPv6 address rotation, aren't caught by per-IP limits. Use the IP denylist, or later ASN rules or Bot Control.
- A fake `Authorization: Token …` header skips the anonymous rule. Django answers those with 401, and they still count toward the 2,000 rule.
- Logged-in staff browsing the site on high-limit accounts fall under the anonymous rule, since WAF can't see their session.
- The default limits sit in `variables.tf`, which is in a public repo. They could move to a secret if that matters.

## Implementation

- `deployment/terraform/waf.tf`: the exempt IP sets, the label rules, the two rate-based rules and the custom 429 response body.
- `deployment/terraform/variables.tf` and `secrets.tf`: `waf_rate_limit_enabled`, `waf_rate_limit_action`, `waf_api_rate_limit_per_ip`, `waf_api_anon_rate_limit_per_ip`, `waf_rate_limit_evaluation_window_sec`, `waf_rate_limit_exempt_ips` / `_secret_name`.
- `deployment/environments/*.tfvars`: rules enabled in Count mode.
- `doc/release/RELEASE-NOTES.md`: entry under 2.32.0.

## Follow-ups

1. Django ticket: find out why the anonymous throttle isn't applied to some IPs (reproduce on staging).
2. Decide whether the unthrottled endpoints should get Django throttling back.
3. After the Count period: review the matches, fill in the exempt list if needed, and switch to Block.
