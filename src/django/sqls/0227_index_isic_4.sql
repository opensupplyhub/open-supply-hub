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


CREATE OR REPLACE FUNCTION index_isic_section(af_id TEXT)
RETURNS TABLE (isic_section TEXT)
LANGUAGE sql
STABLE
AS $Body$
    SELECT index_isic_level_code(af_id, 'section');
$Body$;


CREATE OR REPLACE FUNCTION index_isic_division(af_id TEXT)
RETURNS TABLE (isic_division TEXT)
LANGUAGE sql
STABLE
AS $Body$
    SELECT index_isic_level_code(af_id, 'division');
$Body$;


CREATE OR REPLACE FUNCTION index_isic_group(af_id TEXT)
RETURNS TABLE (isic_group TEXT)
LANGUAGE sql
STABLE
AS $Body$
    SELECT index_isic_level_code(af_id, 'group');
$Body$;


CREATE OR REPLACE FUNCTION index_isic_class(af_id TEXT)
RETURNS TABLE (isic_class TEXT)
LANGUAGE sql
STABLE
AS $Body$
    SELECT index_isic_level_code(af_id, 'class');
$Body$;
