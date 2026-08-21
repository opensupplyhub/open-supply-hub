/*
api_facility_processing_value holds every distinct facility type and
processing type carried by api_facilityindex together with the number of
locations carrying it. It backs the processing type typeahead, which cannot
aggregate the two array columns of api_facilityindex per request: that is a
sequential scan of a table measured at 12 GB.

The counts are maintained by triggers on api_facilityindex rather than
rebuilt on a schedule. api_facilityindex is itself maintained one row at a
time (see perform_extended_field_indexing in 0131_create_table_triggers.sql),
and the processing types of a location change a few hundred times a day, so
applying deltas costs a handful of primary key lookups where a periodic
rebuild would rescan the whole table every time.

Bulk paths that rewrite api_facilityindex wholesale - index_facilities() and
backfill_facility_index - fire the delta triggers once per changed row. Run
the recompute_facility_processing_value_index management command after them
instead, and disable the triggers below for the duration if the run is large
enough for the counter updates to matter.
*/
DROP MATERIALIZED VIEW IF EXISTS api_facility_processing_value;

CREATE TABLE api_facility_processing_value (
	kind TEXT NOT NULL,
	identity TEXT NOT NULL,
	value TEXT NOT NULL,
	facility_count INTEGER NOT NULL,
	PRIMARY KEY (kind, identity)
);

CREATE TABLE api_facility_processing_value_variant (
	kind TEXT NOT NULL,
	identity TEXT NOT NULL,
	value TEXT NOT NULL,
	facility_count INTEGER NOT NULL,
	PRIMARY KEY (kind, value)
);

COMMENT ON TABLE api_facility_processing_value IS
	'Case-normalized facility_type and processing_type values indexed on '
	'api_facilityindex with the number of locations carrying any casing. '
	'Maintained by the facility_index_processing_value_* triggers and '
	'rebuilt by the recompute_facility_processing_value_index management '
	'command.';

CREATE INDEX api_facility_processing_value_value_trgm_idx
	ON api_facility_processing_value USING gin (value gin_trgm_ops);

CREATE INDEX api_facility_processing_value_variant_identity_idx
	ON api_facility_processing_value_variant (kind, identity);

/*Placeholders contributors upload instead of leaving the field empty. Kept
in sync with the exclusions of index_processing_type() and
index_facility_type(), which keep them out of api_facilityindex in the first
place; the check is repeated here so rows indexed before those exclusions
existed cannot reach the typeahead either. The length cap keeps the primary
key entry under the 2704 byte limit of a btree index and drops free text too
long to ever be a useful suggestion.*/
CREATE OR REPLACE
FUNCTION is_indexable_facility_processing_value(raw_value TEXT)
RETURNS BOOLEAN
LANGUAGE SQL
IMMUTABLE
AS $body$
SELECT
	raw_value IS NOT NULL
	AND btrim(raw_value) <> ''
	AND length(raw_value) <= 500
	AND lower(btrim(raw_value)) <> ALL (ARRAY[
		'null', 'none', 'n/a', 'na', 'unknown', 'other', '-'
	]);
$body$;

/*Apply both exact-variant and lower-case identity deltas. A facility carrying
multiple casing variants increments each variant once but increments their
shared identity only once.*/
CREATE OR REPLACE
PROCEDURE apply_facility_processing_value_delta(
	value_kind TEXT,
	old_values VARCHAR[],
	new_values VARCHAR[]
)
LANGUAGE plpgsql
AS $body$
DECLARE
	removed_values VARCHAR[];
	added_values VARCHAR[];
	removed_identities TEXT[];
	added_identities TEXT[];
	affected_identities TEXT[];

BEGIN
IF old_values IS NOT DISTINCT FROM new_values THEN
	RETURN;
END IF;

SELECT
	array_agg(removed)
INTO
	removed_values
FROM
	(
	SELECT unnest(COALESCE(old_values, '{}'::VARCHAR[]))
	EXCEPT
	SELECT unnest(COALESCE(new_values, '{}'::VARCHAR[]))
) AS removals(removed);

SELECT
	array_agg(added)
INTO
	added_values
FROM
	(
	SELECT unnest(COALESCE(new_values, '{}'::VARCHAR[]))
	EXCEPT
	SELECT unnest(COALESCE(old_values, '{}'::VARCHAR[]))
) AS additions(added);

SELECT
	array_agg(removed_identity)
INTO
	removed_identities
FROM
	(
	SELECT DISTINCT lower(old_value) AS removed_identity
	FROM unnest(COALESCE(old_values, '{}'::VARCHAR[])) AS old_values(old_value)
	WHERE is_indexable_facility_processing_value(old_value)
	EXCEPT
	SELECT DISTINCT lower(new_value)
	FROM unnest(COALESCE(new_values, '{}'::VARCHAR[])) AS new_values(new_value)
	WHERE is_indexable_facility_processing_value(new_value)
) AS removals;

