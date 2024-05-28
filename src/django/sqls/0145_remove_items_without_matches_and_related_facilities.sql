CREATE OR REPLACE PROCEDURE remove_items_without_matches_and_related_facilities()
LANGUAGE plpgsql
AS $$
DECLARE
    item_ids INTEGER[];
BEGIN
    SELECT array_agg(id) INTO item_ids
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
    )
    AND api_facilitylistitem.updated_at < (NOW() - interval '1 month');

    -- Perform deletions using the stored arrays of IDs
    DELETE FROM api_facilitylistitemfield
    WHERE facility_list_item_id = ANY(item_ids);

    DELETE FROM api_extendedfield
    WHERE facility_list_item_id = ANY(item_ids);

    DELETE FROM api_historicalextendedfield
    WHERE facility_list_item_id = ANY(item_ids);

    -- Delete the items that do not have matches and are not have facilities created from them
    DELETE FROM api_facilitylistitem WHERE id = ANY(item_ids);
END;
$$;
