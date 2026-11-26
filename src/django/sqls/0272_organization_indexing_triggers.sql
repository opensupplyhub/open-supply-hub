/*
Organization level: the facility index now names the organization a
contribution was recorded against, so it has to follow two more changes.

1. Recording an organization on a source or a claim. The guard added by
   0271_skip_indexing_on_organization_stamp.sql, which skipped
   re-indexing when organization_id was the only column an UPDATE
   changed, is removed: the two trigger functions go back to the bodies
   created by 0131_create_table_triggers.sql.

2. Renaming an organization. A new trigger on api_organization
   re-indexes every production location that has a contribution or a
   claim recorded against the organization. Nothing else on the
   organization is read by the index, so only a change of name fires it.
*/

CREATE OR REPLACE
FUNCTION handle_source_post_update_insert_indexing_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $body$
BEGIN
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
	CALL perform_facility_claim_indexing(NEW.facility_id);
	RETURN NEW;
END;

$body$;

CREATE OR REPLACE
PROCEDURE perform_organization_indexing(organization_identifier integer)
LANGUAGE plpgsql
AS $body$
DECLARE facility_ids TEXT[];

BEGIN
SELECT
	COALESCE(array_agg(DISTINCT attributed.facility_id),
	'{}')
INTO
	facility_ids
FROM
	(
	SELECT
		afli.facility_id
	FROM
		api_facilitylistitem afli
	JOIN api_source asrc ON
		asrc.id = afli.source_id
	WHERE
		asrc.organization_id = organization_identifier
		AND afli.facility_id IS NOT NULL
UNION
	SELECT
		afc.facility_id
	FROM
		api_facilityclaim afc
	WHERE
		afc.organization_id = organization_identifier
) AS attributed;

IF array_length(facility_ids,
1) > 0 THEN
	CALL index_facilities_by(facility_ids);
END IF;
END;

$body$;

CREATE OR REPLACE
FUNCTION handle_organization_post_update_indexing_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $body$
BEGIN
	CALL perform_organization_indexing(NEW.id);
	RETURN NEW;
END;

$body$;

DROP TRIGGER IF EXISTS organization_post_update_indexing_trigger
	ON api_organization;

CREATE TRIGGER organization_post_update_indexing_trigger
    AFTER
UPDATE
	ON
	api_organization
	FOR EACH ROW
	WHEN (OLD.name IS DISTINCT FROM NEW.name)
    EXECUTE FUNCTION handle_organization_post_update_indexing_trigger();
