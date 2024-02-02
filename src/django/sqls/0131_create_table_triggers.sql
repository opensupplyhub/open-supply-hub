/*Triggers and trigger-related functionality for the api_contributor table.
The columns of the api_facilityindex table that will be updated
are chosen based on the rule that data generated for them can be
dependent on the api_contributor table.*/
CREATE OR REPLACE
PROCEDURE perform_contributor_indexing(contributor_identifier integer)
LANGUAGE plpgsql
AS $body$
DECLARE facility_ids TEXT[];

BEGIN
SELECT
	COALESCE(array_agg(af.id),
	'{}')
INTO
	facility_ids
FROM
	api_facility af
JOIN api_facilitylistitem afli ON
	af.id = afli.facility_id
JOIN api_source asrc ON
	afli.source_id = asrc.id
WHERE
	asrc.contributor_id = contributor_identifier;

IF array_length(facility_ids,
1) > 0 THEN
UPDATE
	api_facilityindex afin
SET
	(
	contributors_count,
	contrib_types,
	contributors,
	custom_text,
	facility_names,
	facility_list_items,
	facility_locations,
	approved_claim,
	facility_addresses,
	claim_info,
	custom_field_info,
	extended_fields,
	created_from_info,
	activity_reports_info,
	item_sectors,
	claim_sectors,
	custom_text_search,
	updated_at) =
(
	SELECT
COALESCE((SELECT count(contributor) FROM index_contributors_count(af.id)), 0), -- contributors_count
COALESCE((SELECT array_agg(contrib_type) FROM index_contrib_types(af.id)), '{}'), -- contrib_types
COALESCE((SELECT array_agg(contributor) FROM index_contributors(af.id)), '{}'), -- contributors
COALESCE((SELECT array_agg(DISTINCT(custom_text)) FROM custom_text(af.id)), '{}'), -- custom_text
COALESCE((SELECT array_agg(facility_name) FROM index_facility_names(af.id)), '{}'), -- facility_names
COALESCE((SELECT array_agg(facility_list_item) FROM index_facility_list_items(af.id, af.location)), '{}'), -- facility_list_items
COALESCE((SELECT array_agg(facility_location) FROM index_facility_locations(af.id)), '{}'), -- facility_locations
COALESCE((SELECT approved_claim FROM index_approved_claim(af.id))), -- approved_claim
COALESCE((SELECT array_agg(facility_address) FROM index_facility_addresses(af.id)), '{}'), -- facility_addresses
COALESCE((SELECT claim_info FROM index_claim_info(af.id))), -- claim_info
COALESCE((SELECT ARRAY_AGG(custom_field_info) FROM index_custom_field_info(af.id)), '{}'), -- custom_field_info
COALESCE((SELECT array_agg(extended_field) FROM index_extended_fields(af.id)), '{}'), -- extended_fields
COALESCE((SELECT info FROM index_created_from_info(af.created_from_id)), '{}'), --created_from_info
COALESCE((SELECT array_agg(activity_report_info) FROM index_activity_reports_info(af.id, af.name)), '{}'), --activity_reports_info
COALESCE((SELECT array_agg(item_sectors) FROM index_item_sectors(af.id)), '{}'), -- item_sectors
COALESCE((SELECT array_agg(claim_sector) FROM index_claim_sectors(af.id)), '{}'), -- claim_sectors
COALESCE((SELECT string_agg(DISTINCT(custom_text),' ') FROM custom_text(af.id)), ''), -- custom_text_search
now() -- updated_at
FROM api_facility af
WHERE
af.id = afin.id)
WHERE afin.id = ANY(facility_ids);
END IF;
END;

$body$;

CREATE OR REPLACE
FUNCTION handle_contributor_post_update_insert_indexing_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $body$
BEGIN
	CALL perform_contributor_indexing(NEW.id);
	RETURN NEW;
END;

$body$;

