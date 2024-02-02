CREATE OR REPLACE PROCEDURE index_facilities()
LANGUAGE SQL 
AS $Body$

DELETE 
FROM api_facilityindex afi WHERE 
 	afi.id NOT IN (
        SELECT id
        FROM api_facility af
    );

INSERT INTO api_facilityindex
SELECT 
af.id, -- id
af.name, -- name
af.address, -- address
af.country_code, -- country_code
af.location, -- location
coalesce((select count(ac.id) from api_contributor ac 
	where (ac.id in 
		(select as1.contributor_id from api_source as1 where as1.id in 
			(select fli.source_id FROM api_facilitylistitem fli
			left join api_facilitymatch afm on afm.facility_list_item_id = fli.id
			where fli.facility_id = af.id
			and afm.is_active
			and (afm.status = 'AUTOMATIC' or afm.status = 'CONFIRMED' or afm.status = 'MERGED'))
			and as1.is_active 
			and as1.is_public))),
0), -- contributors_count
coalesce(
	(
		select array_agg(distinct(as2.contributor_id)) from api_facilitymatch afm
		left join api_facilitylistitem af2 on af2.id = afm.facility_list_item_id
		left join api_source as2 on as2.id = af2.source_id and as2.is_active and as2.is_public
		where afm.facility_id = af.id and afm.is_active and afm.status in ('AUTOMATIC', 'CONFIRMED', 'MERGED') and as2.contributor_id is not null
	),
	'{}'), -- contributors_id
coalesce((select array_agg(afc.id) from api_facilityclaim afc where afc.facility_id = af.id and afc.status = 'APPROVED'),'{}'), -- approved_claim_ids
af.ppe_product_types, -- ppe_product_types
af.ppe_contact_email, -- ppe_contact_email
af.ppe_contact_phone, -- ppe_contact_phone
af.ppe_website, -- ppe_website
af.is_closed, -- is_closed
af.new_os_id, -- new_os_id
af.has_inexact_coordinates, -- has_inexact_coordinates
coalesce((select array_agg(ac.contrib_type) from api_contributor ac 
	where (ac.id in 
		(select as1.contributor_id from api_source as1 where as1.id in 
			(select afli.source_id FROM api_facilitylistitem afli where afli.id in 
				(select afm.facility_list_item_id from api_facilitymatch afm where afm.is_active) and afli.facility_id = af.id) and as1.is_active and as1.is_public))),
'{}'), -- contrib_types
coalesce((select array_agg(json_build_object(
	'id', ac.id,
	'admin_id', ac.admin_id,
	'fl_id', afl.id, 
	'name', case 
		when afl.id is not null then concat(ac."name", ' (', afl."name" , ')')
		else ac."name"
	end,
	'contributor_name', ac."name",
	'contrib_type', ac.contrib_type,
	'should_display_associations', afm.is_active and as1.is_active and as1.is_public,
	'is_verified', ac.is_verified,
	'list_name', afl."name")) from api_facilitymatch afm
	left join api_facilitylistitem afli on afli.id = afm.facility_list_item_id
	left join api_source as1 on as1.id = afli.source_id
	left join api_contributor ac on ac.id = as1.contributor_id 
	left join api_facilitylist afl on afl.id = as1.facility_list_id
	where afm.facility_id = af.id and (afm.status = 'AUTOMATIC' or afm.status = 'CONFIRMED' or afm.status = 'MERGED')), '{}'), -- contributors
concat(af.ppe_product_types,af.ppe_contact_phone,af.ppe_contact_email,af.ppe_website), -- ppe
coalesce((select array_agg(distinct(ttt)) from (
select unnest(afli.sector) as ttt
from api_facilitylistitem afli
where afli.facility_id = af.id and (afli.status = 'MATCHED' or afli.status = 'CONFIRMED_MATCH')
union all
select unnest(afc.sector) as ttt
from api_facilityclaim afc 
where afc.facility_id = af.id and afc.status = 'APPROVED'
) as x), '{}'), -- sector
coalesce(
	(
		select array_agg(distinct(as2.facility_list_id)) from api_facilitymatch afm
		left join api_facilitylistitem af2 on af2.id = afm.facility_list_item_id
		left join api_source as2 on as2.id = af2.source_id and as2.is_active and as2.is_public
		where afm.facility_id = af.id and afm.is_active and afm.status in ('AUTOMATIC', 'CONFIRMED', 'MERGED') and as2.facility_list_id is not null
	),
	'{}'), -- lists
	'{}', -- custom_text
