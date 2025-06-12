CREATE OR REPLACE FUNCTION set_origin_source()
RETURNS trigger AS $$
BEGIN
    IF NEW.origin_source IS NULL THEN
        BEGIN
            NEW.origin_source := current_setting('app.origin_source', true);
        EXCEPTION WHEN others THEN
            NEW.origin_source := 'os_hub';
        END;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
