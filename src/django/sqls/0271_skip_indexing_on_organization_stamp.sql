/*
Recording an organization on a source or a claim changes nothing the
facility index holds, but the indexing triggers on api_source and
api_facilityclaim fire on every UPDATE and re-index every production
location tied to the row. Attributing a member's earlier contributions
to their organization updates many such rows at once, so without a
guard it would re-index all of the member's production locations for
no visible change.

These two trigger functions are re-created to return early when an
UPDATE changed organization_id and nothing else. Inserts, and updates
that touch any other column, behave exactly as before.
*/

CREATE OR REPLACE
FUNCTION handle_source_post_update_insert_indexing_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $body$
BEGIN
	IF TG_OP = 'UPDATE'
		AND NEW.organization_id IS DISTINCT FROM OLD.organization_id
		AND (to_jsonb(NEW) - 'organization_id') = (to_jsonb(OLD) - 'organization_id')
	THEN
		RETURN NEW;
	END IF;

	CALL perform_source_indexing(NEW.id);
	RETURN NEW;
END;

$body$;

CREATE OR REPLACE
FUNCTION handle_facility_claim_post_update_insert_indexing_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $body$
BEGIN
	IF TG_OP = 'UPDATE'
		AND NEW.organization_id IS DISTINCT FROM OLD.organization_id
		AND (to_jsonb(NEW) - 'organization_id') = (to_jsonb(OLD) - 'organization_id')
	THEN
		RETURN NEW;
	END IF;

	CALL perform_facility_claim_indexing(NEW.facility_id);
	RETURN NEW;
END;

$body$;