CREATE OR REPLACE
FUNCTION handle_contributor_post_delete_indexing_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $body$
BEGIN
	CALL perform_contributor_indexing(OLD.id);
	RETURN OLD;
END;

$body$;

CREATE TRIGGER contributor_post_insert_update_indexing_trigger
    AFTER
INSERT
	OR
UPDATE
	ON
	api_contributor
	FOR EACH ROW
    EXECUTE FUNCTION handle_contributor_post_update_insert_indexing_trigger();

CREATE TRIGGER contributor_post_delete_indexing_trigger
    AFTER
DELETE
	ON
	api_contributor
	FOR EACH ROW
    EXECUTE FUNCTION handle_contributor_post_delete_indexing_trigger();

/*Triggers and trigger-related functionality for the api_extendedfield table.
The columns of the api_facilityindex table that will be updated
are chosen based on the rule that data generated for them can be
dependent on the api_extendedfield table.*/
CREATE OR REPLACE
PROCEDURE perform_extended_field_indexing(facility_identifier TEXT)
LANGUAGE plpgsql
AS $body$

BEGIN
IF facility_identifier IS NOT NUll THEN
UPDATE
	api_facilityindex afin
SET
	(
	number_of_workers,
	facility_type,
	processing_type,
	product_type,
	parent_company_name,
	native_language_name,
	parent_company_id,
	extended_fields,
	updated_at) =
(
	SELECT
COALESCE((SELECT array_agg(DISTINCT(number)) FROM index_number_of_workers(af.id)), '{}'), -- number_of_workers
COALESCE((SELECT array_agg(DISTINCT(facility_type)) FROM index_facility_type(af.id)), '{}'), -- facility_type
COALESCE((SELECT array_agg(DISTINCT(processing_type)) FROM index_processing_type(af.id)), '{}'), -- processing_type
COALESCE((SELECT array_agg(DISTINCT(product_type)) FROM index_product_type(af.id)), '{}'), -- product_type
COALESCE((SELECT array_agg(DISTINCT (parent_company_name)) FROM index_parent_company_name(af.id)), '{}'), -- parent_company_name
COALESCE((SELECT array_agg(DISTINCT (native_language_name)) FROM index_native_language_name(af.id)), '{}'), -- native_language_name
COALESCE((SELECT array_agg(DISTINCT (parent_company_id)) FROM index_parent_company_id(af.id)), '{}'), -- parent_company_id
COALESCE((SELECT array_agg(extended_field) FROM index_extended_fields(af.id)), '{}'), -- extended_fields
now() -- updated_at
FROM api_facility af
WHERE
af.id = afin.id)
WHERE
afin.id = facility_identifier;
END IF;
END;

$body$;

CREATE OR REPLACE
FUNCTION handle_extended_field_post_update_insert_indexing_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $body$
BEGIN
	CALL perform_extended_field_indexing(NEW.facility_id);
	RETURN NEW;
END;

$body$;

CREATE OR REPLACE
FUNCTION handle_extended_field_post_delete_indexing_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $body$
BEGIN
	CALL perform_extended_field_indexing(OLD.facility_id);
	RETURN OLD;
END;

$body$;

CREATE TRIGGER extended_field_post_update_insert_indexing_trigger
    AFTER
UPDATE
	OR
INSERT
	ON
	api_extendedfield
	FOR EACH ROW
    EXECUTE FUNCTION handle_extended_field_post_update_insert_indexing_trigger();

CREATE TRIGGER extended_field_post_delete_indexing_trigger
    AFTER
DELETE
	ON
	api_extendedfield
	FOR EACH ROW
    EXECUTE FUNCTION handle_extended_field_post_delete_indexing_trigger();

/*Triggers and trigger-related functionality for the api_facility table.
The columns of the api_facilityindex table that will be updated
are chosen based on the rule that data generated for them can be
dependent on the api_facility table.*/
CREATE OR REPLACE
FUNCTION handle_facility_post_update_insert_indexing_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $body$
BEGIN
	CALL index_facilities_by(ARRAY[NEW.id]);
	RETURN NEW;
