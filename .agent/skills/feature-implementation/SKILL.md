---
name: feature-implementation
description: >-
  Implement a feature end-to-end in Open Supply Hub from a Jira ticket: fetch
  the issue, create a git branch, analyse scope, then write code for the
  React frontend and/or Django backend. Use when the user provides a Jira
  ticket key (e.g. OSDEV-XXXX) and asks to start, implement, or work on a
  feature or task.
---

# Feature Implementation

## Step 1 — Fetch the Jira ticket

1. Call `getAccessibleAtlassianResources` (no args) and capture the `id` for the opensupplyhub cloud.
2. Call `getJiraIssue` with `cloudId` and the ticket key (e.g. `OSDEV-2470`).
3. Note: **summary**, **description**, **acceptance criteria**, and any linked designs.

## Step 2 — Create the branch

Follow the [github-branch-creation](.cursor/rules/github-branch-creation.mdc) rule:

- Derive the branch name from the issue summary (kebab-case, prefixed with the ticket key).
- Ask the user which parent branch to use if not obvious (`develop` is the default).
- Push the branch with `git push -u origin <branch-name>`.

## Step 3 — Analyse scope

Read the ticket and decide which layers are touched:

| Signal in ticket | Likely work |
|---|---|
| UI / design / component / page | Frontend (React) |
| API / endpoint / serializer / model / migration | Backend (Django) |
| Matching / deduplication / Kafka | Dedupe Hub |
| Search index / OpenSearch field / pipeline filter | Logstash (OpenSearch) |
| Multiple signals | Full-stack — see ordering in Step 4 |

When unsure, ask the user before writing code.

## Step 4 — Implement

### Frontend (React)

Follow the [react-component skill](.agent/skills/react-component/SKILL.md) for all component work:

- PascalCase folder per component, files: `ComponentName.jsx`, `styles.js`, optional `constants.js / utils.js / hooks.js`.
- Arrow-function components, `withStyles` (MUI v3), `PropTypes` inline, no `index.js` barrel files.
- Redux: `connect` + `mapStateToProps` / `mapDispatchToProps` in the same file.
- Reference implementation: `src/react/src/components/ProductionLocation/`.

Additional FE patterns:
- Actions → `src/react/src/actions/`
- Reducers → `src/react/src/reducers/`
- Selectors → `src/react/src/selectors/`
- Route constants → `src/react/src/util/constants.js`
- Routing: `react-router-dom` (`withRouter`, `<Route>`, `<Link>`)

### Backend (Django)

Reference area: `src/django/api/`

- **Models**: add/modify in `src/django/api/models/`; create a migration with `python manage.py makemigrations`.
- **Serializers**: `src/django/api/serializers/`; use DRF `ModelSerializer` or plain `Serializer`.
- **Views / ViewSets**: `src/django/api/views/`; register in `src/django/api/urls.py`.
- **Permissions & feature flags**: use `waffle` switches/flags where the ticket calls for gated rollout.
- Run `docker compose exec django python manage.py check` to validate before committing.

### Dedupe Hub

Reference area: `src/dedupe-hub/api/app/`

- **FastAPI service** (`main.py`) — consumes and produces Kafka messages via `aiokafka`.
- **Matching logic**: `matching/` — `facilities_matcher.py` orchestrates; `matcher/` holds the gazetteer/exact/cumulative strategies.
- **Data layer**: `database/` — SQLAlchemy models and `signals/` for event-driven side-effects.
- **DTOs**: `matching/DTOs/` — plain dataclasses; add new fields here when the matching contract changes.
- **Config**: `app/config.py` (Pydantic `Settings`); new env vars go here and in the relevant `docker-compose` service.
- When adding a new matching strategy, follow the existing pattern in `matcher/` and register it in `facilities_matcher.py`.
- Run tests: `docker compose exec dedupe-hub python -m pytest src/dedupe-hub/api/tests/`.

### Logstash (OpenSearch)

Reference area: `src/logstash/`

- **Pipelines**: `pipeline/*.conf` — one pipeline per index (`sync_production_locations.conf`, `sync_moderation_events.conf`).
  - `input`: JDBC query, polling schedule, tracking column.
  - `filter`: JSON parse raw columns → Ruby scripts transform → `mutate` to clean up temp fields.
  - `output`: OpenSearch plugin with index name, document ID, and template reference.
- **Index templates**: `indexes/*.json` — define OpenSearch mappings. When adding a new field to the index, update the template JSON here.
- **Ruby scripts**: `scripts/<index>/` — one `.rb` file per field transformation; keep each script focused on a single field.
- **SQL queries**: `sql/` — the JDBC `statement_filepath` points here; update the query when adding a new column to sync.
- Adding a new indexed field end-to-end:
  1. Add the column to the SQL query (`sql/`).
  2. Add a Ruby transform script (`scripts/<index>/new_field.rb`).
  3. Reference the script in the pipeline `.conf` filter block.
  4. Add the field mapping to the index template JSON (`indexes/`).
  5. Add any intermediate column names to the `mutate { remove_field [...] }` block.

### Full-stack order

When touching multiple layers, implement in this order:
1. DB migration (if schema changes needed)
2. Django serializer + view + URL
3. Dedupe Hub DTOs / matching logic (if matching contract changes)
4. Logstash SQL + Ruby scripts + index template (if search index changes)
5. React action/reducer/selector
6. Component(s)

## Step 5 — Verify

```bash
# Frontend
docker compose exec react yarn lint

# Django
docker compose exec django python manage.py check
docker compose exec django python manage.py test api.tests.<relevant_module>

# Dedupe Hub
docker compose exec dedupe-hub python -m pytest src/dedupe-hub/api/tests/

# Logstash — no automated tests; verify pipeline syntax with:
docker compose exec logstash bin/logstash --config.test_and_exit -f /usr/share/logstash/pipeline/<pipeline>.conf
```

Fix any lint or type errors before presenting the work.

## Step 6 — Wrap up

Once implementation is complete, remind the user to:
- Write tests using the [test-writer skill](.agent/skills/test-writer/SKILL.md).
- Update release notes using the [release-notes skill](.agent/skills/release-notes/SKILL.md).
- Write a PR description using the [pr-description skill](.agent/skills/pr-description/SKILL.md).
