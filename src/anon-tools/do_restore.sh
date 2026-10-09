#!/bin/bash


aws s3 cp --only-show-errors s3://oshub-dumps-anonymized/osh_prod_large_anon.dump /dumps/osh_prod_large.dump

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
    PGCONNECT_TIMEOUT=10 psql -h localhost -p 5433 -d "$DATABASE_NAME" -U "$DATABASE_USERNAME" -w \
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
# Restore in parallel: -j loads tables and builds indexes over several
# connections at once (all through the same SSM session). It needs the dump
# file as an argument, not on stdin. More memory for index and constraint
# builds, and no synchronous commit (a failed restore is simply re-run),
# apply only to the restore's own connections. Size both to the target RDS
# instance: jobs <= its vCPUs, jobs x memory well below its RAM (defaults
# sized for 16 vCPU / 64 GB: 8 x 1GB = 8 GB at most).
RESTORE_JOBS="${RESTORE_JOBS:-8}"
RESTORE_MAINTENANCE_WORK_MEM="${RESTORE_MAINTENANCE_WORK_MEM:-1GB}"
echo "[info] Restoring with $RESTORE_JOBS parallel jobs (maintenance_work_mem=$RESTORE_MAINTENANCE_WORK_MEM)"
PGOPTIONS="-c maintenance_work_mem=$RESTORE_MAINTENANCE_WORK_MEM -c synchronous_commit=off" \
  pg_restore --verbose --clean --if-exists --no-acl --no-owner -j "$RESTORE_JOBS" \
  -d "$DATABASE_NAME" -U "$DATABASE_USERNAME" -h localhost -p 5433 \
  /dumps/osh_prod_large.dump
RESTORE_CODE=$?
echo "[info] pg_restore finished with exit code $RESTORE_CODE"
exit $RESTORE_CODE
