# OSDEV-2542 — [Spotlight] Add Partner Field Group & Data Partner filters to platform search

**Type**: User Story
**Status**: Planning
**Date**: 2026-05-12

---

## Ticket Overview

This ticket adds a new "Spotlight Data Partners" search filter to the Open Supply Hub platform (homepage and facilities page). The filter exposes a two-level hierarchy: partner field groups (Emissions, Certifications, Assessments, Grievance Mechanisms, Living Wage) at the top level, and individual data partners (e.g., Climate TRACE, WRAP, amfori) as nested options. Selecting a group alone returns any facility that has data from any partner in that group; selecting specific partners returns only facilities that have data from *all* of those partners (AC4–5). A checkbox to include shared-facility contributions is also required. The ticket also mandates an API/network audit on the homepage and facilities page to eliminate redundant or duplicate requests.

Filtering is implemented exclusively against the **`GET /api/facilities/`** endpoint using Django ORM queries. The `GET /api/v1/production-locations/` endpoint and OpenSearch/Logstash are out of scope for this ticket.

## Acceptance Criteria

- **AC1** — A new "Spotlight Data Partners" filter option is visible on the platform homepage/search interface.
- **AC2** — Opening the filter shows partner field groups (Emissions, Certifications, Assessments, Grievance Mechanisms, Living Wage) as first-level options.
- **AC3** — Selecting a group expands it to reveal individual data partners within that group (e.g., amfori, SLCP, Worldly, International Accord under Assessments).
- **AC4** — Selecting specific partners across one or more groups filters results to locations that have data from **all** selected partners.
- **AC5** — Selecting only a group (no individual partners chosen within it) returns locations with data from **any** partner in that group.
- **AC6** — New partners added to the database are automatically included in the filter without code changes.
- **AC7** — Page load time is not noticeably slower after the filter is added.
- **AC8** — All API/network requests on the homepage and facilities page are audited; duplicate, redundant, or unnecessary requests are removed without breaking search or filters.

---

## Affected Layers

| Layer | Changes Required | Notes |
|---|---|---|
| React frontend | Yes | New 2-level filter component; Redux state; `createQueryStringFromSearchFilters`; tile layers; network audit |
| Django backend | Yes | New query params on `GET /api/facilities/`; ORM-based filtering via `api_extendedfield`/`api_partnerfield`; enrich partner-field-groups API response |
| Dedupe Hub | No | Matching pipeline is independent of search/filter UI |
| Logstash / OpenSearch | No | Filtering targets `GET /api/facilities/` (PostgreSQL ORM); no index changes required |
| Kafka tools | No | Topic-bootstrap tooling only; no new topics required |
| Database | No | Groups and partner field links already exist in production DB; no migration needed |
| Batch | No | No batch jobs identified as relevant to spotlight search filters |
| Anon-tools | No | Generic PII anonymisation; no Spotlight table references |
| Deployment / Infra | No | No mandatory Terraform changes; CloudFront already has a cache behavior for the partner-field-groups path |

---

## Implementation Plan

### 1. Database — Not applicable

No changes required in the `Database` layer. The five `PartnerFieldGroup` rows (Emissions, Certifications, Assessments, Grievance Mechanisms, Living Wage) are already seeded in the production DB and all `PartnerField` rows are already linked to their respective groups. No data migration is needed.

---

### 2. Logstash / OpenSearch — Not applicable

No changes required in `Logstash / OpenSearch`. Filtering is implemented entirely via Django ORM against PostgreSQL. The `GET /api/v1/production-locations/` endpoint and its OpenSearch query builder are not modified.

---

### 3. Django backend — API enrichment and ORM-based filtering on `GET /api/facilities/`

**Background**: The `GET /api/facilities/` endpoint is served by `FacilitiesViewSet`. All queryset filtering is centralised in `FacilityIndexNewManager.filter_by_query_params` (`src/django/api/models/facility/facility_manager_index_new.py`), which operates on `FacilityIndex` rows.

There are **two distinct partner field types** that require different filter strategies:

