CREATE OR REPLACE FUNCTION isic_4_entry_elements(af_id TEXT)
RETURNS SETOF jsonb
LANGUAGE plpgsql
STABLE
AS $Body$
DECLARE
    isic_field_name constant text := 'isic_4';
    raw_value_key constant text := 'raw_value';
BEGIN
    RETURN QUERY
    SELECT elem
    FROM api_extendedfield aef,
    LATERAL jsonb_array_elements(
        CASE jsonb_typeof(aef.value -> raw_value_key)
            WHEN 'array' THEN aef.value -> raw_value_key
            ELSE jsonb_build_array(aef.value -> raw_value_key)
        END
    ) AS elem
    WHERE aef.facility_id = af_id
      AND aef.field_name = isic_field_name
      AND aef.value ? raw_value_key
      AND jsonb_typeof(aef.value -> raw_value_key) IN ('array', 'object');
END;
$Body$;


CREATE OR REPLACE FUNCTION index_isic_level_code(af_id TEXT, level_key TEXT)
RETURNS SETOF TEXT
LANGUAGE sql
STABLE
AS $Body$
    SELECT DISTINCT extract_isic_code(elem ->> level_key)
    FROM isic_4_entry_elements(af_id) AS elem
    WHERE extract_isic_code(elem ->> level_key) IS NOT NULL;
$Body$;


CREATE OR REPLACE FUNCTION index_isic_class(af_id TEXT)
RETURNS TABLE (isic_class TEXT)
LANGUAGE sql
STABLE
AS $Body$
    SELECT index_isic_level_code(af_id, 'class');
$Body$;


CREATE OR REPLACE FUNCTION index_isic_group(af_id TEXT)
RETURNS TABLE (isic_group TEXT)
LANGUAGE sql
STABLE
AS $Body$
    SELECT DISTINCT derived.isic_group
    FROM (
        SELECT COALESCE(
            CASE
                WHEN extract_isic_code(elem ->> 'group') ~ '^\d{3}$'
                    THEN extract_isic_code(elem ->> 'group')
            END,
            CASE
                WHEN extract_isic_code(elem ->> 'class') ~ '^\d{4}$'
                    THEN left(extract_isic_code(elem ->> 'class'), 3)
            END
        ) AS isic_group
        FROM isic_4_entry_elements(af_id) AS elem
    ) AS derived
    WHERE derived.isic_group IS NOT NULL;
$Body$;


CREATE OR REPLACE FUNCTION index_isic_division(af_id TEXT)
RETURNS TABLE (isic_division TEXT)
LANGUAGE sql
STABLE
AS $Body$
    SELECT DISTINCT derived.isic_division
    FROM (
        SELECT COALESCE(
            CASE
                WHEN extract_isic_code(elem ->> 'division') ~ '^\d{2}$'
                    THEN extract_isic_code(elem ->> 'division')
            END,
            CASE
                WHEN extract_isic_code(elem ->> 'group') ~ '^\d{3}$'
                    THEN left(extract_isic_code(elem ->> 'group'), 2)
            END,
            CASE
                WHEN extract_isic_code(elem ->> 'class') ~ '^\d{4}$'
                    THEN left(extract_isic_code(elem ->> 'class'), 2)
            END
        ) AS isic_division
        FROM isic_4_entry_elements(af_id) AS elem
    ) AS derived
    WHERE derived.isic_division IS NOT NULL;
$Body$;


CREATE OR REPLACE FUNCTION isic_rev4_section_for_division(
    division_code TEXT
)
RETURNS TEXT
LANGUAGE sql
IMMUTABLE
AS $Body$
    SELECT CASE
        WHEN division_code !~ '^\d{2}$' THEN NULL
        WHEN division_code::INTEGER BETWEEN 1 AND 3 THEN 'A'
        WHEN division_code::INTEGER BETWEEN 5 AND 9 THEN 'B'
        WHEN division_code::INTEGER BETWEEN 10 AND 33 THEN 'C'
        WHEN division_code::INTEGER = 35 THEN 'D'
        WHEN division_code::INTEGER BETWEEN 36 AND 39 THEN 'E'
        WHEN division_code::INTEGER BETWEEN 41 AND 43 THEN 'F'
        WHEN division_code::INTEGER BETWEEN 45 AND 47 THEN 'G'
        WHEN division_code::INTEGER BETWEEN 49 AND 53 THEN 'H'
        WHEN division_code::INTEGER BETWEEN 55 AND 56 THEN 'I'
        WHEN division_code::INTEGER BETWEEN 58 AND 63 THEN 'J'
        WHEN division_code::INTEGER BETWEEN 64 AND 66 THEN 'K'
        WHEN division_code::INTEGER = 68 THEN 'L'
        WHEN division_code::INTEGER BETWEEN 69 AND 75 THEN 'M'
        WHEN division_code::INTEGER BETWEEN 77 AND 82 THEN 'N'
        WHEN division_code::INTEGER = 84 THEN 'O'
        WHEN division_code::INTEGER = 85 THEN 'P'
        WHEN division_code::INTEGER BETWEEN 86 AND 88 THEN 'Q'
        WHEN division_code::INTEGER BETWEEN 90 AND 93 THEN 'R'
        WHEN division_code::INTEGER BETWEEN 94 AND 96 THEN 'S'
        WHEN division_code::INTEGER BETWEEN 97 AND 98 THEN 'T'
        WHEN division_code::INTEGER = 99 THEN 'U'
        ELSE NULL
    END;
$Body$;


CREATE OR REPLACE FUNCTION index_isic_section(af_id TEXT)
RETURNS TABLE (isic_section TEXT)
LANGUAGE sql
STABLE
AS $Body$
    SELECT DISTINCT derived.isic_section
    FROM (
        SELECT COALESCE(
            CASE
                WHEN extract_isic_code(elem ->> 'section') ~ '^[A-Z]$'
                    THEN extract_isic_code(elem ->> 'section')
            END,
            isic_rev4_section_for_division(
                COALESCE(
                    CASE
                        WHEN extract_isic_code(
                            elem ->> 'division'
                        ) ~ '^\d{2}$'
                            THEN extract_isic_code(elem ->> 'division')
                    END,
                    CASE
                        WHEN extract_isic_code(
                            elem ->> 'group'
                        ) ~ '^\d{3}$'
                            THEN left(
                                extract_isic_code(elem ->> 'group'),
                                2
                            )
                    END,
                    CASE
                        WHEN extract_isic_code(
                            elem ->> 'class'
                        ) ~ '^\d{4}$'
                            THEN left(
                                extract_isic_code(elem ->> 'class'),
                                2
                            )
                    END
                )
            )
        ) AS isic_section
        FROM isic_4_entry_elements(af_id) AS elem
    ) AS derived
    WHERE derived.isic_section IS NOT NULL;
$Body$;
