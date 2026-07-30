# How a facility's displayed sectors are chosen (and kept in sync with search)

This documents the selection rules behind the **sector** field on a location
profile and the searchable sector index, as of OSDEV-992 (2.28.0). If you
change any rule here, read the [Coupling](#coupling-display--search) section
first.

## Where sector data comes from

A facility accumulates sector values from two kinds of contributions:

1. **List items** (`api_facilitylistitem.sector`) — every list upload, API
   submission, or SLC contribution carries a sector array. A facility
   typically has many items, from many contributors, submitted over years.
2. **Approved claims** (`api_facilityclaim.sector`) — the claimant's own
   statement about the facility.

The profile does **not** show the union of all of this. It shows a curated
subset, selected as follows.

## Display rules (profile sector field)

Implemented in `get_sector` on `FacilityIndexDetailsSerializer`
(`src/django/api/serializers/facility/facility_index_serializer.py`) over the
pre-aggregated `FacilityIndex.item_sectors` / `claim_sectors` JSON columns
(`src/django/sqls/0120_index_item_sectors.sql`,
`0130_index_claim_sectors.sql`), with the selection logic in
`regroup_items_for_sector_field` / `regroup_claims_for_sector_field` and
`format_sectors` (`src/django/api/serializers/facility/utils.py`).

1. **Candidate items** — all of the facility's list items with status
   `MATCHED` or `CONFIRMED_MATCH` (one candidate row per item × facility
   match, because `index_item_sectors()` joins matches).
2. **One item per contributor** — candidates are grouped by contributor and
   only the first item of each group is displayed, ordered by:
   1. items from **active sources** first (`source.is_active`);
   2. then by facility-match activity — currently items whose match is
      **inactive** sort first (`facilitymatch.is_active` ascending, with no
      negation, unlike the source key). This is suspected to be an accident
      and is tracked as [OSDEV-3144](https://opensupplyhub.atlassian.net/browse/OSDEV-3144);
   3. then **most recent first**, by `updated_at` — or by `created_at` when
      the request carries `created_at_of_data_points=true`. Note the two
      orderings can pick *different* items for the same contributor.
3. **Claims win placement** — the latest approved claim per contributor is
   listed before all item-based entries.
4. **Anonymization hides the name, not the values** — when the viewer cannot
   see details, or the item's source is inactive/non-public, or the item has
   no active complete match, the *contributor* is anonymized but the sector
   values are still displayed.
5. **"Unspecified" is depromoted** — entries whose only value is
   `Unspecified` sort to the end.
6. **Embed mode** — entries are additionally filtered to the embedding
   contributor.

Practical consequence of rule 2: when a contributor re-submits a facility,
their newest item's sector array **replaces** their older one on the profile
(the old value remains visible only in the contribution history). Across
contributors, sectors are a union — one contributor's upload never hides
another's.

## Search rules (sector filter)

`GET /api/facilities/?sectors=...` filters `FacilityIndex.sector`
(`sector__overlap`, `src/django/api/models/facility/facility_manager_index_new.py`).
That column is populated by the SQL function `index_sector()`
(`src/django/sqls/0221_index_sector.sql`), which replicates rules 1–3 above:
per contributor, the sectors of the single displayed item, plus the latest
approved claim's sectors per contributor.

Deliberate limits of the replication:

- The index mirrors the **default** ordering (`updated_at`). The
  `created_at_of_data_points=true` display variant cannot be represented in
  the same indexed column.
- The `facilitymatch.is_active` quirk (rule 2.ii) is mirrored **bug-for-bug**
  so search always matches what the profile actually shows.

## Coupling: display ↔ search

`index_sector()` is a hand-maintained SQL copy of the Python display logic.
There is no shared implementation, so **any change to the display rules must
change `index_sector()` in the same PR**, followed by a targeted reindex of
existing rows (`backfill_facility_index --fields sector` — the field group is
registered in `src/django/api/facility_index_backfill/specs.py`). Otherwise
search and profile drift apart again, which is exactly the bug OSDEV-992
fixed (superseded sectors like "Toys" staying searchable for facilities whose
profiles no longer showed them).

History: OSDEV-1034 fixed the same class of display-vs-search mismatch for
the processing type filter; OSDEV-1094 is the umbrella for the remaining
filter-alignment work; OSDEV-3144 tracks the display quirks noted above.

Note: this covers the legacy `/api/facilities/` path only. The v1
(`/api/v1/production-locations/`) OpenSearch index builds its sector data
separately via Logstash (`src/logstash/`) and is not covered by these rules.