**1. Regular (contributor-uploaded) partner fields** — stored in `api_extendedfield` and indexed into `FacilityIndex.extended_fields` (an `ArrayField(JSONField)`). Each element has a `field_name` key matching `PartnerField.name`. Filter: `extended_fields__contains=[{"field_name": "<name>"}]` (PostgreSQL `@>` containment).

**2. System partner fields** — computed dynamically from country/geo lookups by `SystemPartnerFieldProvider` subclasses in `src/django/api/partner_fields/`. They are **never written to `api_extendedfield`** and are **absent from `FacilityIndex.extended_fields`**. They require a different filter on `FacilityIndex` directly:

| System field | Provider | Source table | Filter on `FacilityIndex` |
|---|---|---|---|
| `wage_indicator` | `WageIndicatorProvider` | `WageIndicatorCountryData` (keyed by `country_code`) | `country_code__in=Subquery(WageIndicatorCountryData.objects.values('country_code'))` |
| `mit_living_wage` | `MITLivingWageProvider` | `USCountyTigerline` (geo lookup by lat/lng) | `country_code__in=['US', 'PR', 'VI']` — every facility in those territories with a location has a match |

The filter implementation must detect whether a selected `partner_field` name is a system field and route to the appropriate filter. The list of system field names is already enumerated in `SystemPartnerFieldRegistry` (`src/django/api/partner_fields/registry.py`).

#### 3a. Enrich the partner-field-groups API response

**Files to create / modify:**
- `src/django/api/serializers/partner_field_group/partner_field_group_serializer.py` — switch `partner_fields` from `SlugRelatedField(slug_field="name")` to a nested serializer exposing at least `name` (the query-string key), a display label, and `active`; ensure the nested queryset only includes active fields.
- `src/django/api/views/partner_field_groups/partner_field_groups_view_set.py` — fix `prefetch_related("partner_fields")` to use a `Prefetch` object with `PartnerField.objects.filter(active=True)` so inactive partners are not exposed.

**Steps:**
1. Update the serializer to return richer partner metadata (`name` + display label).
2. Fix the viewset prefetch.
3. Test via `GET /api/partner-field-groups/` in docker.

#### 3b. Add spotlight filter params to `GET /api/facilities/`

**Files to create / modify:**
- `src/django/api/constants.py` — add new constants to `FacilitiesQueryParams`, e.g. `PARTNER_FIELD_GROUP = 'partner_field_group'` and `PARTNER_FIELD = 'partner_field'`.
- `src/django/api/models/facility/facility_manager_index_new.py` — add spotlight filter logic at the end of `filter_by_query_params`, after the existing `sector` filter:
  - Read `partner_field_groups = params.getlist(FacilitiesQueryParams.PARTNER_FIELD_GROUP)` and `partner_fields = params.getlist(FacilitiesQueryParams.PARTNER_FIELD)`.
  - Define a helper `_spotlight_q(name)` that returns the correct `Q` object based on the field type:
    - `wage_indicator` → `Q(country_code__in=Subquery(WageIndicatorCountryData.objects.values('country_code')))`
    - `mit_living_wage` → `Q(country_code__in=['US', 'PR', 'VI'])`
    - all others → `Q(extended_fields__contains=[{"field_name": name}])`
  - **AC5 — group selected, no individual partners**: resolve all active `PartnerField.name` values for each selected group from DB (`PartnerField.objects.filter(group__slug=group_slug, active=True).values_list('name', flat=True)`), then apply an OR filter using `_spotlight_q` across all names in the group. Each selected group is an independent AND constraint (AND between groups, OR within a group).
  - **AC4 — specific partners selected**: for each selected `partner_field` name, chain a separate `.filter(_spotlight_q(name))` — chained `filter()` calls produce AND semantics at the SQL level.
  - **Mixed (group + individual partners)**: process group constraints first (OR within group), then AND individual partner constraints on top.
- `src/django/api/views/facility/facility_parameters.py` — add Swagger `openapi.Parameter` declarations for the two new query params.

