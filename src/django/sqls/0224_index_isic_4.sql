CREATE OR REPLACE FUNCTION isic_4_entry_elements(af_id TEXT)
RETURNS SETOF jsonb
LANGUAGE sql
STABLE
AS $Body$
    SELECT elem
    FROM api_extendedfield aef,
    LATERAL jsonb_array_elements(
        CASE jsonb_typeof(aef.value -> 'raw_value')
            WHEN 'array' THEN aef.value -> 'raw_value'
            ELSE jsonb_build_array(aef.value -> 'raw_value')
        END
    ) AS elem
    WHERE aef.facility_id = af_id
      AND aef.field_name = 'isic_4'
      AND aef.value ? 'raw_value'
      AND jsonb_typeof(aef.value -> 'raw_value') IN ('array', 'object');
$Body$;


CREATE OR REPLACE FUNCTION index_isic_section(af_id TEXT)
RETURNS TABLE (isic_section TEXT)
LANGUAGE sql
STABLE
AS $Body$
    SELECT DISTINCT extract_isic_code(elem ->> 'section')
    FROM isic_4_entry_elements(af_id) AS elem
    WHERE extract_isic_code(elem ->> 'section') IS NOT NULL;
$Body$;


CREATE OR REPLACE FUNCTION index_isic_division(af_id TEXT)
RETURNS TABLE (isic_division TEXT)
LANGUAGE sql
STABLE
AS $Body$
    SELECT DISTINCT extract_isic_code(elem ->> 'division')
    FROM isic_4_entry_elements(af_id) AS elem
    WHERE extract_isic_code(elem ->> 'division') IS NOT NULL;
$Body$;


CREATE OR REPLACE FUNCTION index_isic_group(af_id TEXT)
RETURNS TABLE (isic_group TEXT)
LANGUAGE sql
STABLE
AS $Body$
    SELECT DISTINCT extract_isic_code(elem ->> 'group')
    FROM isic_4_entry_elements(af_id) AS elem
    WHERE extract_isic_code(elem ->> 'group') IS NOT NULL;
$Body$;


CREATE OR REPLACE FUNCTION index_isic_class(af_id TEXT)
RETURNS TABLE (isic_class TEXT)
LANGUAGE sql
STABLE
AS $Body$
    SELECT DISTINCT extract_isic_code(elem ->> 'class')
    FROM isic_4_entry_elements(af_id) AS elem
    WHERE extract_isic_code(elem ->> 'class') IS NOT NULL;
$Body$;
