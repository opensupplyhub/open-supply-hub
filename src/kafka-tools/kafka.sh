#!/bin/bash

# Creates any topics from list.txt that don't exist yet.
# RF=2 with cluster-level min.insync.replicas=1 (MinISR must be < RF so a
# single broker failure doesn't block producers using acks=all).

REPLICATION_FACTOR="${REPLICATION_FACTOR:-2}"
PARTITIONS="${PARTITIONS:-1}"

topics_to_create=($(cat "list.txt"))
existing_topics=$(./bin/kafka-topics.sh --bootstrap-server "$BOOTSTRAP_SERVERS" --list)

for topic in "${topics_to_create[@]}"; do
    # -F is required: topic names contain dots (e.g. dedupe.hub.topic), which as
    # a regex would match any character and could match a different topic,
    # silently skipping a required create.
    if echo "$existing_topics" | grep -qxF "$topic"; then
        echo "$topic topic already exists"
    else
        ./bin/kafka-topics.sh --bootstrap-server "$BOOTSTRAP_SERVERS" \
            --create --topic "$topic" \
            --replication-factor "$REPLICATION_FACTOR" \
            --partitions "$PARTITIONS"
    fi
done
