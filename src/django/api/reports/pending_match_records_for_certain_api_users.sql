SELECT 
    src.contributor_id,
    ac.name AS contributor_name,
    COUNT(*) AS pending_matches_count
FROM 
    api_facilitymatch afm
JOIN 
    api_facilitylistitem afli ON afm.facility_list_item_id = afli.id
JOIN 
    api_source src ON afli.source_id = src.id
JOIN
    api_contributor ac ON src.contributor_id = ac.id
WHERE 
    afm.status = 'PENDING'
    AND src.contributor_id IN (2060, 1045, 685, 3356)
GROUP BY 
    src.contributor_id, ac.name
