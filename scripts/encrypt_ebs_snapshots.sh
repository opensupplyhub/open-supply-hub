#!/usr/bin/env bash
#
# encrypt_ebs_snapshots.sh
#
# One-time backfill: finds self-owned UNENCRYPTED EBS snapshots and creates
# encrypted copies (preserving tags + description). AMI-backed snapshots are
# skipped (deleting them breaks the AMI). Deletion of the originals is NOT
# automated — the script prints reviewed delete commands for you to run once
# the encrypted copies show as "completed".
#
# Requires: awscli v2, jq
#
# Usage:
#   ./encrypt_ebs_snapshots.sh                           # scans eu-west-1
#   REGION=eu-west-1 ./encrypt_ebs_snapshots.sh
#   KMS_KEY_ID=alias/my-cmk ./encrypt_ebs_snapshots.sh   # use a CMK instead of aws/ebs
#
set -euo pipefail

command -v jq >/dev/null || { echo "jq is required"; exit 1; }

ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
REGION="${REGION:-eu-west-1}"

cleanup_commands=""

echo "── Scanning ${REGION} ─────────────────────────────"

  unencrypted=$(aws ec2 describe-snapshots \
    --region "$REGION" \
    --owner-ids "$ACCOUNT_ID" \
    --query "Snapshots[?Encrypted==\`false\`].SnapshotId" \
    --output text)

  if [ -z "$unencrypted" ]; then
    echo "🟢 No unencrypted snapshots."
    exit 0
  fi

  # Snapshots referenced by self-owned AMIs — must not be copied/deleted here.
  ami_snaps=$(aws ec2 describe-images \
    --region "$REGION" \
    --owners "$ACCOUNT_ID" \
    --query 'Images[].BlockDeviceMappings[].Ebs.SnapshotId' \
    --output text)

  for snap in $unencrypted; do
    if grep -qw "$snap" <<< "$ami_snaps"; then
      echo "  ⏭️  $snap is AMI-backed — skipping (handle AMI re-encryption separately)."
      continue
    fi

    echo "  → Copying $snap ..."
    desc=$(aws ec2 describe-snapshots --region "$REGION" --snapshot-ids "$snap" \
             --query 'Snapshots[0].Description' --output text)

    # Build copy-snapshot args (optional CMK)
    copy_args=(--region "$REGION" --source-region "$REGION" \
               --source-snapshot-id "$snap" --encrypted \
               --description "Encrypted copy of ${snap}: ${desc}")
    [ -n "${KMS_KEY_ID:-}" ] && copy_args+=(--kms-key-id "$KMS_KEY_ID")

    if ! new_snap=$(aws ec2 copy-snapshot "${copy_args[@]}" \
                      --query SnapshotId --output text 2>/dev/null); then
      echo "    ❌ copy failed for $snap — leaving source untouched."
      continue
    fi
    echo "    🟢 Encrypted copy initiated: $new_snap"

    # Preserve original tags (excluding AWS-reserved 'aws:*' keys) + record provenance
    tags=$(aws ec2 describe-snapshots --region "$REGION" --snapshot-ids "$snap" \
             --query 'Snapshots[0].Tags' --output json \
             | jq -c '[.[]? | select(.Key | startswith("aws:") | not)]')
    if [ "$tags" != "[]" ]; then
      aws ec2 create-tags --region "$REGION" --resources "$new_snap" --tags "$tags"
    fi
    aws ec2 create-tags --region "$REGION" --resources "$new_snap" \
      --tags "Key=source-snapshot-id,Value=${snap}"

    cleanup_commands="${cleanup_commands}aws ec2 delete-snapshot --region ${REGION} --snapshot-id ${snap}  # replaced by ${new_snap}\n"
  done

if [ -z "$cleanup_commands" ]; then
  echo -e "\n🎉 Nothing to clean up."
  exit 0
fi

echo -e "\n🎉 Copies initiated. Verify each new snapshot shows 'completed' (aws ec2 wait snapshot-completed --snapshot-ids <id>), then delete the originals:\n"
echo -e "$cleanup_commands"
