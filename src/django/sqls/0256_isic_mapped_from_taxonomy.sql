/*
OSDEV-3382. Derives ISIC Rev 4 codes for a location from its OS Hub Facility
Type and Processing Type through the api_isiccrosswalkentry table, and keeps
them in the isic_mapped_* columns of api_facilityindex, apart from the
isic_* columns that hold what contributors submitted.

isic_mapped_codes() takes the two taxonomy arrays already in the index, so
the mapping sees exactly the values the location shows (the same match and
claim visibility rules as index_facility_type / index_processing_type) and
needs no extra reads of api_extendedfield.

Precedence, per facility type:
  * A processing type is the more specific signal. Every crosswalk row whose
    facility type and processing type are both on the location applies, and
    its facility type counts as covered, including rows that deliberately map
    to nothing.
  * A facility type that is not covered falls back to its facility-type-only
    row (empty processing_type), if there is one.

The index arrays do not keep which facility type each processing type was
submitted with. The OS Hub taxonomy files each processing type under one
facility type, so the pairing is unambiguous in practice.
*/

/*The crosswalk rows that apply to a location. The profile reads these
directly to say which Facility Type or Processing Type a mapped value came
from; isic_mapped_codes() below flattens them into codes for the index.*/
CREATE OR REPLACE
FUNCTION isic_mapped_entries(
	facility_types VARCHAR[],
	processing_types VARCHAR[]
)
RETURNS SETOF api_isiccrosswalkentry
LANGUAGE sql
STABLE
PARALLEL SAFE
AS $Body$
WITH location_facility_types AS (
	SELECT DISTINCT lower(btrim(value)) AS facility_type_key
	FROM unnest(COALESCE(facility_types, '{}'::VARCHAR[])) AS value
),
location_processing_types AS (
	SELECT DISTINCT lower(btrim(value)) AS processing_type_key
	FROM unnest(COALESCE(processing_types, '{}'::VARCHAR[])) AS value
),
pair_rows AS (
	SELECT crosswalk.*
	FROM api_isiccrosswalkentry crosswalk
	WHERE crosswalk.processing_type <> ''
		AND lower(crosswalk.facility_type) IN (
			SELECT facility_type_key FROM location_facility_types
		)
		AND lower(crosswalk.processing_type) IN (
			SELECT processing_type_key FROM location_processing_types
		)
),
facility_type_rows AS (
	SELECT crosswalk.*
	FROM api_isiccrosswalkentry crosswalk
	WHERE crosswalk.processing_type = ''
		AND lower(crosswalk.facility_type) IN (
			SELECT facility_type_key FROM location_facility_types
		)
		AND lower(crosswalk.facility_type) NOT IN (
			SELECT lower(facility_type) FROM pair_rows
		)
)
SELECT * FROM pair_rows
UNION ALL
SELECT * FROM facility_type_rows;
$Body$;

CREATE OR REPLACE
FUNCTION isic_mapped_codes(
	facility_types VARCHAR[],
	processing_types VARCHAR[]
)
RETURNS TABLE (isic_level TEXT, isic_code TEXT)
LANGUAGE sql
STABLE
PARALLEL SAFE
AS $Body$
SELECT DISTINCT levels.isic_level, levels.isic_code
FROM isic_mapped_entries(facility_types, processing_types) AS applied_rows
CROSS JOIN LATERAL (
	VALUES
		('section', applied_rows.isic_section),
		('division', applied_rows.isic_division),
		('group', applied_rows.isic_group),
		('class', applied_rows.isic_class)
) AS levels(isic_level, isic_code)
WHERE levels.isic_code <> '';
$Body$;

/*Every api_facilityindex write that changes facility_type or processing_type
goes through these triggers, whichever procedure made it (index_facilities,
index_facilities_by and the perform_*_indexing procedures of 0131, 0235 and
0236), so none of those procedures needs to know about the mapped columns.*/
CREATE OR REPLACE
FUNCTION set_isic_mapped_columns()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $Body$
BEGIN
	SELECT
		COALESCE(array_agg(isic_code ORDER BY isic_code)
			FILTER (WHERE isic_level = 'section'), '{}'),
		COALESCE(array_agg(isic_code ORDER BY isic_code)
			FILTER (WHERE isic_level = 'division'), '{}'),
		COALESCE(array_agg(isic_code ORDER BY isic_code)
			FILTER (WHERE isic_level = 'group'), '{}'),
		COALESCE(array_agg(isic_code ORDER BY isic_code)
			FILTER (WHERE isic_level = 'class'), '{}')
	INTO
		NEW.isic_mapped_section,
		NEW.isic_mapped_division,
		NEW.isic_mapped_group,
		NEW.isic_mapped_class
	FROM isic_mapped_codes(NEW.facility_type, NEW.processing_type);
	RETURN NEW;
END;
$Body$;

DROP TRIGGER IF EXISTS facility_index_isic_mapped_insert_trigger
	ON api_facilityindex;
CREATE TRIGGER facility_index_isic_mapped_insert_trigger
	BEFORE INSERT
	ON api_facilityindex
	FOR EACH ROW
	EXECUTE FUNCTION set_isic_mapped_columns();

DROP TRIGGER IF EXISTS facility_index_isic_mapped_update_trigger
	ON api_facilityindex;
CREATE TRIGGER facility_index_isic_mapped_update_trigger
	BEFORE UPDATE OF facility_type, processing_type
	ON api_facilityindex
	FOR EACH ROW
	WHEN (
		OLD.facility_type IS DISTINCT FROM NEW.facility_type
		OR OLD.processing_type IS DISTINCT FROM NEW.processing_type
	)
	EXECUTE FUNCTION set_isic_mapped_columns();
