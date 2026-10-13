#!/usr/bin/env bash
# Set the production_locations Logstash JDBC last_run date on AWS.
# Stops Logstash, rewrites the file on EFS through the bastion (SSM), starts Logstash.
#
# Usage: ./set_logstash_last_run.sh <Environment> "<YYYY-MM-DD HH:MM:SS>"   (UTC)
#   e.g. ./set_logstash_last_run.sh Production "2026-10-01 00:00:00"
set -euo pipefail
export MSYS_NO_PATHCONV=1                       # Git Bash: don't rewrite /paths
export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-eu-west-1}"

ENV="${1:?Environment, e.g. Production}"
DATE="${2:?UTC date, e.g. \"2026-10-01 00:00:00\"}"
[[ "$DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}\ [0-9]{2}:[0-9]{2}:[0-9]{2}$ ]] \
  || { echo "Date must look like 2026-10-01 00:00:00"; exit 1; }
VALUE="--- ${DATE}.000000000 Z"
CLUSTER="ecsOpenSupplyHub${ENV}Cluster"
SERVICE="OpenSupplyHub${ENV}AppLogstash"

EFS_ID=$(aws efs describe-file-systems --output text \
  --query "FileSystems[?Tags[?Key=='Environment' && Value=='${ENV}'] && Tags[?Key=='Name' && Value=='efsAppLogstash']].FileSystemId")
EFS_AP_ID=$(aws efs describe-access-points --file-system-id "$EFS_ID" --output text \
  --query 'AccessPoints[0].AccessPointId')
BASTION_ID=$(aws ec2 describe-instances --output text \
  --filters "Name=tag:Environment,Values=${ENV}" "Name=tag:Name,Values=Bastion" "Name=instance-state-name,Values=running" \
  --query 'Reservations[0].Instances[0].InstanceId')
echo "EFS=$EFS_ID  AP=$EFS_AP_ID  bastion=$BASTION_ID  value='$VALUE'"
for v in "$EFS_ID" "$EFS_AP_ID" "$BASTION_ID"; do
  [[ -n "$v" && "$v" != "None" ]] || { echo "Lookup failed, nothing changed."; exit 1; }
done

echo "Stopping Logstash..."
aws ecs update-service --cluster "$CLUSTER" --service "$SERVICE" --desired-count 0 >/dev/null
trap 'echo "Starting Logstash..."; aws ecs update-service --cluster "$CLUSTER" --service "$SERVICE" --desired-count 1 >/dev/null' EXIT
aws ecs wait services-stable --cluster "$CLUSTER" --services "$SERVICE"

REMOTE=$(cat <<EOF
set -eu
MNT=\$(mktemp -d)
mount -t efs -o tls,accesspoint=${EFS_AP_ID} ${EFS_ID}:/ "\$MNT"
trap 'umount "\$MNT"; rmdir "\$MNT"' EXIT
F="\$MNT/production_locations_jdbc_last_run"
echo "before: \$(cat "\$F" 2>/dev/null || echo missing)"
if [ -f "\$F" ]; then cp "\$F" "\$F.bak"; fi
printf '%s\n' '${VALUE}' > "\$F"
echo "after:  \$(cat "\$F")"
EOF
)
B64=$(printf '%s' "$REMOTE" | base64 -w0)

CMD_ID=$(aws ssm send-command --instance-ids "$BASTION_ID" --document-name AWS-RunShellScript \
  --comment "Set production_locations JDBC last_run" \
  --parameters "commands=[\"echo $B64 | base64 -d | bash\"]" \
  --query 'Command.CommandId' --output text)
echo "SSM command: $CMD_ID"

STATUS=Pending
for _ in $(seq 1 60); do
  sleep 5
  STATUS=$(aws ssm get-command-invocation --command-id "$CMD_ID" --instance-id "$BASTION_ID" \
    --query Status --output text 2>/dev/null || echo Pending)
  case "$STATUS" in Pending|InProgress|Delayed) ;; *) break ;; esac
done
aws ssm get-command-invocation --command-id "$CMD_ID" --instance-id "$BASTION_ID" \
  --query '[StandardOutputContent,StandardErrorContent]' --output text
echo "Status: $STATUS"
[ "$STATUS" = "Success" ]
