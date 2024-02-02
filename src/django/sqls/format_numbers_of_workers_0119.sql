
DROP FUNCTION IF EXISTS format_numbers_of_workers(int, int);

create or replace function format_numbers_of_workers(max int, min int)
returns text[]
as
$$
declare
	res text[] = array[]::text[];
begin
	if max >= 10001 then
		res = res || array['More than 10000'];
	end if;
	if (max >= 5001 and min <= 10000) then
		res = res || array['5001-10000'];
	end if;
	if (max >= 1001 and min <= 5000) then
		res = res || array['1001-5000'];
	end if;
	if min <= 1000 then
		res = res || array[ 'Less than 1000'];
	end if;
	
	return res;
end
$$
language plpgsql;