select * from(select TO_CHAR(af.created_at, 'YYYY-MM') AS month,
COUNT(af.id) filter (where (length(af.sector::text) > 2 and af.sector::text != '{Unspecified}')
or length(af.extended_fields::text) > 2
) as total,
COUNT(af.id) filter (where (length(af.sector::text) > 2 and af.sector::text != '{Unspecified}')
) as sector
from api_facilityindex af
group by month
order by month) as query1
INNER JOIN (
SELECT
    TO_CHAR(ae.created_at, 'YYYY-MM') AS month,
    SUM(COUNT(*) FILTER (WHERE ae.field_name ='number_of_workers')) OVER (PARTITION BY EXTRACT(YEAR FROM ae.created_at) ORDER BY TO_CHAR(ae.created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) AS number_of_workers,
    SUM(COUNT(*) FILTER (WHERE ae.field_name ='facility_type')) OVER (PARTITION BY EXTRACT(YEAR FROM ae.created_at) ORDER BY TO_CHAR(ae.created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) AS facility_type,
    SUM(COUNT(*) FILTER (WHERE ae.field_name ='processing_type')) OVER (PARTITION BY EXTRACT(YEAR FROM ae.created_at) ORDER BY TO_CHAR(ae.created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) AS processing_type,
    SUM(COUNT(*) FILTER (WHERE ae.field_name ='product_type')) OVER (PARTITION BY EXTRACT(YEAR FROM ae.created_at) ORDER BY TO_CHAR(ae.created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) AS product_type,
    SUM(COUNT(*) FILTER (WHERE ae.field_name ='parent_company')) OVER (PARTITION BY EXTRACT(YEAR FROM ae.created_at) ORDER BY TO_CHAR(ae.created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) AS parent_company,
    SUM(COUNT(*) FILTER (WHERE ae.field_name ='native_language_name')) OVER (PARTITION BY EXTRACT(YEAR FROM ae.created_at) ORDER BY TO_CHAR(ae.created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) AS native_language_name,
    SUM(COUNT(*) FILTER (WHERE ae.field_name ='address')) OVER (PARTITION BY EXTRACT(YEAR FROM ae.created_at) ORDER BY TO_CHAR(ae.created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) AS address_claimed,
    SUM(COUNT(*) FILTER (WHERE ae.field_name ='name')) OVER (PARTITION BY EXTRACT(YEAR FROM ae.created_at) ORDER BY TO_CHAR(ae.created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) AS name_claimed
FROM
    api_extendedfield ae
GROUP BY
    TO_CHAR(ae.created_at, 'YYYY-MM'),
    EXTRACT(YEAR FROM ae.created_at)
ORDER BY month DESC
  ) as query2 USING (month)