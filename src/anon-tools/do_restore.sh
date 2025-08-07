#!/bin/bash


aws s3 cp s3://oshub-dumps-anonymized/osh_prod_large_anon.dump /dumps/osh_prod_large.dump

bastion="$(aws ec2 describe-instances --filters "Name=tag:Environment,Values=$ENVIRONMENT" "Name=tag:Name,Values=Bastion" --query 'Reservations[0].Instances[0].PublicDnsName' --output text)"

echo "Bastion: $bastion"

chmod 600 /keys/key

echo "localhost:5433:$DATABASE_NAME:$DATABASE_USERNAME:$DATABASE_PASSWORD" > ~/.pgpass
chmod 600 ~/.pgpass
ssh-keyscan $bastion > ~/.ssh/known_hosts

ssh -f -i /keys/key -L 5433:database.service.osh.internal:5432 -N ec2-user@$bastion

SQL_SCRIPT="DO \$\$
DECLARE
BEGIN
  DROP SCHEMA public CASCADE;
  CREATE SCHEMA public;
  GRANT ALL ON SCHEMA public TO public;
END \$\$;"

echo "Dropping tables"
psql -d $DATABASE_NAME -U $DATABASE_USERNAME -h localhost -p 5433 -c "$SQL_SCRIPT"
pg_restore --verbose --clean --if-exists --no-acl --no-owner -d $DATABASE_NAME -U $DATABASE_USERNAME -h localhost -p 5433 < /dumps/osh_prod_large.dump
