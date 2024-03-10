#!/bin/sh
docker-entrypoint.sh "$@" &

sleep 5s

echo "Running anonymize script"

createdb -U anonymizer -E UTF8 -T template0 anonymizer

pg_restore -U anonymizer -d anonymizer -F c -c < /usr/local/bin/dump_file.custom


psql -U $POSTGRES_USER -d $POSTGRES_DB -f /scripts/anonimize_script.sql

pg_dump -F tar -U anonymizer -d anonymizer -v -Ft -f /outcome/anonymized_dump.tar

echo "Finish anonymize script"