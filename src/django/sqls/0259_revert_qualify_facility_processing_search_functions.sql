/*Restores the unqualified bodies 0233 created. Doing so reintroduces the
restore failure described in the forward file.*/
CREATE OR REPLACE
FUNCTION immutable_unaccent(txt TEXT)
RETURNS TEXT
LANGUAGE SQL
IMMUTABLE
PARALLEL SAFE
STRICT
AS $body$
SELECT unaccent('unaccent'::regdictionary, txt);
$body$;

CREATE OR REPLACE
FUNCTION facility_processing_search_text(
	facility_types VARCHAR[],
	processing_types VARCHAR[]
)
RETURNS TEXT
LANGUAGE SQL
IMMUTABLE
PARALLEL SAFE
AS $body$
SELECT immutable_unaccent(lower(array_to_string(
	COALESCE(facility_types, '{}'::VARCHAR[])
	|| COALESCE(processing_types, '{}'::VARCHAR[]),
	' '
)));
$body$;
