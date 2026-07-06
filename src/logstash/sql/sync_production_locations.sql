-- Each promoted field is selected by a LATERAL subquery that ranks all
-- eligible candidates in a single pass and returns the winning value together
-- with its attribution (emitted as a *_source JSON column). Tier order:
--   1. claimant data: values from the approved claim OR contributed by the
--      claimant's contributor account (SLC/list items); most recent wins
--   2. moderator-promoted data (created_from item with a promote_match action)
--   3. data from a verified contributor
--   4. most recent data
--   5. canonical facility value (name/address only)
-- Candidates are compared by created_at (original contribution date) because
-- claim extended fields are re-saved wholesale on every claim edit, which
-- makes updated_at unreliable for per-field recency.
-- List-item candidates are only eligible while they have an active match
-- (AUTOMATIC/CONFIRMED/MERGED) from an active, public source.
SELECT
  af.id AS os_id,
  COALESCE(name_ranked.value_text, af.name) AS name,
  name_ranked.source_json AS name_source,
  local_name_ranked.value_string AS local_name_value,
  local_name_ranked.source_json AS local_name_source,
  afc.facility_description AS description_value,
  afc.opening_date AS opened_at_value,
  afc.closing_date AS closed_at_value,
  afc.energy_coal AS energy_coal_value,
  afc.energy_natural_gas AS energy_natural_gas_value,
  afc.energy_diesel AS energy_diesel_value,
  afc.energy_kerosene AS energy_kerosene_value,
  afc.energy_biomass AS energy_biomass_value,
  afc.energy_charcoal AS energy_charcoal_value,
  afc.energy_animal_waste AS energy_animal_waste_value,
  afc.energy_electricity AS energy_electricity_value,
  afc.energy_other AS energy_other_value,
  afc.estimated_annual_throughput AS estimated_annual_throughput_value,
  COALESCE(address_ranked.value_text, af.address) AS address,
  address_ranked.source_json AS address_source,
  afc.facility_website AS business_url_value,
  COALESCE(
    sector_ranked.value_array,
    (
      SELECT
        afli.sector
      FROM
        api_facilitylistitem afli
      WHERE
        afli.id = af.created_from_id
    )
  ) AS sector_value,
  sector_ranked.source_json AS sector_source,
  parent_company_ranked.value_json AS parent_company_value,
  parent_company_ranked.source_json AS parent_company_source,
  product_type_ranked.value_json AS product_type_value,
  product_type_ranked.source_json AS product_type_source,
  location_type_ranked.value_json AS location_type_value,
  location_type_ranked.source_json AS location_type_source,
  processing_type_ranked.value_json AS processing_type_value,
  processing_type_ranked.source_json AS processing_type_source,
  number_of_workers_ranked.value_json AS number_of_workers_value,
  number_of_workers_ranked.source_json AS number_of_workers_source,
  rba_id_ranked.value_json AS rba_id_value,
  rba_id_ranked.source_json AS rba_id_source,
  duns_id_ranked.value_json AS duns_id_value,
  duns_id_ranked.source_json AS duns_id_source,
  lei_id_ranked.value_json AS lei_id_value,
  lei_id_ranked.source_json AS lei_id_source,
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
  ) AS claimed_at_value
