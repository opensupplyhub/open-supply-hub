DO $$
DECLARE
    current_table text;
    column_exists_email boolean;
    column_exists_username boolean;
    column_exists_password boolean;
    column_exists_phone_number boolean;
    rows_updated integer;
BEGIN
    FOR current_table IN (SELECT table_name FROM information_schema.tables WHERE table_schema = 'public')
    LOOP
        EXECUTE 'SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = ''' || current_table || ''' AND column_name = ''email'')' INTO column_exists_email;
        EXECUTE 'SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = ''' || current_table || ''' AND column_name = ''username'')' INTO column_exists_username;
        EXECUTE 'SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = ''' || current_table || ''' AND column_name = ''password'')' INTO column_exists_password;
        EXECUTE 'SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = ''' || current_table || ''' AND column_name = ''phone_number'')' INTO column_exists_phone_number;

        IF column_exists_email THEN
            -- Update email column
            EXECUTE 'UPDATE ' || current_table || ' SET
                email = CASE WHEN email NOT LIKE ''%@speedandfunction.com'' AND email NOT LIKE ''%@opensupplyhub.org'' THEN md5(random()::text) || ''@'' || substring(email from position(''@'' in email) + 1) ELSE email END';

            -- Update username column
            IF column_exists_username THEN
                EXECUTE 'UPDATE ' || current_table || ' SET
                    username = CASE WHEN email NOT LIKE ''%@speedandfunction.com'' AND email NOT LIKE ''%@opensupplyhub.org'' THEN substr(md5(random()::text), 1, 20) ELSE username END';
            END IF;

            -- Update password column
            IF column_exists_password THEN
                EXECUTE 'UPDATE ' || current_table || ' SET
                    password = CASE WHEN email NOT LIKE ''%@speedandfunction.com'' AND email NOT LIKE ''%@opensupplyhub.org'' THEN md5(random()::text) ELSE password END';
            END IF;

            -- Update phone_number column
            IF column_exists_phone_number THEN
                EXECUTE 'UPDATE ' || current_table || ' SET
                    phone_number = CASE WHEN email NOT LIKE ''%@speedandfunction.com'' AND email NOT LIKE ''%@opensupplyhub.org'' THEN md5(random()::text) ELSE phone_number END';
            END IF;

            -- Output the number of rows updated
            GET DIAGNOSTICS rows_updated = ROW_COUNT;
            RAISE NOTICE 'Updated % rows in table %', rows_updated, current_table;

        ELSE
            IF column_exists_username THEN
                EXECUTE 'UPDATE ' || current_table || ' SET
                    username = substr(md5(random()::text), 1, 20)';
            END IF;

            IF column_exists_password THEN
                EXECUTE 'UPDATE ' || current_table || ' SET
                    password = md5(random()::text)';
            END IF;

            IF column_exists_phone_number THEN
                EXECUTE 'UPDATE ' || current_table || ' SET
                    phone_number = md5(random()::text)';
            END IF;

            -- Output the number of rows updated
            GET DIAGNOSTICS rows_updated = ROW_COUNT;
            RAISE NOTICE 'Updated % rows in table %', rows_updated, current_table;
        END IF;
    END LOOP;
END $$;
