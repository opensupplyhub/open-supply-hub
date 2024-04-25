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
        TO_CHAR(created_at, 'YYYY-MM') AS month,
        SUM(COUNT(id) FILTER (WHERE (LENGTH(sector::text) > 2 AND sector::text != '{Unspecified}') OR LENGTH(extended_fields::text) > 2)) OVER (PARTITION BY EXTRACT(YEAR FROM created_at) ORDER BY TO_CHAR(created_at, 'YYYY-MM')) AS total,
        SUM(COUNT(id) FILTER (WHERE LENGTH(sector::text) > 2 AND sector::text != '{Unspecified}')) OVER (PARTITION BY EXTRACT(YEAR FROM created_at) ORDER BY TO_CHAR(created_at, 'YYYY-MM')) AS sector
    FROM api_facilityindex
    GROUP BY TO_CHAR(created_at, 'YYYY-MM'), EXTRACT(YEAR FROM created_at)
) AS query1
FULL OUTER JOIN (
    SELECT
        TO_CHAR(created_at, 'YYYY-MM') AS month,
        SUM(COUNT(*) FILTER (WHERE field_name ='number_of_workers')) OVER (PARTITION BY EXTRACT(YEAR FROM created_at) ORDER BY TO_CHAR(created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) AS number_of_workers,
        SUM(COUNT(*) FILTER (WHERE field_name ='facility_type')) OVER (PARTITION BY EXTRACT(YEAR FROM created_at) ORDER BY TO_CHAR(created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) AS facility_type,
        SUM(COUNT(*) FILTER (WHERE field_name ='processing_type')) OVER (PARTITION BY EXTRACT(YEAR FROM created_at) ORDER BY TO_CHAR(created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) AS processing_type,
        SUM(COUNT(*) FILTER (WHERE field_name ='product_type')) OVER (PARTITION BY EXTRACT(YEAR FROM created_at) ORDER BY TO_CHAR(created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) AS product_type,
        SUM(COUNT(*) FILTER (WHERE field_name ='parent_company')) OVER (PARTITION BY EXTRACT(YEAR FROM created_at) ORDER BY TO_CHAR(created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) AS parent_company,
        SUM(COUNT(*) FILTER (WHERE field_name ='native_language_name')) OVER (PARTITION BY EXTRACT(YEAR FROM created_at) ORDER BY TO_CHAR(created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) AS native_language_name,
        SUM(COUNT(*) FILTER (WHERE field_name ='address')) OVER (PARTITION BY EXTRACT(YEAR FROM created_at) ORDER BY TO_CHAR(created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) AS address_claimed,
        SUM(COUNT(*) FILTER (WHERE field_name ='name')) OVER (PARTITION BY EXTRACT(YEAR FROM created_at) ORDER BY TO_CHAR(created_at, 'YYYY-MM') ROWS UNBOUNDED PRECEDING) AS name_claimed
    FROM
        api_extendedfield
    GROUP BY TO_CHAR(created_at, 'YYYY-MM'), EXTRACT(YEAR FROM created_at)
) AS query2 ON query1.month = query2.month
ORDER BY COALESCE(query1.month, query2.month) DESC;
