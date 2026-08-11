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

# Prefer Secrets Manager name inputs (public tfvars). Fall back to legacy
# plaintext list variables for local/dev transition.
ip_whitelist_secret_name=$(extract_scalar "ip_whitelist_secret_name")
ip_denylist_secret_name=$(extract_scalar "ip_denylist_secret_name")

if [[ -n "$ip_whitelist_secret_name" && -n "$ip_denylist_secret_name" ]]; then
  echo "ERROR: You cannot define both ip_whitelist_secret_name and ip_denylist_secret_name!"
  exit 1
fi

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
fi

echo "Whitelist and denylist validation passed."
