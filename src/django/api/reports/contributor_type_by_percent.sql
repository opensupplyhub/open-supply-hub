-- Count the total number of contributors which cumulate each month
-- Count cumulative level of contributor type by % only for contributors that have active data.

CREATE OR REPLACE FUNCTION calc_column(total_count bigint, filtered_count bigint)
RETURNS text AS $$
DECLARE
BEGIN
    IF total_count = 0 THEN
        RETURN '0%';
    ELSE
        RETURN round(100.0 * filtered_count / total_count, 2) || '%';
    END IF;
END;
$$ LANGUAGE plpgsql;
WITH base_query AS (
  SELECT
    min(to_char(s.created_at, 'YYYY-MM')) AS month,
    c.id,
    c.contrib_type
  FROM api_facilitymatch m
    JOIN api_facilitylistitem i ON m.facility_list_item_id = i.id
    JOIN api_source s ON i.source_id = s.id
    JOIN api_contributor c ON s.contributor_id = c.id
    JOIN api_user u ON u.id = c.admin_id
  WHERE m.status NOT IN ('REJECTED', 'PENDING')
    AND u.email NOT LIKE '%openapparel.org%'
    AND u.email NOT LIKE '%opensupplyhub.org%'
  GROUP BY c.id, c.contrib_type
),
monthly_counts AS (
  SELECT
    month,
    COUNT(*) AS total_contributors,
    COUNT(*) FILTER (WHERE contrib_type = 'Brand / Retailer') AS "Brand / Retailer",
    COUNT(*) FILTER (WHERE contrib_type = 'Civil Society Organization') AS "Civil Society Organization",
    COUNT(*) FILTER (WHERE contrib_type = 'Facility / Factory / Manufacturing Group / Supplier / Vendor') AS "Facility / Factory / Manufacturing Group / Supplier / Vendor",
    COUNT(*) FILTER (WHERE contrib_type = 'Multi-Stakeholder Initiative') AS "Multi-Stakeholder Initiative",
    COUNT(*) FILTER (WHERE contrib_type = 'Auditor / Certification Scheme / Service Provider') AS "Auditor / Certification Scheme / Service Provider",
    COUNT(*) FILTER (WHERE contrib_type = 'Academic / Researcher / Journalist / Student') AS "Academic / Researcher / Journalist / Student",
    COUNT(*) FILTER (WHERE contrib_type = 'Other') AS "Other"
  FROM base_query
  GROUP BY month
),
cumulative_counts AS (
  SELECT
    month,
    SUM(total_contributors) OVER (ORDER BY month) AS total_contributors,
    SUM("Brand / Retailer") OVER (ORDER BY month) AS "Brand / Retailer",
    SUM("Civil Society Organization") OVER (ORDER BY month) AS "Civil Society Organization",
    SUM("Facility / Factory / Manufacturing Group / Supplier / Vendor") OVER (ORDER BY month) AS "Facility / Factory / Manufacturing Group / Supplier / Vendor",
    SUM("Multi-Stakeholder Initiative") OVER (ORDER BY month) AS "Multi-Stakeholder Initiative",
    SUM("Auditor / Certification Scheme / Service Provider") OVER (ORDER BY month) AS "Auditor / Certification Scheme / Service Provider",
    SUM("Academic / Researcher / Journalist / Student") OVER (ORDER BY month) AS "Academic / Researcher / Journalist / Student",
    SUM("Other") OVER (ORDER BY month) AS "Other"
  FROM monthly_counts
)
SELECT
  month,
  total_contributors,
  calc_column(total_contributors, "Brand / Retailer") AS "Brand / Retailer",
  calc_column(total_contributors, "Civil Society Organization") AS "Civil Society Organization",
  calc_column(total_contributors, "Facility / Factory / Manufacturing Group / Supplier / Vendor") AS "Facility / Factory / Manufacturing Group / Supplier / Vendor",
  calc_column(total_contributors, "Multi-Stakeholder Initiative") AS "Multi-Stakeholder Initiative",
  calc_column(total_contributors, "Auditor / Certification Scheme / Service Provider") AS "Auditor / Certification Scheme / Service Provider",
  calc_column(total_contributors, "Academic / Researcher / Journalist / Student") AS "Academic / Researcher / Journalist / Student",
  calc_column(total_contributors, "Other") AS "Other"
FROM cumulative_counts
ORDER BY month DESC;