# Earth Genome Phase 1 — QA runbook (OSDEV-3250)

A one-hour checklist for the staging / Development run of the Earth Genome
candidate pipeline (epic OSDEV-2566). It walks the same path the automated
end-to-end module `src/django/api/tests/test_candidate_lifecycle_e2e.py`
walks, against a deployed environment with a real browser, OpenSearch and
logstash. Tick every box; anything unticked is a release blocker or an
explicit, written waiver.

Design references (locked): `option3-implementation-plan.md` and
`option3-design-decisions.md` in this folder (D1 empty-string sentinel,
D2 synthetic Source / item / match, D3 hard delete + tombstone, D5 re-ingest
suppression, D6 derived states).

---

## 0. Branch state and merge order

The `eg-phase1-integration` branch is a staging construct: every ticket
merges to `main` through its own draft PR, in this order (from
`~/Code/eg-tools/STATUS.md`):

| Step | Ticket | PR | Why this position |
|---|---|---|---|
| 1 | OSDEV-3380 default manager | #1308 | parent of the stack; `Facility.objects` hides candidates |
| 2 | OSDEV-3243 out-of-ORM exclusion | #1326 | migration `0246_exclude_candidates_from_facility_index`, logstash `NOT af.is_candidate`, dedupe-hub exclusion |
| 3 | OSDEV-3246 tombstone | #1327 | its migration was authored as `0246`; **renumber to `0247_facility_alias_tombstone` depending on `0246_exclude_candidates_from_facility_index`** before merging (the integration branch already carries this renumber) |
| 4 | OSDEV-3379 admin, OSDEV-3377 reports, OSDEV-3248 guard, OSDEV-3378 index surfaces, OSDEV-3376 audit | #1322, #1323, #1324, #1325, #1328 | any order; independent of each other |
| 5 | OSDEV-3244 ingest | #1329 | needs 3248 (guard setting) and 3246 (`is_retired_detection`) |
| 6 | OSDEV-3245 votes | #1330 | migration `0248_facility_candidate_vote` depends on `0247` |
| 7 | OSDEV-3249 candidate detail API | #1331 | needs 3245 |
| 8 | OSDEV-3247 React panel | #1332 | needs 3249 |
| 9 | OSDEV-3250 QA (this) | — | tests + this runbook |

- [ ] Every PR merged in that order; `src/django/api/migrations` has exactly
  one leaf (`python manage.py makemigrations --check --dry-run api` reports
  only the pre-existing drift, nothing for `api_facility*` models).
- [ ] `doc/release/RELEASE-NOTES.md` on `main` carries the bullets of every
  PR above. Known gap: the integration branch dropped the release-notes
  bullets of OSDEV-3243, 3244, 3246, 3248 and 3377 (and the `0246` / `0247`
  migration entries) while resolving merge conflicts. The per-PR merges
  restore them; do not merge the integration branch wholesale.

## 1. Prerequisites (10 min)

- [ ] Deploy the release; `migrate` ran in `post_deployment` and applied
  `0246_exclude_candidates_from_facility_index`,
  `0247_facility_alias_tombstone`, `0248_facility_candidate_vote`:

  ```sql
  SELECT name FROM django_migrations
  WHERE app = 'api' AND name LIKE '024[678]%' ORDER BY name;
  ```

- [ ] Create the Earth Genome contributor once per environment (Django admin:
  Users → add a service account such as `earth-genome@<env>`; Contributors →
  add, name **Earth Genome**, type Other, admin = that user), then note its
  `api_contributor.id`:

  ```sql
  SELECT id FROM api_contributor WHERE name = 'Earth Genome';
  ```

- [ ] Set `EARTH_GENOME_CONTRIBUTOR_ID=<that id>` on the Django service
  (OSDEV-3248). Deployed environments: Terraform variable
  `earth_genome_contributor_id` in `deployment/environments/terraform-<env>.tfvars`
  → `deployment/terraform/task-definitions/app.json`; apply, then redeploy
  the app and CLI tasks. Local: `.env` / `docker-compose.yml`. Unset means
  nobody may create candidates and the ingest command refuses to start.

  ```bash
  python manage.py shell -c "from django.conf import settings; print(settings.EARTH_GENOME_CONTRIBUTOR_ID)"
  ```

- [ ] Thresholds (OSDEV-3245) left at the pilot defaults unless Product
  decided otherwise: `CANDIDATE_VOTE_THRESHOLD=3`,
  `CANDIDATE_CONFIRM_MARGIN=0.6`, `CANDIDATE_RETIRE_MARGIN=0.75`,
  `CANDIDATE_AUTO_RETIRE` **unset** (moderator-gated retirement). Proximity
  suggestions: `CANDIDATE_SUGGESTION_RADIUS_M=500`,
  `CANDIDATE_SUGGESTION_LIMIT=5` (OSDEV-3244). All are read from the
  environment at start-up.
