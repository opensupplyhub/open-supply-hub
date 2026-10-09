#!/usr/bin/env bash
#
# Delete the custom OpenSearch indexes and templates, and the Logstash JDBC
# pipeline lock files on EFS, so new index mappings are applied and the
# indexes are rebuilt when Logstash restarts.
#
# OSDEV-3531: runs on the GitHub runner and reaches the private resources
# through the bastion with AWS Systems Manager instead of SSH:
#   - OpenSearch: SSM port forward to the domain's VPC endpoint; requests are
#     signed on the runner, so no credentials are sent to the bastion.
#   - EFS lock files: SSM Run Command on the bastion, which mounts the
#     Logstash file system and removes them.
#
# Environment:
#   CLEAR_OPENSEARCH_TARGET  none | production-locations | moderation-events | both
#   OPENSEARCH_DOMAIN        VPC endpoint of the OpenSearch domain
#   EFS_ID, EFS_AP_ID        Logstash EFS file system and access point
#   ENVIRONMENT              bastion Environment tag (e.g. Test)
#   AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION

set -euo pipefail

target="${CLEAR_OPENSEARCH_TARGET:?}"
: "${OPENSEARCH_DOMAIN:?}" "${EFS_ID:?}" "${EFS_AP_ID:?}" "${AWS_DEFAULT_REGION:?}"

if [ "$target" = "none" ]; then
  echo "CLEAR_OPENSEARCH_TARGET is none; nothing to clear."
  exit 0
fi

clear_production_locations=false
clear_moderation_events=false
case "$target" in
  both) clear_production_locations=true; clear_moderation_events=true ;;
  production-locations) clear_production_locations=true ;;
  moderation-events) clear_moderation_events=true ;;
  *) echo "Unknown CLEAR_OPENSEARCH_TARGET: $target" >&2; exit 2 ;;
esac

TUNNEL="$(cd "$(dirname "$0")/../ssm" && pwd)/ssm_tunnel.sh"
LOCAL_PORT=9443

#
# OpenSearch indexes and templates
#
bash "$TUNNEL" start "$OPENSEARCH_DOMAIN" 443 "$LOCAL_PORT"
trap 'bash "$TUNNEL" stop "$LOCAL_PORT"' EXIT

# --connect-to sends the request to the local end of the port forward while
# keeping the domain name for TLS verification and request signing.
CURL_OPTS=(
  --silent --show-error
  --aws-sigv4 "aws:amz:${AWS_DEFAULT_REGION}:es"
  --user "${AWS_ACCESS_KEY_ID}:${AWS_SECRET_ACCESS_KEY}"
  --connect-to "${OPENSEARCH_DOMAIN}:443:127.0.0.1:${LOCAL_PORT}"
)
if [ -n "${AWS_SESSION_TOKEN:-}" ]; then
  CURL_OPTS+=(-H "x-amz-security-token: ${AWS_SESSION_TOKEN}")
fi
BASE="https://${OPENSEARCH_DOMAIN}"

os_delete() {
  echo "DELETE $1"
  curl -X DELETE "${BASE}$1" "${CURL_OPTS[@]}"
  echo
}

if [ "$clear_production_locations" = true ]; then
  echo -e "\nDelete production-locations index and template\n"
  os_delete "/production-locations"
  os_delete "/_index_template/production_locations_template"
fi

if [ "$clear_moderation_events" = true ]; then
  echo -e "\nDelete moderation-events index and template\n"
  os_delete "/moderation-events"
  os_delete "/_index_template/moderation_events_template"
fi

#
# Logstash JDBC lock files on EFS (removed on the bastion with Run Command)
#
echo -e "\nRemove the JDBC input lock files from the EFS storage connected to Logstash\n"

remote_script="set -eu
MNT=\$(mktemp -d)
mount -t efs -o tls,accesspoint=${EFS_AP_ID} ${EFS_ID}:/ \"\$MNT\"
trap 'umount \"\$MNT\" && rmdir \"\$MNT\"' EXIT"
if [ "$clear_production_locations" = true ]; then
  remote_script+="
echo 'Remove production_locations_jdbc_last_run lock file'
rm -f \"\$MNT/production_locations_jdbc_last_run\""
fi
if [ "$clear_moderation_events" = true ]; then
  remote_script+="
echo 'Remove moderation_events_jdbc_last_run lock file'
rm -f \"\$MNT/moderation_events_jdbc_last_run\""
fi

params_file="$(mktemp)"
jq -n --arg script "$remote_script" \
  '{commands: ($script | split("\n")), executionTimeout: ["300"]}' >"$params_file"

bastion_id="$(bash "$TUNNEL" bastion-id)"
command_id="$(aws ssm send-command \
  --instance-ids "$bastion_id" \
  --document-name AWS-RunShellScript \
  --comment "Clear Logstash JDBC lock files (${target})" \
  --parameters "file://${params_file}" \
  --query 'Command.CommandId' --output text)"
rm -f "$params_file"
echo "Run Command ${command_id} sent to ${bastion_id}"

status="Pending"
for _ in $(seq 1 60); do
  status="$(aws ssm get-command-invocation \
    --command-id "$command_id" --instance-id "$bastion_id" \
    --query 'Status' --output text 2>/dev/null || echo Pending)"
  case "$status" in
    Pending | InProgress | Delayed) sleep 5 ;;
    *) break ;;
  esac
done

aws ssm get-command-invocation \
  --command-id "$command_id" --instance-id "$bastion_id" \
  --query '[StandardOutputContent, StandardErrorContent]' --output text || true

if [ "$status" != "Success" ]; then
  echo "Run Command ${command_id} finished with status: ${status}" >&2
  exit 1
fi
echo "Lock files removed."