coalesce((select array_agg(distinct(sss)) from (select unnest(format_numbers_of_workers((aef.value->'max')::int, (aef.value->'min')::int)) as sss from api_extendedfield aef
	where aef.facility_id = af.id and aef.field_name = 'number_of_workers') as x), '{}'), -- number_of_workers
coalesce((select array_agg(distinct(raw1)) from ( 
	select (raw->>2) as raw1 from ( 
		select jsonb_array_elements(aef.value -> 'matched_values') as raw from api_extendedfield aef
		where aef.facility_id = af.id and aef.field_name = 'facility_type' and aef.value -> 'matched_values' is not null
	) as value where raw->>2 is not null
) as value1), '{}'), -- facility_type
coalesce((select array_agg(distinct(raw1)) from ( 
	select (raw->>-1) as raw1 from ( 
		select jsonb_array_elements(aef.value -> 'matched_values') as raw from api_extendedfield aef
		where aef.facility_id = af.id and aef.field_name = 'processing_type' and aef.value -> 'matched_values' is not null
	) as value where raw ? 'PROCESSING_TYPE'
) as value1), '{}'), -- processing_type
coalesce((select array_agg(distinct(lower(replace(raw,'"','')))) from ( 
	select jsonb_array_elements(aef.value -> 'raw_values')::varchar as raw from api_extendedfield aef
	where aef.facility_id = af.id and aef.field_name = 'product_type' and aef.value -> 'raw_values' is not null
) as value), '{}'), -- product_type
coalesce((select array_agg(distinct (replace(coalesce(aef.value -> 'contributor_name', aef.value -> 'name')::varchar,'"',''))) from api_extendedfield aef
where aef.facility_id = af.id and aef.field_name = 'parent_company' and (aef.value -> 'contributor_name' is not null or aef.value -> 'name' is not null)), '{}'), -- parent_company_name
coalesce((select array_agg(distinct (trim(both '"' from aef.value::TEXT))) from api_extendedfield aef
where aef.facility_id = af.id and aef.field_name = 'native_language_name'), '{}'), -- native_language_name
coalesce((select array_agg(distinct (aef.value -> 'contributor_id')::INTEGER) from api_extendedfield aef
where aef.facility_id = af.id and aef.field_name = 'parent_company' and aef.value -> 'contributor_id' is not null), '{}'), -- parent_company_id
coalesce((select array_agg(json_build_object(
	'name', af2.name,
	'updated_at', af2.updated_at,
	'created_at', af2.created_at,
	'contributor', json_build_object(
		'id', ac.id,
		'name', ac.name,
		'contrib_type', ac.contrib_type,
		'admin_id', ac.admin_id
	)
)) from api_facilitymatch fm_item
left join api_facilitylistitem af2 on af2.id = fm_item.facility_list_item_id 
left join api_source as2 on as2.id = af2.source_id
left join api_contributor ac on ac.id = as2.contributor_id
where (fm_item.status = 'AUTOMATIC' or fm_item.status = 'CONFIRMED' or fm_item.status = 'MERGED')
and fm_item.facility_id = af.id
and fm_item.is_active
and as2.is_active
and as2.is_public), '{}'), -- facility_names
coalesce((select array_agg(json_build_object(
'location_lat', ST_Y(afli.geocoded_point),
'location_lng', ST_X(afli.geocoded_point),
'contributor', json_build_object(
	'admin_id', ac.admin_id,
	'name', ac.name,
	'contrib_type', ac.contrib_type
)
)) from api_facilitymatch afm
left join api_facilitylistitem afli on afli.id = afm.facility_list_item_id
left join api_source as1 on as1.id = afli.source_id
left join api_contributor ac on ac.id = as1.contributor_id
where afm.facility_id = af.id
and (afm.status = 'CONFIRMED' or afm.status = 'AUTOMATIC' or afm.status = 'MERGED')
and afm.is_active
and as1.is_active
and as1.is_public
and afli.geocoded_point is not null
and (ST_Y(afli.geocoded_point) != ST_Y(af.location) or ST_X(afli.geocoded_point) != ST_X(af.location))), '{}'), -- facility_list_items
coalesce((select array_agg(json_build_object(
'location_lat', ST_Y(aflo.location),
'location_lng', ST_X(aflo.location),
'location_notes', aflo.notes,
'contributor', json_build_object(
	'admin_id', ac.admin_id,
	'name', ac.name,
	'contrib_type', ac.contrib_type
)
)) from api_facilitylocation aflo
left join api_contributor ac on ac.id = aflo.contributor_id
where aflo.facility_id = af.id), '{}'), -- facility_locations
coalesce((select json_build_object(
	'id', afc.id, 
	'contact_person', afc.contact_person, 
	'email', afc.email,
	'phone_number', afc.phone_number,
	'company_name', afc.company_name,
	'website', afc.website,
	'facility_description', afc.facility_description,
	'verification_method', afc.verification_method,
	'preferred_contact_method', afc.preferred_contact_method,
	'status', afc.status,
	'created_at', afc.created_at,
	'updated_at', afc.updated_at,
	'contributor_id', afc.contributor_id,
	'contributor', json_build_object(
		'admin_id', ac.admin_id,
		'name', ac.name,
		'contrib_type', ac.contrib_type
	),
	'facility_id', afc.facility_id,
	'status_change_date', afc.status_change_date,
	'status_change_by_id', afc.status_change_by_id,
	'status_change_reason', afc.status_change_reason,
	'facility_address', afc.facility_address,
	'facility_average_lead_time', afc.facility_average_lead_time,
	'facility_minimum_order_quantity', afc.facility_minimum_order_quantity,
	'facility_phone_number', afc.facility_phone_number,
	'facility_phone_number_publicly_visible', afc.facility_phone_number_publicly_visible,
	'facility_website', afc.facility_website,
	'office_address', afc.office_address,
	'office_country_code', afc.office_country_code,
	'office_info_publicly_visible', afc.office_info_publicly_visible,
	'office_official_name', afc.office_official_name,
	'office_phone_number', afc.office_phone_number,
	'point_of_contact_email', afc.point_of_contact_email,
	'point_of_contact_person_name', afc.point_of_contact_person_name,
	'point_of_contact_publicly_visible', afc.point_of_contact_publicly_visible,
	'parent_company_id', afc.parent_company_id,
	'facility_female_workers_percentage', afc.facility_female_workers_percentage,
	'facility_name_english', afc.facility_name_english,
	'facility_name_native_language', afc.facility_name_native_language,
	'facility_type', afc.facility_type,
	'facility_website_publicly_visible', afc.facility_website_publicly_visible,
	'facility_workers_count', afc.facility_workers_count,
	'job_title', afc.job_title,
	'linkedin_profile', afc.linkedin_profile,
	'other_facility_type', afc.other_facility_type,
	'facility_affiliations', afc.facility_affiliations,
	'facility_certifications', afc.facility_certifications,
	'facility_product_types', afc.facility_product_types,
	'facility_production_types', afc.facility_production_types,
	'sector', afc.sector,
	'parent_company_name', afc.parent_company_name,
	'facility_location', afc.facility_location,
	'facility_location_info', json_build_object(
		'lat', ST_Y(afc.facility_location),
		'lng', ST_X(afc.facility_location)
	)
	) from api_facilityclaim afc
left join api_contributor ac on ac.id =	afc.contributor_id
where afc.facility_id = af.id
and afc.status = 'APPROVED'
order by afc.status_change_date desc
limit 1)), -- approved_claim
coalesce((select array_agg(json_build_object(
	'address', af2.address,
	'updated_at', af2.updated_at,
	'created_at', af2.created_at,
	'contributor', json_build_object(
		'id', ac.id,
		'name', ac.name,
		'contrib_type', ac.contrib_type,
		'admin_id', ac.admin_id
	)
)) from api_facilitymatch fm_item
left join api_facilitylistitem af2 on af2.id = fm_item.facility_list_item_id 
left join api_source as2 on as2.id = af2.source_id
left join api_contributor ac on ac.id = as2.contributor_id
where (fm_item.status = 'AUTOMATIC' or fm_item.status = 'CONFIRMED' or fm_item.status = 'MERGED')
and fm_item.facility_id = af.id
and fm_item.is_active
and as2.is_active
and as2.is_public), '{}'), -- facility_addresses
coalesce((select json_build_object(
	'id', afc.id,
	'facility', json_build_object(
		'description', afc.facility_description,
		'name_english', afc.facility_name_english,
		'name_native_language', afc.facility_name_native_language,
		'address', afc.facility_address,
		'website', case
			when afc.facility_website_publicly_visible then afc.facility_website
			else null
		end,
		'parent_company', case 
			when afc.parent_company_id is not null then json_build_object(
				'id', afc.parent_company_id,
				'name', (select ac.name from api_contributor ac
					where ac.id = afc.parent_company_id)
				)
			when afc.parent_company_name is not null then json_build_object(
				'id', afc.parent_company_name,
				'name', parent_company_name
				)
			else null
		end,
		'phone_number', case
			when afc.facility_phone_number_publicly_visible then afc.facility_phone_number
			else null
		end,
		'minimum_order', afc.facility_minimum_order_quantity,
		'average_lead_time', afc.facility_average_lead_time,
		'workers_count', afc.facility_workers_count,
		'female_workers_percentage', afc.facility_female_workers_percentage,
		'facility_type', afc.facility_type,
		'other_facility_type', afc.other_facility_type,
		'affiliations', afc.facility_affiliations,
		'certifications', afc.facility_certifications,
		'product_types', afc.facility_product_types,
		'production_types', afc.facility_production_types,
		'sector', afc.sector,
		'location', case
			when afc.facility_location is not null then st_asgeojson(afc.facility_location)::json
			else null
		end
		),
		'contact', case 
			when afc.point_of_contact_publicly_visible then json_build_object(
				'name', afc.point_of_contact_person_name,
				'email', afc.point_of_contact_email
				)
			else null
		end,
		'office', case 
			when afc.office_info_publicly_visible then json_build_object(
				'name', afc.office_official_name,
				'address', afc.office_address,
				'country', afc.office_country_code,
				'phone_number', afc.office_phone_number
				)
			else null
		end,
		'contributor', json_build_object(
			'id', ac.id,
			'name', ac.name,
			'contrib_type', ac.contrib_type
			)
	)
from api_facilityclaim afc
left join api_contributor ac on afc.contributor_id = ac.id
where status = 'APPROVED'
and facility_id = af.id limit 1
)), -- claim_info
coalesce((SELECT ARRAY_AGG(custom_field_info) FROM index_custom_field_info(af.id)), '{}'), -- custom_field_info
coalesce((select array_agg(json_build_object(
	'id', 	base_query.id,
	'is_verified', base_query.is_verified,
	'value', base_query.value,
	'created_at', base_query.created_at,
	'updated_at', base_query.updated_at,
	'facility_list_item_id', base_query.facility_list_item_id,
	'contributor', (select json_build_object(
		'id', ac.id,
		'name', ac.name,
		'contrib_type', ac.contrib_type,
		'admin_id', ac.admin_id,
		'is_verified', ac.is_verified
		)
		from api_contributor ac 
		where ac.id = base_query.contributor_id),
	'value_count', (
		select count(ae.id)
		from api_extendedfield ae
		left join api_facilitylistitem af4 on af4.id = ae.facility_list_item_id
		left join api_source as3 on as3.id = af4.source_id
		where ae.facility_id = base_query.facility_id
		and ae.field_name = base_query.field_name
		and ae.value = base_query.value
		and (
			ae.facility_list_item_id is null
			or
			as3.is_active
		)
	),
	'field_name', base_query.field_name,
	'should_display_association', (case
		when base_query.facility_list_item_id is not null
		then exists(
			select 1
			from api_facilitymatch af3
			left join api_facilitylistitem af5 on af3.facility_list_item_id = af5.id
			left join api_source as4 on af5.source_id = as4.id
			where af3.facility_list_item_id = base_query.facility_list_item_id
			and af3.is_active = true
			and as4.is_active = true
			and as4.is_public = true
		)
		else true
	end)
	
))
from (
  select *,
    exists
    (select af2.status
    	from api_facilityclaim af2
    	where af2.id = ae.facility_claim_id
    		and af2.status = 'APPROVED'
    ) as has_active_claim,
    (ae.facility_list_item_id in (
      select am.facility_list_item_id
      from (
        select afm.facility_list_item_id
        from api_facilitymatch afm
        where afm.facility_id = af.id
          and afm.status in ('AUTOMATIC', 'CONFIRMED', 'MERGED')
          and afm.is_active = true
      ) as am
      where am.facility_list_item_id in (
        select afli.id
        from api_facilitylistitem afli
        where afli.facility_id = af.id
          and afli.source_id in (
            select as2.id
            from api_source as2
            where as2.is_active = true
          )
      )
    )) as is_active
  from api_extendedfield ae
  where ae.facility_id = af.id
) as base_query
where has_active_claim = true or is_active = true
), '{}'), -- extended_fields
coalesce((select json_build_object(
'should_display_associations', afm.is_active and as1.is_active and as1.is_public,
'created_at', afli.created_at,
'contributor_name', ac.name,
'contrib_type', ac.contrib_type
)
from api_facilitymatch afm
left join api_facilitylistitem afli on afli.id = af.created_from_id
left join api_source as1 on as1.id = afli.source_id
left join api_contributor ac on ac.id = as1.contributor_id
where afm.facility_list_item_id = afli.id 
limit 1
-- group by ac.name, ac.contrib_type, afli.created_at, afm.is_active, as1.is_active, as1.is_public
), '{}'), --created_from_info
coalesce((select array_agg(raw) from (select json_build_object(
'facility', afar.facility_id,
'reported_by_user', au.email,
'reported_by_contributor', ac.name,
'closure_state', afar.closure_state,
'approved_at', afar.approved_at,
'status_change_reason', afar.status_change_reason,
'status', afar.status,
'status_change_by', au1.email,
'status_change_date', afar.status_change_date,
'created_at', afar.created_at,
'updated_at', afar.updated_at,
'id', afar.id,
'reason_for_report', afar.reason_for_report,
'facility_name', af.name
) as raw
from api_facilityactivityreport afar
left join api_user au on au.id = afar.reported_by_user_id
left join api_contributor ac on ac.id = afar.reported_by_contributor_id
left join api_user au1 on au1.id = afar.status_change_by_id
where afar.facility_id = af.id and (afar.status = 'PENDING' or afar.status = 'CONFIRMED')
order by afar.created_at desc) as sqlresult), '{}'), --activity_reports_info
coalesce((
	select array_agg(item_sectors)
	from index_item_sectors(af.id)
), '{}'), -- item_sectors
coalesce((select array_agg(json_build_object(
	'sector', afc.sector,
	'created_at', afc.created_at,
	'updated_at', afc.updated_at,
	'contributor',json_build_object(
		'id', ac.id,
		'name', ac.name,
		'admin_id', ac.admin_id,
		'contrib_type', ac.contrib_type
	)
))
from api_facilityclaim afc
left join api_contributor ac on afc.contributor_id = ac.id
where afc.facility_id = af.id
and afc.status = 'APPROVED'
and afc.sector is not null), '{}'), -- claim_sectors
now(), -- created_at
now(), -- updated_at
'' -- custom_text_search
FROM api_facility af
-- LEFT JOIN api_facilitylistitem afli ON afli.facility_id = af.id
-- LEFT JOIN api_source as2 ON as2.id = afli.source_id
-- LEFT JOIN api_contributor ac ON ac.id = as2.contributor_id
-- left join api_facilitymatch afm on afm.facility_id = af.id
-- GROUP BY af.id
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
ppe=excluded.ppe,
ppe_contact_email=excluded.ppe_contact_email,
ppe_contact_phone=excluded.ppe_contact_phone,
ppe_product_types=excluded.ppe_product_types,
ppe_website=excluded.ppe_website,
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
custom_text_search=excluded.custom_text_search
$Body$;