- [ ] `vector_tile` waffle switch is on (the map draws from tiles).
- [ ] You have: a superuser login (moderator approvals), two or three
  ordinary confirmed accounts (voters), and an API token for one of them.

## 2. Ingest (10 min)

Input files (not committed; they live in the Phase 1 prototype folder /
Earth Genome delivery). The command accepts two shapes:

| File | Shape | Rows | Use |
|---|---|---|---|
| `nc_candidates.json` | prototype JSON list (`eg_id`, `polygon`, `centroid_*`, `confidence_score`) | 3,911 NC detections | **recommended staging file**; supports point-only rows |
| `al_candidates.json` | same | 2,839 AL detections | second state, same source |
| `SouthernStatesCombined_rectpolys_MLP64-16poultry.geojson` | Earth Genome GeoJSON FeatureCollection (`properties.id`, `properties.confidence`) | 16,372 | the full delivery; **2 null geometries (skipped) and 1 invalid ring (`AL674`) → `errors=1` and a non-zero exit, expected**; the other 16,369 rows are written |

`osh_nc.geojson` / `nc_all.geojson` / `us_animal_production_sector.geojson`
are exports of existing OS Hub facilities (Point features) used by the
prototype map; they are **not** ingest inputs (a Point geometry is rejected
as "geometry must be a Polygon").

- [ ] Copy the file into the container / CLI task and dry-run first:

  ```bash
  python manage.py ingest_satellite_detections --file /usr/local/src/nc_candidates.json --country-code US --dry-run --limit 50
  ```

  Expect `Dry run: ingesting 50 record(s) ... Done: created=50 updated=0 ...`
  and a `CREATE <eg_id> -> (new OS ID) confidence=... suggestions=N` line per
  row (proximity suggestions list nearby confirmed facilities).

- [ ] Real run (deployed environments: the same `manage.py` command the way
  other one-off commands such as `backfill_facility_index` are run,
  `deployment/run_cli_task <Env> "python manage.py ingest_satellite_detections --file ..."`):

  ```bash
  python manage.py ingest_satellite_detections --file /usr/local/src/nc_candidates.json --country-code US
  ```

  Record the summary line: `created=N updated=0 skipped_retired=0
  skipped_no_geometry=K errors=0`.

- [ ] Database shape (D1 / D2):

  ```sql
  -- candidates exist, nameless, with OS IDs and polygons
  SELECT count(*) FILTER (WHERE polygon IS NOT NULL) AS with_polygon,
         count(*) FILTER (WHERE polygon IS NULL)     AS point_only,
         count(*) FILTER (WHERE name <> '' OR address <> '') AS named
  FROM api_facility WHERE is_candidate AND source = 'earth_genome';
  -- one synthetic SINGLE source + MATCHED item + AUTOMATIC match per candidate
  SELECT count(*) FROM api_facilitylistitem fli
    JOIN api_facility f ON f.created_from_id = fli.id
    JOIN api_source s ON s.id = fli.source_id
   WHERE f.is_candidate AND fli.status = 'MATCHED' AND s.source_type = 'SINGLE'
     AND s.contributor_id = <EARTH_GENOME_CONTRIBUTOR_ID>;
  -- never in the search index (0246 trigger)
  SELECT count(*) FROM api_facilityindex i
    JOIN api_facility f ON f.id = i.id WHERE f.is_candidate;   -- 0
  ```

- [ ] Re-run the same command once more now: `created=0 updated=N`, same
  OS IDs (`SELECT external_id, id FROM api_facility WHERE is_candidate`
  before and after), `api_source` / `api_facilitylistitem` /
  `api_facilitymatch` counts unchanged.

## 3. Confirmed surfaces do not change (5 min)

Pick one candidate OS ID (`CAND`) and one confirmed facility OS ID (`CONF`)
in the same area.

- [ ] `GET /api/facilities/?q=CAND` → `features: []`; `?q=CONF` → one feature.
- [ ] `GET /api/facilities/count/` equals `SELECT count(*) FROM api_facility WHERE NOT is_candidate`.
- [ ] `GET /api/facilities-downloads/?q=CAND` (logged in) → `count: 0`;
  a full page of the download has no row whose `os_id` is a candidate.
- [ ] Main map: no candidate pin/polygon at the detection sites; search
  results list has no nameless entries.
- [ ] `GET /api/v1/production-locations/?size=10&country=US` (OpenSearch) →
  no candidate OS IDs (`SELECT ... WHERE is_candidate` to cross-check a few).
