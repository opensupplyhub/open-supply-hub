CREATE OR REPLACE PROCEDURE remove_items_where_facility_id_is_null()
LANGUAGE plpgsql
AS $$
DECLARE
    item_ids INTEGER[];
BEGIN
    -- Update facility_id in api_facilitylistitem
    UPDATE api_facilitylistitem
    SET facility_id = api_facility.id
    FROM api_facility
    WHERE api_facilitylistitem.id = api_facility.created_from_id
    AND api_facilitylistitem.facility_id IS NULL;

    -- Store IDs of api_facilitylistitem where facility_id is NULL and updated_at is more than 30 days ago in an array
    SELECT array_agg(id) INTO item_ids
    FROM api_facilitylistitem 
    WHERE facility_id IS NULL AND updated_at < (NOW() - INTERVAL '30 days');

    -- Use the array of IDs to perform deletions
    DELETE FROM api_facilitymatch
    WHERE facility_list_item_id = ANY(item_ids);

    DELETE FROM api_facilitylistitemfield
    WHERE facility_list_item_id = ANY(item_ids);

    DELETE FROM api_extendedfield
    WHERE facility_list_item_id = ANY(item_ids);

    DELETE FROM api_historicalfacilitymatch
    WHERE facility_list_item_id = ANY(item_ids);

    DELETE FROM api_historicalextendedfield
    WHERE facility_list_item_id = ANY(item_ids);

    -- Delete the items that have facility_id as NULL using the stored IDs
    DELETE FROM api_facilitylistitem 
    WHERE id = ANY(item_ids);
END;
$$;
