chmod 700 /root/.ssh
chmod 400 /root/.ssh/id_rsa
chmod +x /script/clear_opensearch.sh
scp /script/clear_opensearch.sh ec2-user@$BASTION_IP:
ssh ec2-user@$BASTION_IP ./clear_opensearch.sh
