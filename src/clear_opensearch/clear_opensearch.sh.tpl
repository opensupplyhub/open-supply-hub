#!/bin/bash
curl -X DELETE https://$OPENSEARCH_DOMAIN/production-locations --aws-sigv4 "aws:amz:eu-west-1:es" --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY"
sudo mount -t efs -o tls,accesspoint=$EFS_AP_ID $EFS_ID:/ /mnt
sudo rm /mnt/logstash_jdbc_last_run
sudo umount /mnt
