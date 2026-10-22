#!/bin/bash

# Restore the anonymized production dump into the target environment's
# database.
#
# Runs as a Fargate task inside the target environment's VPC
# (deployment/run_restore_task, task definition in
# deployment/terraform/database_restore.tf), so it reaches RDS directly at
# DATABASE_HOST:DATABASE_PORT. The defaults (localhost:5433) still allow a
# manual run through an SSM port forward.
#
# Environment:
#   DATABASE_NAME, DATABASE_USERNAME, DATABASE_PASSWORD (required)
#   DATABASE_HOST, DATABASE_PORT   default localhost / 5433
#   DUMP_S3_URI                    default the weekly anonymized dump
#   RESTORE_JOBS                   pg_restore parallel jobs, default 8
#   RESTORE_MAINTENANCE_WORK_MEM   per-connection index build memory, default 1GB

DATABASE_HOST="${DATABASE_HOST:-localhost}"
DATABASE_PORT="${DATABASE_PORT:-5433}"
DUMP_S3_URI="${DUMP_S3_URI:-s3://oshub-dumps-anonymized/osh_prod_large_anon.dump}"
DUMP_FILE=/dumps/osh_prod_large.dump

echo "[info] Downloading $DUMP_S3_URI"
if ! aws s3 cp --only-show-errors "$DUMP_S3_URI" "$DUMP_FILE"; then
  echo "[error] Could not download $DUMP_S3_URI" >&2
  exit 1
fi
echo "[info] Dump size: $(du -h "$DUMP_FILE" | cut -f1)"

echo "$DATABASE_HOST:$DATABASE_PORT:$DATABASE_NAME:$DATABASE_USERNAME:$DATABASE_PASSWORD" > ~/.pgpass
chmod 600 ~/.pgpass

max_tries=20
try=1
until pg_isready -h "$DATABASE_HOST" -p "$DATABASE_PORT" -d "$DATABASE_NAME" -U "$DATABASE_USERNAME" >/dev/null 2>&1; do
  if [ "$try" -ge "$max_tries" ]; then
    echo "[error] Database at $DATABASE_HOST:$DATABASE_PORT not ready after $max_tries attempts." >&2
    exit 1
  fi
  echo "[info] Waiting for the database (attempt $try/$max_tries)..."
  sleep 2
  try=$((try+1))
done

# Only through an SSM port forward: Session Manager closes sessions that
# carry no data for longer than its idle timeout (20 minutes by default), and
# index and constraint builds can be silent for longer, so send a trivial
# query through the tunnel every few minutes.
if [ "$DATABASE_HOST" = "localhost" ]; then
  (
    while true; do
      sleep 240
      PGCONNECT_TIMEOUT=10 psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -d "$DATABASE_NAME" -U "$DATABASE_USERNAME" -w \
        -c 'SELECT 1' >/dev/null 2>&1 || true
    done
  ) &
  HEARTBEAT_PID=$!
  trap 'kill "$HEARTBEAT_PID" 2>/dev/null || true' EXIT
fi

SQL_SCRIPT="DO \$\$
DECLARE
BEGIN
  DROP SCHEMA public CASCADE;
  CREATE SCHEMA public;
  GRANT ALL ON SCHEMA public TO public;
END \$\$;"

echo "Dropping tables"
psql -d "$DATABASE_NAME" -U "$DATABASE_USERNAME" -h "$DATABASE_HOST" -p "$DATABASE_PORT" -c "$SQL_SCRIPT"

# Restore in parallel: -j loads tables and builds indexes over several
# connections at once; it needs the dump file as an argument, not on stdin.
# More memory for index and constraint builds, and no synchronous commit (a
# failed restore is simply re-run), apply only to the restore's own
# connections. Size both to the target RDS instance: jobs <= its vCPUs,
# jobs x memory well below its RAM (Test db.t3.2xlarge: 8 vCPU / 32 GB;
# Preprod db.m6in.4xlarge: 16 vCPU / 64 GB; 8 x 1GB = 8 GB at most).
RESTORE_JOBS="${RESTORE_JOBS:-8}"
RESTORE_MAINTENANCE_WORK_MEM="${RESTORE_MAINTENANCE_WORK_MEM:-1GB}"
echo "[info] Restoring with $RESTORE_JOBS parallel jobs (maintenance_work_mem=$RESTORE_MAINTENANCE_WORK_MEM)"
PGOPTIONS="-c maintenance_work_mem=$RESTORE_MAINTENANCE_WORK_MEM -c synchronous_commit=off" \
  pg_restore --verbose --clean --if-exists --no-acl --no-owner -j "$RESTORE_JOBS" \
  -d "$DATABASE_NAME" -U "$DATABASE_USERNAME" -h "$DATABASE_HOST" -p "$DATABASE_PORT" \
  "$DUMP_FILE"
RESTORE_CODE=$?
echo "[info] pg_restore finished with exit code $RESTORE_CODE"
exit $RESTORE_CODE
