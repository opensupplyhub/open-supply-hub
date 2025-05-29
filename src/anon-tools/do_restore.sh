#!/bin/bash


aws s3 cp s3://oshub-dumps-anonymized-2/osh_prod_large_anon.dump /dumps/osh_prod_large.dump

chmod 600 /keys/key

echo "localhost:5433:$DATABASE_NAME:$DATABASE_USERNAME:$DATABASE_PASSWORD" > ~/.pgpass
chmod 600 ~/.pgpass
ssh-keyscan $BASTION > ~/.ssh/known_hosts

ssh -f -i /keys/key -L 5433:database.service.osh.internal:5432 -N ec2-user@$BASTION

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
