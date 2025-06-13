CREATE TRIGGER contributor_post_delete_indexing_trigger
    AFTER
DELETE
	ON
	api_contributor
	FOR EACH ROW
    EXECUTE FUNCTION handle_contributor_post_delete_indexing_trigger();

CREATE TRIGGER contributor_post_insert_update_indexing_trigger
    AFTER
INSERT
	OR
UPDATE
	ON
	api_contributor
	FOR EACH ROW
    EXECUTE FUNCTION handle_contributor_post_update_insert_indexing_trigger();

CREATE TRIGGER extended_field_post_delete_indexing_trigger
    AFTER
DELETE
	ON
	api_extendedfield
	FOR EACH ROW
    EXECUTE FUNCTION handle_extended_field_post_delete_indexing_trigger();

CREATE TRIGGER extended_field_post_update_insert_indexing_trigger
    AFTER
UPDATE
	OR
INSERT
	ON
	api_extendedfield
	FOR EACH ROW
    EXECUTE FUNCTION handle_extended_field_post_update_insert_indexing_trigger();

CREATE TRIGGER facility_post_delete_indexing_trigger
    AFTER
DELETE
	ON
	api_facility
	FOR EACH ROW
    EXECUTE FUNCTION handle_facility_post_delete_indexing_trigger();

CREATE TRIGGER facility_post_update_insert_indexing_trigger
    AFTER
UPDATE
	OR
INSERT
	ON
	api_facility
	FOR EACH ROW
    EXECUTE FUNCTION handle_facility_post_update_insert_indexing_trigger();

CREATE TRIGGER facility_claim_post_delete_indexing_trigger
    AFTER
DELETE
	ON
	api_facilityclaim
	FOR EACH ROW
    EXECUTE FUNCTION handle_facility_claim_post_delete_indexing_trigger();

CREATE TRIGGER facility_claim_post_update_insert_indexing_trigger
    AFTER
UPDATE
	OR
INSERT
	ON
	api_facilityclaim
	FOR EACH ROW
    EXECUTE FUNCTION handle_facility_claim_post_update_insert_indexing_trigger();

CREATE TRIGGER manual_list_reject_revert_trigger
    AFTER
UPDATE
	ON
	api_facilitylist
	FOR EACH ROW
    EXECUTE FUNCTION handle_manual_list_reject_revert_trigger();

CREATE TRIGGER delete_fli
    BEFORE delete ON api_facilitylistitem
    FOR EACH ROW
    EXECUTE procedure delete_facility_list_item_fields_trigger();

CREATE TRIGGER facility_list_item_post_delete_indexing_trigger
    AFTER
DELETE
	ON
	api_facilitylistitem
	FOR EACH ROW
    EXECUTE FUNCTION handle_facility_list_item_post_delete_indexing_trigger();

CREATE TRIGGER update_fli_1
    AFTER update or insert ON api_facilitylistitem
    FOR EACH ROW
    EXECUTE procedure update_facility_list_item_fields_trigger();

CREATE TRIGGER update_fli_2
    AFTER
UPDATE
	OR
INSERT
	ON
	api_facilitylistitem
	FOR EACH ROW
    EXECUTE FUNCTION handle_facility_list_item_post_update_insert_indexing_trigger();

CREATE TRIGGER facility_match_post_delete_indexing_trigger
    AFTER
DELETE
	ON
	api_facilitymatch
	FOR EACH ROW
    EXECUTE FUNCTION handle_facility_match_post_delete_indexing_trigger();

CREATE TRIGGER facility_match_post_update_insert_indexing_trigger
    AFTER
UPDATE
	OR
INSERT
	ON
	api_facilitymatch
	FOR EACH ROW
    EXECUTE FUNCTION handle_facility_match_post_update_insert_indexing_trigger();

CREATE TRIGGER source_post_delete_indexing_trigger
    AFTER
DELETE
	ON
	api_source
	FOR EACH ROW
    EXECUTE FUNCTION handle_source_post_delete_indexing_trigger();

CREATE TRIGGER source_post_update_insert_indexing_trigger
    AFTER
UPDATE
	OR
INSERT
	ON
	api_source
	FOR EACH ROW
    EXECUTE FUNCTION handle_source_post_update_insert_indexing_trigger();
