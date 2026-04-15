CREATE OR REPLACE
FUNCTION index_approved_claim(af_id TEXT)
RETURNS TABLE (approved_claim json)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
SELECT
	(json_build_object(
	'id',
	afc.id, 
	'contact_person',
	afc.contact_person,
	'company_name',
	afc.company_name,
	'website',
	afc.website,
	'facility_description',
	afc.facility_description,
	'status',
	afc.status,
	'created_at',
	afc.created_at,
	'updated_at',
	afc.updated_at,
	'contributor_id',
	afc.contributor_id,
	'contributor',
	json_build_object(
		'admin_id',
	ac.admin_id,
		'name',
	ac.name,
		'contrib_type',
	ac.contrib_type
	),
	'facility_id',
	afc.facility_id,
	'status_change_date',
	afc.status_change_date,
	'status_change_by_id',
	afc.status_change_by_id,
	'status_change_reason',
	afc.status_change_reason,
	'facility_address',
	afc.facility_address,
	'facility_average_lead_time',
	afc.facility_average_lead_time,
	'facility_minimum_order_quantity',
	afc.facility_minimum_order_quantity,
	'facility_phone_number',
	afc.facility_phone_number,
	'facility_phone_number_publicly_visible',
	afc.facility_phone_number_publicly_visible,
	'facility_website',
	afc.facility_website,
	'office_address',
	afc.office_address,
	'office_country_code',
	afc.office_country_code,
	'office_info_publicly_visible',
	afc.office_info_publicly_visible,
	'office_official_name',
	afc.office_official_name,
	'office_phone_number',
	afc.office_phone_number,
	'point_of_contact_person_name',
	afc.point_of_contact_person_name,
	'point_of_contact_email',
	afc.point_of_contact_email,
	'point_of_contact_publicly_visible',
	afc.point_of_contact_publicly_visible,
	'parent_company_id',
	afc.parent_company_id,
	'facility_female_workers_percentage',
	afc.facility_female_workers_percentage,
	'facility_name_english',
	afc.facility_name_english,
	'facility_name_native_language',
	afc.facility_name_native_language,
	'facility_type',
	afc.facility_type,
	'facility_website_publicly_visible',
	afc.facility_website_publicly_visible,
	'job_title',
	afc.job_title,
	'linkedin_profile',
	afc.linkedin_profile,
	'other_facility_type',
	afc.other_facility_type,
	'facility_affiliations',
	afc.facility_affiliations,
	'facility_certifications',
	afc.facility_certifications,
	'facility_product_types',
	afc.facility_product_types,
	'facility_production_types',
	afc.facility_production_types,
	'sector',
	afc.sector,
	'parent_company_name',
	CASE
		WHEN afc.parent_company_id IS NOT NULL THEN (
			SELECT ac.name FROM api_contributor ac WHERE ac.id = afc.parent_company_id
		)
		ELSE afc.parent_company_name
	END,
	'facility_location',
	afc.facility_location,
	'facility_location_info',
	json_build_object(
		'lat',
	ST_Y(afc.facility_location),
		'lng',
	ST_X(afc.facility_location)
	),
	'facility_workers_count',
	afc.facility_workers_count
	) :: jsonb ||
	json_build_object(
	'opening_date',
	CASE
		WHEN afc.opening_date IS NOT NULL THEN to_char(afc.opening_date, 'YYYY')
		ELSE NULL
	END,
	'closing_date',
	CASE
		WHEN afc.closing_date IS NOT NULL THEN to_char(afc.closing_date, 'YYYY-MM')
		ELSE NULL
	END,
	'estimated_annual_throughput',
	afc.estimated_annual_throughput,
	'energy_coal',
	afc.energy_coal,
	'energy_natural_gas',
	afc.energy_natural_gas,
	'energy_diesel',
	afc.energy_diesel,
	'energy_kerosene',
	afc.energy_kerosene,
	'energy_biomass',
	afc.energy_biomass,
	'energy_charcoal',
	afc.energy_charcoal,
	'energy_animal_waste',
	afc.energy_animal_waste,
	'energy_electricity',
	afc.energy_electricity,
	'energy_other',
	afc.energy_other
	) :: jsonb
	) :: json
FROM
	api_facilityclaim afc
LEFT JOIN api_contributor ac ON
	ac.id = afc.contributor_id
WHERE
	afc.facility_id = af_id
	AND afc.status = 'APPROVED'
ORDER BY
	afc.status_change_date DESC
LIMIT 1;
END;

$Body$;
