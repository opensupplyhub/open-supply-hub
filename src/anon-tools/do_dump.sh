#!/bin/bash

bastion="$(AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID_PROD \
           AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY_PROD \
           AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION_PROD \
           aws ec2 describe-instances --filters "Name=tag:Environment,Values=Production" --query 'Reservations[0].Instances[0].PublicDnsName' --output text)"

echo "Bastion: $bastion"
ssh-keyscan $bastion > ~/.ssh/known_hosts

echo "localhost:5433:$DATABASE_NAME:$DATABASE_USERNAME:$DATABASE_PASSWORD" > ~/.pgpass
chmod 600 ~/.pgpass


chmod 600 /keys/key
ssh -f -i /keys/key -L 5433:database.service.osh.internal:5432 -N ec2-user@$bastion

pg_dump --clean --no-owner --no-privileges -Fc -h localhost  -d $DATABASE_NAME -U $DATABASE_USERNAME -p 5433 -f /dumps/osh_prod_large.dump -w --verbose
ls -la /dumps

echo "Start anonymization"

docker-entrypoint.sh -c 'shared_buffers=2048MB' -c 'max_connections=10' &

sleep 15s
pg_isready -d anondb -U anondb -h localhost -p 5432

SQL_SCRIPT="DO \$\$
DECLARE
    current_table text;
    column_exists_email boolean;
    column_exists_username boolean;
    column_exists_password boolean;
    column_exists_phone_number boolean;
BEGIN
    FOR current_table IN (SELECT table_name FROM information_schema.tables WHERE table_schema = 'public')
    LOOP
        EXECUTE 'SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = ''' || current_table || ''' AND column_name = ''email'')' INTO column_exists_email;
        EXECUTE 'SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = ''' || current_table || ''' AND column_name = ''username'')' INTO column_exists_username;
        EXECUTE 'SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = ''' || current_table || ''' AND column_name = ''password'')' INTO column_exists_password;
        EXECUTE 'SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = ''' || current_table || ''' AND column_name = ''phone_number'')' INTO column_exists_phone_number;

        IF column_exists_email THEN
            EXECUTE 'UPDATE ' || current_table || ' SET 
                email = CASE WHEN email NOT LIKE ''%@speedandfunction.com'' AND email NOT LIKE ''%@opensupplyhub.org'' THEN md5(random()::text) || ''@'' || substring(email from position(''@'' in email) + 1) ELSE email END';

            IF column_exists_username THEN
                EXECUTE 'UPDATE ' || current_table || ' SET 
                    username = CASE WHEN email NOT LIKE ''%@speedandfunction.com'' AND email NOT LIKE ''%@opensupplyhub.org'' THEN substr(md5(random()::text), 1, 20) ELSE username END';
            END IF;

            IF column_exists_password THEN
                EXECUTE 'UPDATE ' || current_table || ' SET 
                    password = CASE WHEN email NOT LIKE ''%@speedandfunction.com'' AND email NOT LIKE ''%@opensupplyhub.org'' THEN md5(random()::text) ELSE password END';
            END IF;

            IF column_exists_phone_number THEN
                EXECUTE 'UPDATE ' || current_table || ' SET 
                    phone_number = CASE WHEN email NOT LIKE ''%@speedandfunction.com'' AND email NOT LIKE ''%@opensupplyhub.org'' THEN md5(random()::text) ELSE phone_number END';
            END IF;
        END IF;
    END LOOP;
END \$\$;"


pg_restore --verbose --clean --if-exists --no-acl --no-owner -d anondb -U anondb -h localhost -p 5432 < /dumps/osh_prod_large.dump
psql -U anondb -d anondb -h localhost -p 5432 -c "$SQL_SCRIPT"
pg_dump --clean --no-owner --no-privileges -Fc -d anondb -U anondb  -f /dumps/osh_prod_large_anonimized.dump -w --verbose

ls -la /dumps

echo "Finished anonymization"

AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID_TEST \
    AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY_TEST \
    AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION_TEST \
    aws s3 cp /dumps/osh_prod_large_anonimized.dump s3://oshub-dumps-anonymized/osh_prod_large_anon.dump