**Steps:**
1. Add constants to `FacilitiesQueryParams`.
2. Implement `_spotlight_q(name)` helper in `facility_manager_index_new.py`; determine system fields by checking against the names registered in `SystemPartnerFieldRegistry` (or a simple hardcoded set `{"wage_indicator", "mit_living_wage"}` that is kept in sync with the registry).
3. Implement the full filter block in `filter_by_query_params` covering AC4, AC5, and mixed; write unit tests for each case including system-field-only, regular-field-only, and mixed groups.
4. Verify via `GET /api/facilities/?partner_field=wage_indicator` (should return US/PR/VI facilities) and `GET /api/facilities/?partner_field=climate_trace` in docker.
5. Confirm paginated counts are correct (filter runs entirely at DB level).

---

### 4. React frontend — UI, Redux, URL sync, network audit

**Background**: `src/react/src/actions/partnerFieldGroups.js` already defines `fetchPartnerFieldGroups` (calls `GET /api/partner-field-groups/?limit=100`) and the corresponding `PartnerFieldGroupsReducer` holds `{ fetching, data, error }`. Currently these are only used on production-location detail pages. The search filter pipeline flows through `createQueryStringFromSearchFilters` → `fetchFacilities` → `GET /api/facilities/`. A new two-level filter component must be wired into that pipeline on both the homepage and the facilities page. Partner group data is loaded **lazily** — fetched only when the filter dropdown is first opened by the user, not on page load.

#### 4a. New filter component

**Files to create / modify:**
- `src/react/src/components/Filters/SpotlightDataPartnersFilter.jsx` — **CREATE**: two-level tree; top-level group checkboxes that expand to show partner checkboxes; a "Show only shared facilities for this partner selection" checkbox (separate from the contributor `combine_contributors` checkbox).
- `src/react/src/components/FilterSidebarSearchTab.jsx` — **MODIFY**: render `<SpotlightDataPartnersFilter />` in the facilities search column.
- `src/react/src/components/HomepageSidebarSearch.jsx` — **MODIFY**: surface the filter on the homepage (placement decision: primary column vs "More Search Filters" drawer); extend `hiddenFields` / `allFields` / `checkIfAnyFieldSelected` if drawer placement is chosen.

#### 4b. Redux state

**Files to create / modify:**
- `src/react/src/reducers/FiltersReducer.js` — **MODIFY**: add `partnerFieldGroups: []`, `partnerFields: []`, `combineSpotlight: false` (or equivalent names) to `initialState`; add case handlers; extend `resetAllFilters` and `resetDrawerFilters`.
- `src/react/src/actions/filters.js` — **MODIFY**: add new `createAction`s for set/clear of the new filter fields; extend `setFiltersFromQueryString` and `createFiltersFromQueryString` with the new keys.
- `src/react/src/selectors/partnerFieldGroupsSelectors.js` — **MODIFY** or extend: add search-oriented selectors that format `state.partnerFieldGroups.data` into `{ value, label, children: [...] }` for the filter component.

#### 4c. Query-string and tile sync

**Files to create / modify:**
- `src/react/src/util/util.js` — **MODIFY**: extend `createQueryStringFromSearchFilters` to serialise the new filter fields; extend `createFiltersFromQueryString` to deserialise them (round-trip test required).
- `src/react/src/util/propTypes.js` — **MODIFY**: update `filtersPropType` to include the new filter keys if any wrapper relies on it.
- `src/react/src/components/VectorTileFacilityGridLayer.jsx` — **MODIFY**: include new spotlight QS keys in the tile URL so the map stays in sync.
- `src/react/src/components/VectorTileFacilitiesLayer.jsx` — **MODIFY**: same as above.
- `src/react/src/actions/downloadFacilities.js` — **REVIEW**: confirm download URL inherits the new filter params via `createQueryStringFromSearchFilters`; no change needed if it already delegates fully.

#### 4d. Lazy data loading for partner groups

Partner groups are fetched **on first open** of the dropdown, not on page load (AC7 — no impact on page load time).

**Files to create / modify:**
- `src/react/src/actions/partnerFieldGroups.js` — **MODIFY**: add a `fetchPartnerFieldGroupsIfNeeded` thunk that checks `state.partnerFieldGroups.data` and `state.partnerFieldGroups.fetching` before dispatching `fetchPartnerFieldGroups`. If data is already loaded or a fetch is in flight, the thunk is a no-op.

