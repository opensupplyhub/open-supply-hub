DROP FUNCTION IF EXISTS format_numbers_of_workers(int, int);

create or replace function format_numbers_of_workers(max int, min int)
returns text
as
$$
declare
 result text = null;
begin
	if min >= 10001 then
		result = 'More than 10000';
	elsif min >= 5001 and max <= 10000 then
		result = '5001-10000';
	elsif min >= 1001 and max <= 5000 then
		result = '1001-5000';
	else
		result = 'Less than 1000';
	end if;
	
	return result;
end
$$
language plpgsql;