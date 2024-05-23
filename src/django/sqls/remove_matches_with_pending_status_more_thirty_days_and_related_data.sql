CREATE OR REPLACE FUNCTION remove_matches_with_pending_status_more_thirty_days_and_related_data()
RETURNS void AS $$
BEGIN
    -- Delete the matches that have status as PENDING and updated_at more than 30 days ago
    DELETE FROM api_facilitymatch
    WHERE api_facilitymatch.status='PENDING' 
    AND api_facilitymatch.updated_at < (NOW() - interval '1 month');

    DELETE FROM api_facilitymatchtemp 
    WHERE api_facilitymatchtemp.status='PENDING'
    AND api_facilitymatchtemp.updated_at < (NOW() - interval '1 month');

    -- Create temporary tables to store the IDs of the items that do not have matches and are not have facilities created from them
    CREATE TEMPORARY TABLE temporary_facility_list_item_ids AS
    SELECT id 
    FROM api_facilitylistitem 
        WHERE NOT EXISTS (
        SELECT 1
        FROM api_facilitymatch
        WHERE api_facilitymatch.facility_list_item_id = api_facilitylistitem.id
    )
    AND NOT EXISTS (
        SELECT 1
        FROM api_facility
        WHERE api_facility.created_from_id = api_facilitylistitem.id
    );

    CREATE TEMPORARY TABLE temporary_facility_list_item_temp_ids AS
    SELECT id
    FROM api_facilitylistitemtemp 
    WHERE NOT EXISTS (
        SELECT 1
        FROM api_facilitymatchtemp
        WHERE api_facilitymatchtemp.facility_list_item_id = api_facilitylistitemtemp.id
    )
    AND NOT EXISTS (
        SELECT 1
        FROM api_facility
        WHERE api_facility.created_from_id = api_facilitylistitemtemp.id
    );

    -- Perform deletions using the temporary collected IDs table
    DELETE FROM api_facilitylistitemfield
    WHERE facility_list_item_id IN (SELECT id FROM temporary_facility_list_item_ids);

    DELETE FROM api_extendedfield
    WHERE facility_list_item_id IN (SELECT id FROM temporary_facility_list_item_ids);

    DELETE FROM api_historicalfacilitymatch
    WHERE facility_list_item_id IN (SELECT id FROM temporary_facility_list_item_ids);

    DELETE FROM api_historicalextendedfield
    WHERE facility_list_item_id IN (SELECT id FROM temporary_facility_list_item_ids);

    DELETE FROM api_historicalfacilitymatchtemp
    WHERE facility_list_item_id IN (SELECT id FROM temporary_facility_list_item_temp_ids);

    -- Delete the items that do not have matches and are not have facilities created from them
    DELETE FROM api_facilitylistitem WHERE id IN (SELECT id FROM temporary_facility_list_item_ids);
    DELETE FROM api_facilitylistitemtemp WHERE id IN (SELECT id FROM temporary_facility_list_item_temp_ids);

    -- Drop the temporary tables
    DROP TABLE IF EXISTS temporary_facility_list_item_ids;
    DROP TABLE IF EXISTS temporary_facility_list_item_temp_ids;

END;
$$ LANGUAGE plpgsql;

SELECT remove_matches_with_pending_status_more_thirty_days_and_related_data();
