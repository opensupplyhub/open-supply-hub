/*
OSDEV-3428. The facility_type and processing_type columns of
api_facilityindex have depended on api_facilitymatch and api_source since
0231_index_facility_type.sql / 0231_index_processing_type.sql (OSDEV-3189)
gated them on an active match with status AUTOMATIC, CONFIRMED, or MERGED.
The per-table indexing procedures below were never updated for that new
dependency, so any event that changes matches or sources without touching
extended fields leaves both columns stale. The visible case: locations
approved via a moderation event (v1 API / SLC) computed the columns before
their FacilityMatch existed and were never recomputed, making them
invisible to the Facility Type and Processing Type search filters.

This file re-creates the three procedures with the two columns added,
following the file's own rule that a procedure recomputes every
api_facilityindex column whose data can depend on its table.
*/

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
	facility_type,
	processing_type,
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
COALESCE((SELECT array_agg(DISTINCT(facility_type)) FROM index_facility_type(af.id)), '{}'), -- facility_type
COALESCE((SELECT array_agg(DISTINCT(processing_type)) FROM index_processing_type(af.id)), '{}'), -- processing_type
now() -- updated_at
FROM api_facility af
WHERE
af.id = afin.id)
WHERE afin.id = facility_indentfier;
END IF;
END;

$body$;

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
	facility_type,
	processing_type,
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
COALESCE((SELECT array_agg(DISTINCT(facility_type)) FROM index_facility_type(af.id)), '{}'), -- facility_type
COALESCE((SELECT array_agg(DISTINCT(processing_type)) FROM index_processing_type(af.id)), '{}'), -- processing_type
now() -- updated_at
FROM api_facility af
WHERE
af.id = afin.id)
WHERE afin.id = facility_identifier;
END;

$body$;

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
	facility_type,
	processing_type,
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
COALESCE((SELECT array_agg(DISTINCT(facility_type)) FROM index_facility_type(af.id)), '{}'), -- facility_type
COALESCE((SELECT array_agg(DISTINCT(processing_type)) FROM index_processing_type(af.id)), '{}'), -- processing_type
now() -- updated_at
FROM api_facility af
WHERE
af.id = afin.id)
WHERE afin.id = ANY(facility_ids);
END IF;
END;

$body$;
