SELECT COALESCE(query1.month, query2.month) AS month,
       COALESCE(query1.total, 0) AS total,
       COALESCE(query1.sector, 0) AS sector,
       COALESCE(query2.number_of_workers, 0) AS number_of_workers,
       COALESCE(query2.facility_type, 0) AS facility_type,
       COALESCE(query2.processing_type, 0) AS processing_type,
       COALESCE(query2.product_type, 0) AS product_type,
       COALESCE(query2.parent_company, 0) AS parent_company,
       COALESCE(query2.native_language_name, 0) AS native_language_name,
       COALESCE(query2.address_claimed, 0) AS address_claimed,
       COALESCE(query2.name_claimed, 0) AS name_claimed
FROM (
    SELECT
        TO_CHAR(af.created_at, 'YYYY-MM') AS month,
        SUM(COUNT(af.id) FILTER (WHERE (LENGTH(coalesce((SELECT array_agg(distinct(sector)) FROM index_sector(af.id)), '{}')::text) > 2 AND coalesce((SELECT array_agg(distinct(sector)) FROM index_sector(af.id)), '{}')::text != '{Unspecified}') OR LENGTH(afi.extended_fields::text) > 2)) OVER (PARTITION BY EXTRACT(YEAR FROM af.created_at) ORDER BY TO_CHAR(af.created_at, 'YYYY-MM')) AS total,
        SUM(COUNT(af.id) FILTER (WHERE LENGTH(coalesce((SELECT array_agg(distinct(sector)) FROM index_sector(af.id)), '{}')::text) > 2 AND coalesce((SELECT array_agg(distinct(sector)) FROM index_sector(af.id)), '{}')::text != '{Unspecified}')) OVER (PARTITION BY EXTRACT(YEAR FROM af.created_at) ORDER BY TO_CHAR(af.created_at, 'YYYY-MM')) AS sector
    FROM api_facility af
       JOIN api_facilityindex afi ON af.id=afi.id
       WHERE af.created_at >= '2021-12-31 23:59:59.999999+00:00'
    GROUP BY TO_CHAR(af.created_at, 'YYYY-MM'), EXTRACT(YEAR FROM af.created_at)
) AS query1
FULL OUTER JOIN (
    SELECT
        TO_CHAR(created_at, 'YYYY-MM') AS month,
        SUM(COUNT(DISTINCT CASE WHEN field_name = 'number_of_workers' THEN facility_id END)) OVER (PARTITION BY EXTRACT(YEAR FROM created_at) ORDER BY TO_CHAR(created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) AS number_of_workers,
        SUM(COUNT(DISTINCT CASE WHEN field_name = 'facility_type' THEN facility_id END)) OVER (PARTITION BY EXTRACT(YEAR FROM created_at) ORDER BY TO_CHAR(created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) as facility_type,
        SUM(COUNT(DISTINCT CASE WHEN field_name = 'processing_type' THEN facility_id END)) OVER (PARTITION BY EXTRACT(YEAR FROM created_at) ORDER BY TO_CHAR(created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) as processing_type,
        SUM(COUNT(DISTINCT CASE WHEN field_name = 'product_type' THEN facility_id END)) OVER (PARTITION BY EXTRACT(YEAR FROM created_at) ORDER BY TO_CHAR(created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) as product_type,
        SUM(COUNT(DISTINCT CASE WHEN field_name = 'parent_company' THEN facility_id END)) OVER (PARTITION BY EXTRACT(YEAR FROM created_at) ORDER BY TO_CHAR(created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) as parent_company,
        SUM(COUNT(DISTINCT CASE WHEN field_name = 'native_language_name' THEN facility_id END)) OVER (PARTITION BY EXTRACT(YEAR FROM created_at) ORDER BY TO_CHAR(created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) as native_language_name,
        SUM(COUNT(DISTINCT CASE WHEN field_name = 'address' THEN facility_id END)) OVER (PARTITION BY EXTRACT(YEAR FROM created_at) ORDER BY TO_CHAR(created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) as address_claimed,
        SUM(COUNT(DISTINCT CASE WHEN field_name = 'name' THEN facility_id END)) OVER (PARTITION BY EXTRACT(YEAR FROM created_at) ORDER BY TO_CHAR(created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) as name_claimed
    FROM
        api_extendedfield
    GROUP BY TO_CHAR(created_at, 'YYYY-MM'), EXTRACT(YEAR FROM created_at)
) AS query2 ON query1.month = query2.month
ORDER BY COALESCE(query1.month, query2.month) DESC;
