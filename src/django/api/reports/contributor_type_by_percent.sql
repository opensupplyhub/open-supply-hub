SELECT
  month,
  COUNT(*) AS total_contributors,
  CASE
     WHEN COUNT(*)=0  THEN 0 || '%'
     ELSE round(100.0 * COUNT(*) filter (where contrib_type = 'Brand / Retailer') /COUNT(*),2) || '%'
end as "Brand / Retailer",
  CASE
     WHEN COUNT(*)=0  THEN 0 || '%'
     ELSE round(100.0 * COUNT(*) filter (where contrib_type = 'Civil Society Organization') /COUNT(*),2) || '%'
end as "Civil Society Organization",
  CASE
     WHEN COUNT(*)=0  THEN 0 || '%'
     ELSE round(100.0 * COUNT(*) filter (where contrib_type = 'Facility / Factory / Manufacturing Group / Supplier / Vendor') /COUNT(*),2) || '%'
end as "Facility / Factory / Manufacturing Group / Supplier / Vendor",
  CASE
     WHEN COUNT(*)=0  THEN 0 || '%'
     ELSE round(100.0 * COUNT(*) filter (where contrib_type = 'Multi-Stakeholder Initiative') /COUNT(*),2) || '%'
end as "Multi-Stakeholder Initiative",
  CASE
     WHEN COUNT(*)=0  THEN 0 || '%'
     ELSE round(100 * COUNT(*) filter (where contrib_type = 'Auditor / Certification Scheme / Service Provider') /COUNT(*),2) || '%'
end as "Auditor / Certification Scheme / Service Provider",
  CASE
     WHEN COUNT(*)=0  THEN 0 || '%'
     ELSE round(100 * COUNT(*) filter (where contrib_type = 'Academic / Researcher / Journalist / Student') /COUNT(*),2) || '%'
end as "Academic / Researcher / Journalist / Student",
  CASE
     WHEN COUNT(*)=0  THEN 0 || '%'
     ELSE round(100 * COUNT(*) filter (where contrib_type = 'Other') /COUNT(*),2) || '%'
end as "Other"
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