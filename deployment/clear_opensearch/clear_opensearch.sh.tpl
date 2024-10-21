#!/bin/bash
echo -e "\nDelete OpenSearch indexes\n"
curl -X DELETE https://$OPENSEARCH_DOMAIN/production-locations --aws-sigv4 "aws:amz:eu-west-1:es" --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY"
curl -X DELETE https://$OPENSEARCH_DOMAIN/moderation-events --aws-sigv4 "aws:amz:eu-west-1:es" --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY"

echo -e "\nRemove the JDBC input lock files from the EFS connected to Logstash\n"
sudo mount -t efs -o tls,accesspoint=$EFS_AP_ID $EFS_ID:/ /mnt
sudo rm /mnt/production_locations_jdbc_last_run
sudo rm /mnt/moderation_events_jdbc_last_run
sudo umount /mnt
