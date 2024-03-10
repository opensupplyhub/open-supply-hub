# pg_dump --clean --no-owner --no-privileges -Fc -h host.docker.internal -U opensupplyhub -p 5433 -f /dumps/osh_prod_large.dump -w --verbose
## echo "Running anonymize script" > /dumps/dump.dump


docker-entrypoint.sh -c 'shared_buffers=2048MB' -c 'max_connections=10' &


sleep 5s
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
                email = CASE WHEN email NOT LIKE ''%@speedandfuncion.com'' AND email NOT LIKE ''%@opensupplyhub.com'' THEN md5(random()::text) || ''@'' || substring(email from position(''@'' in email) + 1) ELSE email END';

            IF column_exists_username THEN
                EXECUTE 'UPDATE ' || current_table || ' SET 
                    username = CASE WHEN email NOT LIKE ''%@speedandfuncion.com'' AND email NOT LIKE ''%@opensupplyhub.com'' THEN substr(md5(random()::text), 1, 20) ELSE username END';
            END IF;

            IF column_exists_password THEN
                EXECUTE 'UPDATE ' || current_table || ' SET 
                    password = CASE WHEN email NOT LIKE ''%@speedandfuncion.com'' AND email NOT LIKE ''%@opensupplyhub.com'' THEN md5(random()::text) ELSE password END';
            END IF;

            IF column_exists_phone_number THEN
                EXECUTE 'UPDATE ' || current_table || ' SET 
                    phone_number = CASE WHEN email NOT LIKE ''%@speedandfuncion.com'' AND email NOT LIKE ''%@opensupplyhub.com'' THEN md5(random()::text) ELSE phone_number END';
            END IF;
        END IF;
    END LOOP;
END \$\$;"


pg_restore --verbose --clean --no-acl --no-owner -d anondb -U anondb -h localhost -p 5432 < /dumps/osh_prod_large.dump
psql -U anondb -d anondb -h localhost -p 5432 -c "$SQL_SCRIPT"
pg_dump --clean --no-owner --no-privileges -Fc -d anondb -U anondb  -f /dumps/osh_prod_large_res.dump -w --verbose

echo "Finshed anonymization"