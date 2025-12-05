CREATE OR REPLACE
FUNCTION index_claim_info(af_id TEXT)
RETURNS TABLE (claim_info json)
LANGUAGE plpgsql
AS $Body$
BEGIN
	RETURN QUERY
SELECT
	json_build_object(
	'id',
	afc.id,
	'facility',
	json_build_object(
		'description',
	afc.facility_description,
		'name_english',
	afc.facility_name_english,
		'name_native_language',
	afc.facility_name_native_language,
		'address',
	afc.facility_address,
		'website',
	CASE
			WHEN afc.facility_website_publicly_visible THEN afc.facility_website
		ELSE NULL
	END,
		'parent_company',
	CASE 
			WHEN afc.parent_company_id IS NOT NULL THEN json_build_object(
				'id',
		afc.parent_company_id,
				'name',
		(
		SELECT
			ac.name
		FROM
			api_contributor ac
		WHERE
			ac.id = afc.parent_company_id)
				)
		WHEN afc.parent_company_name IS NOT NULL THEN json_build_object(
				'id',
		afc.parent_company_name,
				'name',
		parent_company_name
				)
		ELSE NULL
	END,
		'phone_number',
	CASE
			WHEN afc.facility_phone_number_publicly_visible THEN afc.facility_phone_number
		ELSE NULL
	END,
		'minimum_order',
	afc.facility_minimum_order_quantity,
		'average_lead_time',
	afc.facility_average_lead_time,
		'workers_count',
	afc.facility_workers_count,
		'female_workers_percentage',
	afc.facility_female_workers_percentage,
		'facility_type',
	afc.facility_type,
		'other_facility_type',
	afc.other_facility_type,
		'affiliations',
	afc.facility_affiliations,
		'certifications',
	afc.facility_certifications,
		'product_types',
	afc.facility_product_types,
		'production_types',
	afc.facility_production_types,
		'sector',
	afc.sector,
		'location',
	CASE
			WHEN afc.facility_location IS NOT NULL THEN st_asgeojson(afc.facility_location)::json
		ELSE NULL
	END,
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
    'actual_annual_energy_consumption',
    json_build_object(
        'coal', afc.energy_coal,
        'natural_gas', afc.energy_natural_gas,
        'diesel', afc.energy_diesel,
        'kerosene', afc.energy_kerosene,
        'biomass', afc.energy_biomass,
        'charcoal', afc.energy_charcoal,
        'animal_waste', afc.energy_animal_waste,
        'electricity', afc.energy_electricity,
        'other', afc.energy_other
    )
		),
		'contact',
	CASE 
			WHEN afc.point_of_contact_publicly_visible THEN json_build_object(
				'name',
		afc.point_of_contact_person_name,
				'email',
		afc.point_of_contact_email
				)
		ELSE NULL
	END,
		'office',
	CASE 
			WHEN afc.office_info_publicly_visible THEN json_build_object(
				'name',
		afc.office_official_name,
				'address',
		afc.office_address,
				'country',
		afc.office_country_code,
				'phone_number',
		afc.office_phone_number
				)
		ELSE NULL
	END,
		'contributor',
	json_build_object(
			'id',
	ac.id,
			'name',
	ac.name,
			'contrib_type',
	ac.contrib_type
			)
	)
FROM
	api_facilityclaim afc
LEFT JOIN api_contributor ac ON
	afc.contributor_id = ac.id
WHERE
	status = 'APPROVED'
	AND facility_id = af_id
LIMIT 1
;
END;

$Body$;
