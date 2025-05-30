#!/bin/bash

set -e

TFVARS_FILE="$1"

extract_array() {
  local varname="$1"
  awk -v var="$varname" '
    BEGIN { in_array=0; array="" }
    $0 ~ "^"var"[[:space:]]*=" {
      in_array=1
      gsub(/^.*=\s*/, "")
      array = $0
      if ($0 ~ /\]/) {
        in_array=0
        print array
        exit
      }
      next
    }
    in_array {
      array = array "\n" $0
      if ($0 ~ /\]/) {
        in_array=0
        print array
        exit
      }
    }
  ' "$TFVARS_FILE"
}

ip_whitelist=$(extract_array "ip_whitelist" | tr -d '[]", \n')
ip_denylist=$(extract_array "ip_denylist" | tr -d '[]", \n')

if [[ -n "$ip_whitelist" && -n "$ip_denylist" ]]; then
  echo "ERROR: You cannot define both ip_whitelist and ip_denylist!"
  exit 1
else
  echo "Whitelist and denylist validation passed."
fi
