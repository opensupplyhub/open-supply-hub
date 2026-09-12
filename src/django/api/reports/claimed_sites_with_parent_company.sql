-- Approved claimed facilities where a parent company has been listed.
-- Parent company may be stored as a linked contributor (parent_company_id)
-- or as free text (parent_company_name). COALESCE prefers the linked
-- contributor name when both are present.
-- Run with: docker compose exec -T database psql -U opensupplyhub < src/django/api/reports/claimed_sites_with_parent_company.sql

SELECT
    f.id                                            AS os_id,
    f.name                                          AS facility_name,
    f.address                                       AS facility_address,
    f.country_code,
    COALESCE(pc.name, fc.parent_company_name)       AS parent_company,
    c.name                                          AS claimed_by,
    fc.status_change_date                           AS claim_approved_date
FROM api_facilityclaim fc
JOIN api_facility f          ON f.id  = fc.facility_id
JOIN api_contributor c       ON c.id  = fc.contributor_id
LEFT JOIN api_contributor pc ON pc.id = fc.parent_company_id
WHERE fc.status = 'APPROVED'
  AND (
      fc.parent_company_id IS NOT NULL
      OR (fc.parent_company_name IS NOT NULL AND fc.parent_company_name != '')
  )
ORDER BY fc.status_change_date DESC;
