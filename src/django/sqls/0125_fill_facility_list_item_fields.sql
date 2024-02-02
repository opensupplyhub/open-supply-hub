create or replace PROCEDURE update_facility_list_item_fields(lvs jsonb, fli_i int4)
LANGUAGE plpgsql
AS $$
declare
   key1   text;
   value1 text;
begin
   FOR key1, value1 in SELECT * FROM jsonb_each_text(lvs)
    LOOP
     	insert into public.api_facilitylistitemfield (
     		id, 
     		key, 
     		value, 
     		"type", 
     		updated_at, 
     		created_at, 
     		facility_list_item_id
     	) values ( 
			default,
			key1, -- key
			json_build_object('value', value1), -- value
			0, -- type: RAW
			now(),
			now(),
			fli_i
		) on conflict (facility_list_item_id, key) do update set
			value=excluded.value,
			type=excluded.type,
			updated_at=now();
    END LOOP;   
end;
$$;

create or replace function migrate_facility_list_item_fields_trigger() returns  trigger
LANGUAGE plpgsql
AS $$
declare 
	jsn jsonb = null ;
begin
	jsn = new.raw_json || jsonb_build_object(
		'name', new.name,
		'address', new.address,
		''
		'sector', new.sector);
	call update_facility_list_item_fields(jsn, new.id); 
  
end;
$$;

create or replace function update_facility_list_item_fields_trigger() returns  trigger
LANGUAGE plpgsql
AS $$
declare 
	jsn jsonb = null ;
begin
	jsn = new.raw_json || jsonb_build_object(
		'name', new.name,
		'address', new.address,
		''
		'sector', new.sector);
	call update_facility_list_item_fields(jsn, new.id); 
   return new;
end;
$$;

create or replace function delete_facility_list_item_fields_trigger() returns  trigger
LANGUAGE plpgsql
AS $$
begin
	delete from api_facilitylistitemfield where facility_list_item_id = old.id;
   return old;
end;
$$;

create trigger update_fli
    AFTER update or insert ON api_facilitylistitem
    FOR EACH ROW
    EXECUTE procedure update_facility_list_item_fields_trigger();

CREATE TRIGGER delete_fli
    BEFORE delete ON api_facilitylistitem
    FOR EACH ROW
    EXECUTE procedure delete_facility_list_item_fields_trigger();


update api_facilitylistitem set name=name;
