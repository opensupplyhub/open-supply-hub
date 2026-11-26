/*
Reverts 0272_organization_indexing_triggers.sql: drops the organization
trigger. The guard on the api_source and api_facilityclaim trigger
functions is put back by 0271_skip_indexing_on_organization_stamp.sql,
which the migration runs after this file.
*/

DROP TRIGGER IF EXISTS organization_post_update_indexing_trigger
	ON api_organization;

DROP FUNCTION IF EXISTS handle_organization_post_update_indexing_trigger();

DROP PROCEDURE IF EXISTS perform_organization_indexing(integer);
