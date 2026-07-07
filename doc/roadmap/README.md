# OS Hub Working Product Roadmap — Handoff

A live-from-Jira product roadmap that powers the weekly product execution meeting. Currently in **Draft 2.6**.

---

## Live URL

**https://tylerheath1.github.io/reports/2026-roadmaps/draft-2.6-roadmap.html**

## Files in this folder

- `draft-2.6-roadmap.html` — the full source. Self-contained HTML + CSS + JS, no build step. Open it directly in a browser.
- `README.md` — this doc.

## Repo location

The page is hosted from **GitHub Pages** at the repo `TylerHeath1/reports`:
- Path: `2026-roadmaps/draft-2.6-roadmap.html`
- Pages config: `main` branch, `/` root, public.
- The "production" version lives at `2026-roadmaps/os-hub-roadmap.html` (older, hand-coded). Don't edit that one yet — work in `draft-2.6-roadmap.html` until we promote.

---

## What this artifact is — and what it isn't

**It is** a static HTML page that displays a snapshot of Jira data for the OS Hub product roadmap. It's organized:

- **Top-level rows = Initiatives** (renamed from "user stories" — Jira issue type `Initiative`, hierarchy level 2)
- Click an Initiative → its **Epics** expand inline below, on a mini-timeline
- Click an Epic → its **Product Execution Update** reveals as a sticky-note card

**It isn't** a live web app. There is **no backend**. Jira data is fetched manually, baked into the HTML's `initiatives` array, and committed to git. The page itself doesn't call Jira at runtime (CORS + auth would make that messy from a static page).

The model going forward: **source of truth = Jira**. This page is a read-only display layer. To change what shows up, owners edit the relevant Jira field on the Epic; the page picks it up on the next refresh.

---

## Hierarchy & data model

Jira's hierarchy:

```
Theme   (issue type id 10324, hierarchy 3)  — top-level grouping (e.g. "Usability", "Data Breadth (Quantity)")
  └─ Initiative   (issue type id 10011, hierarchy 2)  — the "user-story-level" rows on the page
       └─ Epic   (issue type id 10000, hierarchy 1)  — what the team works on; rendered as bars
            └─ Story / Task / Sub-task / Bug   (hierarchy 0)  — not shown on this page
```

The page shows **Initiatives → Epics**. It does not render Stories. Theme is shown as a chip on the Initiative row (sourced from `parent.summary` of the Initiative).

### Custom fields used

These were the central discovery of this work — once you have these IDs, you can pull everything you need:

| Field name              | Custom field ID         | Type                   | Purpose                                                                   |
| ----------------------- | ----------------------- | ---------------------- | ------------------------------------------------------------------------- |
| **Project Health**      | `customfield_10499`     | cascading-select       | On Track / At Risk / Off Track / Complete / Not Started — drives bar color |
| **Product Execution Update** | `customfield_10498` | textarea (ADF)         | Per-Epic narrative shown when the bar is clicked                          |
| **Funding Mechanism**   | `customfield_10245`     | multi-select           | PJM / HSF / General Paying Customer(s) / General No Donor / etc.          |
| **Prioritized Quarter** | `customfield_10731`     | multi-select           | FY26Q2 / FY26Q3 / … — an epic can belong to several quarters. Replaced the single-select `customfield_10533` ("Prioritized Quarter (old)") on 2026-07-06; the page stores it as a `quarter` array and the Quarter filter matches with `includes()`. |
| **Start date**          | `customfield_10015`     | datepicker             | Bar start position                                                        |
| **Due date**            | `duedate` (system)      | date                   | Bar end position; right-anchored chip on each Epic                        |
| Target start (alt)      | `customfield_10022`     | JPO baseline-start     | Available, not used. Could swap in if Plans is preferred over Start date. |
| Target end (alt)        | `customfield_10023`     | JPO baseline-end       | Same as above for end date.                                               |
| Assignee (Owner)        | `assignee` (system)     | user                   | Owner avatar pill                                                         |
| Parent                  | `parent` (system)       | issue link             | Epic → Initiative → Theme chain                                           |

