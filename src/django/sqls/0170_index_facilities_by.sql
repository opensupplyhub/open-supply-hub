CREATE OR REPLACE PROCEDURE index_facilities_by(ids text[])
LANGUAGE SQL 
AS $Body$

DELETE 
FROM api_facilityindex afi
WHERE 
    afi.id = ANY(ids)
    AND 
	afi.id NOT IN (
        SELECT id
        FROM api_facility af
        WHERE af.id = ANY(ids)
    );

INSERT INTO api_facilityindex
SELECT 
af.id, -- id
af.name, -- name
af.address, -- address
af.country_code, -- country_code
af.location, -- location
coalesce((select count(contributor) from index_contributors_count(af.id)), 0), -- contributors_count
coalesce((select array_agg(distinct(contributor_id)) from index_contributors_id(af.id)), '{}'), -- contributors_id
coalesce((select array_agg(approved_claim_id) from index_approved_claim_ids(af.id)),'{}'), -- approved_claim_ids
af.is_closed, -- is_closed
af.new_os_id, -- new_os_id
af.has_inexact_coordinates, -- has_inexact_coordinates
coalesce((select array_agg(contrib_type) from index_contrib_types(af.id)), '{}'), -- contrib_types
coalesce((select array_agg(contributor) from index_contributors(af.id)), '{}'), -- contributors
coalesce((select array_agg(distinct(sector)) from index_sector(af.id)), '{}'), -- sector
coalesce((select array_agg(distinct(list)) from index_lists(af.id)), '{}'), -- lists
coalesce((select array_agg(distinct(custom_text)) from custom_text(af.id)), '{}'), -- custom_text
coalesce((select array_agg(distinct(number)) from index_number_of_workers(af.id)), '{}'), -- number_of_workers
coalesce((select array_agg(distinct(facility_type)) from index_facility_type(af.id)), '{}'), -- facility_type
coalesce((select array_agg(distinct(processing_type)) from index_processing_type(af.id)), '{}'), -- processing_type
coalesce((select array_agg(distinct(product_type)) from index_product_type(af.id)), '{}'), -- product_type
coalesce((select array_agg(distinct (parent_company_name)) from index_parent_company_name(af.id)), '{}'), -- parent_company_name
coalesce((select array_agg(distinct (native_language_name)) from index_native_language_name(af.id)), '{}'), -- native_language_name
coalesce((select array_agg(distinct (parent_company_id)) from index_parent_company_id(af.id)), '{}'), -- parent_company_id
coalesce((select array_agg(facility_name) from index_facility_names(af.id)), '{}'), -- facility_names
coalesce((select array_agg(facility_list_item) from index_facility_list_items(af.id, af.location)), '{}'), -- facility_list_items
coalesce((select array_agg(facility_location) from index_facility_locations(af.id)), '{}'), -- facility_locations
coalesce((select approved_claim from index_approved_claim(af.id))), -- approved_claim
coalesce((select array_agg(facility_address) from index_facility_addresses(af.id)), '{}'), -- facility_addresses
coalesce((select claim_info from index_claim_info(af.id))), -- claim_info
coalesce((SELECT ARRAY_AGG(custom_field_info) FROM index_custom_field_info(af.id)), '{}'), -- custom_field_info
coalesce((select array_agg(extended_field) from index_extended_fields(af.id)), '{}'), -- extended_fields
coalesce((select info from index_created_from_info(af.created_from_id)), '{}'), --created_from_info
coalesce((select array_agg(activity_report_info) from index_activity_reports_info(af.id, af.name)), '{}'), --activity_reports_info
coalesce((select array_agg(item_sectors) from index_item_sectors(af.id)), '{}'), -- item_sectors
coalesce((select array_agg(claim_sector) from index_claim_sectors(af.id)), '{}'), -- claim_sectors
now(), -- created_at
now(), -- updated_at
coalesce((select string_agg(distinct(custom_text),' ') from custom_text(af.id)), ''), -- custom_text_search
af.origin_source -- origin_source
FROM api_facility af
WHERE af.id = any(ids)
ON CONFLICT (id) DO UPDATE
SET 
name=excluded.name, 
contributors_count=excluded.contributors_count, 
updated_at=now(), 
address=excluded.address, 
approved_claim_ids=excluded.approved_claim_ids, 
contrib_types=excluded.contrib_types,
contributors=excluded.contributors,
country_code=excluded.country_code,
custom_text=excluded.custom_text,
facility_type=excluded.facility_type,
is_closed=excluded.is_closed,
lists=excluded.lists,
location=excluded.location,
native_language_name=excluded.native_language_name,
number_of_workers=excluded.number_of_workers,
parent_company_id=excluded.parent_company_id,
parent_company_name=excluded.parent_company_name,
processing_type=excluded.processing_type,
product_type=excluded.product_type,
sector=excluded.sector,
facility_list_items=excluded.facility_list_items,
facility_locations=excluded.facility_locations,
new_os_id=excluded.new_os_id,
facility_names=excluded.facility_names,
approved_claim=excluded.approved_claim,
facility_addresses=excluded.facility_addresses,
contributors_id=excluded.contributors_id,
claim_info=excluded.claim_info,
custom_field_info=excluded.custom_field_info,
has_inexact_coordinates=excluded.has_inexact_coordinates,
extended_fields=excluded.extended_fields,
created_from_info=excluded.created_from_info,
activity_reports_info=excluded.activity_reports_info,
item_sectors=excluded.item_sectors,
claim_sectors=excluded.claim_sectors,
custom_text_search=excluded.custom_text_search,
origin_source = excluded.origin_source
$Body$;
