#!/bin/sh

set -eu

# Default to Production if not provided from GH Action input.
ENV_TAG="${ENVIRONMENT:-Production}"

echo "[info] Selected ENVIRONMENT: $ENV_TAG"

# OSDEV-3531: the database is reached through an SSM port forward that the
# workflow opens on the runner before starting this container (run with
# --network host), so localhost:5433 is already forwarded to
# database.service.osh.internal:5432 through the bastion.
echo "localhost:5433:$DATABASE_NAME:$DATABASE_USERNAME:$DATABASE_PASSWORD" > ~/.pgpass
chmod 600 ~/.pgpass

# Session Manager closes sessions that carry no data for longer than the
# account's idle timeout (20 minutes by default). Long pg_dump phases can be
# silent on the wire, so send a trivial query through the tunnel every few
# minutes to keep the session alive.
(
  while true; do
    sleep 240
    PGCONNECT_TIMEOUT=10 psql -h localhost -p 5433 -d "$DATABASE_NAME" -U "$DATABASE_USERNAME" -w \
      -c 'SELECT 1' >/dev/null 2>&1 || true
  done
) &
HEARTBEAT_PID=$!
trap 'kill "$HEARTBEAT_PID" 2>/dev/null || true' EXIT

# Wait for the local tunnel to become ready.
max_tries=20
try=1
until pg_isready -h localhost -p 5433 -d "$DATABASE_NAME" -U "$DATABASE_USERNAME" >/dev/null 2>&1; do
  if [ "$try" -ge "$max_tries" ]; then
    echo "[error] Database tunnel to localhost:5433 not ready after $max_tries attempts." >&2
    exit 1
  fi
  echo "[info] Waiting for database tunnel (attempt $try/$max_tries)..."
  sleep 2
  try=$((try+1))
done

echo "[info] Database tunnel is ready. Proceeding with pg_dump."

case "$ENV_TAG" in
  "Rba")
    DUMP_BASE="osh_rba_large"
    ;;
  "Development")
    DUMP_BASE="osh_dev_large"
    ;;
  *)
    DUMP_BASE="osh_prod_large"
    ;;
 esac

DUMP_PATH="/dumps/${DUMP_BASE}.dump"
pg_dump --clean --no-owner --no-privileges -Fc -h localhost -d "$DATABASE_NAME" -U "$DATABASE_USERNAME" -p 5433 -f "$DUMP_PATH" -w --verbose
ls -la /dumps || true

# The remote database is no longer needed; stop the tunnel heartbeat.
kill "$HEARTBEAT_PID" 2>/dev/null || true

DUMP_BYTES=$(wc -c < "$DUMP_PATH" || echo 0)
echo "[info] Raw dump size (bytes): $DUMP_BYTES"
if [ "$DUMP_BYTES" -le 1024 ]; then
  echo "[warn] Dump size looks too small; pg_restore will likely fail."
fi

echo "[info] Start anonymization"

# Start local Postgres inside the container.
ENTRYPOINT_BIN="$(command -v docker-entrypoint.sh || true)"
if [ -z "$ENTRYPOINT_BIN" ]; then
  if [ -x /usr/local/bin/docker-entrypoint.sh ]; then
    ENTRYPOINT_BIN="/usr/local/bin/docker-entrypoint.sh"
  elif [ -x /usr/local/bin/docker-entrypoint ]; then
    ENTRYPOINT_BIN="/usr/local/bin/docker-entrypoint"
  else
    echo "[error] docker-entrypoint.sh not found in PATH or /usr/local/bin" >&2
    exit 1
  fi
fi

"$ENTRYPOINT_BIN" -c 'shared_buffers=2048MB' -c 'max_connections=10' &

# Wait for local Postgres on 5432 to be ready.
max_tries=30
try=1
until pg_isready -d anondb -U anondb -h localhost -p 5432 >/dev/null 2>&1; do
  if [ "$try" -ge "$max_tries" ]; then
    echo "[error] Local Postgres on 5432 not ready after $max_tries attempts." >&2
    exit 1
  fi
  echo "[info] Waiting for local Postgres (attempt $try/$max_tries)..."
  sleep 2
  try=$((try+1))
done

echo "[info] Pre-dropping PostGIS extensions to avoid dependency issues"
psql -U anondb -d anondb -h localhost -p 5432 -v ON_ERROR_STOP=1 -c "\
  DROP EXTENSION IF EXISTS postgis_tiger_geocoder CASCADE;\
  DROP EXTENSION IF EXISTS postgis_topology CASCADE;\
  DROP EXTENSION IF EXISTS postgis CASCADE;\
"