SELECT
	array_agg(added_identity)
INTO
	added_identities
FROM
	(
	SELECT DISTINCT lower(new_value) AS added_identity
	FROM unnest(COALESCE(new_values, '{}'::VARCHAR[])) AS new_values(new_value)
	WHERE is_indexable_facility_processing_value(new_value)
	EXCEPT
	SELECT DISTINCT lower(old_value)
	FROM unnest(COALESCE(old_values, '{}'::VARCHAR[])) AS old_values(old_value)
	WHERE is_indexable_facility_processing_value(old_value)
) AS additions;

IF removed_values IS NOT NULL THEN
UPDATE
	api_facility_processing_value_variant
SET
	facility_count = facility_count - 1
WHERE
	kind = value_kind
	AND value = ANY(removed_values);

DELETE
FROM
	api_facility_processing_value_variant
WHERE
	kind = value_kind
	AND value = ANY(removed_values)
	AND facility_count <= 0;
END IF;

IF added_values IS NOT NULL THEN
INSERT
	INTO
	api_facility_processing_value_variant (
		kind, identity, value, facility_count
	)
SELECT
	value_kind,
	lower(added),
	added,
	1
FROM
	unnest(added_values) AS additions(added)
WHERE
	is_indexable_facility_processing_value(added)
ON
	CONFLICT (kind, value)
DO
UPDATE
SET
	facility_count =
		api_facility_processing_value_variant.facility_count + 1;
END IF;

IF removed_identities IS NOT NULL THEN
UPDATE
	api_facility_processing_value
SET
	facility_count = facility_count - 1
WHERE
	kind = value_kind
	AND identity = ANY(removed_identities);

DELETE
FROM
	api_facility_processing_value
WHERE
	kind = value_kind
	AND identity = ANY(removed_identities)
	AND facility_count <= 0;
END IF;

IF added_identities IS NOT NULL THEN
INSERT
	INTO
	api_facility_processing_value (kind, identity, value, facility_count)
SELECT
	value_kind,
	added_identity,
	added_identity,
	1
FROM
	unnest(added_identities) AS additions(added_identity)
ON
	CONFLICT (kind, identity)
DO
UPDATE
SET
	facility_count = api_facility_processing_value.facility_count + 1;
END IF;

SELECT array_agg(DISTINCT identity)
INTO affected_identities
FROM unnest(
	COALESCE(removed_values, '{}'::VARCHAR[])
	|| COALESCE(added_values, '{}'::VARCHAR[])
) AS affected(value)
CROSS JOIN LATERAL (SELECT lower(value) AS identity) normalized;

UPDATE api_facility_processing_value logical_value
SET value = (
	SELECT variant.value
	FROM api_facility_processing_value_variant variant
	WHERE
		variant.kind = logical_value.kind
		AND variant.identity = logical_value.identity
	ORDER BY
		variant.facility_count DESC,
		variant.value COLLATE "C" ASC
	LIMIT 1
)
WHERE
	logical_value.kind = value_kind
	AND logical_value.identity = ANY(
		COALESCE(affected_identities, '{}'::TEXT[])
	)
	AND EXISTS (
		SELECT 1
		FROM api_facility_processing_value_variant variant
		WHERE
			variant.kind = logical_value.kind
			AND variant.identity = logical_value.identity
	);
END;

$body$;

/*Rebuild every count from api_facilityindex. TRUNCATE holds an ACCESS
EXCLUSIVE lock until this procedure commits, so a location indexed while the
rebuild runs is either visible to the SELECT below or applies its delta
afterwards, never both and never neither.*/
CREATE OR REPLACE
PROCEDURE recompute_facility_processing_values()
LANGUAGE plpgsql
AS $body$
DECLARE
	facility_type_kind CONSTANT TEXT := 'facility_type';
	processing_type_kind CONSTANT TEXT := 'processing_type';

BEGIN
TRUNCATE api_facility_processing_value_variant;
TRUNCATE api_facility_processing_value;

INSERT
	INTO
	api_facility_processing_value_variant (
		kind, identity, value, facility_count
	)
SELECT
	kind,
	lower(value),
	value,
	count(DISTINCT facility_id)::INTEGER
FROM
	(
	SELECT
		fi.id AS facility_id,
		facility_type_kind AS kind,
		raw_value AS value
	FROM
		api_facilityindex fi
	CROSS JOIN LATERAL unnest(fi.facility_type) AS ft(raw_value)
	WHERE
		fi.facility_type <> '{}'

	UNION ALL

	SELECT
		fi.id AS facility_id,
		processing_type_kind AS kind,
		raw_value AS value
	FROM
		api_facilityindex fi
	CROSS JOIN LATERAL unnest(fi.processing_type) AS pt(raw_value)
	WHERE
		fi.processing_type <> '{}'
) AS unnested_values
WHERE
	is_indexable_facility_processing_value(value)
