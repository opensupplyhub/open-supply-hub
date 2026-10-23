-- extended_fields is aggregated in ExtendedField id order, so owners'
-- values (e.g. embed downloads joined with "|") come out the same way
-- every time; before, the order was whatever the plan returned.
/*
OSDEV-3340. isic_4 ExtendedFields count toward the isic_* columns of
api_facilityindex only while they are visible on the location (an approved
claim, or an active match from an active source; see
isic_4_entry_elements() in 0254_index_isic_4.sql), the rule
index_facility_type / index_processing_type follow. So, as 0235 and 0236 did
for facility_type and processing_type, the procedures of the tables that
visibility depends on recompute the four ISIC columns too: list items,
matches, sources and claims. Each is re-created in full from its 0235 / 0236
definition with the ISIC columns added before updated_at.
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
	isic_section,
	isic_division,
	isic_group,
	isic_class,
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
COALESCE((SELECT array_agg(extended_field ORDER BY (extended_field->>'id')::int) FROM index_extended_fields(af.id)), '{}'), -- extended_fields
COALESCE((SELECT info FROM index_created_from_info(af.created_from_id)), '{}'), --created_from_info
COALESCE((SELECT array_agg(item_sectors) FROM index_item_sectors(af.id)), '{}'), -- item_sectors
COALESCE((SELECT string_agg(DISTINCT(custom_text),' ') FROM custom_text(af.id)), ''), -- custom_text_search
COALESCE((SELECT array_agg(DISTINCT(facility_type)) FROM index_facility_type(af.id)), '{}'), -- facility_type
COALESCE((SELECT array_agg(DISTINCT(processing_type)) FROM index_processing_type(af.id)), '{}'), -- processing_type
COALESCE((SELECT array_agg(DISTINCT(isic_section)) FROM index_isic_section(af.id)), '{}'), -- isic_section
COALESCE((SELECT array_agg(DISTINCT(isic_division)) FROM index_isic_division(af.id)), '{}'), -- isic_division
COALESCE((SELECT array_agg(DISTINCT(isic_group)) FROM index_isic_group(af.id)), '{}'), -- isic_group
COALESCE((SELECT array_agg(DISTINCT(isic_class)) FROM index_isic_class(af.id)), '{}'), -- isic_class
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
	isic_section,
	isic_division,
	isic_group,
	isic_class,
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
COALESCE((SELECT array_agg(extended_field ORDER BY (extended_field->>'id')::int) FROM index_extended_fields(af.id)), '{}'), -- extended_fields
COALESCE((SELECT array_agg(item_sectors) FROM index_item_sectors(af.id)), '{}'), -- item_sectors
COALESCE((SELECT string_agg(DISTINCT(custom_text),' ') FROM custom_text(af.id)), ''), -- custom_text_search
COALESCE((SELECT array_agg(DISTINCT(facility_type)) FROM index_facility_type(af.id)), '{}'), -- facility_type
COALESCE((SELECT array_agg(DISTINCT(processing_type)) FROM index_processing_type(af.id)), '{}'), -- processing_type
COALESCE((SELECT array_agg(DISTINCT(isic_section)) FROM index_isic_section(af.id)), '{}'), -- isic_section
COALESCE((SELECT array_agg(DISTINCT(isic_division)) FROM index_isic_division(af.id)), '{}'), -- isic_division
COALESCE((SELECT array_agg(DISTINCT(isic_group)) FROM index_isic_group(af.id)), '{}'), -- isic_group
COALESCE((SELECT array_agg(DISTINCT(isic_class)) FROM index_isic_class(af.id)), '{}'), -- isic_class
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
	isic_section,
	isic_division,
	isic_group,
	isic_class,
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
COALESCE((SELECT array_agg(extended_field ORDER BY (extended_field->>'id')::int) FROM index_extended_fields(af.id)), '{}'), -- extended_fields
COALESCE((SELECT info FROM index_created_from_info(af.created_from_id)), '{}'), --created_from_info
COALESCE((SELECT array_agg(item_sectors) FROM index_item_sectors(af.id)), '{}'), -- item_sectors
COALESCE((SELECT string_agg(DISTINCT(custom_text),' ') FROM custom_text(af.id)), ''), -- custom_text_search
COALESCE((SELECT array_agg(DISTINCT(facility_type)) FROM index_facility_type(af.id)), '{}'), -- facility_type
COALESCE((SELECT array_agg(DISTINCT(processing_type)) FROM index_processing_type(af.id)), '{}'), -- processing_type
COALESCE((SELECT array_agg(DISTINCT(isic_section)) FROM index_isic_section(af.id)), '{}'), -- isic_section
COALESCE((SELECT array_agg(DISTINCT(isic_division)) FROM index_isic_division(af.id)), '{}'), -- isic_division
COALESCE((SELECT array_agg(DISTINCT(isic_group)) FROM index_isic_group(af.id)), '{}'), -- isic_group
COALESCE((SELECT array_agg(DISTINCT(isic_class)) FROM index_isic_class(af.id)), '{}'), -- isic_class
now() -- updated_at
FROM api_facility af
WHERE
af.id = afin.id)
WHERE afin.id = ANY(facility_ids);
END IF;
END;

$body$;

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
	facility_type,
	processing_type,
	isic_section,
	isic_division,
	isic_group,
	isic_class,
	updated_at) =
(
	SELECT
COALESCE((SELECT array_agg(approved_claim_id) FROM index_approved_claim_ids(af.id)),'{}'), -- approved_claim_ids
COALESCE((SELECT array_agg(DISTINCT(sector)) FROM index_sector(af.id)), '{}'), -- sector
COALESCE((SELECT approved_claim FROM index_approved_claim(af.id))), -- approved_claim
COALESCE((SELECT claim_info FROM index_claim_info(af.id))), -- claim_info
COALESCE((SELECT array_agg(extended_field ORDER BY (extended_field->>'id')::int) FROM index_extended_fields(af.id)), '{}'), -- extended_fields
COALESCE((SELECT array_agg(claim_sector) FROM index_claim_sectors(af.id)), '{}'), -- claim_sectors
COALESCE((SELECT array_agg(DISTINCT(facility_type)) FROM index_facility_type(af.id)), '{}'), -- facility_type
COALESCE((SELECT array_agg(DISTINCT(processing_type)) FROM index_processing_type(af.id)), '{}'), -- processing_type
COALESCE((SELECT array_agg(DISTINCT(isic_section)) FROM index_isic_section(af.id)), '{}'), -- isic_section
COALESCE((SELECT array_agg(DISTINCT(isic_division)) FROM index_isic_division(af.id)), '{}'), -- isic_division
COALESCE((SELECT array_agg(DISTINCT(isic_group)) FROM index_isic_group(af.id)), '{}'), -- isic_group
COALESCE((SELECT array_agg(DISTINCT(isic_class)) FROM index_isic_class(af.id)), '{}'), -- isic_class
now() -- updated_at
FROM api_facility af
WHERE
af.id = afin.id)
WHERE
afin.id = facility_identifier;
END;

$body$;
