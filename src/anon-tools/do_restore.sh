#!/bin/bash

# ls -la /keys
# chmod 600 /keys/id_rsa

# echo "localhost:5433:opensupplyhub:opensupplyhub:" > ~/.pgpass
# chmod 600 ~/.pgpass
# ssh-keyscan ec2-54-154-210-219.eu-west-1.compute.amazonaws.com >> ~/.ssh/known_hosts

# ssh -f -i /keys/id_rsa -L 5433:database.service.osh.internal:5432 -N ec2-user@ec2-54-154-210-219.eu-west-1.compute.amazonaws.com

aws s3 cp s3://oshub-dumps-anonymized/osh_prod_large_anon.dump /dumps/osh_prod_large.dump

aws ec2 describe-instances --filters "Name=tag:Environment,Values=Preprod" --query 'Reservations[*].Instances[*].[InstanceId]' --output text | xargs -I {} aws ec2 start-instances --instance-ids {}