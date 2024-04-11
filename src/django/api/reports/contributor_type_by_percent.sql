CREATE OR REPLACE FUNCTION calc_value(total_count bigint, filtered_count bigint)
RETURNS text AS $$
DECLARE
begin
	IF total_count=0 then
        RETURN '0%';
    ELSE
        RETURN round(100.0 * filtered_count /total_count,2) || '%';
    END IF;
END;
$$ LANGUAGE plpgsql;
SELECT
  month,
  COUNT(*) AS total_contributors,
  calc_column(COUNT(*), COUNT(*) filter (where contrib_type ="Brand / Retailer")) as "Brand / Retailer",
  calc_column(COUNT(*), COUNT(*) filter (where contrib_type ="Civil Society Organization")) as "Civil Society Organization",
  calc_column(COUNT(*), COUNT(*) filter (where contrib_type ="Facility / Factory / Manufacturing Group / Supplier / Vendor")) as "Facility / Factory / Manufacturing Group / Supplier / Vendor",
  calc_column(COUNT(*), COUNT(*) filter (where contrib_type ="Multi-Stakeholder Initiative")) as "Multi-Stakeholder Initiative",
  calc_column(COUNT(*), COUNT(*) filter (where contrib_type ="Auditor / Certification Scheme / Service Provider")) as "Auditor / Certification Scheme / Service Provider",
  calc_column(COUNT(*), COUNT(*) filter (where contrib_type ="Academic / Researcher / Journalist / Student")) as "Academic / Researcher / Journalist / Student",
  calc_column(COUNT(*), COUNT(*) filter (where contrib_type ="Other")) as "Other"

FROM (
  SELECT distinct
    min(to_char(s.created_at, 'YYYY-MM')) AS month,
    c.id,
    c.contrib_type
    FROM api_facilitymatch m
        JOIN api_facilitylistitem i on m.facility_list_item_id = i.id
        JOIN api_source s on i.source_id = s.id
        JOIN api_contributor c ON s.contributor_id = c.id
        JOIN api_user u ON u.id = c.admin_id
    WHERE m.status NOT IN ('REJECTED', 'PENDING')
    AND u.email NOT LIKE '%openapparel.org%'
    AND u.email NOT LIKE '%opensupplyhub.org%'
  GROUP BY c.id, c.contrib_type
) q
GROUP BY month
ORDER BY month DESC;