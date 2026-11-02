DROP TRIGGER IF EXISTS facility_index_isic_mapped_update_trigger
	ON api_facilityindex;
DROP TRIGGER IF EXISTS facility_index_isic_mapped_insert_trigger
	ON api_facilityindex;
DROP FUNCTION IF EXISTS set_isic_mapped_columns();
DROP FUNCTION IF EXISTS isic_mapped_codes(VARCHAR[], VARCHAR[]);
DROP FUNCTION IF EXISTS isic_mapped_entries(VARCHAR[], VARCHAR[]);