END;

$body$;

CREATE OR REPLACE
FUNCTION handle_facility_post_delete_indexing_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $body$
BEGIN
	CALL index_facilities_by(ARRAY[OLD.id]);
	RETURN OLD;
END;

$body$;

CREATE TRIGGER facility_post_update_insert_indexing_trigger
    AFTER
UPDATE
	OR
INSERT
	ON
	api_facility
	FOR EACH ROW
    EXECUTE FUNCTION handle_facility_post_update_insert_indexing_trigger();

CREATE TRIGGER facility_post_delete_indexing_trigger
    AFTER
DELETE
	ON
	api_facility
	FOR EACH ROW
    EXECUTE FUNCTION handle_facility_post_delete_indexing_trigger();

/*Triggers and trigger-related functionality for the api_facilityclaim table.
The columns of the api_facilityindex table that will be updated
are chosen based on the rule that data generated for them can be
dependent on the api_facilityclaim table.*/
CREATE OR REPLACE
PROCEDURE perform_facility_claim_indexing(facility_identifier TEXT)
LANGUAGE plpgsql
AS $body$

BEGIN
UPDATE
	api_facilityindex afin
SET
	(
	approved_claim_ids,
	sector,
	approved_claim,
	claim_info,
	extended_fields,
	claim_sectors,
	updated_at) =
(
	SELECT
COALESCE((SELECT array_agg(approved_claim_id) FROM index_approved_claim_ids(af.id)),'{}'), -- approved_claim_ids
COALESCE((SELECT array_agg(DISTINCT(sector)) FROM index_sector(af.id)), '{}'), -- sector
COALESCE((SELECT approved_claim FROM index_approved_claim(af.id))), -- approved_claim
COALESCE((SELECT claim_info FROM index_claim_info(af.id))), -- claim_info
COALESCE((SELECT array_agg(extended_field) FROM index_extended_fields(af.id)), '{}'), -- extended_fields
COALESCE((SELECT array_agg(claim_sector) FROM index_claim_sectors(af.id)), '{}'), -- claim_sectors
now() -- updated_at
FROM api_facility af
WHERE
af.id = afin.id)
WHERE
afin.id = facility_identifier;
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

CREATE OR REPLACE
FUNCTION handle_facility_claim_post_delete_indexing_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $body$
BEGIN
	CALL perform_facility_claim_indexing(OLD.facility_id);
	RETURN OLD;
END;

$body$;

CREATE TRIGGER facility_claim_post_update_insert_indexing_trigger
    AFTER
UPDATE
	OR
INSERT
	ON
	api_facilityclaim
	FOR EACH ROW
    EXECUTE FUNCTION handle_facility_claim_post_update_insert_indexing_trigger();

CREATE TRIGGER facility_claim_post_delete_indexing_trigger
    AFTER
DELETE
	ON
	api_facilityclaim
	FOR EACH ROW
    EXECUTE FUNCTION handle_facility_claim_post_delete_indexing_trigger();

/*Triggers and trigger-related functionality for the api_facilitylistitem table.
The columns of the api_facilityindex table that will be updated
are chosen based on the rule that data generated for them can be
dependent on the api_facilitylistitem table.*/
CREATE OR REPLACE
PROCEDURE perform_facility_list_item_indexing(facility_indentfier TEXT,
fli_status TEXT)
LANGUAGE plpgsql
AS $body$

BEGIN
IF facility_indentfier IS NOT NULL
AND fli_status IN ('MATCHED', 'CONFIRMED_MATCH') THEN
UPDATE
	api_facilityindex afin
SET
	(
	contributors_count,
	contributors_id,
	contrib_types,
	contributors,
	sector,
	lists,
	custom_text,
	facility_names,
	facility_list_items,
	facility_addresses,
	custom_field_info,
	extended_fields,
	created_from_info,
	item_sectors,
	custom_text_search,
	updated_at) =
