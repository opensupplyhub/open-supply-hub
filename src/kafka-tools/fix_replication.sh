#!/bin/bash
# One-time fix for the AWS MSK "MinISR = RF" advisory (OSDEV-3063).
#
# The advisory condition is min.insync.replicas >= replication factor. Two
# separate things can cause it, and both are handled here:
#
#   1. Replication factor too low (RF=1 topics created by kafka.sh). Fixed by a
#      partition reassignment that adds replicas.
#   2. A topic-level min.insync.replicas override. The MSK cluster default set in
#      kafka.tf does NOT apply to these topics, so raising RF alone leaves them
#      non-compliant. Fixed with kafka-configs.sh --alter.
#
# Invariant enforced at the end: every topic satisfies
#   min.insync.replicas <= replication factor - 1
#
# Run from the kafka-tools image (WORKDIR /opt/kafka_2.13-3.8.0) with
# BOOTSTRAP_SERVERS set, or from any host with the Kafka CLI and broker access.
#
# Usage:
#   ./fix_replication.sh             # dry run: print the full plan, change nothing
#   ./fix_replication.sh --execute   # apply reassignment + config repairs, then verify
#
# Env overrides:
#   BROKER_IDS   space-separated MSK broker IDs (default "1 2")
#   TARGET_RF    replication factor to raise under-replicated topics to (default 2)
#
# NOTE: reassignment copies partition data between brokers; run off-peak.
# NOTE: --describe covers internal topics (e.g. __consumer_offsets), so they can
#       appear in the plan. Review the dry-run output before using --execute.

set -euo pipefail

# word-split intended
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

# MinISR <= RF-1 is unsatisfiable below RF=2: the repair target would be
# min.insync.replicas=0, which Kafka rejects (minimum is 1).
if [ "$TARGET_RF" -lt 2 ]; then
    echo "ERROR: TARGET_RF=$TARGET_RF cannot satisfy MinISR <= RF-1; use 2 or more." >&2
    exit 1
fi

# Locates fields by label because the header line includes TopicId only on some
# Kafka versions, so positional parsing is not portable.
AWK_FIELD='
    function field(label) {
        for (i = 1; i < NF; i++) if ($i == label) return $(i + 1)
        return ""
    }
    function minisr(line,   s, p) {
        if (match(line, /min\.insync\.replicas=[0-9]+/)) {
            s = substr(line, RSTART, RLENGTH)
            split(s, p, "=")
            return p[2]
        }
        return "-"
    }
'

describe=$(./bin/kafka-topics.sh --bootstrap-server "$BOOTSTRAP_SERVERS" --describe)

# --- Plan part 1: partitions needing more replicas -------------------------

