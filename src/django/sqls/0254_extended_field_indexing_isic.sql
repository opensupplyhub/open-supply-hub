-- extended_fields is aggregated in ExtendedField id order, so owners'
-- values (e.g. embed downloads joined with "|") come out the same way
-- every time; before, the order was whatever the plan returned.
/*
OSDEV-3340. The ISIC columns of api_facilityindex are derived only from
isic_4 ExtendedFields, so the procedure the api_extendedfield triggers call
must recompute them. Without this, an isic_4 value added to a facility that
is already indexed (the normal path: the facility row is inserted before its
ExtendedFields) never reaches the index. Re-creates the 0131 definition with
the four ISIC columns added.
*/
CREATE OR REPLACE
PROCEDURE perform_extended_field_indexing(facility_identifier TEXT)
LANGUAGE plpgsql
AS $body$

BEGIN
IF facility_identifier IS NOT NUll THEN
UPDATE
	api_facilityindex afin
SET
	(
	number_of_workers,
	facility_type,
	processing_type,
	product_type,
	isic_section,
	isic_division,
	isic_group,
	isic_class,
	isic5_section,
	isic5_division,
	isic5_group,
	isic5_class,
	parent_company_name,
	native_language_name,
	parent_company_id,
	extended_fields,
	updated_at) =
(
	SELECT
COALESCE((SELECT array_agg(DISTINCT(number)) FROM index_number_of_workers(af.id)), '{}'), -- number_of_workers
COALESCE((SELECT array_agg(DISTINCT(facility_type)) FROM index_facility_type(af.id)), '{}'), -- facility_type
COALESCE((SELECT array_agg(DISTINCT(processing_type)) FROM index_processing_type(af.id)), '{}'), -- processing_type
COALESCE((SELECT array_agg(DISTINCT(product_type)) FROM index_product_type(af.id)), '{}'), -- product_type
COALESCE((SELECT array_agg(DISTINCT(isic_section)) FROM index_isic_section(af.id)), '{}'), -- isic_section
COALESCE((SELECT array_agg(DISTINCT(isic_division)) FROM index_isic_division(af.id)), '{}'), -- isic_division
COALESCE((SELECT array_agg(DISTINCT(isic_group)) FROM index_isic_group(af.id)), '{}'), -- isic_group
COALESCE((SELECT array_agg(DISTINCT(isic_class)) FROM index_isic_class(af.id)), '{}'), -- isic_class
COALESCE((SELECT array_agg(code) FROM index_isic_level_code(af.id, 'section', 'isic_5') AS code), '{}'), -- isic5_section
COALESCE((SELECT array_agg(code) FROM index_isic_level_code(af.id, 'division', 'isic_5') AS code), '{}'), -- isic5_division
COALESCE((SELECT array_agg(code) FROM index_isic_level_code(af.id, 'group', 'isic_5') AS code), '{}'), -- isic5_group
COALESCE((SELECT array_agg(code) FROM index_isic_level_code(af.id, 'class', 'isic_5') AS code), '{}'), -- isic5_class
COALESCE((SELECT array_agg(DISTINCT (parent_company_name)) FROM index_parent_company_name(af.id)), '{}'), -- parent_company_name
COALESCE((SELECT array_agg(DISTINCT (native_language_name)) FROM index_native_language_name(af.id)), '{}'), -- native_language_name
COALESCE((SELECT array_agg(DISTINCT (parent_company_id)) FROM index_parent_company_id(af.id)), '{}'), -- parent_company_id
COALESCE((SELECT array_agg(extended_field ORDER BY (extended_field->>'id')::int) FROM index_extended_fields(af.id)), '{}'), -- extended_fields
now() -- updated_at
FROM api_facility af
WHERE
af.id = afin.id)
WHERE
afin.id = facility_identifier;
END IF;
END;

$body$;
