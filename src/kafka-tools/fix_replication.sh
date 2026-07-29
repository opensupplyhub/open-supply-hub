#!/bin/bash
# One-time fix for the AWS MSK "MinISR = RF" advisory (OSDEV-3063).
#
# Finds every topic whose replication factor is below TARGET_RF, generates a
# partition reassignment plan that adds replicas, and optionally executes it.
# Also reports any topic-level min.insync.replicas override that would still
# leave MinISR == RF after the reassignment.
#
# Run from the kafka-tools image (WORKDIR /opt/kafka_2.13-3.8.0) with
# BOOTSTRAP_SERVERS set, or from any host with the Kafka CLI and broker access.
#
# Usage:
#   ./fix_replication.sh             # dry run: write add-replicas.json, print it
#   ./fix_replication.sh --execute   # apply the reassignment and verify
#
# Env overrides:
#   BROKER_IDS   space-separated MSK broker IDs (default "1 2")
#   TARGET_RF    desired replication factor    (default 2)
#
# Reassignment copies partition data between brokers; run off-peak.
#
# NOTE: --describe covers internal topics (e.g. __consumer_offsets), so they can
# appear in the plan. Review the dry-run output before using --execute.

set -euo pipefail

BROKERS=(${BROKER_IDS:-1 2})
TARGET_RF="${TARGET_RF:-2}"
PLAN_FILE="add-replicas.json"
VERIFY_MAX_ATTEMPTS=120   # 120 x 5s = 10 minutes

if [ -z "${BOOTSTRAP_SERVERS:-}" ]; then
    echo "ERROR: BOOTSTRAP_SERVERS is not set." >&2
    exit 1
fi

if [ "${#BROKERS[@]}" -lt "$TARGET_RF" ]; then
    echo "ERROR: TARGET_RF=$TARGET_RF but only ${#BROKERS[@]} broker(s) given: ${BROKERS[*]}" >&2
    exit 1
fi

describe=$(./bin/kafka-topics.sh --bootstrap-server "$BOOTSTRAP_SERVERS" --describe)

# Warn about topic-level min.insync.replicas overrides. The cluster default
# (min.insync.replicas=1) does not apply to topics that set their own value, so
# these need checking by hand after the reassignment.
overrides=$(echo "$describe" | grep "min.insync.replicas=" || true)
if [ -n "$overrides" ]; then
    echo "WARNING: topics with a topic-level min.insync.replicas override -"
    echo "verify each is below its replication factor once this script finishes:"
    echo "$overrides"
    echo
fi

# Emit "topic partition replica[,replica...]" for partitions of under-replicated
# topics. Fields are located by label rather than position, because the header
# line includes TopicId only on some Kafka versions.
rows=()
mapfile -t rows < <(echo "$describe" | awk -v target="$TARGET_RF" '
    function field(label) {
        for (i = 1; i < NF; i++) if ($i == label) return $(i + 1)
        return ""
    }
    # Topic header line, e.g. "Topic: x  TopicId: y  PartitionCount: 1  ReplicationFactor: 1  Configs: ..."
    $1 == "Topic:" && field("ReplicationFactor:") != "" {
        if (field("ReplicationFactor:") + 0 < target) under[$2] = 1
        next
    }
    # Partition line, e.g. "  Topic: x  Partition: 0  Leader: 1  Replicas: 1  Isr: 1"
    field("Partition:") != "" {
        if (under[$2]) print $2, field("Partition:"), field("Replicas:")
    }
')

if [ ${#rows[@]} -eq 0 ]; then
    echo "No topics below RF=$TARGET_RF. Nothing to reassign."
    exit 0
fi

echo "Found ${#rows[@]} partition(s) below RF=$TARGET_RF."

# Build the plan: keep existing replicas (first stays preferred leader), then
# append brokers not yet holding the partition until we reach TARGET_RF.
{
    printf '{"version":1,"partitions":[\n'
    first=true
    for row in "${rows[@]}"; do
        read -r topic partition replicas <<< "$row"
        new_replicas="$replicas"
        count=$(awk -F, '{print NF}' <<< "$replicas")
        for b in "${BROKERS[@]}"; do
            [ "$count" -ge "$TARGET_RF" ] && break
            if ! echo ",$replicas," | grep -q ",$b,"; then
                new_replicas="$new_replicas,$b"
                count=$((count + 1))
            fi
        done
        if [ "$count" -lt "$TARGET_RF" ]; then
            echo "ERROR: cannot reach RF=$TARGET_RF for $topic-$partition" \
                 "(replicas=$replicas, brokers=${BROKERS[*]})" >&2
            exit 1
        fi
        $first || printf ',\n'
        first=false
        printf '  {"topic":"%s","partition":%s,"replicas":[%s]}' \
            "$topic" "$partition" "$new_replicas"
    done
    printf '\n]}\n'
} > "$PLAN_FILE"

echo "Reassignment plan ($PLAN_FILE):"
cat "$PLAN_FILE"

if [ "${1:-}" != "--execute" ]; then
    echo
    echo "Dry run only. Re-run with --execute to apply."
    exit 0
fi

echo
echo "Executing reassignment..."
./bin/kafka-reassign-partitions.sh --bootstrap-server "$BOOTSTRAP_SERVERS" \
    --reassignment-json-file "$PLAN_FILE" --execute

# kafka-reassign-partitions --verify reports "is still in progress" per pending
# partition; treat absence of that phrase as done.
attempt=0
while :; do
    attempt=$((attempt + 1))
    verify_out=$(./bin/kafka-reassign-partitions.sh \
        --bootstrap-server "$BOOTSTRAP_SERVERS" \
        --reassignment-json-file "$PLAN_FILE" --verify 2>&1 || true)
    if ! echo "$verify_out" | grep -q "still in progress"; then
        echo "$verify_out"
        break
    fi
    if [ "$attempt" -ge "$VERIFY_MAX_ATTEMPTS" ]; then
        echo "$verify_out"
        echo "ERROR: reassignment still in progress after $attempt checks." >&2
        echo "Re-run --verify manually; do not re-run --execute." >&2
        exit 1
    fi
    sleep 5
done

echo
echo "Verifying no topic remains below RF=$TARGET_RF:"
remaining=$(./bin/kafka-topics.sh --bootstrap-server "$BOOTSTRAP_SERVERS" --describe \
    | awk -v target="$TARGET_RF" '
        function field(label) {
            for (i = 1; i < NF; i++) if ($i == label) return $(i + 1)
            return ""
        }
        $1 == "Topic:" && field("ReplicationFactor:") != "" &&
        field("ReplicationFactor:") + 0 < target { print }
    ')
if [ -n "$remaining" ]; then
    echo "$remaining"
    echo "ERROR: some topics are still below RF=$TARGET_RF." >&2
    exit 1
fi
echo "OK - all topics have RF >= $TARGET_RF."
