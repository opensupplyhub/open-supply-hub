# Logstash `production-locations` sync: last_run reset and re-indexing facilities

## Why this is needed

The Logstash `production_locations` pipeline only indexes what changed since its last successful run:

```sql
WHERE af.updated_at > :sql_last_value   -- src/logstash/sql/sync_production_locations.sql
```

`:sql_last_value` lives in `production_locations_jdbc_last_run` on the Logstash EFS. It is only written when a **whole** run succeeds. If the task keeps crashing during the full load, the value stays at `1970-01-01` and every run starts from scratch.

`set_logstash_last_run.sh` moves that value forward so Logstash stops re-reading everything. Any facility whose `updated_at` is **older** than the new value is then never picked up again on its own. To get those facilities into OpenSearch, **bump their `updated_at`** and Logstash re-indexes them on its next run (every 15 min on AWS). The document id is the OS ID, so this overwrites existing documents rather than duplicating them.

## 1. Move the last_run date forward

Run from the repo root in Git Bash, with AWS credentials for the target account:

```bash
bash "scripts/set_logstash_last_run.sh" Production "2026-10-01 00:00:00"   # UTC
```

The script stops Logstash, rewrites the file on EFS through the bastion (SSM Run Command), keeps a `.bak` copy and starts Logstash again. Within one interval, the Logstash logs should show `af.updated_at > '2026-10-01 00:00:00…'`.

## 2. Query OpenSearch (AWS)

The domain is only reachable inside the VPC, so open an SSM port-forward and sign requests with SigV4:

```bash
export AWS_DEFAULT_REGION=eu-west-1 MSYS_NO_PATHCONV=1 ENVIRONMENT=Production
eval "$(aws configure export-credentials --format env)"     # works with profiles/SSO too
DOMAIN=$(aws es describe-elasticsearch-domains --domain-names production-os-domain \
  --query 'DomainStatusList[0].Endpoints.vpc' --output text)
bash deployment/ssm/ssm_tunnel.sh start "$DOMAIN" 443 9443

osq() {
  curl -s --aws-sigv4 "aws:amz:${AWS_DEFAULT_REGION}:es" \
    --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY" \
    ${AWS_SESSION_TOKEN:+-H "x-amz-security-token: $AWS_SESSION_TOKEN"} \
    --connect-to "$DOMAIN:443:127.0.0.1:9443" \
    -H 'Content-Type: application/json' "https://$DOMAIN$1" "${@:2}"
}
```

Useful checks:

```bash
osq "/_cat/indices/production-locations?v"              # health, docs.count, size
osq "/production-locations/_count"                      # compare with: SELECT count(*) FROM api_facility;
osq "/production-locations/_doc/<OS_ID>"                # one facility ("found": false = not indexed)

# Which of these OS IDs are in the index?
osq "/production-locations/_mget?_source=false&filter_path=docs._id,docs.found" \
  -d '{"ids":["<OS_ID_1>","<OS_ID_2>"]}'

# Search by name and/or country
osq "/production-locations/_search?filter_path=hits.total,hits.hits._source" -d '{
  "size": 10, "_source": ["os_id","name","address","country.alpha_2"],
  "query": {"bool": {"must": [{"match": {"name": "<name>"}}],
                     "filter": [{"term": {"country.alpha_2": "<CC>"}}]}}}'

# Export every OS ID in the index (needs jq)
osq "/production-locations/_search?scroll=2m&filter_path=_scroll_id,hits.hits._id" \
  -d '{"size":10000,"_source":false,"sort":["_doc"]}' > page.json
jq -r '.hits.hits[]?._id' page.json | tr -d '\r' > os_ids_in_index.txt
while jq -e '(.hits.hits // []) | length > 0' page.json >/dev/null; do
  osq "/_search/scroll?filter_path=_scroll_id,hits.hits._id" \
    -d "{\"scroll\":\"2m\",\"scroll_id\":\"$(jq -r ._scroll_id page.json)\"}" > page.json
  jq -r '.hits.hits[]?._id' page.json | tr -d '\r' >> os_ids_in_index.txt
done
wc -l os_ids_in_index.txt

bash deployment/ssm/ssm_tunnel.sh stop 9443             # when done
```

Locally (docker compose) use plain `curl localhost:9200/...` with the same paths.

## 3. Bump `updated_at` for facilities missing from the index

Connect to the database and load the exported IDs:

```sql
CREATE TEMP TABLE indexed_os_ids (id text PRIMARY KEY);
\copy indexed_os_ids FROM 'os_ids_in_index.txt'

-- Facilities in the DB but missing from OpenSearch
SELECT count(*) FROM api_facility af
LEFT JOIN indexed_os_ids i ON i.id = af.id
WHERE i.id IS NULL;

-- Touch them in batches; wait for a Logstash run between batches
UPDATE api_facility SET updated_at = now()
WHERE id IN (
  SELECT af.id FROM api_facility af
  LEFT JOIN indexed_os_ids i ON i.id = af.id
  WHERE i.id IS NULL
  LIMIT 10000
);
```

Notes:

- Batches keep each Logstash run small, so the task doesn't hit the same memory limit as the full load.
- Bumping `updated_at` changes that column for real. Check that nothing else depends on it before running this in Production.
- To touch specific facilities instead, use `UPDATE api_facility SET updated_at = now() WHERE id IN ('<OS_ID>', ...);`
- Documents in the index whose facility no longer exists in the DB are never removed by the pipeline. List them with `SELECT i.id FROM indexed_os_ids i LEFT JOIN api_facility af ON af.id = i.id WHERE af.id IS NULL;` and delete them with `osq "/production-locations/_doc/<OS_ID>" -X DELETE`.
- After the next run, re-check with `_count` or `_mget`.
