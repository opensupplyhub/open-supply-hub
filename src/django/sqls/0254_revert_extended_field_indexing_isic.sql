/*Restores perform_extended_field_indexing to its 0131 definition.*/
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
COALESCE((SELECT array_agg(DISTINCT (parent_company_name)) FROM index_parent_company_name(af.id)), '{}'), -- parent_company_name
COALESCE((SELECT array_agg(DISTINCT (native_language_name)) FROM index_native_language_name(af.id)), '{}'), -- native_language_name
COALESCE((SELECT array_agg(DISTINCT (parent_company_id)) FROM index_parent_company_id(af.id)), '{}'), -- parent_company_id
COALESCE((SELECT array_agg(extended_field) FROM index_extended_fields(af.id)), '{}'), -- extended_fields
now() -- updated_at
FROM api_facility af
WHERE
af.id = afin.id)
WHERE
afin.id = facility_identifier;
END IF;
END;

$body$;
