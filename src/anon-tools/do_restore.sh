#!/bin/bash


aws s3 cp s3://oshub-dumps-anonymized/osh_prod_large_anon.dump /dumps/osh_prod_large.dump

bastion="$(aws ec2 describe-instances --filters "Name=tag:Environment,Values=$ENVIRONMENT" --query 'Reservations[0].Instances[0].PublicDnsName' --output text)"

echo "Bastion: $bastion"
ls -la
cd /keys
ls -la


chmod 600 /keys/key

echo "localhost:5433:$DATABASE_NAME:$DATABASE_USERNAME:$DATABASE_PASSWORD" > ~/.pgpass
chmod 600 ~/.pgpass
ssh-keyscan $bastion >> ~/.ssh/known_hosts

ssh -f -i /keys/id_rsa -L 5433:database.service.osh.internal:5432 -N ec2-user@ec2-54-154-210-219.eu-west-1.compute.amazonaws.com

pg_restore --verbose --clean --no-acl --no-owner -d $DATABASE_NAME -U $DATABASE_USERNAME -h localhost -p 5433 < /dumps/osh_prod_large.dump