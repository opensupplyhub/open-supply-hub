CREATE OR REPLACE PROCEDURE remove_facilitylistitems_where_facility_id_is_null()
LANGUAGE plpgsql
AS $$
BEGIN
    -- Update facility_id in api_facilitylistitem
    UPDATE api_facilitylistitem
    SET facility_id = api_facility.id
    FROM api_facility
    WHERE api_facilitylistitem.id = api_facility.created_from_id
    AND api_facilitylistitem.facility_id IS NULL;

    -- Create temporary tables to store the IDs of the items that have facility_id as NULL
    CREATE TEMPORARY TABLE temporary_facility_list_item_ids AS
    SELECT id 
    FROM api_facilitylistitem 
    WHERE facility_id IS NULL;

    CREATE TEMPORARY TABLE temporary_facility_list_item_temp_ids AS
    SELECT id
    FROM api_facilitylistitemtemp 
    WHERE facility_id IS NULL;

    -- Perform deletions using the temporary collected IDs table
    DELETE FROM api_facilitymatch
    WHERE facility_list_item_id IN (SELECT id FROM temporary_facility_list_item_ids);

    DELETE FROM api_facilitylistitemfield
    WHERE facility_list_item_id IN (SELECT id FROM temporary_facility_list_item_ids);

    DELETE FROM api_extendedfield
    WHERE facility_list_item_id IN (SELECT id FROM temporary_facility_list_item_ids);

    DELETE FROM api_historicalfacilitymatch
    WHERE facility_list_item_id IN (SELECT id FROM temporary_facility_list_item_ids);

    DELETE FROM api_historicalextendedfield
    WHERE facility_list_item_id IN (SELECT id FROM temporary_facility_list_item_ids);

    DELETE FROM api_facilitymatchtemp
    WHERE facility_list_item_id IN (SELECT id FROM temporary_facility_list_item_temp_ids);

    DELETE FROM api_historicalfacilitymatchtemp
    WHERE facility_list_item_id IN (SELECT id FROM temporary_facility_list_item_temp_ids);

    -- Delete the items that have facility_id as NULL
    DELETE FROM api_facilitylistitem 
    WHERE facility_id IS NULL;

    DELETE FROM api_facilitylistitemtemp 
    WHERE facility_id IS NULL;

    -- Drop the temporary tables
    DROP TABLE IF EXISTS temporary_facility_list_item_ids;
    DROP TABLE IF EXISTS temporary_facility_list_item_temp_ids;
END;
$$;
