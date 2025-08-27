#!/bin/bash

# Run the database sync
python manage.py sync_databases \
  --source-host "${source_db_host}" \
  --source-port "${source_db_port}" \
  --source-name "${source_db_name}" \
  --source-user "${source_db_user}" \
  --source-password "${source_db_password}" \
  --last-run-path /db-sync \
  --verbose

echo '[DB_SYNC] === SYNC COMPLETION STATUS ==='
for model in User Contributor FacilityList Source FacilityListItem Facility FacilityMatch FacilityLocation FacilityClaim ExtendedField FacilityActivityReport FacilityAlias; do
  model_lower=$(echo $model | tr '[:upper:]' '[:lower:]')
  if [ -f "/db-sync/${model_lower}_last_run" ]; then
    echo "[DB_SYNC] SUCCESS ${model}: /db-sync/${model_lower}_last_run"
    echo "[DB_SYNC] ${model} last sync: $(cat /db-sync/${model_lower}_last_run)"
  else
    echo "[DB_SYNC] FAILED ${model}: file not found" >&2
  fi
done

echo '[DB_SYNC] === TIMESTAMP CHECK ==='
if [ -f "/db-sync/facilitylistitem_last_run_facility_updates" ]; then
  echo "[DB_SYNC] SUCCESS FacilityListItem facility updates: /db-sync/facilitylistitem_last_run_facility_updates"
  echo "[DB_SYNC] FacilityListItem facility updates last sync: $(cat /db-sync/facilitylistitem_last_run_facility_updates)"
else
  echo "[DB_SYNC] FAILED FacilityListItem facility updates: file not found" >&2
fi

echo '[DB_SYNC] === EFS DIRECTORY LISTING ==='
echo '[DB_SYNC] Total files in /db-sync:'
ls -la /db-sync
echo '[DB_SYNC] === SYNC COMPLETED ==='
