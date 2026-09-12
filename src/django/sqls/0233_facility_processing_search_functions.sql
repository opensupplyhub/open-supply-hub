/*
Immutable helpers that make the facility type and processing type filters of
the location search indexable.

api_facilityindex stores both taxonomy labels and raw contributor values in
the facility_type and processing_type arrays, with whatever casing and accents
were submitted. Matching those case- and accent-insensitively means wrapping
the column in an expression, and an expression can only be indexed when every
function in it is immutable. unaccent() is not, because it reads a dictionary
that can be reloaded; the two-argument form that names the dictionary
explicitly is, and is the documented way to index unaccented text.
*/
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

/*Lower-case every element of an array so a case-insensitive filter can be an
array overlap against an index instead of a per-row unnest. Returns NULL for
an empty array, which no overlap matches - the same outcome as a location
carrying none of the requested values.*/
CREATE OR REPLACE
FUNCTION lower_varchar_array(vals VARCHAR[])
RETURNS TEXT[]
LANGUAGE SQL
IMMUTABLE
PARALLEL SAFE
AS $body$
SELECT array_agg(lower(val)) FROM unnest(vals) AS elements(val);
$body$;

/*Both arrays flattened into one normalized string for trigram matching. The
free-text branch of the filter searches facility_type and processing_type
together, so indexing them together lets one index scan gather the candidate
locations that the precise word-boundary regex then rechecks.*/
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
