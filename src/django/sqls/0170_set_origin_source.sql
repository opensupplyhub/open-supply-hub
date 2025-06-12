CREATE OR REPLACE FUNCTION set_origin_source()
RETURNS trigger AS $$
BEGIN
    BEGIN
        NEW.origin_source := current_setting('app.origin_source', true);
    EXCEPTION WHEN others THEN
        NEW.origin_source := 'os_hub';
    END;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