### Health values (exact strings as they appear in Jira)

`On Track`, `At Risk`, `Off Track`, `Complete`, `Not Started`. Empty/null = "Not Set".

### Status values seen in the wild (Jira `status.name`)

`Open`, `Ideation`, `In Progress`, `Done`, `To Do`, `Abandoned`. (Abandoned issues should be excluded from the page — currently filtered manually in the JQL.)

---

## Current scope: the Q2 2026 plan (18 Epics)

These are the Epics currently baked into the page. List provided by Tyler / Pranali:

**Linked to an Initiative (7):**

| Epic key   | Initiative parent | Title                                                                  |
| ---------- | ----------------- | ---------------------------------------------------------------------- |
| OSDEV-2566 | OSDEV-2565        | Satellite Image Processing and Detection — Earth Genome/PJM            |
| OSDEV-2554 | OSDEV-2565        | Grant Support & Technical Deliverables (Ongoing)                       |
| OSDEV-2628 | OSDEV-2556        | FY26Q2 — Data Monitoring and Uploads                                   |
| OSDEV-2638 | OSDEV-2556        | [CI/CD] Faster delivery pipeline                                       |
| OSDEV-2559 | OSDEV-2505        | Automate Claims Moderation Process                                     |
| OSDEV-2546 | OSDEV-2505        | Automate SLC Moderation Process                                        |
| OSDEV-2548 | OSDEV-2475        | Data Quality Investment User Story                                     |

**Standalone — no Initiative parent in Jira (11):**

OSDEV-2543, OSDEV-2270, OSDEV-2553, OSDEV-2555, OSDEV-2631, OSDEV-2629, OSDEV-2653, OSDEV-2655, OSDEV-2656, OSDEV-2427, OSDEV-392.

These render in a "Standalone Epics" strip at the bottom (dashed pink). Linking them to Initiatives in Jira will move them into the main flow.

### Initiatives in scope (4)

| Initiative key | Theme parent           | Title                                                                                       |
| -------------- | ---------------------- | ------------------------------------------------------------------------------------------- |
| OSDEV-2565     | Data Breadth (Quantity)| I want OS Hub to reach 3M OS IDs through multi-stakeholder contributions and public data ingestion |
| OSDEV-2556     | Usability              | I want to ensure that the OS Hub Platform is performant, secure, and reliable as an integral part of my business workflow |
| OSDEV-2505     | Usability              | I want to spend my moderation time on quality review — not on data entry, duplicate detection, or administrative work |
| OSDEV-2475     | Data Depth (Quality)   | I want to get better data back from OS Hub than what I put in — so that my OS Hub profile becomes a valuable source for other users |

There are more Initiatives in Jira (e.g. OSDEV-2516 "Trade union privacy") that are not currently in the Q2 plan view because none of their Epics are in scope.

---

## How to refresh the data

The current refresh is manual. **There is no scheduled job yet** — that's a TODO (see below).

### Step 1 — Pull from Jira

Use any tool that can hit Jira's REST API. Atlassian cloudId for OS Hub: `ce4a9d75-c0aa-460b-92fa-28cb0a11baa6`. Project key: `OSDEV`.

JQL for the 18-Epic Q2 plan as it stands today:

```jql
key in (OSDEV-2559, OSDEV-2631, OSDEV-2270, OSDEV-2543, OSDEV-2628, OSDEV-2653,
        OSDEV-2553, OSDEV-2655, OSDEV-2554, OSDEV-2427, OSDEV-392, OSDEV-2638,
        OSDEV-2629, OSDEV-2546, OSDEV-2566, OSDEV-2656, OSDEV-2548, OSDEV-2555)
```

Fields to request:

```
summary, status, assignee, issuetype, parent, duedate, labels,
customfield_10015, customfield_10245, customfield_10498, customfield_10499
```

