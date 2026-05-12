---
name: product-release-notes
description: >-
  Create product release notes pages in Confluence for an Open Supply Hub
  release. Use when the user asks to create, draft, write, or publish product
  release notes, or when preparing a new Confluence release notes page for a
  sprint or version release.
---

# Product Release Notes Skill

## Overview

This skill creates Confluence release notes pages for Open Supply Hub releases
by:
1. Looking up available Jira release versions in the OSDEV project
2. Confirming the release number and hotfixes with the user
3. Fetching all issues associated with each version
4. Creating a formatted Confluence page per version in the Release Notes folder

---

## Configuration

| Setting | Value |
|---|---|
| Jira project | `OSDEV` |
| Confluence space ID | `15859716` (space key: `SD`) |
| Confluence parent folder ID | `649494530` (Release Notes, under Product) |
| Page title format | `{version} - {Mon D YYYY} - Release Notes` |
| Reference page (2.21.0) | Page ID `1216282625` |

---

## Step 1 — Find available Jira releases

Fetch the full list of versions for the OSDEV project using the Atlassian MCP
`fetch` tool:

```
GET https://opensupplyhub.atlassian.net/rest/api/3/project/OSDEV/versions
```

From the response, filter for versions whose name starts with the target release
number (e.g. all versions starting with `"2.22"`). This will capture:
- The main release (e.g. `2.22.0`)
- Any hotfixes (e.g. `2.22`, `2.221`)

Present the matching versions to the user in a clear list showing:
- Version name
- Release date (if set in Jira)
- Whether it is released or unreleased

**Ask the user to confirm:**
- Which version is the **main release**
- Which versions are **hotfixes**

**Do not proceed until the user confirms.**

---

## Step 2 — Fetch issues for each version

For each confirmed version, use `searchJiraIssuesUsingJql` to retrieve all
issues in that version:

```
project = OSDEV AND fixVersion = "{version_name}" ORDER BY created ASC
```

Collect for each issue:
- Issue key (e.g. `OSDEV-2451`)
- Summary
- Issue type
- Status
- Full Jira URL: `https://opensupplyhub.atlassian.net/browse/{issue_key}`

Also retrieve the Jira version ID (numeric) from the versions API response —
you will need it for the Release smart link in the Confluence page.

---

## Step 3 — Gather remaining details

Before creating pages, ask the user for any missing information:
- **Sprint number(s)** — e.g. `Sprint 80 + 81` (not available from Jira API)
- **Release date** — if not set in Jira, ask the user for the date
- **Contributors** — ask the user who should be listed as contributors (or
  leave blank for them to fill in later)

---

## Step 4 — Create one Confluence page per version

Create a separate page for each version (main release + each hotfix) using
`createConfluencePage`.

### Page title
```
{version} - {Mon D YYYY} - Release Notes
```
Example: `2.22.0 - May 15 2026 - Release Notes`

### Parent and space
- `spaceId`: `15859716`
- `parentId`: `649494530`

### Page content — two tables

Follow the exact structure of the 2.21.0 reference page (ID: `1216282625`).

#### Table 1 — Release metadata

| **Release** | Smart link to `https://opensupplyhub.atlassian.net/projects/OSDEV/versions/{version_id}` |
| **Release Date** | The release date |
| **Version** | The version number (e.g. `2.22.0`) |
| **Sprint** | Sprint number(s) provided by user |
| **Description** | A concise narrative summary of all issues in this release. Group related issues thematically. Use emoji section headers (💥 for major themes, 🔹 for individual items) matching the style of the 2.21.0 page. Each item should reference its OSDEV ticket number in italics at the end, e.g. *(OSDEV-2451)*. |
| **Contributors** | Names provided by user, or leave blank |

#### Table 2 — Issues tracking

One row per issue from Step 2:

| **Issue** | **For Internal Use (Team Discussions + Slack Post)** | **For External Use (Info Site)** |
|---|---|---|
| Smart link to `https://opensupplyhub.atlassian.net/browse/{OSDEV-XXXX}` | *(leave blank — user to fill in)* | *(leave blank — user to fill in)* |

The "For Internal Use" and "For External Use" columns require human judgment.
Leave them blank when creating the page. The team will fill them in with status
lozenges (`HIGHLIGHT` or `don't include` / `include` or `don't include`).

---

## Writing Rules for the Description

1. **Group issues thematically** — identify 2–4 major themes across all issues
   and group related tickets under each theme.
2. **Use emoji headers** matching the 2.21.0 style:
   - 💥 for major feature or theme headings
   - 🔹 for individual issue bullets within a theme
3. **End each bullet** with the OSDEV ticket in italics: *(OSDEV-XXXX)*
4. **Be descriptive** — explain what changed and why it matters to users or
   the team, not just what the ticket title says.
5. **Hotfix pages** have shorter descriptions — just 1–2 sentences per fix.

---

## Notes

- Create **one Confluence page per version** — main release and each hotfix
  each get their own separate page
- Always confirm the version list with the user before creating any pages
- If the Jira version has no `releaseDate`, ask the user before proceeding
- After creating each page, share the Confluence page URL with the user so
  they can review it immediately