(
	SELECT
COALESCE((SELECT count(contributor) FROM index_contributors_count(af.id)), 0), -- contributors_count
COALESCE((SELECT array_agg(DISTINCT(contributor_id)) FROM index_contributors_id(af.id)), '{}'), -- contributors_id
COALESCE((SELECT array_agg(contrib_type) FROM index_contrib_types(af.id)), '{}'), -- contrib_types
COALESCE((SELECT array_agg(contributor) FROM index_contributors(af.id)), '{}'), -- contributors
COALESCE((SELECT array_agg(DISTINCT(sector)) FROM index_sector(af.id)), '{}'), -- sector
COALESCE((SELECT array_agg(DISTINCT(list)) FROM index_lists(af.id)), '{}'), -- lists
COALESCE((SELECT array_agg(DISTINCT(custom_text)) FROM custom_text(af.id)), '{}'), -- custom_text
COALESCE((SELECT array_agg(facility_name) FROM index_facility_names(af.id)), '{}'), -- facility_names
COALESCE((SELECT array_agg(facility_list_item) FROM index_facility_list_items(af.id, af.location)), '{}'), -- facility_list_items
COALESCE((SELECT array_agg(facility_address) FROM index_facility_addresses(af.id)), '{}'), -- facility_addresses
COALESCE((SELECT ARRAY_AGG(custom_field_info) FROM index_custom_field_info(af.id)), '{}'), -- custom_field_info
COALESCE((SELECT array_agg(extended_field) FROM index_extended_fields(af.id)), '{}'), -- extended_fields
COALESCE((SELECT info FROM index_created_from_info(af.created_from_id)), '{}'), --created_from_info
COALESCE((SELECT array_agg(item_sectors) FROM index_item_sectors(af.id)), '{}'), -- item_sectors
COALESCE((SELECT string_agg(DISTINCT(custom_text),' ') FROM custom_text(af.id)), ''), -- custom_text_search
now() -- updated_at
FROM api_facility af
WHERE
af.id = afin.id)
WHERE afin.id = facility_indentfier;
END IF;
END;

$body$;

CREATE OR REPLACE
FUNCTION handle_facility_list_item_post_update_insert_indexing_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $body$
BEGIN
	CALL perform_facility_list_item_indexing(NEW.facility_id,
NEW.status);

RETURN NEW;
END;

$body$;

CREATE OR REPLACE
FUNCTION handle_facility_list_item_post_delete_indexing_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $body$
BEGIN
	CALL perform_facility_list_item_indexing(OLD.facility_id,
OLD.status);

RETURN OLD;
END;

$body$;

/*Change the name of the existing update_fli trigger on
api_facilitylistitem to ensure it is called before
update_fli_2 trigger. This adjustment is necessary because
update_fli_2 relies on the updated data generated by
update_fli. In Postgres, when multiple triggers of the
same type are defined for the same event, they are fired in
alphabetical order based on their names. This is why '1'
and '2' are used as markers to ensure the correct firing
sequence.*/
ALTER TRIGGER update_fli ON
api_facilitylistitem RENAME TO update_fli_1;

CREATE TRIGGER update_fli_2
    AFTER
UPDATE
	OR
INSERT
	ON
	api_facilitylistitem
	FOR EACH ROW
    EXECUTE FUNCTION handle_facility_list_item_post_update_insert_indexing_trigger();

CREATE TRIGGER facility_list_item_post_delete_indexing_trigger
    AFTER
DELETE
	ON
	api_facilitylistitem
	FOR EACH ROW
    EXECUTE FUNCTION handle_facility_list_item_post_delete_indexing_trigger();

/*Triggers and trigger-related functionality for the api_facilitymatch table.
The columns of the api_facilityindex table that will be updated
are chosen based on the rule that data generated for them can be
dependent on the api_facilitymatch table.*/
CREATE OR REPLACE
PROCEDURE perform_facility_match_indexing(facility_identifier TEXT)
LANGUAGE plpgsql
AS $body$

