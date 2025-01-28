ANALYZE VERBOSE;

DO $$
DECLARE
-- Variables for pg_trgm.
current_version_pg_trgm TEXT;
target_version_pg_trgm TEXT := '1.6';

BEGIN
-- Extension 1: Check and upgrade "pg_trgm" to its target version.
SELECT
	extversion
INTO
	current_version_pg_trgm
FROM
	pg_extension
WHERE
	extname = 'pg_trgm';

IF current_version_pg_trgm IS NULL
THEN
	RAISE EXCEPTION 'Extension "pg_trgm" is not installed.';
ELSIF current_version_pg_trgm < target_version_pg_trgm
THEN
	EXECUTE FORMAT('ALTER EXTENSION pg_trgm UPDATE TO %L', target_version_pg_trgm);
	RAISE NOTICE 'Extension "pg_trgm" has been upgraded from % to %.', current_version_pg_trgm, target_version_pg_trgm;
ELSE
	RAISE NOTICE 'Extension "pg_trgm" is already at the target version or higher.';
END IF;
END $$;
