SELECT
  af.id AS os_id,
  (
    SELECT
      COALESCE(NULLIF(afc.facility_name_english, ''), af.name)
  ) AS name,
  afc.facility_name_native_language AS name_local_value,
  afc.facility_description AS description_value,
  (
    SELECT
      COALESCE(NULLIF(afc.facility_address, ''), af.address)
  ) AS address,
  (
    SELECT
      COALESCE(afc.sector, afli.sector)
    FROM
      api_facilitylistitem afli
    WHERE
      afli.id = af.created_from_id
  ) AS sector_value,
  (
    SELECT
      ae.value::TEXT
    FROM
      api_extendedfield ae
    WHERE
      ae.field_name = 'parent_company'
      AND (
        ae.facility_list_item_id = af.created_from_id
        OR ae.facility_claim_id = afc.id
      )
    ORDER BY
      ae.facility_claim_id IS NOT NULL DESC
    LIMIT
      1
  ) AS parent_company_value,
  (
    SELECT
      ae.value::TEXT
    FROM
      api_extendedfield ae
    WHERE
      ae.field_name = 'product_type'
      AND (
        ae.facility_list_item_id = af.created_from_id
        OR ae.facility_claim_id = afc.id
      )
    ORDER BY
      ae.facility_claim_id IS NOT NULL DESC
    LIMIT
      1
  ) AS product_type_value,
  (
    SELECT
      ae.value::TEXT
    FROM
      api_extendedfield ae
    WHERE
      ae.field_name = 'facility_type'
      AND (
        ae.facility_list_item_id = af.created_from_id
        OR ae.facility_claim_id = afc.id
      )
    ORDER BY
      ae.facility_claim_id IS NOT NULL DESC
    LIMIT
      1
  ) AS facility_type_value,
  (
    SELECT
      ae.value::TEXT
    FROM
      api_extendedfield ae
    WHERE
      ae.field_name = 'processing_type'
      AND (
        ae.facility_list_item_id = af.created_from_id
        OR ae.facility_claim_id = afc.id
      )
    ORDER BY
      ae.facility_claim_id IS NOT NULL DESC
    LIMIT
      1
  ) AS processing_type_value,
  (
    SELECT
      ae.value::TEXT
    FROM
      api_extendedfield ae
    WHERE
      ae.field_name = 'number_of_workers'
      AND (
        ae.facility_list_item_id = af.created_from_id
        OR ae.facility_claim_id = afc.id
      )
    ORDER BY
      ae.facility_claim_id IS NOT NULL DESC
    LIMIT
      1
  ) AS number_of_workers_value,
  ST_Y (COALESCE(afc.facility_location, af.location)) AS latitude,
  ST_X (COALESCE(afc.facility_location, af.location)) AS longitude,
  afc.facility_minimum_order_quantity AS minimum_order_quantity_value,
  afc.facility_average_lead_time AS average_lead_time_value,
  afc.facility_female_workers_percentage AS percent_female_workers_value,
  afc.facility_affiliations AS affiliations_value,
  afc.facility_certifications AS certifications_standards_regulations_value,
  af.country_code AS country_value,
  (
    SELECT
      ARRAY_AGG(afc2.status)
    FROM
      api_facilityclaim afc2
    WHERE
      afc2.facility_id = af.id
  ) AS claim_status_value,
  af.updated_at
FROM
  api_facility af
  LEFT JOIN api_facilityclaim afc ON afc.facility_id = af.id
  AND afc.status = 'APPROVED'
WHERE
  af.updated_at > :sql_last_value
  AND af.updated_at < CURRENT_TIMESTAMP
ORDER BY
  af.updated_at ASC