GROUP BY
	kind,
	value;

INSERT
	INTO
	api_facility_processing_value (kind, identity, value, facility_count)
SELECT DISTINCT ON (logical_counts.kind, logical_counts.identity)
	logical_counts.kind,
	logical_counts.identity,
	variant.value,
	logical_counts.facility_count
FROM (
	SELECT
		kind,
		lower(value) AS identity,
		count(DISTINCT facility_id)::INTEGER AS facility_count
	FROM (
		SELECT
			fi.id AS facility_id,
			facility_type_kind AS kind,
			raw_value AS value
		FROM api_facilityindex fi
		CROSS JOIN LATERAL
			unnest(fi.facility_type) AS ft(raw_value)
		WHERE fi.facility_type <> '{}'

		UNION ALL

		SELECT
			fi.id AS facility_id,
			processing_type_kind AS kind,
			raw_value AS value
		FROM api_facilityindex fi
		CROSS JOIN LATERAL
			unnest(fi.processing_type) AS pt(raw_value)
		WHERE fi.processing_type <> '{}'
	) unnested_values
	WHERE is_indexable_facility_processing_value(value)
	GROUP BY kind, lower(value)
) logical_counts
JOIN api_facility_processing_value_variant variant
	ON variant.kind = logical_counts.kind
	AND variant.identity = logical_counts.identity
ORDER BY
	logical_counts.kind,
	logical_counts.identity,
	variant.facility_count DESC,
	variant.value COLLATE "C" ASC;
END;

$body$;

CREATE OR REPLACE
FUNCTION handle_facility_index_processing_value_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $body$
DECLARE
	facility_type_kind CONSTANT TEXT := 'facility_type';
	processing_type_kind CONSTANT TEXT := 'processing_type';

BEGIN
	IF TG_OP = 'INSERT' THEN
		CALL apply_facility_processing_value_delta(
			facility_type_kind, '{}'::VARCHAR[], NEW.facility_type
		);
		CALL apply_facility_processing_value_delta(
			processing_type_kind, '{}'::VARCHAR[], NEW.processing_type
		);
		RETURN NEW;
	ELSIF TG_OP = 'UPDATE' THEN
		CALL apply_facility_processing_value_delta(
			facility_type_kind, OLD.facility_type, NEW.facility_type
		);
		CALL apply_facility_processing_value_delta(
			processing_type_kind, OLD.processing_type, NEW.processing_type
		);
		RETURN NEW;
	ELSE
		CALL apply_facility_processing_value_delta(
			facility_type_kind, OLD.facility_type, '{}'::VARCHAR[]
		);
		CALL apply_facility_processing_value_delta(
			processing_type_kind, OLD.processing_type, '{}'::VARCHAR[]
		);
		RETURN OLD;
	END IF;
END;

$body$;

/*api_facilityindex is rewritten by the indexing triggers of half a dozen
tables, almost always for columns this table does not care about. The WHEN
clauses keep those writes free.*/
CREATE TRIGGER facility_index_processing_value_insert_trigger
    AFTER
INSERT
	ON
	api_facilityindex
	FOR EACH ROW
	WHEN (
		COALESCE(NEW.facility_type, '{}'::VARCHAR[]) <> '{}'::VARCHAR[]
		OR COALESCE(NEW.processing_type, '{}'::VARCHAR[]) <> '{}'::VARCHAR[]
	)
    EXECUTE FUNCTION handle_facility_index_processing_value_trigger();

CREATE TRIGGER facility_index_processing_value_update_trigger
    AFTER
UPDATE
	ON
	api_facilityindex
	FOR EACH ROW
	WHEN (
		OLD.facility_type IS DISTINCT FROM NEW.facility_type
		OR OLD.processing_type IS DISTINCT FROM NEW.processing_type
	)
    EXECUTE FUNCTION handle_facility_index_processing_value_trigger();

CREATE TRIGGER facility_index_processing_value_delete_trigger
    AFTER
DELETE
	ON
	api_facilityindex
	FOR EACH ROW
	WHEN (
		COALESCE(OLD.facility_type, '{}'::VARCHAR[]) <> '{}'::VARCHAR[]
		OR COALESCE(OLD.processing_type, '{}'::VARCHAR[]) <> '{}'::VARCHAR[]
	)
    EXECUTE FUNCTION handle_facility_index_processing_value_trigger();

CALL recompute_facility_processing_values();