BEGIN
UPDATE
	api_facilityindex afin
SET
	(
	contributors_count,
	contributors_id,
	contrib_types,
	contributors,
	lists,
	custom_text,
	facility_names,
	facility_list_items,
	facility_addresses,
	custom_field_info,
	extended_fields,
	item_sectors,
	custom_text_search,
	updated_at) =
(
	SELECT
COALESCE((SELECT count(contributor) FROM index_contributors_count(af.id)), 0), -- contributors_count
COALESCE((SELECT array_agg(DISTINCT(contributor_id)) FROM index_contributors_id(af.id)), '{}'), -- contributors_id
COALESCE((SELECT array_agg(contrib_type) FROM index_contrib_types(af.id)), '{}'), -- contrib_types
COALESCE((SELECT array_agg(contributor) FROM index_contributors(af.id)), '{}'), -- contributors
COALESCE((SELECT array_agg(DISTINCT(list)) FROM index_lists(af.id)), '{}'), -- lists
COALESCE((SELECT array_agg(DISTINCT(custom_text)) FROM custom_text(af.id)), '{}'), -- custom_text
COALESCE((SELECT array_agg(facility_name) FROM index_facility_names(af.id)), '{}'), -- facility_names
COALESCE((SELECT array_agg(facility_list_item) FROM index_facility_list_items(af.id, af.location)), '{}'), -- facility_list_items
COALESCE((SELECT array_agg(facility_address) FROM index_facility_addresses(af.id)), '{}'), -- facility_addresses
COALESCE((SELECT ARRAY_AGG(custom_field_info) FROM index_custom_field_info(af.id)), '{}'), -- custom_field_info
COALESCE((SELECT array_agg(extended_field) FROM index_extended_fields(af.id)), '{}'), -- extended_fields
COALESCE((SELECT array_agg(item_sectors) FROM index_item_sectors(af.id)), '{}'), -- item_sectors
COALESCE((SELECT string_agg(DISTINCT(custom_text),' ') FROM custom_text(af.id)), ''), -- custom_text_search
now() -- updated_at
FROM api_facility af
WHERE
af.id = afin.id)
WHERE afin.id = facility_identifier;
END;

$body$;

CREATE OR REPLACE
FUNCTION handle_facility_match_post_update_insert_indexing_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $body$
BEGIN
	CALL perform_facility_match_indexing(NEW.facility_id);
	RETURN NEW;
END;

$body$;

CREATE OR REPLACE
FUNCTION handle_facility_match_post_delete_indexing_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $body$
BEGIN
	CALL perform_facility_match_indexing(OLD.facility_id);
	RETURN OLD;
END;

$body$;

CREATE TRIGGER facility_match_post_update_insert_indexing_trigger
    AFTER
UPDATE
	OR
INSERT
	ON
	api_facilitymatch
	FOR EACH ROW
    EXECUTE FUNCTION handle_facility_match_post_update_insert_indexing_trigger();

CREATE TRIGGER facility_match_post_delete_indexing_trigger
    AFTER
DELETE
	ON
	api_facilitymatch
	FOR EACH ROW
    EXECUTE FUNCTION handle_facility_match_post_delete_indexing_trigger();

/*Triggers and trigger-related functionality for the api_source table.
The columns of the api_facilityindex table that will be updated
are chosen based on the rule that data generated for them can be
dependent on the api_source table.*/
CREATE OR REPLACE
PROCEDURE perform_source_indexing(source_identifier integer)
LANGUAGE plpgsql
AS $body$
DECLARE facility_ids TEXT[];

BEGIN
SELECT
	COALESCE(array_agg(af.id),
	'{}')
INTO
	facility_ids
FROM
	api_facility af
JOIN api_facilitylistitem afli ON
	af.id = afli.facility_id
WHERE
	afli.source_id = source_identifier;

