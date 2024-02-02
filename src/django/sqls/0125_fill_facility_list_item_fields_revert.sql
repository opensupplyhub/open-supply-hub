
DROP procedure if exists update_facility_list_item_fields(jsonb,integer);
DROP trigger if exists update_fli ON api_facilitylistitem;
DROP trigger if exists delete_fli ON api_facilitylistitem;
drop function if exists delete_facility_list_item_fields_trigger();
drop function if exists update_facility_list_item_fields_trigger();
delete from api_facilitylistitemfield;
