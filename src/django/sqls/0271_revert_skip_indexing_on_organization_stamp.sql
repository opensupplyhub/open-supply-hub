/*
Restores the two trigger functions to the bodies created by
0131_create_table_triggers.sql.
*/

CREATE OR REPLACE
FUNCTION handle_source_post_update_insert_indexing_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $body$
BEGIN
	CALL perform_source_indexing(NEW.id);
	RETURN NEW;
END;

$body$;

CREATE OR REPLACE
FUNCTION handle_facility_claim_post_update_insert_indexing_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $body$
BEGIN
	CALL perform_facility_claim_indexing(NEW.facility_id);
	RETURN NEW;
END;

$body$;
