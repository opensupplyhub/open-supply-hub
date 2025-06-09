CREATE OR REPLACE FUNCTION set_origin_source()
RETURNS trigger AS $$
DECLARE
    origin TEXT;
BEGIN
    BEGIN
        origin := current_setting('app.origin_source', true);
    EXCEPTION WHEN others THEN
        origin := 'os_hub';
    END;

    EXECUTE format(
        'UPDATE %I SET origin_source = $1 WHERE origin_source IS NULL',
        TG_TABLE_NAME
    )
    USING origin;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;