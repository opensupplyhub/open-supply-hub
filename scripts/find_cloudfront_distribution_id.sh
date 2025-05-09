#!/bin/bash
set -euo pipefail

domain="$1"
found_id=""

for id in $(aws cloudfront list-distributions --query "DistributionList.Items[*].Id" --output text); do
  domains=$(aws cloudfront get-distribution-config --id "$id" --query "DistributionConfig.Aliases.Items" --output text)
  if [[ "$domains" == "$domain" ]]; then
    if [ -n "$found_id" ]; then
      echo "Error: Multiple CloudFront distributions found for domain: $domain" >&2
      exit 1
    fi
    found_id="$id"
  fi
done

echo "$found_id"
