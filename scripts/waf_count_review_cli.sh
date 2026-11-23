#!/usr/bin/env bash
#
# WAF API rate limit review (OSDEV-3614). Runbook: doc/ops/waf_rate_limit_runbook.md
# Lists the web ACL's rules and pulls,
# per day, how many requests each rate rule and denylist rule blocked
# (BlockedRequests) or counted (CountedRequests, while a rule is in Count
# mode). Read-only: it only calls list/get/describe APIs.
# Used for the quarterly review; START defaults to 90 days ago.
#
# Usage:
#   ENVIRONMENT=Production ./scripts/waf_count_review_cli.sh
#   ENVIRONMENT=Staging START=2026-10-30T00:00:00Z ./scripts/waf_count_review_cli.sh
#
# Needs AWS credentials for the account that owns the environment.
# CloudFront web ACLs and their metrics always live in us-east-1.

set -euo pipefail

ENVIRONMENT="${ENVIRONMENT:-Production}"
DEFAULT_START="$(date -u -d '90 days ago' +%Y-%m-%dT00:00:00Z 2>/dev/null \
  || date -u -v-90d +%Y-%m-%dT00:00:00Z)"
START="${START:-$DEFAULT_START}"
END="${END:-$(date -u +%Y-%m-%dT%H:%M:%SZ)}"
REGION="us-east-1"
ACL_NAME="${ENVIRONMENT}-web-acl"
RULES=("ApiRateLimitPerIp" "ApiRateLimitAnonPerIp")
DENYLIST_RULES=("BlockDenylistedIPv4" "BlockDenylistedIPv6")

ACL_ID="$(aws wafv2 list-web-acls --scope CLOUDFRONT --region "$REGION" \
  --query "WebACLs[?Name=='${ACL_NAME}'].Id | [0]" --output text)"
if [ -z "$ACL_ID" ] || [ "$ACL_ID" = "None" ]; then
  echo "Web ACL ${ACL_NAME} not found in ${REGION} (CLOUDFRONT scope)" >&2
  exit 1
fi

echo "== Rules in ${ACL_NAME} (priority, name, action)"
aws wafv2 get-web-acl --scope CLOUDFRONT --region "$REGION" \
  --name "$ACL_NAME" --id "$ACL_ID" \
  --query 'WebACL.Rules[].[Priority, Name, keys(Action || OverrideAction)[0]]' \
  --output table

# CloudWatch only lists metrics that had data in the last 2 weeks, so take the
# dimension set from the web ACL's own AllowedRequests metric (Rule=ALL,
# always present while the ACL receives traffic) and swap in each rule name.
base_dims="$(aws cloudwatch list-metrics --region "$REGION" --namespace AWS/WAFV2 \
  --metric-name AllowedRequests \
  --dimensions "Name=WebACL,Value=${ACL_NAME}" "Name=Rule,Value=ALL" \
  --query 'Metrics[0].Dimensions' --output json)"
if [ "$base_dims" = "null" ]; then
  echo "No WAF metrics found for ${ACL_NAME}" >&2
  exit 1
fi

daily_sum() {  # $1 = metric name, $2 = rule name
  local dims="${base_dims//\"ALL\"/\"$2\"}"
  aws cloudwatch get-metric-statistics --region "$REGION" --namespace AWS/WAFV2 \
    --metric-name "$1" --dimensions "$dims" \
    --start-time "$START" --end-time "$END" --period 86400 --statistics Sum \
    --query 'sort_by(Datapoints, &Timestamp)[].[Timestamp, Sum]' --output table
}

echo
echo "== All requests allowed by ${ACL_NAME} per day (context: whole site, not only /api/)"
daily_sum AllowedRequests ALL

for rule in "${RULES[@]}"; do
  for metric in BlockedRequests CountedRequests; do
    echo
    echo "== ${rule}: ${metric} per day (${START} -> ${END}); days without data are not listed"
    daily_sum "$metric" "$rule"
  done

  echo "== ${rule}: IPs over the limit right now"
  aws wafv2 get-rate-based-statement-managed-keys --scope CLOUDFRONT --region "$REGION" \
    --web-acl-name "$ACL_NAME" --web-acl-id "$ACL_ID" --rule-name "$rule" \
    --query '[ManagedKeysIPV4.Addresses, ManagedKeysIPV6.Addresses]' --output json
done

for rule in "${DENYLIST_RULES[@]}"; do
  echo
  echo "== ${rule}: BlockedRequests per day (${START} -> ${END}); empty if the rule doesn't exist"
  daily_sum BlockedRequests "$rule"
done
