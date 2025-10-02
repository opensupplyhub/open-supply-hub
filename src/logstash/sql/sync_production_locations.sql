SELECT
  af.id AS os_id,
  (
    SELECT
      COALESCE(
        NULLIF(afc.facility_name_english, ''),
        (
          SELECT
            afli.name
          FROM
            api_facilitylistitem afli
          WHERE
            afli.id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            )
        ),
        (
          SELECT
            afli.name
          FROM
            api_facilitylistitem afli
          WHERE
            afli.facility_id = af.id
          ORDER BY
            afli.created_at DESC
          LIMIT
            1
        ),
        af.name
      )
  ) AS name,
  afc.facility_name_native_language AS local_name_value,
  afc.facility_description AS description_value,
  (
    SELECT
      COALESCE(
        NULLIF(afc.facility_address, ''),
        (
          SELECT
            afli.address
          FROM
            api_facilitylistitem afli
          WHERE
            afli.id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            )
        ),
        (
          SELECT
            afli.address
          FROM
            api_facilitylistitem afli
          WHERE
            afli.facility_id = af.id
          ORDER BY
            afli.created_at DESC
          LIMIT
            1
        ),
        af.address
      )
  ) AS address,
  afc.facility_website AS business_url_value,
  (
    SELECT
      COALESCE(
        (
          CASE
            WHEN NOT EXISTS (
              SELECT
                1
              FROM
                UNNEST(afc.sector) AS unnested_sector_value
              WHERE
                unnested_sector_value = 'Unspecified'
            ) THEN afc.sector
            ELSE NULL
          END
        ),
        (
          SELECT
            afli.sector
          FROM
            api_facilitylistitem afli
          WHERE
            afli.id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            )
            AND NOT EXISTS (
              SELECT
                1
              FROM
                UNNEST(afli.sector) AS unnested_sector_value
              WHERE
                unnested_sector_value = 'Unspecified'
            )
        ),
        (
          SELECT
            afli.sector
          FROM
            api_facilitylistitem afli
          WHERE
            afli.facility_id = af.id
            AND NOT EXISTS (
              SELECT
                1
              FROM
                UNNEST(afli.sector) AS unnested_sector_value
              WHERE
                unnested_sector_value = 'Unspecified'
            )
          ORDER BY
            afli.created_at DESC
          LIMIT
            1
        ),
        (
          SELECT
            afli.sector
          FROM
            api_facilitylistitem afli
          WHERE
            afli.id = af.created_from_id
        )
      )
  ) AS sector_value,
  (
    SELECT
      COALESCE(
        (
          SELECT
            ae.value::TEXT
          FROM
            api_extendedfield ae
          WHERE
            ae.field_name = 'parent_company'
            AND ae.facility_claim_id = afc.id
        ),
        (
          SELECT
            ae.value::TEXT
          FROM
            api_extendedfield ae
            LEFT JOIN api_facilitylistitem afli ON afli.id = af.created_from_id
          WHERE
            ae.field_name = 'parent_company'
            AND ae.facility_list_item_id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            )
        ),
        (
          SELECT
            ae.value::TEXT
          FROM
            api_extendedfield ae
          WHERE
            ae.facility_id = af.id
            AND ae.facility_claim_id IS NULL
            AND ae.field_name = 'parent_company'
          ORDER BY
            created_at DESC
          LIMIT
            1
        )
      )
  ) AS parent_company_value,
  (
    SELECT
      COALESCE(
        (
          SELECT
            ae.value::TEXT
          FROM
            api_extendedfield ae
          WHERE
            ae.field_name = 'product_type'
            AND ae.facility_claim_id = afc.id
        ),
        (
          SELECT
            ae.value::TEXT
          FROM
            api_extendedfield ae
            LEFT JOIN api_facilitylistitem afli ON afli.id = af.created_from_id
          WHERE
            ae.field_name = 'product_type'
            AND ae.facility_list_item_id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            )
        ),
        (
          SELECT
            ae.value::TEXT
          FROM
            api_extendedfield ae
          WHERE
            ae.facility_id = af.id
            AND ae.facility_claim_id IS NULL
            AND ae.field_name = 'product_type'
          ORDER BY
            created_at DESC
          LIMIT
            1
        )
      )
  ) AS product_type_value,
  (
    SELECT
      COALESCE(
        (
          SELECT
            ae.value::TEXT
          FROM
            api_extendedfield ae
          WHERE
            ae.field_name = 'facility_type'
            AND ae.facility_claim_id = afc.id
        ),
        (
          SELECT
            ae.value::TEXT
          FROM
            api_extendedfield ae
            LEFT JOIN api_facilitylistitem afli ON afli.id = af.created_from_id
          WHERE
            ae.field_name = 'facility_type'
            AND ae.facility_list_item_id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            )
        ),
        (
          SELECT
            ae.value::TEXT
          FROM
            api_extendedfield ae
          WHERE
            ae.facility_id = af.id
            AND ae.facility_claim_id IS NULL
            AND ae.field_name = 'facility_type'
          ORDER BY
            created_at DESC
          LIMIT
            1
        )
      )
  ) AS location_type_value,
  (
    SELECT
      COALESCE(
        (
          SELECT
            ae.value::TEXT
          FROM
            api_extendedfield ae
          WHERE
            ae.field_name = 'processing_type'
            AND ae.facility_claim_id = afc.id
        ),
        (
          SELECT
            ae.value::TEXT
          FROM
            api_extendedfield ae
            LEFT JOIN api_facilitylistitem afli ON afli.id = af.created_from_id
          WHERE
            ae.field_name = 'processing_type'
            AND ae.facility_list_item_id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            )
        ),
        (
          SELECT
            ae.value::TEXT
          FROM
            api_extendedfield ae
          WHERE
            ae.facility_id = af.id
            AND ae.facility_claim_id IS NULL
            AND ae.field_name = 'processing_type'
          ORDER BY
            created_at DESC
          LIMIT
            1
        )
      )
  ) AS processing_type_value,
  (
    SELECT
      COALESCE(
        (
          SELECT
            ae.value::TEXT
          FROM
            api_extendedfield ae
          WHERE
            ae.field_name = 'number_of_workers'
            AND ae.facility_claim_id = afc.id
        ),
        (
          SELECT
            ae.value::TEXT
          FROM
            api_extendedfield ae
            LEFT JOIN api_facilitylistitem afli ON afli.id = af.created_from_id
          WHERE
            ae.field_name = 'number_of_workers'
            AND ae.facility_list_item_id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            )
        ),
        (
          SELECT
            ae.value::TEXT
          FROM
            api_extendedfield ae
          WHERE
            ae.facility_id = af.id
            AND ae.facility_claim_id IS NULL
            AND ae.field_name = 'number_of_workers'
          ORDER BY
            created_at DESC
          LIMIT
            1
        )
      )
  ) AS number_of_workers_value,
  (
    SELECT
      COALESCE(
        (
          SELECT
            ae.value::TEXT
          FROM
            api_extendedfield ae
            LEFT JOIN api_facilitylistitem afli ON afli.id = af.created_from_id
          WHERE
            ae.field_name = 'rba_id'
            AND ae.facility_list_item_id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            )
        ),
        (
          SELECT
            ae.value::TEXT
          FROM
            api_extendedfield ae
          WHERE
            ae.facility_id = af.id
            AND ae.facility_claim_id IS NULL
            AND ae.field_name = 'rba_id'
          ORDER BY
            created_at DESC
          LIMIT
            1
        )
      )
  ) AS rba_id_value,
  (
    SELECT
      COALESCE(
        (
          SELECT
            ae.value::TEXT
          FROM
            api_extendedfield ae
            LEFT JOIN api_facilitylistitem afli ON afli.id = af.created_from_id
          WHERE
            ae.field_name = 'duns_id'
            AND ae.facility_list_item_id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            )
        ),
        (
          SELECT
            ae.value::TEXT
          FROM
            api_extendedfield ae
          WHERE
            ae.facility_id = af.id
            AND ae.facility_claim_id IS NULL
            AND ae.field_name = 'duns_id'
          ORDER BY
            created_at DESC
          LIMIT
            1
        )
      )
  ) AS duns_id_value,
  (
    SELECT
      COALESCE(
        (
          SELECT
            ae.value::TEXT
          FROM
            api_extendedfield ae
            LEFT JOIN api_facilitylistitem afli ON afli.id = af.created_from_id
          WHERE
            ae.field_name = 'lei_id'
            AND ae.facility_list_item_id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            )
        ),
        (
          SELECT
            ae.value::TEXT
          FROM
            api_extendedfield ae
          WHERE
            ae.facility_id = af.id
            AND ae.facility_claim_id IS NULL
            AND ae.field_name = 'lei_id'
          ORDER BY
            created_at DESC
          LIMIT
            1
        )
      )
  ) AS lei_id_value,
  ST_Y (
    COALESCE(
      afc.facility_location,
      (
        SELECT
          afli.geocoded_point
        FROM
          api_facilitylistitem afli
        WHERE
          afli.id = af.created_from_id
          AND afli.geocoded_point IS NOT NULL
          AND EXISTS (
            SELECT
              1
            FROM
              jsonb_array_elements(afli.processing_results) AS elem
            WHERE
              elem ->> 'action' = 'promote_match'
          )
      ),
      (
        SELECT
          afli.geocoded_point
        FROM
          api_facilitylistitem afli
        WHERE
          afli.facility_id = af.id
          AND afli.geocoded_point IS NOT NULL
        ORDER BY
          afli.created_at DESC
        LIMIT
          1
      ),
      af.location
    )
  ) AS latitude,
  ST_X (
    COALESCE(
      afc.facility_location,
      (
        SELECT
          afli.geocoded_point
        FROM
          api_facilitylistitem afli
        WHERE
          afli.id = af.created_from_id
          AND afli.geocoded_point IS NOT NULL
          AND EXISTS (
            SELECT
              1
            FROM
              jsonb_array_elements(afli.processing_results) AS elem
            WHERE
              elem ->> 'action' = 'promote_match'
          )
      ),
      (
        SELECT
          afli.geocoded_point
        FROM
          api_facilitylistitem afli
        WHERE
          afli.facility_id = af.id
          AND afli.geocoded_point IS NOT NULL
        ORDER BY
          afli.created_at DESC
        LIMIT
          1
      ),
      af.location
    )
  ) AS longitude,
  (
    WITH geocode_extractor AS (
      SELECT 
        afli.id,
        afli.facility_id,
        afli.created_at,
        (
          SELECT elem::TEXT
          FROM jsonb_array_elements(afli.processing_results) AS elem
          WHERE elem ? 'action' AND elem ? 'error' 
            AND elem->>'action' = 'geocode'
            AND elem->>'error' = 'false'
          LIMIT 1
        ) as geocode_value,
        EXISTS (
          SELECT 1
          FROM jsonb_array_elements(afli.processing_results) AS elem
          WHERE elem ? 'action' AND elem->>'action' = 'promote_match'
        ) as has_promote_match
      FROM api_facilitylistitem afli
      WHERE afli.id = af.created_from_id OR afli.facility_id = af.id
    )
    SELECT 
      COALESCE(
        (SELECT ge.geocode_value FROM geocode_extractor ge 
         WHERE ge.id = af.created_from_id AND ge.has_promote_match),
        (SELECT ge.geocode_value FROM geocode_extractor ge 
         WHERE ge.facility_id = af.id 
         ORDER BY ge.created_at DESC LIMIT 1)
      )
  ) AS geocode_value,
  afc.facility_minimum_order_quantity AS minimum_order_quantity_value,
  afc.facility_average_lead_time AS average_lead_time_value,
  afc.facility_female_workers_percentage AS percent_female_workers_value,
  afc.facility_affiliations AS affiliations_value,
  afc.facility_certifications AS certifications_standards_regulations_value,
  (
    COALESCE(
      (
        SELECT
          afli.country_code
        FROM
          api_facilitylistitem afli
        WHERE
          afli.id = af.created_from_id
          AND EXISTS (
            SELECT
              1
            FROM
              jsonb_array_elements(afli.processing_results) AS elem
            WHERE
              elem ->> 'action' = 'promote_match'
          )
      ),
      (
        SELECT
          afli.country_code
        FROM
          api_facilitylistitem afli
        WHERE
          afli.facility_id = af.id
        ORDER BY
          afli.created_at DESC
        LIMIT
          1
      ),
      af.country_code
    )
  ) AS country_value,
  (
    SELECT
      ARRAY_AGG(afc2.status)
    FROM
      api_facilityclaim afc2
    WHERE
      afc2.facility_id = af.id
  ) AS claim_status_value,
  (
    SELECT
      ARRAY_AGG(afa.os_id)
    FROM
      api_facilityalias afa
    WHERE
      afa.facility_id = af.id
  ) AS historical_os_id_value,
  af.updated_at,
  (
    SELECT
      afc3.updated_at
    FROM
      api_facilityclaim afc3
    WHERE
      afc3.facility_id = af.id
      AND afc3.status IN ('APPROVED', 'PENDING')
    ORDER BY
      afc3.updated_at DESC
    LIMIT
      1
  ) AS claimed_at_value,
  (
    SELECT afc_sub.opened_at
    FROM api_facilityclaim afc_sub
    WHERE afc_sub.facility_id = af.id
      AND afc_sub.opened_at IS NOT NULL
    ORDER BY afc_sub.opened_at DESC NULLS LAST
    LIMIT 1
  ) AS opened_at_value
FROM
  api_facility af
  LEFT JOIN api_facilityclaim afc ON afc.facility_id = af.id
  AND afc.status = 'APPROVED'
WHERE
  af.updated_at > :sql_last_value
  AND af.updated_at < CURRENT_TIMESTAMP
ORDER BY
  af.updated_at ASC