```js
export function fetchPartnerFieldGroupsIfNeeded() {
    return (dispatch, getState) => {
        const { data, fetching } = getState().partnerFieldGroups;
        if (data !== null || fetching) return;
        dispatch(fetchPartnerFieldGroups());
    };
}
```

- `src/react/src/components/Filters/SpotlightDataPartnersFilter.jsx` — dispatch `fetchPartnerFieldGroupsIfNeeded` in the dropdown's `onOpen` callback (or in a `useEffect` gated on an `isOpen` state flag).

**Steps (4a–4d):**
1. Add `fetchPartnerFieldGroupsIfNeeded` to `partnerFieldGroups.js`.
2. Build `SpotlightDataPartnersFilter.jsx` in isolation with mocked data; trigger `fetchPartnerFieldGroupsIfNeeded` on open; show a loading state while `fetching === true`.
3. Add Redux filter state and wire actions/selectors.
4. Extend `createQueryStringFromSearchFilters` + `createFiltersFromQueryString`; add round-trip unit tests in `src/react/src/__tests__/utils.tests.js`.
5. Mount the component in `FilterSidebarSearchTab` and `HomepageSidebarSearch`; verify against the enriched `/api/partner-field-groups/` response.
6. Wire tile layers to include the new params.
7. Run `yarn test --watchAll=false` in docker; fix any broken snapshot or unit tests.

---

### 5. React frontend — Network audit (AC8)

**Background**: `fetchAllPrimaryFilterOptions` in `src/react/src/actions/filterOptions.js` dispatches `fetchContributorOptions`, `fetchCountryOptions`, and `fetchListOptions`. Additional options (sectors, grouped sectors, parent companies, facility/processing types, number of workers, claim statuses) are fetched separately from other mount points. Both `FilterSidebar` and `HomepageSidebar` trigger these fetches on mount; the same API calls may fire on both pages or on re-mount without checking if data already exists in Redux.

**Files to audit and modify:**

- `src/react/src/actions/filterOptions.js` — **AUDIT**: identify all fetch functions that have no guard against already-loaded data. Add `IfNeeded` variants (following the same `fetchPartnerFieldGroupsIfNeeded` pattern) for any fetch that can fire more than once per session without new data being needed.
- `src/react/src/components/FilterSidebar.jsx` — **AUDIT**: identify all `dispatch(fetch...)` calls on `componentDidMount` / `useEffect`; confirm each is either gated or deduplicated.
- `src/react/src/components/HomepageSidebar.jsx` — **AUDIT**: same; confirm the homepage and facilities sidebar do not both fire the same requests independently on page load.
- `src/react/src/components/FilterSidebarSearchTab.jsx` — **AUDIT**: check for any option fetches that should only happen when a specific filter section is opened.
- `src/react/src/components/FilterSidebarExtendedSearch.jsx` — **AUDIT**: same.

**Concrete steps:**
1. Record all network requests fired on initial load of `/` (homepage) and `/facilities` using browser DevTools; document each request with its source component/action.
2. For each fetch that fires on mount unconditionally, check whether the Redux slice already has data (`data !== null && !error`); if so, add a guard (e.g., `fetchContributorOptionsIfNeeded`).
3. Ensure `fetchAllPrimaryFilterOptions` and all extended filter fetches respect existing Redux state so navigating between homepage and facilities page does not re-fetch already-loaded options.
4. Confirm that `fetchPartnerFieldGroupsIfNeeded` fires at most once per session and is a no-op on dropdown re-opens.
5. Re-record network requests after changes; confirm the set of requests on page load is unchanged or reduced.
6. Run `yarn test --watchAll=false` in docker; fix any broken tests.

---

## Open Questions