- [ ] Django admin → Facilities: default filter shows confirmed only;
  candidates are view-only (OSDEV-3379).
- [ ] Reports (`/admin` → Reports, OSDEV-3377): facility totals exclude
  candidates.

## 4. Candidate detail, map and votes in the UI (15 min)

- [ ] `GET /api/facilities/CAND/` → 200, `properties.is_candidate: true`,
  `properties.candidate.state: "unverified"`, `properties.name: ""`;
  response headers carry `X-Robots-Tag: noindex` and
  `Cache-Control: private`.
- [ ] `GET /api/v1/production-locations/CAND/` → 200 with `is_candidate`,
  `source`, `external_id`, `confidence`, `polygon`, `validation`,
  `suggested_matches`.
- [ ] `GET /api/v1/production-locations/candidates/?bbox=<minLng,minLat,maxLng,maxLat>`
  around the site (≤ 2° a side) → FeatureCollection with Polygon (or Point
  for point-only) features, `properties.state`, `tally`, `centroid`.
- [ ] Browser, logged out: open `/facilities/CAND`. Expect the
  "Satellite-detected candidate" badge and placeholder title (name is empty
  by design), the detection polygon drawn on the detail map (dashed amber
  outline = unverified), the confidence / source provenance, the proximity
  suggestions, and the validation panel showing the tally with a login
  prompt instead of vote buttons.
- [ ] Browser, logged in as voter 1: the panel offers **Confirm** and
  **Not a facility**; vote Not a facility → tally updates, state still
  unverified (below threshold). Change your vote → tally moves, still one
  vote per account.
- [ ] Voter 2 votes Not a facility, voter 3 votes Confirm → state
  **disputed** (1–2 at the threshold), the disputed label/outline shows on
  the detail page and in the bbox layer, voting stays open (D6).
- [ ] Two more Confirm votes (3–2) → **confirmed**: panel shows the
  confirmed copy and no vote buttons; `POST .../candidate-votes/` from any
  account → **409**; the row stays `is_candidate = true` (confirmed is a
  derived state) and remains off the confirmed surfaces of section 3.

## 5. Retirement by consensus-no and moderator approval (10 min)

Use a second candidate `CAND2`.

- [ ] Three accounts vote Not a facility → `state: "retirement_pending"`;
  the OS ID still resolves (200) and a request row exists:

  ```sql
  SELECT id, facility_id, tally FROM api_facilitycandidateretirementrequest;
  ```

- [ ] As superuser: `GET /api/v1/candidate-retirement-requests/` lists it;
  `POST /api/v1/candidate-retirement-requests/<id>/approve/` → 200,
  `state: "retired"`.
- [ ] Both detail endpoints now answer **410 Gone** with
  `{"detail": "This OS ID was retired: ...", "os_id": CAND2, "retired_at": ...}`;
  `GET .../CAND2/candidate-votes/` → 410; the browser page shows the retired
  copy.
- [ ] Database (D3): the row and its synthetic graph are gone, the tombstone
  remains:

  ```sql
  SELECT os_id, reason, facility_id, retired_source, retired_external_id, retirement_tally
    FROM api_facilityalias WHERE os_id = 'CAND2';            -- 1 row, NOT_A_FACILITY, facility_id NULL
  SELECT count(*) FROM api_facility WHERE id = 'CAND2';       -- 0
  SELECT count(*) FROM api_facilityindex WHERE id = 'CAND2';  -- 0
  SELECT count(*) FROM api_facilitycandidatevote WHERE facility_id = 'CAND2';            -- 0
  SELECT count(*) FROM api_facilitycandidateretirementrequest WHERE facility_id = 'CAND2'; -- 0
  -- the synthetic source / item / match (note their ids before approving)
  SELECT count(*) FROM api_facilitylistitem WHERE id = <item id>;   -- 0
  SELECT count(*) FROM api_facilitymatch WHERE facility_list_item_id = <item id>; -- 0
  SELECT count(*) FROM api_source WHERE id = <source id>;           -- 0
  ```

- [ ] OpenSearch: `GET <opensearch>/production-locations/_doc/CAND2` → 404
  (a candidate never has a document); the Django log shows
  `Candidate CAND2 had no OpenSearch document; nothing to remove.` and no
  "data inconsistency" error notification was sent.
- [ ] Optional, if Product enabled it in this environment:
  `CANDIDATE_AUTO_RETIRE=True` makes the third Not-a-facility vote retire on
  the spot (`state: "retired"` in the vote response, immediate 410). Leave
  it off for the pilot otherwise.

