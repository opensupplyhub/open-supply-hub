/*
Schema-qualify every name these two function bodies resolve through the
search path, so the expression indexes built on them can be restored.

pg_dump writes `SET search_path = ''` and `SET check_function_bodies = false`
into every dump. The functions therefore restore cleanly, but when pg_restore
reaches CREATE INDEX it inlines them, and an unqualified unaccent(),
'unaccent'::regdictionary or immutable_unaccent() resolves against nothing.
Both trigram indexes fail, pg_restore exits 1, and the anonymized database
restore that Preprod is rebuilt from never finishes. A plain migrate has
public on the search path, which is why this only ever surfaced on restore.

Replacing the bodies does not invalidate the indexes: the signatures and the
results are unchanged, so no reindex is needed.

SET search_path on the functions would fix the lookup too, but it would also
make them uninlinable, and inlining is what lets the planner use these
indexes at all.
*/
CREATE OR REPLACE
FUNCTION immutable_unaccent(txt TEXT)
RETURNS TEXT
LANGUAGE SQL
IMMUTABLE
PARALLEL SAFE
STRICT
AS $body$
SELECT public.unaccent('public.unaccent'::regdictionary, txt);
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
SELECT public.immutable_unaccent(lower(array_to_string(
	COALESCE(facility_types, '{}'::VARCHAR[])
	|| COALESCE(processing_types, '{}'::VARCHAR[]),
	' '
)));
$body$;