IF array_length(facility_ids,
1) > 0 THEN
UPDATE
	api_facilityindex afin
SET
	(
	contributors_count,
	contributors_id,
	contrib_types,
	contributors,
	lists,
	custom_text,
	facility_names,
	facility_list_items,
	facility_addresses,
	custom_field_info,
	extended_fields,
	created_from_info,
	item_sectors,
	custom_text_search,
	updated_at) =
(
	SELECT
COALESCE((SELECT count(contributor) FROM index_contributors_count(af.id)), 0), -- contributors_count
COALESCE((SELECT array_agg(DISTINCT(contributor_id)) FROM index_contributors_id(af.id)), '{}'), -- contributors_id
COALESCE((SELECT array_agg(contrib_type) FROM index_contrib_types(af.id)), '{}'), -- contrib_types
COALESCE((SELECT array_agg(contributor) FROM index_contributors(af.id)), '{}'), -- contributors
COALESCE((SELECT array_agg(DISTINCT(list)) FROM index_lists(af.id)), '{}'), -- lists
COALESCE((SELECT array_agg(DISTINCT(custom_text)) FROM custom_text(af.id)), '{}'), -- custom_text
COALESCE((SELECT array_agg(facility_name) FROM index_facility_names(af.id)), '{}'), -- facility_names
COALESCE((SELECT array_agg(facility_list_item) FROM index_facility_list_items(af.id, af.location)), '{}'), -- facility_list_items
COALESCE((SELECT array_agg(facility_address) FROM index_facility_addresses(af.id)), '{}'), -- facility_addresses
COALESCE((SELECT ARRAY_AGG(custom_field_info) FROM index_custom_field_info(af.id)), '{}'), -- custom_field_info
COALESCE((SELECT array_agg(extended_field) FROM index_extended_fields(af.id)), '{}'), -- extended_fields
COALESCE((SELECT info FROM index_created_from_info(af.created_from_id)), '{}'), --created_from_info
COALESCE((SELECT array_agg(item_sectors) FROM index_item_sectors(af.id)), '{}'), -- item_sectors
COALESCE((SELECT string_agg(DISTINCT(custom_text),' ') FROM custom_text(af.id)), ''), -- custom_text_search
now() -- updated_at
FROM api_facility af
WHERE
af.id = afin.id)
WHERE afin.id = ANY(facility_ids);
END IF;
END;

$body$;

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
FUNCTION handle_source_post_delete_indexing_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $body$
BEGIN
	CALL perform_source_indexing(OLD.id);
	RETURN OLD;
END;

$body$;

CREATE TRIGGER source_post_update_insert_indexing_trigger
    AFTER
UPDATE
	OR
INSERT
	ON
	api_source
	FOR EACH ROW
    EXECUTE FUNCTION handle_source_post_update_insert_indexing_trigger();

CREATE TRIGGER source_post_delete_indexing_trigger
    AFTER
DELETE
	ON
	api_source
	FOR EACH ROW
    EXECUTE FUNCTION handle_source_post_delete_indexing_trigger();

--Trigger and trigger-related functionality for the api_facilitylist table.
CREATE OR REPLACE
FUNCTION handle_manual_list_reject_revert_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $body$
BEGIN
	    IF NEW.status = 'REJECTED' THEN
        UPDATE
	api_source ase
SET
	is_active = FALSE
WHERE
	ase.facility_list_id = NEW.id;
ELSE
        UPDATE
	api_source ase
SET
	is_active = TRUE
WHERE
	ase.facility_list_id = NEW.id;
END IF;

RETURN NEW;
END;

$body$;

/*Establish a post UDPATE trigger for the api_facilitylist table to
update the is_active field of the associated api_source entry when
the list status is manually modified by a data moderator.*/
CREATE TRIGGER manual_list_reject_revert_trigger
    AFTER
UPDATE
	ON
	api_facilitylist
	FOR EACH ROW
    EXECUTE FUNCTION handle_manual_list_reject_revert_trigger();