echo "[info] Restoring into local anonymization DB"
# Capture restore stderr and continue to report errors.
set +e
pg_restore --verbose --clean --if-exists --no-acl --no-owner \
  -d anondb -U anondb -h localhost -p 5432 "$DUMP_PATH" \
  2> /dumps/restore.err
RESTORE_CODE=$?
set -e

if [ "$RESTORE_CODE" -ne 0 ]; then
  echo "[error] pg_restore exited with code: $RESTORE_CODE" >&2
  if grep -qi "error:" /dumps/restore.err; then
    echo "==== pg_restore first error (context) ====" >&2
    LINE=$(grep -n -i "error:" -m 1 /dumps/restore.err | cut -d: -f1)
    if [ -n "$LINE" ]; then
      START=$((LINE>5 ? LINE-5 : 1))
      sed -n "${START},${LINE}p" /dumps/restore.err
    else
      echo "[info] Could not locate error line" >&2
    fi
    echo "========================================="
  else
    echo "[info] No explicit 'error:' lines found; see /dumps/restore.err" >&2
  fi
fi

echo "[info] Applying anonymization SQL"
psql -U anondb -d anondb -h localhost -p 5432 <<'SQL'
DO $$
DECLARE
    current_table text;
    column_exists_email boolean;
    column_exists_username boolean;
    column_exists_password boolean;
    column_exists_phone_number boolean;
BEGIN
    FOR current_table IN (SELECT table_name FROM information_schema.tables WHERE table_schema = 'public')
    LOOP
        EXECUTE 'SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = ''' || current_table || ''' AND column_name = ''email'')' INTO column_exists_email;
        EXECUTE 'SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = ''' || current_table || ''' AND column_name = ''username'')' INTO column_exists_username;
        EXECUTE 'SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = ''' || current_table || ''' AND column_name = ''password'')' INTO column_exists_password;
        EXECUTE 'SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = ''' || current_table || ''' AND column_name = ''phone_number'')' INTO column_exists_phone_number;
        IF column_exists_email THEN
            EXECUTE 'UPDATE ' || current_table || ' SET
                email = CASE WHEN email NOT LIKE ''%@speedandfunction.com'' AND email NOT LIKE ''%@opensupplyhub.org'' THEN md5(random()::text) || ''@'' || substring(email from position(''@'' in email) + 1) ELSE email END';
            IF column_exists_username THEN
                EXECUTE 'UPDATE ' || current_table || ' SET
                    username = CASE WHEN email NOT LIKE ''%@speedandfunction.com'' AND email NOT LIKE ''%@opensupplyhub.org'' THEN substr(md5(random()::text), 1, 20) ELSE username END';
            END IF;
            IF column_exists_password THEN
                EXECUTE 'UPDATE ' || current_table || ' SET
                    password = CASE WHEN email NOT LIKE ''%@speedandfunction.com'' AND email NOT LIKE ''%@opensupplyhub.org'' THEN md5(random()::text) ELSE password END';
            END IF;
            IF column_exists_phone_number THEN
                EXECUTE 'UPDATE ' || current_table || ' SET
                    phone_number = CASE WHEN email NOT LIKE ''%@speedandfunction.com'' AND email NOT LIKE ''%@opensupplyhub.org'' THEN md5(random()::text) ELSE phone_number END';
            END IF;
        END IF;
    END LOOP;
END $$;
SQL

ANON_DUMP_PATH="/dumps/${DUMP_BASE}_anonymized.dump"
echo "[info] Creating anonymized dump: $ANON_DUMP_PATH"
pg_dump --clean --no-owner --no-privileges -Fc -d anondb -U anondb -f "$ANON_DUMP_PATH" -w --verbose

ANON_BYTES=$(wc -c < "$ANON_DUMP_PATH" || echo 0)
echo "[info] Anonymized dump size (bytes): $ANON_BYTES"

ls -la /dumps || true

echo "[info] Uploading anonymized dump to S3"
S3_KEY="s3://oshub-dumps-anonymized/${DUMP_BASE}_anon.dump"
AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID_TEST \
AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY_TEST \
AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION_TEST \
  aws s3 cp --only-show-errors "$ANON_DUMP_PATH" "$S3_KEY"

echo "[info] Uploaded: $S3_KEY"