1. **System field coverage for `mit_living_wage`**: The filter `country_code__in=['US', 'PR', 'VI']` is a conservative proxy — it matches any US/PR/VI facility regardless of whether it actually falls inside a `USCountyTigerline` polygon. Confirm with product whether this approximation is acceptable, or whether the filter must perform the actual point-in-polygon check (which would require a subquery join against `USCountyTigerline` and cannot run cheaply against `FacilityIndex` without a spatial index or a precomputed flag).
2. **Combined boolean logic**: When a user selects both a whole group AND individual partners from another group, what is the exact AND/OR composition? (Proposed: each distinct group constraint is independent; within a group, choosing no individual partners → `__in` across all group members; choosing specific partners → chained `filter()` per partner to enforce AND.)
3. **`combine_spotlight` param naming and semantics**: The ticket says "check box to also select shared facilities for that partner criteria selection." Clarify whether this maps to the existing `combine_contributors=AND` mechanism or is a completely new boolean param; backend and frontend naming must align.
4. **`PartnerField.group` enforcement**: Should the `PartnerField.group` FK be non-nullable for Spotlight partners so the UI never shows ungrouped fields? Currently the FK is nullable (no DB-level constraint).
5. **Inactive partner fields on the groups endpoint**: `PartnerFieldGroupsViewSet` uses `prefetch_related("partner_fields")` without the `active` manager filter — inactive fields currently leak through. This should be fixed as part of the serializer work.
6. **Embed mode**: The `embed=1` filter UI partially hides the contributor filter. Confirm whether the new spotlight filter should also be hidden in embed mode.
7. **Homepage filter placement**: AC1 requires visibility on the homepage. Confirm whether the filter goes in the primary sidebar column (always visible) or the "More Search Filters" drawer (requires an extra click). This decision affects `resetDrawerFilters` behavior and `checkIfAnyFieldSelected` logic.
8. **ORM query performance**: The `extended_fields__contains=[{"field_name": name}]` lookup uses PostgreSQL's JSONB `@>` containment operator on an `ArrayField(JSONField)`. Chaining multiple such filters for AC4 (one per selected partner) each generates an independent `WHERE` clause. Confirm that a GIN index on `api_facilityindex.extended_fields` exists and is effective; add one if needed (`GinIndex(fields=["extended_fields"])`). Benchmark against production data volumes before shipping.

## Out of Scope

- **`/production-location/<os-id>` React page** — no changes to the production location detail page or any of its components (`ProductionLocationDetailsContainer`, `PartnerDataContainer`, `NavBar`, etc.).
- **`GET /api/v1/production-locations/` endpoint** — no changes; spotlight filtering is exclusively on `GET /api/facilities/`.
- **OpenSearch / Logstash** — no index changes, no SQL changes, no pipeline changes.
- Changes to the Dedupe Hub matching pipeline (no spotlight data flows through Kafka matching for this feature).
- Kafka topics or schema registry changes.
- Anon-tools changes (partner/spotlight data is non-PII).
- New Terraform resources (existing CloudFront path `api/partner-field-groups/*` already has a CDN cache behavior).
- Modifying the `DataSourceFilter.jsx` (moderation domain, unrelated to platform search).
- Batch job changes (no batch jobs identified as relevant).
- Implementing the spotlight data itself (this ticket only adds the _filter_ UI; the data ingestion pipelines for Climate TRACE, WRAP, etc. are separate concerns).

## References

- Jira: [OSDEV-2542](https://opensupplyhub.atlassian.net/browse/OSDEV-2542)
- Design: Not linked in ticket (confirm with PM/design team if Figma spec exists)
- Related models: `src/django/api/models/partner_field_group.py`, `src/django/api/models/partner_field.py`, `src/django/api/models/contributor/contributor.py` (`Contributor.partner_fields` M2M)
- `FacilityIndex` model: `src/django/api/models/facility/facility_index.py` (`extended_fields` ArrayField)
- Facility queryset filter: `src/django/api/models/facility/facility_manager_index_new.py` (`filter_by_query_params`)
- System partner field providers: `src/django/api/partner_fields/` (`registry.py`, `base_provider.py`, `wage_indicator_provider.py`, `mit_living_wage_provider.py`)
- System field source tables: `src/django/api/models/wage_indicator_country_data.py`, `src/django/api/models/us_county_tigerline.py`
- Existing partner-field-groups API: `GET /api/partner-field-groups/` (registered in `src/django/oar/urls.py`)
- Existing Redux action: `src/react/src/actions/partnerFieldGroups.js`
- Existing Redux reducer: `src/react/src/reducers/PartnerFieldGroupsReducer.js`
- Filter options actions: `src/react/src/actions/filterOptions.js`
