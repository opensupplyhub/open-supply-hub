# PR #907 – Description (paste into GitHub)

Copy the markdown below into the PR description at https://github.com/opensupplyhub/open-supply-hub/pull/907 (Edit → replace or paste into the description field → Save).

---

## Summary

[Jira: OSDEV-2367](https://opensupplyhub.atlassian.net/browse/OSDEV-2367)

Implements the **Supply Chain Network** section in the Production Location page sidebar and refactors it for maintainability and clearer data flow.

## What's new (user-facing)

- **Supply Chain Network section** in the sidebar:
  - Breakdown of contributing organizations by type with counts (e.g. "3 Brands", "1 Auditor") using pluralized type labels.
  - Public contributors listed as named links (to contributor profiles) sorted by contributor type.
  - **"View all N data sources"** button that opens a slide-out drawer.
- **All Data Sources drawer** (slide-out from the right):
  - Subtitle with total count (e.g. "4 organizations have shared data about this production location").
  - Info box explaining the open data model with a **"Learn more"** link.
  - Type summary chips (same counts as in the section).
  - Public contributor cards: name (link to profile), type, and uploaded list names where available.
  - **Anonymized Data Sources** section grouping non-public contributors by type and count.
- Section is hidden when there are no contributors.

## Code changes and refactors

- **Data flow:** Contributors are read from Redux (`facilities.singleFacility.data.properties.contributors`). `SupplyChain` is connected via `connect(mapStateToProps)`; no prop drilling from `ProductionLocationDetailsContainer`.
- **Drawer structure:** `SupplyChainNetworkDrawer` is split into section components, each with its own folder, styles, and constants:
  - `DrawerHeader` – title, icon, close button
  - `DrawerSubtitle` – total count text
  - `InfoBoxSection` – info box and "Learn more" link
  - `TypeSummarySection` – type chips
  - `PublicContributorsSection` – list of public contributors with links and list names
  - `AnonymizedSection` – anonymized data sources block
- **SupplyChain:** Logic moved into `utils.js` (`buildTypeCounts`, `aggregateByType`, `getTotalCount`, `pluralizeContributorType`), `constants.js` (`PLURAL_MAP`), and `hooks.js` (`useDrawerOpen`, `useDerivedContributors`). Derived contributor data is memoized via `useDerivedContributors(contributors)`.
- **Tests:** `SupplyChainNetwork.test.jsx` updated to provide contributors through Redux `preloadedState` instead of props.
- **Release notes:** Entry added for **Release 2.20.0** → **What's new** in `doc/release/RELEASE-NOTES.md`.

## Dependencies

- **OSDEV-2355** (merged): `contributor_type` and `count` on `api/facilities/{os_id}/` response.
- Drawer styling aligned with the reusable ContributionsDrawer pattern (OSDEV-2370).

## Risk

**Medium.** New contributor aggregation/sorting and drawer UI; moderate risk of UI regressions or incorrect counts/grouping. Covered by unit tests for render conditions, contributor display, drawer open/close, and anonymized section.