For Initiatives separately:

```jql
key in (OSDEV-2565, OSDEV-2556, OSDEV-2505, OSDEV-2475)
```

(Pull `parent` to get the Theme name — `parent.fields.summary`.)

### Step 2 — Map into the page's data shape

In `draft-2.6-roadmap.html`, find the `const initiatives = [ ... ]` block (around line 200). Each Initiative entry has:

```js
{
  key: "OSDEV-2565",
  url: "https://opensupplyhub.atlassian.net/browse/OSDEV-2565",
  title: "<Initiative summary>",
  theme: "<parent.summary on the Initiative>",
  color: 0,                    // 0–5: bar accent palette
  epics: [
    {
      key: "OSDEV-2566",
      url: "...",
      title: "<Epic summary>",
      owner: "<assignee.displayName>",       // null = "Owner: TBD" pill
      status: "Open",                        // exact Jira status.name
      health: "On Track",                    // null = "Not Set"
      funding: ["PJM"],                      // array of customfield_10245 values
      startDate: "2026-04-01",               // ISO yyyy-mm-dd; null OK
      dueDate:   "2026-06-01",               // ISO yyyy-mm-dd; null OK
      execUpdate: "Plain text. \\n for line breaks."  // flatten ADF to plain text
    }
  ]
}
```

Orphan Epics go in the special trailing entry with `key: "_orphans"`, `standalone: true`. That's the "Standalone Epics" strip at the bottom.

### Step 3 — Flatten the Product Execution Update from ADF

Jira returns `customfield_10498` as Atlassian Document Format (ADF) JSON. To flatten to plain text, walk the tree and join `.text` values from `text` nodes; treat `hardBreak` as `\n`.

A working `jq` recipe (from this session):

```bash
jq '[.fields.customfield_10498 | recurse(.content // empty | .[]?) | select(.type=="text") | .text] | join(" ")'
```

(Newlines between paragraphs get lost with `join(" ")` — improve to insert `\n` between paragraph blocks if needed.)

### Step 4 — Update the timestamp

Find `const LAST_SYNC = "2026-05-05";` near the top of the data block. Bump to the date you refreshed.

### Step 5 — Commit & push

```bash
# from a checkout of TylerHeath1/reports
cp draft-2.6-roadmap.html 2026-roadmaps/draft-2.6-roadmap.html
git add 2026-roadmaps/draft-2.6-roadmap.html
git commit -m "Refresh roadmap from Jira (YYYY-MM-DD)"
git push
```

GitHub Pages rebuilds in ~30 seconds.

---

## Visual / design decisions made (don't undo without intent)

- **Page background = warm cream `#faf6ec`** — softer than white, less clinical.
- **Initiative bars** = palette color (yellow/orange/teal/blue/violet/pink).
- **Epic bar background = HEALTH color** — green/yellow/orange/purple/grey. This makes status scannable at a glance.
- **Epic bar left border = Initiative color** (4–5px) — preserves the visual link to the parent Initiative.
- **Expand panel** (when Initiative is opened) is tinted by the Initiative's color so context never gets lost when scrolling through Epics.
- **Owner pill** = small dark circle with initials + name. Most prominent chip on the Epic row (Tyler asked for this — owners give meeting status updates, so make them findable).
- **Chip order on each Epic** is: **Owner → Health → Status → Funding** (left-to-right). Don't reorder.
- **Initiative row chips** are intentionally minimal — only Theme + Epic count + "no dates yet" fallback. Health/Status/Funding live on the Epic, not the Initiative.
- **Due date right-anchored** on each Epic bar. Urgent treatment (red) for items due in the next 14 days; purple for Complete.
- **Product Execution Update reveal** styled as a sticky-note (warm yellow `#fffceb` with shadow + tab indent). Replaces the previous white-on-grey panel that felt clinical.
- **Year ↔ Q2 view toggle**. Year shows full 2026; Q2 zooms to Apr/May/Jun with month columns. Bars rescale, out-of-window dates disappear.
- **Bar minimum width = 18%** of the visible timeline so titles never wrap letter-by-letter.

