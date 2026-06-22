#!/bin/bash

# This script is necessary to delete the custom OpenSearch indexes,
# templates, and Logstash pipeline lock files in order to apply
# new index mappings or to refresh the OpenSearch cluster after
# restarting Logstash, with the lock files deleted from EFS
# storage for each pipeline.

clear_production_locations="${CLEAR_PRODUCTION_LOCATIONS:-false}"
clear_moderation_events="${CLEAR_MODERATION_EVENTS:-false}"

CURL_OPTS=(--aws-sigv4 "aws:amz:eu-west-1:es" --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY")
BASE="https://$OPENSEARCH_DOMAIN"

if [ "$clear_production_locations" = "true" ]; then
  echo -e "\nDelete production-locations index and template\n"
  curl -X DELETE "$BASE/production-locations" "${CURL_OPTS[@]}"
  curl -X DELETE "$BASE/_index_template/production_locations_template" "${CURL_OPTS[@]}"
fi

if [ "$clear_moderation_events" = "true" ]; then
  echo -e "\nDelete moderation-events index and template\n"
  curl -X DELETE "$BASE/moderation-events" "${CURL_OPTS[@]}"
  curl -X DELETE "$BASE/_index_template/moderation_events_template" "${CURL_OPTS[@]}"
fi

if [ "$clear_production_locations" = "true" ] || [ "$clear_moderation_events" = "true" ]; then
  echo -e "\nRemove the JDBC input lock files from the EFS storage connected to Logstash\n"
  sudo mount -t efs -o tls,accesspoint=$EFS_AP_ID $EFS_ID:/ /mnt
  if [ "$clear_production_locations" = "true" ]; then
    sudo rm -f /mnt/production_locations_jdbc_last_run
  fi
  if [ "$clear_moderation_events" = "true" ]; then
    sudo rm -f /mnt/moderation_events_jdbc_last_run
  fi
  sudo umount /mnt
fi
