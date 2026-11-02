/*
OSDEV-3382. Adds each location's Sectors to the ISIC Rev 4 values mapped
through api_isiccrosswalkentry (see 0256), so a location's isic_mapped_*
columns hold what its Facility Type / Processing Type map to and what its
Sectors map to.

Sector rows have an empty facility_type and processing_type. They apply
whenever the location has that sector, independently of the facility type
precedence rules in 0256: a location gets both its sector's value and its
facility or processing type's value, even when one is broader than the
other.

The two-argument functions from 0256 are replaced by three-argument ones,
and the update trigger now also fires when the sector column changes.
*/

DROP FUNCTION IF EXISTS isic_mapped_codes(VARCHAR[], VARCHAR[]);
DROP FUNCTION IF EXISTS isic_mapped_entries(VARCHAR[], VARCHAR[]);

/*The crosswalk rows that apply to a location. The profile reads these
directly; isic_mapped_codes() below flattens them into codes for the
index.*/
CREATE OR REPLACE
FUNCTION isic_mapped_entries(
	facility_types VARCHAR[],
	processing_types VARCHAR[],
	sectors VARCHAR[]
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
location_sectors AS (
	SELECT DISTINCT lower(btrim(value)) AS sector_key
	FROM unnest(COALESCE(sectors, '{}'::VARCHAR[])) AS value
),
pair_rows AS (
	SELECT crosswalk.*
	FROM api_isiccrosswalkentry crosswalk
	WHERE crosswalk.sector = ''
		AND crosswalk.processing_type <> ''
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
	WHERE crosswalk.sector = ''
		AND crosswalk.processing_type = ''
		AND lower(crosswalk.facility_type) IN (
			SELECT facility_type_key FROM location_facility_types
		)
		AND lower(crosswalk.facility_type) NOT IN (
			SELECT lower(facility_type) FROM pair_rows
		)
),
sector_rows AS (
	SELECT crosswalk.*
	FROM api_isiccrosswalkentry crosswalk
	WHERE crosswalk.sector <> ''
		AND lower(crosswalk.sector) IN (
			SELECT sector_key FROM location_sectors
		)
)
SELECT * FROM pair_rows
UNION ALL
SELECT * FROM facility_type_rows
UNION ALL
SELECT * FROM sector_rows;
$Body$;

CREATE OR REPLACE
FUNCTION isic_mapped_codes(
	facility_types VARCHAR[],
	processing_types VARCHAR[],
	sectors VARCHAR[]
)
RETURNS TABLE (isic_level TEXT, isic_code TEXT)
LANGUAGE sql
STABLE
PARALLEL SAFE
AS $Body$
SELECT DISTINCT levels.isic_level, levels.isic_code
FROM isic_mapped_entries(facility_types, processing_types, sectors)
	AS applied_rows
CROSS JOIN LATERAL (
	VALUES
		('section', applied_rows.isic_section),
		('division', applied_rows.isic_division),
		('group', applied_rows.isic_group),
		('class', applied_rows.isic_class)
) AS levels(isic_level, isic_code)
WHERE levels.isic_code <> '';
$Body$;

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
	FROM isic_mapped_codes(
		NEW.facility_type, NEW.processing_type, NEW.sector
	);
	RETURN NEW;
END;
$Body$;

DROP TRIGGER IF EXISTS facility_index_isic_mapped_update_trigger
	ON api_facilityindex;
CREATE TRIGGER facility_index_isic_mapped_update_trigger
	BEFORE UPDATE OF facility_type, processing_type, sector
	ON api_facilityindex
	FOR EACH ROW
	WHEN (
		OLD.facility_type IS DISTINCT FROM NEW.facility_type
		OR OLD.processing_type IS DISTINCT FROM NEW.processing_type
		OR OLD.sector IS DISTINCT FROM NEW.sector
	)
	EXECUTE FUNCTION set_isic_mapped_columns();