### Health color palette (locked in this version)

| Health        | Bar background | Border    | Chip background |
| ------------- | -------------- | --------- | --------------- |
| On Track      | `#e3f5e6` 🟢   | `#3aaa3a` | `#c8e6c9`       |
| At Risk       | `#fff4c2` 🟡   | `#eab308` | `#fff3cd`       |
| Off Track     | `#ffedd5` 🟠   | `#ea580c` | `#ffedd5`       |
| Complete      | `#ede9fe` 🟣   | `#8b5cf6` | `#ede9fe`       |
| Not Started   | `#ececec` ⚪   | `#6b7280` | `#e5e7eb`       |
| Not Set       | `#f7f5ee`      | `#a1a1a1` (dashed) | `#f3f4f6` |

### Initiative color palette

`c0` amber, `c1` orange, `c2` teal, `c3` blue, `c4` violet, `c5` pink. Standalone-Epics container uses a dashed pink pattern (`.init-bar.standalone`).

---

## Known data quality issues (good to know)

- **OSDEV-2655** — typed as Epic, but its summary literally says "User story: OS Hub data is credible, consolidated, and accurate". Probably should be promoted to Initiative type in Jira.
- **OSDEV-392** — has 2024 dates (Jul 5 – Aug 10). Out of the 2026 view, so renders as TBD. The exec update says "Not prioritized for Q2"; consider removing from Q2 plan.
- **11 of 18 Epics have no Initiative parent.** They fall into the "Standalone Epics" strip. The page would feel much cleaner if these got linked to Initiatives in Jira (or new Initiatives created for them — e.g. customer-paying / Spotlight has 3 Epics that could share one).
- **"General No Donor"** appears as a Funding chip on 12 of 18 Epics. It's the default and adds visual noise. Tyler is open to hiding it on the page; not done yet.

---

## Open items / what's next

- [ ] **Daily auto-refresh** — currently manual. Wire a GitHub Action that runs a script each morning to pull from Jira and commit the regenerated HTML. Needs a Jira API token stored as a repo secret.
- [ ] **Confluence landing page** — a stable URL the team can bookmark, with a description of what the page is and a link to the latest. Pranali to own (she's the artifact owner going forward).
- [ ] **Sort Initiatives by Jira Rank** (`customfield_10019`) so the order is editable in Jira's backlog without code changes. Currently the order is fixed in code.
- [ ] **Link orphan Epics to Initiatives in Jira** (or create new Initiatives) — Pranali. This is the highest-leverage cleanup.
- [ ] **"Due in next 2 weeks" callout** at the top of the Q2 view — a 1-line summary box surfacing urgent Epics. Designed but not implemented.
- [ ] **Hide "General No Donor" funding chip** as default — option discussed, not implemented.
- [ ] **Promote `os-hub-roadmap.html` → use `draft-2.6-roadmap.html` as the canonical** once the team signs off.

---

## Useful context

- **Issue source of truth** = Jira (`opensupplyhub.atlassian.net`, project `OSDEV`)
- **Atlassian cloudId** = `ce4a9d75-c0aa-460b-92fa-28cb0a11baa6`
- **GitHub repo** = `TylerHeath1/reports` (public, `main` branch)
- **Page bundle** = single self-contained HTML file. No build, no dependencies.
- **Browser support** = modern desktop browsers (Chrome / Safari / Firefox / Edge). Not optimized for mobile but works.
- **Print** = the print stylesheet hides filters and the source banner so screenshots / PDFs are clean.

---

## Who to ask

- **Tyler Heath** — origin of the artifact, voice and direction, GitHub repo owner. Github: `TylerHeath1`.
- **Pranali Chhatbar** — Product Manager; owns the artifact going forward. Source of truth for what should be in the Q2 plan, who's the Epic owner, and how Project Health is filled in.
