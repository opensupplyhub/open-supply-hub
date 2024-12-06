#!/bin/bash

# This script is necessary to delete custom OpenSearch indexes,
# templates, and Logstash pipeline lock files in order to apply
# new index mappings or to refresh the OpenSearch cluster after
# restarting Logstash, with the lock files deleted from EFS
# storage for each pipeline.
#
# The script can be modified to delete only specific templates,
# indexes, and Logstash pipeline lock files, allowing for a more
# targeted refresh without affecting the entire OpenSearch cluster.
# This can help speed up the deployment process of new changes.

echo -e "\nDelete custom OpenSearch indexes\n"
curl -X DELETE https://$OPENSEARCH_DOMAIN/production-locations --aws-sigv4 "aws:amz:eu-west-1:es" --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY"
curl -X DELETE https://$OPENSEARCH_DOMAIN/moderation-events --aws-sigv4 "aws:amz:eu-west-1:es" --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY"

echo -e "\nDelete custom OpenSearch templates\n"
curl -X DELETE https://$OPENSEARCH_DOMAIN/_index_template/production_locations_template --aws-sigv4 "aws:amz:eu-west-1:es" --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY"
curl -X DELETE https://$OPENSEARCH_DOMAIN/_index_template/moderation_events_template --aws-sigv4 "aws:amz:eu-west-1:es" --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY"

echo -e "\nRemove the JDBC input lock files from the EFS storage connected to Logstash\n"
sudo mount -t efs -o tls,accesspoint=$EFS_AP_ID $EFS_ID:/ /mnt
sudo rm /mnt/production_locations_jdbc_last_run
sudo rm /mnt/moderation_events_jdbc_last_run
sudo umount /mnt
