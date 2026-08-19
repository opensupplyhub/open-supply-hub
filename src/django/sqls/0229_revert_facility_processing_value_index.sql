DROP TRIGGER IF EXISTS facility_index_processing_value_insert_trigger
	ON api_facilityindex;

DROP TRIGGER IF EXISTS facility_index_processing_value_update_trigger
	ON api_facilityindex;

DROP TRIGGER IF EXISTS facility_index_processing_value_delete_trigger
	ON api_facilityindex;

DROP FUNCTION IF EXISTS handle_facility_index_processing_value_trigger();

DROP PROCEDURE IF EXISTS recompute_facility_processing_values();

DROP PROCEDURE IF EXISTS apply_facility_processing_value_delta(
	TEXT, VARCHAR[], VARCHAR[]
);

DROP FUNCTION IF EXISTS is_indexable_facility_processing_value(TEXT);

DROP TABLE IF EXISTS api_facility_processing_value;
