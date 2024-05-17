CREATE OR REPLACE PROCEDURE remove_facilitylistitems_with_potential_match_status_more_thirty_days()
LANGUAGE SQL
AS $$

-- Begin the transaction for deletion
BEGIN;

-- Use CTE to store the IDs of items to be deleted
WITH cte_facility_list_item_ids AS (
    SELECT id 
    FROM api_facilitylistitem 
    WHERE facility_id IS NULL
)

-- Delete from api_facilitymatch using the CTE
DELETE FROM api_facilitymatch
WHERE facility_list_item_id IN (SELECT id FROM cte_facility_list_item_ids);

-- Delete from api_facilitylistitemfield using the CTE
DELETE FROM api_facilitylistitemfield
WHERE facility_list_item_id IN (SELECT id FROM cte_facility_list_item_ids);

-- Commit the transaction
COMMIT;
