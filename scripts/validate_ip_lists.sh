#!/bin/bash

set -e

TFVARS_FILE="$1"

extract_scalar() {
  local varname="$1"
  awk -v var="$varname" '
    $0 ~ "^"var"[[:space:]]*=" {
      sub(/^[^=]*=[[:space:]]*/, "")
      gsub(/[[:space:]]*#.*$/, "")
      gsub(/^"/, "")
      gsub(/"$/, "")
      print
      exit
    }
  ' "$TFVARS_FILE"
}

ip_whitelist_secret_name=$(extract_scalar "ip_whitelist_secret_name")
ip_denylist_secret_name=$(extract_scalar "ip_denylist_secret_name")

if [[ -n "$ip_whitelist_secret_name" && -n "$ip_denylist_secret_name" ]]; then
  echo "ERROR: You cannot define both ip_whitelist_secret_name and ip_denylist_secret_name!"
  exit 1
fi

echo "Whitelist and denylist validation passed."