rows=()
mapfile -t rows < <(echo "$describe" | awk -v target="$TARGET_RF" "$AWK_FIELD"'
    $1 == "Topic:" && field("ReplicationFactor:") != "" {
        if (field("ReplicationFactor:") + 0 < target) under[$2] = 1
        next
    }
    field("Partition:") != "" {
        if (under[$2]) print $2, field("Partition:"), field("Replicas:")
    }
')

# --- Plan part 2: topic-level min.insync.replicas overrides to repair ------
#
# A topic's RF after this script runs is max(current RF, TARGET_RF), so the
# highest compliant MinISR is that value minus one. Only topics that set their
# own override are listed; the rest inherit the compliant cluster default.

repairs=()
mapfile -t repairs < <(echo "$describe" | awk -v target="$TARGET_RF" "$AWK_FIELD"'
    $1 == "Topic:" && field("ReplicationFactor:") != "" {
        rf = field("ReplicationFactor:") + 0
        eff_rf = (rf < target) ? target : rf
        m = minisr($0)
        if (m != "-" && m + 0 > eff_rf - 1) print $2, m, eff_rf - 1
    }
')

if [ ${#rows[@]} -eq 0 ] && [ ${#repairs[@]} -eq 0 ]; then
    echo "Nothing to do: no topic is below RF=$TARGET_RF and no topic-level"
    echo "min.insync.replicas override violates MinISR <= RF-1."
    exit 0
fi

echo "=== PLAN ==="
echo

if [ ${#rows[@]} -gt 0 ]; then
    echo "Partition reassignments (${#rows[@]} partition(s) below RF=$TARGET_RF):"
else
    echo "Partition reassignments: none needed."
fi

# Build the reassignment plan: keep existing replicas (first stays preferred
# leader), then append brokers not already holding the partition.
if [ ${#rows[@]} -gt 0 ]; then
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
    cat "$PLAN_FILE"
fi

echo
if [ ${#repairs[@]} -gt 0 ]; then
    echo "Topic-level min.insync.replicas repairs (${#repairs[@]} topic(s)):"
    for r in "${repairs[@]}"; do
        read -r topic current wanted <<< "$r"
        echo "  $topic: min.insync.replicas $current -> $wanted"
    done
    echo
    echo "  NOTE: lowering MinISR trades durability for availability. On a"
    echo "  ${#BROKERS[@]}-broker cluster it is the only compliant option, since RF cannot"
    echo "  exceed the broker count. Raising RF instead requires more brokers."
else
    echo "Topic-level min.insync.replicas repairs: none needed."
fi

echo
if [ "${1:-}" != "--execute" ]; then
    echo "Dry run only. Re-run with --execute to apply."
    exit 0
fi

# --- Apply -----------------------------------------------------------------

# Config repairs go FIRST. An RF=1 topic carrying min.insync.replicas=2 rejects
# every acks=all write right now, and it keeps rejecting them throughout the
# reassignment (the new replica is not in sync until it catches up). Lowering
# MinISR first unblocks producers immediately; doing it last would leave those
# topics failing for the whole duration of the data copy.
for r in "${repairs[@]}"; do
    read -r topic current wanted <<< "$r"
    echo "Setting min.insync.replicas=$wanted on $topic (was $current)..."
    ./bin/kafka-configs.sh --bootstrap-server "$BOOTSTRAP_SERVERS" \
        --entity-type topics --entity-name "$topic" \
        --alter --add-config "min.insync.replicas=$wanted"
done

if [ ${#rows[@]} -gt 0 ]; then
    echo "Executing reassignment..."
    ./bin/kafka-reassign-partitions.sh --bootstrap-server "$BOOTSTRAP_SERVERS" \
        --reassignment-json-file "$PLAN_FILE" --execute

    # --verify reports one line per planned partition, in one of several states:
    #   "Reassignment of partition X is complete[d]."          -> success
    #   "Reassignment of partition X is still in progress."    -> keep polling
    #   "Reassignment of partition X failed."                  -> terminal failure
    #   "There is no active reassignment of partition X, but
    #    replica set is A rather than B."                      -> terminal failure
    #
    # Completion is therefore only established by counting explicit successes
    # against the number of partitions in the plan. Inferring it from the absence
    # of "still in progress" would treat a failure state, or a CLI error such as
    # a dropped connection, as a finished reassignment.
    expected=${#rows[@]}
    attempt=0
    while :; do
        attempt=$((attempt + 1))

        set +e
        verify_out=$(./bin/kafka-reassign-partitions.sh \
            --bootstrap-server "$BOOTSTRAP_SERVERS" \
            --reassignment-json-file "$PLAN_FILE" --verify 2>&1)
        verify_status=$?
        set -e

        if [ "$verify_status" -ne 0 ]; then
            echo "$verify_out"
            echo "ERROR: --verify exited with status $verify_status." >&2
            echo "The reassignment is likely still running on the brokers. Re-check with:" >&2
            echo "  ./bin/kafka-reassign-partitions.sh --bootstrap-server \$BOOTSTRAP_SERVERS \\" >&2
            echo "    --reassignment-json-file $PLAN_FILE --verify" >&2
            echo "Do NOT re-run --execute." >&2
            exit 1
        fi

        if echo "$verify_out" | grep -Eqi "failed|no active reassignment"; then
            echo "$verify_out"
            echo "ERROR: reassignment reported a terminal failure state." >&2
            exit 1
        fi

        # "is complete" matches both "is complete." and "is completed."
        completed=$(echo "$verify_out" | grep -c "is complete" || true)
        in_progress=$(echo "$verify_out" | grep -c "still in progress" || true)

        if [ "$completed" -eq "$expected" ] && [ "$in_progress" -eq 0 ]; then
            echo "$verify_out"
            echo "All $completed of $expected partition reassignment(s) completed."
            break
        fi

        if [ "$attempt" -ge "$VERIFY_MAX_ATTEMPTS" ]; then
            echo "$verify_out"
            echo "ERROR: after $attempt checks, only $completed of $expected partition(s)" >&2
            echo "reported completion ($in_progress still in progress)." >&2
            echo "Re-run --verify manually; do not re-run --execute." >&2
            exit 1
        fi

        echo "Waiting: $completed/$expected completed, $in_progress in progress ($(date +%T))"
        sleep 5
    done
fi

# --- Verify the invariant --------------------------------------------------

echo
echo "=== VERIFICATION ==="
violations=$(./bin/kafka-topics.sh --bootstrap-server "$BOOTSTRAP_SERVERS" --describe \
    | awk -v target="$TARGET_RF" "$AWK_FIELD"'
        $1 == "Topic:" && field("ReplicationFactor:") != "" {
            rf = field("ReplicationFactor:") + 0
            m = minisr($0)
            if (rf < target)
                printf "%s: RF=%d is below target %d\n", $2, rf, target
            else if (m != "-" && m + 0 > rf - 1)
                printf "%s: min.insync.replicas=%s violates MinISR <= RF-1 (RF=%d)\n", $2, m, rf
        }
    ')

if [ -n "$violations" ]; then
    echo "$violations" >&2
    echo "ERROR: cluster is still non-compliant with the advisory." >&2
    exit 1
fi

echo "OK - every topic has RF >= $TARGET_RF and min.insync.replicas <= RF-1."
