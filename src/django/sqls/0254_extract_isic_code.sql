CREATE OR REPLACE FUNCTION extract_isic_code(raw_string TEXT)
RETURNS TEXT
LANGUAGE plpgsql
IMMUTABLE
AS $Body$
DECLARE
    trimmed TEXT;
    code TEXT;
BEGIN
    IF raw_string IS NULL THEN
        RETURN NULL;
    END IF;

    trimmed := btrim(raw_string);
    IF trimmed = '' THEN
        RETURN NULL;
    END IF;

    IF trimmed ~ '^\s*([A-Za-z]|\d+)\s*-\s+' THEN
        code := substring(trimmed FROM '^\s*([A-Za-z]|\d+)\s*-\s+');
        IF code ~ '^[A-Za-z]$' THEN
            RETURN upper(code);
        END IF;
        RETURN code;
    END IF;

    IF trimmed ~ '^[A-Za-z]$' THEN
        RETURN upper(trimmed);
    END IF;

    IF trimmed ~ '^\d+$' THEN
        RETURN trimmed;
    END IF;

    RETURN NULL;
END;
$Body$;
