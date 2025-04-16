#!/bin/bash

chmod 700 /root/.ssh
chmod 600 /root/.ssh/id_rsa
chmod 600 /root/.ssh/config
chown -R root:root /root/.ssh
chmod +x /script/clear_opensearch.sh
echo -e "\nCopy script to Bastion host\n"
scp /script/clear_opensearch.sh ec2-user@$BASTION_IP:
echo -e "\nRun cleaning OpenSearch indexes\n"
ssh ec2-user@$BASTION_IP ./clear_opensearch.sh
