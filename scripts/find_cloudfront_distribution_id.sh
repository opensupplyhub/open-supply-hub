#!/bin/bash
set -euo pipefail

domain="$1"
found_id=""

aliases=$(aws cloudfront get-distribution-config --id "$id" --query "DistributionConfig.Aliases.Items[]" --output text)
for alias in $aliases; do
  if [[ "$alias" == "$domain" ]]; then
    if [ -n "$found_id" ]; then
      echo "Error: Multiple CloudFront distributions found for domain: $domain" >&2
      exit 1
    fi
    found_id="$id"
    break
  fi
done

echo "$found_id"
