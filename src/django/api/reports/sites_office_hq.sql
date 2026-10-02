-- Production sites where at least one contributor has submitted a facility
-- type that maps to "Office/HQ". Raw values are aggregated across all
-- contributing sources with " | " as the separator.
-- Run with: docker compose exec -T database psql -U opensupplyhub < src/django/api/reports/sites_office_hq.sql

SELECT
    f.id                                                        AS os_id,
    f.name,
    f.address,
    f.country_code,
    ST_Y(f.location)                                            AS lat,
    ST_X(f.location)                                            AS lng,
    STRING_AGG(DISTINCT ef.value->>'raw_values', ' | ')         AS facility_type_raw,
    STRING_AGG(DISTINCT c.name, ' | ')                          AS claimed_by
FROM api_facility f
JOIN api_extendedfield ef
    ON ef.facility_id = f.id
    AND ef.field_name = 'facility_type'
LEFT JOIN api_facilityclaim fc
    ON fc.facility_id = f.id
    AND fc.status = 'APPROVED'
LEFT JOIN api_contributor c
    ON c.id = fc.contributor_id
WHERE EXISTS (
    SELECT 1
    FROM api_extendedfield ef2,
         jsonb_array_elements(ef2.value->'matched_values') AS mv
    WHERE ef2.facility_id = f.id
      AND ef2.field_name  = 'facility_type'
      AND mv->>2          = 'Office / HQ'
)
GROUP BY f.id, f.name, f.address, f.country_code, f.location
ORDER BY STRING_AGG(DISTINCT c.name, ' | ') IS NULL, f.id;
