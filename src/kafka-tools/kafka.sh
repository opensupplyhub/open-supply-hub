#!/bin/bash

# aws s3 cp

# bootstrap-server=$bs
# run=${./bin/kafka-topics.sh --bootstrap-server $bs --command-config ssl.config}

topics_to_create=($(cat "list.txt"))
topics_are_exist=$(./bin/kafka-topics.sh --bootstrap-server $BOOTSTRAP_SERVERS  --list)

for element in "${topics_to_create[@]}"; do
    for topic in "${topics_are_exist[@]}"; do
        if [[ "$element" == "$topic" ]]; then
            echo "$element topic already exist"
        else
            ./bin/kafka-topics.sh --bootstrap-server $BOOTSTRAP_SERVERS --replication-factor 1 --partitions 1 --topic $element  --create
        fi
    done
done