## 6. Re-ingest suppression (5 min)

- [ ] Run the ingest command a third time with the same file. Expect
  `created=0 updated=N-1 skipped_retired=1`; `CAND2`'s `external_id` has no
  `api_facility` row, the tombstone is still there, the other OS IDs are
  unchanged and the confirmed candidate's votes are intact.

## 7. Index / OpenSearch / dedupe-hub hygiene (5 min)

- [ ] `SELECT count(*) FROM api_facilityindex i JOIN api_facility f ON f.id = i.id WHERE f.is_candidate;` → 0.
- [ ] Logstash: `src/logstash/sql/sync_production_locations.sql` contains
  `AND NOT af.is_candidate` in its driving `WHERE`; after a sync cycle,
  `GET <opensearch>/production-locations/_count` equals the confirmed count,
  and `_doc/CAND` is 404.
- [ ] Dedupe Hub: upload a one-row list whose address sits inside a
  candidate polygon → the item matches a confirmed facility or becomes a
  new facility, never a candidate (`SELECT facility_id FROM
  api_facilitymatch WHERE facility_id IN (SELECT id FROM api_facility WHERE
  is_candidate)` stays 0 apart from the synthetic rows whose
  `results->>'match_type' = 'satellite_detection_candidate'`). Unit coverage:
  `src/dedupe-hub/api/tests/test_candidate_exclusion.py` (15 tests; run with
  `python -m unittest tests.test_candidate_exclusion` inside the dedupe-hub
  image with the compose environment).
- [ ] Vector tiles: the `facilities` layer is built from `Facility.objects`
  and the `facilitygrid` layer from `api_facilityindex`; a tile over a
  detection-only area is empty.

## 8. Rollback notes

Reverse order of application; each is reversible, with these caveats:

| Migration | `migrate api <previous>` | Effect of reversing |
|---|---|---|
| `0248_facility_candidate_vote` | `0247_facility_alias_tombstone` | drops `api_facilitycandidatevote` and `api_facilitycandidateretirementrequest`; **all votes and open requests are lost** (tombstones keep final tallies of already-retired candidates) |
| `0247_facility_alias_tombstone` | `0246_exclude_candidates_from_facility_index` | restores `facility_id NOT NULL` on `api_facilityalias`: **fails if any NOT_A_FACILITY tombstone exists** — delete the tombstone rows first (`DELETE FROM api_facilityalias WHERE reason = 'NOT_A_FACILITY'`), which also re-enables re-ingest of those detections |
| `0246_exclude_candidates_from_facility_index` | `0245_add_claim_quality_check_switch` | restores the previous `index_facilities_by` / `index_facilities` procedures; existing candidates get `api_facilityindex` rows on their next update. Only safe together with the Django guard (`FacilityIndex.objects.without_candidates()`, OSDEV-3378) still deployed |

Code rollback to a build without the default-manager exclusion (pre
OSDEV-3380) would expose candidates as nameless facilities. Remove them
first, in one transaction, in the retirement order (matches → items →
facilities → sources), or re-run the ingest later to recreate them:

```sql
BEGIN;
DELETE FROM api_facilitymatch WHERE facility_id IN (SELECT id FROM api_facility WHERE is_candidate);
UPDATE api_facilitylistitem SET facility_id = NULL WHERE facility_id IN (SELECT id FROM api_facility WHERE is_candidate);
DELETE FROM api_facility WHERE is_candidate;
DELETE FROM api_facilitylistitem fli WHERE fli.id IN (
  SELECT fli2.id FROM api_facilitylistitem fli2 JOIN api_source s ON s.id = fli2.source_id
  WHERE s.source_type = 'SINGLE' AND s.contributor_id = <EARTH_GENOME_CONTRIBUTOR_ID> AND fli2.facility_id IS NULL);
DELETE FROM api_source s WHERE s.contributor_id = <EARTH_GENOME_CONTRIBUTOR_ID>
  AND NOT EXISTS (SELECT 1 FROM api_facilitylistitem WHERE source_id = s.id);
COMMIT;
```

The `0237` candidate columns (release 2.30.0) stay; they are additive and
unused without candidate rows. Unsetting `EARTH_GENOME_CONTRIBUTOR_ID`
alone stops any further candidate creation without touching data.

## 9. Sign-off

- [ ] Sections 1–7 all ticked, or each gap written up with the owner.
- [ ] Summary lines from the three ingest runs pasted into the ticket.
- [ ] Full Django suite (`./api/tests`) and React suite green on the
  release branch apart from the documented flakes
  (`test_successfully_geocoded_item_has_correct_results`, live geocoder;
  three timezone-dependent claim-date React tests when run outside UTC).
