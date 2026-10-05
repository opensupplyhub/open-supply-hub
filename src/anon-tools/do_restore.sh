#!/bin/bash


aws s3 cp s3://oshub-dumps-anonymized/osh_prod_large_anon.dump /dumps/osh_prod_large.dump

# OSDEV-3531: the database is reached through an SSM port forward that the
# workflow opens on the runner before starting this container (run with
# --network host), so localhost:5433 is already forwarded to
# database.service.osh.internal:5432 through the bastion.
echo "localhost:5433:$DATABASE_NAME:$DATABASE_USERNAME:$DATABASE_PASSWORD" > ~/.pgpass
chmod 600 ~/.pgpass

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

# Session Manager closes sessions that carry no data for longer than the
# account's idle timeout (20 minutes by default). Index and constraint
# creation during pg_restore can be silent on the wire for a long time, so
# send a trivial query through the tunnel every few minutes.
(
  while true; do
    sleep 240
    psql -h localhost -p 5433 -d "$DATABASE_NAME" -U "$DATABASE_USERNAME" -w \
      -c 'SELECT 1' >/dev/null 2>&1 || true
  done
) &
HEARTBEAT_PID=$!
trap 'kill "$HEARTBEAT_PID" 2>/dev/null || true' EXIT

SQL_SCRIPT="DO \$\$
DECLARE
BEGIN
  DROP SCHEMA public CASCADE;
  CREATE SCHEMA public;
  GRANT ALL ON SCHEMA public TO public;
END \$\$;"

echo "Dropping tables"
psql -d $DATABASE_NAME -U $DATABASE_USERNAME -h localhost -p 5433 -c "$SQL_SCRIPT"
pg_restore --verbose --clean --if-exists --no-acl --no-owner -d $DATABASE_NAME -U $DATABASE_USERNAME -h localhost -p 5433 < /dumps/osh_prod_large.dump
