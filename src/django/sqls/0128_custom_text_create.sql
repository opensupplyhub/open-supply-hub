create or replace function custom_text(fl_id text) returns TABLE (custom_text text)
LANGUAGE plpgsql
AS $$
begin
   RETURN QUERY
   	select concat(ac.id,'|', trim(lower(value->>'value'))) as custom_text from api_facilitylistitemfield flif
	left join api_facilitylistitem fli on fli.id = flif.facility_list_item_id
	left join api_facilitymatch af on af.facility_list_item_id=flif.facility_list_item_id and af.is_active=true
	left join api_source as2 on as2.id  = fli.source_id 
	left join api_contributor ac  on ac.id = as2.contributor_id
	left join api_embedconfig ae on ac.embed_config_id = ae.id
	left join api_embedfield ae2 on ae2.embed_config_id = ae.id and ae2.column_name=flif.key
	where 
		as2.is_active = true and 
		ae2.column_name is not null and 
		value->>'value' != '' and 
		ae2.searchable=true and 
		af.is_active=true and 
		fli.facility_id = fl_id 

	order by ae2."order";
end;
$$;