FROM
  api_facility af
  LEFT JOIN api_facilityclaim afc ON afc.facility_id = af.id
  AND afc.status = 'APPROVED'
  LEFT JOIN LATERAL (
    SELECT
      c.value_text,
      json_build_object(
        'contributor_id', c.contributor_admin_id,
        'contributor_name', c.contributor_name,
        'contributed_at', c.contributed_at,
        'is_claimed_data', c.is_claimed_data,
        'is_promoted', c.is_promoted,
        'is_verified', c.is_verified
      )::TEXT AS source_json
    FROM
      (
        SELECT
          NULLIF(afc.facility_name_english, '') AS value_text,
          afc.created_at AS contributed_at,
          ac.admin_id AS contributor_admin_id,
          ac.name AS contributor_name,
          TRUE AS is_claimed_data,
          FALSE AS is_promoted,
          COALESCE(ac.is_verified, FALSE) AS is_verified
        FROM
          api_contributor ac
        WHERE
          ac.id = afc.contributor_id
          AND NULLIF(afc.facility_name_english, '') IS NOT NULL
        UNION ALL
        SELECT
          NULLIF(afli.name, ''),
          afli.created_at,
          ac.admin_id,
          ac.name,
          COALESCE(s.contributor_id = afc.contributor_id, FALSE),
          COALESCE(
            afli.id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            ),
            FALSE
          ),
          COALESCE(ac.is_verified, FALSE)
        FROM
          api_facilitylistitem afli
          JOIN api_source s ON s.id = afli.source_id
          JOIN api_contributor ac ON ac.id = s.contributor_id
        WHERE
          NULLIF(afli.name, '') IS NOT NULL
          AND s.is_active
          AND s.is_public
          AND EXISTS (
            SELECT
              1
            FROM
              api_facilitymatch afm
            WHERE
              afm.facility_list_item_id = afli.id
              AND afm.facility_id = af.id
              AND afm.status IN ('AUTOMATIC', 'CONFIRMED', 'MERGED')
              AND afm.is_active
          )
      ) c
    ORDER BY
      CASE
        WHEN c.is_claimed_data THEN 1
        WHEN c.is_promoted THEN 2
        WHEN c.is_verified THEN 3
        ELSE 4
      END,
      c.contributed_at DESC
    LIMIT
      1
  ) name_ranked ON TRUE
  LEFT JOIN LATERAL (
    SELECT
      c.value_text,
      json_build_object(
        'contributor_id', c.contributor_admin_id,
        'contributor_name', c.contributor_name,
        'contributed_at', c.contributed_at,
        'is_claimed_data', c.is_claimed_data,
        'is_promoted', c.is_promoted,
        'is_verified', c.is_verified
      )::TEXT AS source_json
    FROM
      (
        SELECT
          NULLIF(afc.facility_address, '') AS value_text,
          afc.created_at AS contributed_at,
          ac.admin_id AS contributor_admin_id,
          ac.name AS contributor_name,
          TRUE AS is_claimed_data,
          FALSE AS is_promoted,
          COALESCE(ac.is_verified, FALSE) AS is_verified
        FROM
          api_contributor ac
        WHERE
          ac.id = afc.contributor_id
          AND NULLIF(afc.facility_address, '') IS NOT NULL
        UNION ALL
        SELECT
          NULLIF(afli.address, ''),
          afli.created_at,
          ac.admin_id,
          ac.name,
          COALESCE(s.contributor_id = afc.contributor_id, FALSE),
          COALESCE(
            afli.id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            ),
            FALSE
          ),
          COALESCE(ac.is_verified, FALSE)
        FROM
          api_facilitylistitem afli
          JOIN api_source s ON s.id = afli.source_id
          JOIN api_contributor ac ON ac.id = s.contributor_id
        WHERE
          NULLIF(afli.address, '') IS NOT NULL
          AND s.is_active
          AND s.is_public
          AND EXISTS (
            SELECT
              1
            FROM
              api_facilitymatch afm
            WHERE
              afm.facility_list_item_id = afli.id
              AND afm.facility_id = af.id
              AND afm.status IN ('AUTOMATIC', 'CONFIRMED', 'MERGED')
              AND afm.is_active
          )
      ) c
    ORDER BY
      CASE
        WHEN c.is_claimed_data THEN 1
        WHEN c.is_promoted THEN 2
        WHEN c.is_verified THEN 3
        ELSE 4
      END,
      c.contributed_at DESC
    LIMIT
      1
  ) address_ranked ON TRUE
  LEFT JOIN LATERAL (
    SELECT
      c.value_array,
      json_build_object(
        'contributor_id', c.contributor_admin_id,
        'contributor_name', c.contributor_name,
        'contributed_at', c.contributed_at,
        'is_claimed_data', c.is_claimed_data,
        'is_promoted', c.is_promoted,
        'is_verified', c.is_verified
      )::TEXT AS source_json
    FROM
      (
        SELECT
          afc.sector AS value_array,
          afc.created_at AS contributed_at,
          ac.admin_id AS contributor_admin_id,
          ac.name AS contributor_name,
          TRUE AS is_claimed_data,
          FALSE AS is_promoted,
          COALESCE(ac.is_verified, FALSE) AS is_verified
        FROM
          api_contributor ac
        WHERE
          ac.id = afc.contributor_id
          AND afc.sector IS NOT NULL
          AND NOT EXISTS (
            SELECT
              1
            FROM
              UNNEST(afc.sector) AS unnested_sector_value
            WHERE
              unnested_sector_value = 'Unspecified'
          )
        UNION ALL
        SELECT
          afli.sector,
          afli.created_at,
          ac.admin_id,
          ac.name,
          COALESCE(s.contributor_id = afc.contributor_id, FALSE),
          COALESCE(
            afli.id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            ),
            FALSE
          ),
          COALESCE(ac.is_verified, FALSE)
        FROM
          api_facilitylistitem afli
          JOIN api_source s ON s.id = afli.source_id
          JOIN api_contributor ac ON ac.id = s.contributor_id
        WHERE
          afli.sector IS NOT NULL
          AND NOT EXISTS (
            SELECT
              1
            FROM
              UNNEST(afli.sector) AS unnested_sector_value
            WHERE
              unnested_sector_value = 'Unspecified'
          )
          AND s.is_active
          AND s.is_public
          AND EXISTS (
            SELECT
              1
            FROM
              api_facilitymatch afm
            WHERE
              afm.facility_list_item_id = afli.id
              AND afm.facility_id = af.id
              AND afm.status IN ('AUTOMATIC', 'CONFIRMED', 'MERGED')
              AND afm.is_active
          )
      ) c
    ORDER BY
      CASE
        WHEN c.is_claimed_data THEN 1
        WHEN c.is_promoted THEN 2
        WHEN c.is_verified THEN 3
        ELSE 4
      END,
      c.contributed_at DESC
    LIMIT
      1
  ) sector_ranked ON TRUE
  LEFT JOIN LATERAL (
    SELECT
      c.value::TEXT AS value_json,
      json_build_object(
        'contributor_id', c.contributor_admin_id,
        'contributor_name', c.contributor_name,
        'contributed_at', c.contributed_at,
        'is_claimed_data', c.is_claimed_data,
        'is_promoted', c.is_promoted,
        'is_verified', c.is_verified
      )::TEXT AS source_json
    FROM
      (
        SELECT
          ae.value,
          ae.created_at AS contributed_at,
          ac.admin_id AS contributor_admin_id,
          ac.name AS contributor_name,
          COALESCE(ae.contributor_id = afc.contributor_id, FALSE) AS is_claimed_data,
          COALESCE(
            ae.facility_list_item_id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            ),
            FALSE
          ) AS is_promoted,
          COALESCE(ac.is_verified, FALSE) AS is_verified
        FROM
          api_extendedfield ae
          JOIN api_contributor ac ON ac.id = ae.contributor_id
          LEFT JOIN api_facilitylistitem afli ON afli.id = ae.facility_list_item_id
          LEFT JOIN api_source s ON s.id = afli.source_id
        WHERE
          ae.facility_id = af.id
          AND ae.field_name = 'parent_company'
          AND (
            ae.facility_claim_id = afc.id
            OR (
              ae.facility_claim_id IS NULL
              AND ae.facility_list_item_id IS NOT NULL
              AND s.is_active
              AND s.is_public
              AND EXISTS (
                SELECT
                  1
                FROM
                  api_facilitymatch afm
                WHERE
                  afm.facility_list_item_id = ae.facility_list_item_id
                  AND afm.facility_id = af.id
                  AND afm.status IN ('AUTOMATIC', 'CONFIRMED', 'MERGED')
                  AND afm.is_active
              )
            )
          )
      ) c
    ORDER BY
      CASE
        WHEN c.is_claimed_data THEN 1
        WHEN c.is_promoted THEN 2
        WHEN c.is_verified THEN 3
        ELSE 4
      END,
      c.contributed_at DESC
    LIMIT
      1
  ) parent_company_ranked ON TRUE
  LEFT JOIN LATERAL (
    SELECT
      c.value::TEXT AS value_json,
      json_build_object(
        'contributor_id', c.contributor_admin_id,
        'contributor_name', c.contributor_name,
        'contributed_at', c.contributed_at,
        'is_claimed_data', c.is_claimed_data,
        'is_promoted', c.is_promoted,
        'is_verified', c.is_verified
      )::TEXT AS source_json
    FROM
      (
        SELECT
          ae.value,
          ae.created_at AS contributed_at,
          ac.admin_id AS contributor_admin_id,
          ac.name AS contributor_name,
          COALESCE(ae.contributor_id = afc.contributor_id, FALSE) AS is_claimed_data,
          COALESCE(
            ae.facility_list_item_id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            ),
            FALSE
          ) AS is_promoted,
          COALESCE(ac.is_verified, FALSE) AS is_verified
        FROM
          api_extendedfield ae
          JOIN api_contributor ac ON ac.id = ae.contributor_id
          LEFT JOIN api_facilitylistitem afli ON afli.id = ae.facility_list_item_id
          LEFT JOIN api_source s ON s.id = afli.source_id
        WHERE
          ae.facility_id = af.id
          AND ae.field_name = 'product_type'
          AND (
            ae.facility_claim_id = afc.id
            OR (
              ae.facility_claim_id IS NULL
              AND ae.facility_list_item_id IS NOT NULL
              AND s.is_active
              AND s.is_public
              AND EXISTS (
                SELECT
                  1
                FROM
                  api_facilitymatch afm
                WHERE
                  afm.facility_list_item_id = ae.facility_list_item_id
                  AND afm.facility_id = af.id
                  AND afm.status IN ('AUTOMATIC', 'CONFIRMED', 'MERGED')
                  AND afm.is_active
              )
            )
          )
      ) c
    ORDER BY
      CASE
        WHEN c.is_claimed_data THEN 1
        WHEN c.is_promoted THEN 2
        WHEN c.is_verified THEN 3
        ELSE 4
      END,
      c.contributed_at DESC
    LIMIT
      1
  ) product_type_ranked ON TRUE
  LEFT JOIN LATERAL (
    SELECT
      c.value::TEXT AS value_json,
      json_build_object(
        'contributor_id', c.contributor_admin_id,
        'contributor_name', c.contributor_name,
        'contributed_at', c.contributed_at,
        'is_claimed_data', c.is_claimed_data,
        'is_promoted', c.is_promoted,
        'is_verified', c.is_verified
      )::TEXT AS source_json
    FROM
      (
        SELECT
          ae.value,
          ae.created_at AS contributed_at,
          ac.admin_id AS contributor_admin_id,
          ac.name AS contributor_name,
          COALESCE(ae.contributor_id = afc.contributor_id, FALSE) AS is_claimed_data,
          COALESCE(
            ae.facility_list_item_id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            ),
            FALSE
          ) AS is_promoted,
          COALESCE(ac.is_verified, FALSE) AS is_verified
        FROM
          api_extendedfield ae
          JOIN api_contributor ac ON ac.id = ae.contributor_id
          LEFT JOIN api_facilitylistitem afli ON afli.id = ae.facility_list_item_id
          LEFT JOIN api_source s ON s.id = afli.source_id
        WHERE
          ae.facility_id = af.id
          AND ae.field_name = 'facility_type'
          AND (
            ae.facility_claim_id = afc.id
            OR (
              ae.facility_claim_id IS NULL
              AND ae.facility_list_item_id IS NOT NULL
              AND s.is_active
              AND s.is_public
              AND EXISTS (
                SELECT
                  1
                FROM
                  api_facilitymatch afm
                WHERE
                  afm.facility_list_item_id = ae.facility_list_item_id
                  AND afm.facility_id = af.id
                  AND afm.status IN ('AUTOMATIC', 'CONFIRMED', 'MERGED')
                  AND afm.is_active
              )
            )
          )
      ) c
    ORDER BY
      CASE
        WHEN c.is_claimed_data THEN 1
        WHEN c.is_promoted THEN 2
        WHEN c.is_verified THEN 3
        ELSE 4
      END,
      c.contributed_at DESC
    LIMIT
      1
  ) location_type_ranked ON TRUE
  LEFT JOIN LATERAL (
    SELECT
      c.value::TEXT AS value_json,
      json_build_object(
        'contributor_id', c.contributor_admin_id,
        'contributor_name', c.contributor_name,
        'contributed_at', c.contributed_at,
        'is_claimed_data', c.is_claimed_data,
        'is_promoted', c.is_promoted,
        'is_verified', c.is_verified
      )::TEXT AS source_json
    FROM
      (
        SELECT
          ae.value,
          ae.created_at AS contributed_at,
          ac.admin_id AS contributor_admin_id,
          ac.name AS contributor_name,
          COALESCE(ae.contributor_id = afc.contributor_id, FALSE) AS is_claimed_data,
          COALESCE(
            ae.facility_list_item_id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            ),
            FALSE
          ) AS is_promoted,
          COALESCE(ac.is_verified, FALSE) AS is_verified
        FROM
          api_extendedfield ae
          JOIN api_contributor ac ON ac.id = ae.contributor_id
          LEFT JOIN api_facilitylistitem afli ON afli.id = ae.facility_list_item_id
          LEFT JOIN api_source s ON s.id = afli.source_id
        WHERE
          ae.facility_id = af.id
          AND ae.field_name = 'processing_type'
          AND (
            ae.facility_claim_id = afc.id
            OR (
              ae.facility_claim_id IS NULL
              AND ae.facility_list_item_id IS NOT NULL
              AND s.is_active
              AND s.is_public
              AND EXISTS (
                SELECT
                  1
                FROM
                  api_facilitymatch afm
                WHERE
                  afm.facility_list_item_id = ae.facility_list_item_id
                  AND afm.facility_id = af.id
                  AND afm.status IN ('AUTOMATIC', 'CONFIRMED', 'MERGED')
                  AND afm.is_active
              )
            )
          )
      ) c
    ORDER BY
      CASE
        WHEN c.is_claimed_data THEN 1
        WHEN c.is_promoted THEN 2
        WHEN c.is_verified THEN 3
        ELSE 4
      END,
      c.contributed_at DESC
    LIMIT
      1
  ) processing_type_ranked ON TRUE
  LEFT JOIN LATERAL (
    SELECT
      c.value::TEXT AS value_json,
      json_build_object(
        'contributor_id', c.contributor_admin_id,
        'contributor_name', c.contributor_name,
        'contributed_at', c.contributed_at,
        'is_claimed_data', c.is_claimed_data,
        'is_promoted', c.is_promoted,
        'is_verified', c.is_verified
      )::TEXT AS source_json
    FROM
      (
        SELECT
          ae.value,
          ae.created_at AS contributed_at,
          ac.admin_id AS contributor_admin_id,
          ac.name AS contributor_name,
          COALESCE(ae.contributor_id = afc.contributor_id, FALSE) AS is_claimed_data,
          COALESCE(
            ae.facility_list_item_id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            ),
            FALSE
          ) AS is_promoted,
          COALESCE(ac.is_verified, FALSE) AS is_verified
        FROM
          api_extendedfield ae
          JOIN api_contributor ac ON ac.id = ae.contributor_id
          LEFT JOIN api_facilitylistitem afli ON afli.id = ae.facility_list_item_id
          LEFT JOIN api_source s ON s.id = afli.source_id
        WHERE
          ae.facility_id = af.id
          AND ae.field_name = 'number_of_workers'
          AND (
            ae.facility_claim_id = afc.id
            OR (
              ae.facility_claim_id IS NULL
              AND ae.facility_list_item_id IS NOT NULL
              AND s.is_active
              AND s.is_public
              AND EXISTS (
                SELECT
                  1
                FROM
                  api_facilitymatch afm
                WHERE
                  afm.facility_list_item_id = ae.facility_list_item_id
                  AND afm.facility_id = af.id
                  AND afm.status IN ('AUTOMATIC', 'CONFIRMED', 'MERGED')
                  AND afm.is_active
              )
            )
          )
      ) c
    ORDER BY
      CASE
        WHEN c.is_claimed_data THEN 1
        WHEN c.is_promoted THEN 2
        WHEN c.is_verified THEN 3
        ELSE 4
      END,
      c.contributed_at DESC
    LIMIT
      1
  ) number_of_workers_ranked ON TRUE
  LEFT JOIN LATERAL (
    SELECT
      c.value #>> '{}' AS value_string,
      json_build_object(
        'contributor_id', c.contributor_admin_id,
        'contributor_name', c.contributor_name,
        'contributed_at', c.contributed_at,
        'is_claimed_data', c.is_claimed_data,
        'is_promoted', c.is_promoted,
        'is_verified', c.is_verified
      )::TEXT AS source_json
    FROM
      (
        SELECT
          ae.value,
          ae.created_at AS contributed_at,
          ac.admin_id AS contributor_admin_id,
          ac.name AS contributor_name,
          COALESCE(ae.contributor_id = afc.contributor_id, FALSE) AS is_claimed_data,
          COALESCE(
            ae.facility_list_item_id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            ),
            FALSE
          ) AS is_promoted,
          COALESCE(ac.is_verified, FALSE) AS is_verified
        FROM
          api_extendedfield ae
          JOIN api_contributor ac ON ac.id = ae.contributor_id
          LEFT JOIN api_facilitylistitem afli ON afli.id = ae.facility_list_item_id
          LEFT JOIN api_source s ON s.id = afli.source_id
        WHERE
          ae.facility_id = af.id
          AND ae.field_name = 'native_language_name'
          AND (
            ae.facility_claim_id = afc.id
            OR (
              ae.facility_claim_id IS NULL
              AND ae.facility_list_item_id IS NOT NULL
              AND s.is_active
              AND s.is_public
              AND EXISTS (
                SELECT
                  1
                FROM
                  api_facilitymatch afm
                WHERE
                  afm.facility_list_item_id = ae.facility_list_item_id
                  AND afm.facility_id = af.id
                  AND afm.status IN ('AUTOMATIC', 'CONFIRMED', 'MERGED')
                  AND afm.is_active
              )
            )
          )
      ) c
    ORDER BY
      CASE
        WHEN c.is_claimed_data THEN 1
        WHEN c.is_promoted THEN 2
        WHEN c.is_verified THEN 3
        ELSE 4
      END,
      c.contributed_at DESC
    LIMIT
      1
  ) local_name_ranked ON TRUE
  LEFT JOIN LATERAL (
    SELECT
      c.value::TEXT AS value_json,
      json_build_object(
        'contributor_id', c.contributor_admin_id,
        'contributor_name', c.contributor_name,
        'contributed_at', c.contributed_at,
        'is_claimed_data', c.is_claimed_data,
        'is_promoted', c.is_promoted,
        'is_verified', c.is_verified
      )::TEXT AS source_json
    FROM
      (
        SELECT
          ae.value,
          ae.created_at AS contributed_at,
          ac.admin_id AS contributor_admin_id,
          ac.name AS contributor_name,
          COALESCE(ae.contributor_id = afc.contributor_id, FALSE) AS is_claimed_data,
          COALESCE(
            ae.facility_list_item_id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            ),
            FALSE
          ) AS is_promoted,
          COALESCE(ac.is_verified, FALSE) AS is_verified
        FROM
          api_extendedfield ae
          JOIN api_contributor ac ON ac.id = ae.contributor_id
          LEFT JOIN api_facilitylistitem afli ON afli.id = ae.facility_list_item_id
          LEFT JOIN api_source s ON s.id = afli.source_id
        WHERE
          ae.facility_id = af.id
          AND ae.field_name = 'rba_id'
          AND (
            ae.facility_claim_id = afc.id
            OR (
              ae.facility_claim_id IS NULL
              AND ae.facility_list_item_id IS NOT NULL
              AND s.is_active
              AND s.is_public
              AND EXISTS (
                SELECT
                  1
                FROM
                  api_facilitymatch afm
                WHERE
                  afm.facility_list_item_id = ae.facility_list_item_id
                  AND afm.facility_id = af.id
                  AND afm.status IN ('AUTOMATIC', 'CONFIRMED', 'MERGED')
                  AND afm.is_active
              )
            )
          )
      ) c
    ORDER BY
      CASE
        WHEN c.is_claimed_data THEN 1
        WHEN c.is_promoted THEN 2
        WHEN c.is_verified THEN 3
        ELSE 4
      END,
      c.contributed_at DESC
    LIMIT
      1
  ) rba_id_ranked ON TRUE
  LEFT JOIN LATERAL (
    SELECT
      c.value::TEXT AS value_json,
      json_build_object(
        'contributor_id', c.contributor_admin_id,
        'contributor_name', c.contributor_name,
        'contributed_at', c.contributed_at,
        'is_claimed_data', c.is_claimed_data,
        'is_promoted', c.is_promoted,
        'is_verified', c.is_verified
      )::TEXT AS source_json
    FROM
      (
        SELECT
          ae.value,
          ae.created_at AS contributed_at,
          ac.admin_id AS contributor_admin_id,
          ac.name AS contributor_name,
          COALESCE(ae.contributor_id = afc.contributor_id, FALSE) AS is_claimed_data,
          COALESCE(
            ae.facility_list_item_id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            ),
            FALSE
          ) AS is_promoted,
          COALESCE(ac.is_verified, FALSE) AS is_verified
        FROM
          api_extendedfield ae
          JOIN api_contributor ac ON ac.id = ae.contributor_id
          LEFT JOIN api_facilitylistitem afli ON afli.id = ae.facility_list_item_id
          LEFT JOIN api_source s ON s.id = afli.source_id
        WHERE
          ae.facility_id = af.id
          AND ae.field_name = 'duns_id'
          AND (
            ae.facility_claim_id = afc.id
            OR (
              ae.facility_claim_id IS NULL
              AND ae.facility_list_item_id IS NOT NULL
              AND s.is_active
              AND s.is_public
              AND EXISTS (
                SELECT
                  1
                FROM
                  api_facilitymatch afm
                WHERE
                  afm.facility_list_item_id = ae.facility_list_item_id
                  AND afm.facility_id = af.id
                  AND afm.status IN ('AUTOMATIC', 'CONFIRMED', 'MERGED')
                  AND afm.is_active
              )
            )
          )
      ) c
    ORDER BY
      CASE
        WHEN c.is_claimed_data THEN 1
        WHEN c.is_promoted THEN 2
        WHEN c.is_verified THEN 3
        ELSE 4
      END,
      c.contributed_at DESC
    LIMIT
      1
  ) duns_id_ranked ON TRUE
  LEFT JOIN LATERAL (
    SELECT
      c.value::TEXT AS value_json,
      json_build_object(
        'contributor_id', c.contributor_admin_id,
        'contributor_name', c.contributor_name,
        'contributed_at', c.contributed_at,
        'is_claimed_data', c.is_claimed_data,
        'is_promoted', c.is_promoted,
        'is_verified', c.is_verified
      )::TEXT AS source_json
    FROM
      (
        SELECT
          ae.value,
          ae.created_at AS contributed_at,
          ac.admin_id AS contributor_admin_id,
          ac.name AS contributor_name,
          COALESCE(ae.contributor_id = afc.contributor_id, FALSE) AS is_claimed_data,
          COALESCE(
            ae.facility_list_item_id = af.created_from_id
            AND EXISTS (
              SELECT
                1
              FROM
                jsonb_array_elements(afli.processing_results) AS elem
              WHERE
                elem ->> 'action' = 'promote_match'
            ),
            FALSE
          ) AS is_promoted,
          COALESCE(ac.is_verified, FALSE) AS is_verified
        FROM
          api_extendedfield ae
          JOIN api_contributor ac ON ac.id = ae.contributor_id
          LEFT JOIN api_facilitylistitem afli ON afli.id = ae.facility_list_item_id
          LEFT JOIN api_source s ON s.id = afli.source_id
        WHERE
          ae.facility_id = af.id
          AND ae.field_name = 'lei_id'
          AND (
            ae.facility_claim_id = afc.id
            OR (
              ae.facility_claim_id IS NULL
              AND ae.facility_list_item_id IS NOT NULL
              AND s.is_active
              AND s.is_public
              AND EXISTS (
                SELECT
                  1
                FROM
                  api_facilitymatch afm
                WHERE
                  afm.facility_list_item_id = ae.facility_list_item_id
                  AND afm.facility_id = af.id
                  AND afm.status IN ('AUTOMATIC', 'CONFIRMED', 'MERGED')
                  AND afm.is_active
              )
            )
          )
      ) c
    ORDER BY
      CASE
        WHEN c.is_claimed_data THEN 1
        WHEN c.is_promoted THEN 2
        WHEN c.is_verified THEN 3
        ELSE 4
      END,
      c.contributed_at DESC
    LIMIT
      1
  ) lei_id_ranked ON TRUE
WHERE
  af.updated_at > :sql_last_value
  AND af.updated_at < CURRENT_TIMESTAMP
ORDER BY
  af.updated_at ASC
