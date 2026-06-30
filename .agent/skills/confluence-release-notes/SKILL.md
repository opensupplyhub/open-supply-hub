---
name: confluence-release-notes
description: >-
  Create business-oriented Confluence release notes (draft) and a Slack post draft
  from GitHub doc/release/RELEASE-NOTES.md. Files the Confluence page via Atlassian
  MCP (createConfluencePage) after user approval; Slack post is chat-only. Page
  structure: metadata table (Description row), Programs warning panel, issue table
  with Jira inline previews. GitHub is source of truth for tickets; Jira provides
  business context.
---

# Confluence Release Notes & Slack Post

| # | Artifact | Destination |
|---|---|---|
| 1 | Confluence page (metadata + description + Programs warning + issue table) | Draft in SD space via `createConfluencePage` |
| 2 | Slack post (org-wide summary + Confluence link) | Chat only — user posts manually |

**Out of scope:** Info-site publishing decisions (Programs Team). Do not recommend what Programs should publish externally beyond filling the issue table's external column with suggested values.

---

## Rules

**GitHub** `doc/release/RELEASE-NOTES.md` is the **source of truth for ticket membership** and release date. Build an allowlist from the target `## Release X.Y.Z` section only (`OSDEV-\d+`, deduplicated). Every narrative bullet and issue-table row must match the allowlist exactly — one row per ticket, no extras, no missing.

**Jira** supplies summaries, descriptions, assignees, and sprints for allowlisted tickets only. Never add tickets from Jira Fix Version, prior Confluence pages, or memory.

Never invent information. If uncertain about grouping, sprint, or ticket membership, ask the user — do not 
guess.

**Prior Confluence pages** in the Release Notes folder supply **page format and Description tone** only. Load the latest via `getConfluencePage`; fallback: [2.25.0](https://opensupplyhub.atlassian.net/wiki/spaces/SD/pages/1329954817).

**Facts-only:** never invent information. `[Follow-up]` items in GitHub count if under the target release section. When Jira Fix Version lists tickets not in GitHub, omit them and note the discrepancy after filing.

---

## Workflow

1. **Confirm release version** (if not provided).
2. **Read GitHub** — `Read` `doc/release/RELEASE-NOTES.md`; extract the `## Release X.Y.Z` section, release date, and ticket allowlist.
3. **Load format reference** — `searchConfluenceUsingCql` (`ancestor = 649494530`, order by `lastmodified DESC`) → `getConfluencePage` (`contentFormat: html`). If a page for this release already exists, update it instead of creating a duplicate.
4. **Fetch Jira** — `searchJiraIssuesUsingJql` for allowlisted keys only:
   - `cloudId: opensupplyhub.atlassian.net`
   - `fields: summary, description, assignee, customfield_10020, fixVersions`
   - Paginate with `nextPageToken` if >50 tickets
   - **Release** link: Jira Fix Version URL from `fixVersions` — do not invent version IDs
5. **Infer Sprint** — sprint with the most tickets (e.g. `Sprint 84`). Add an italic clarifying note only when tickets span multiple sprints.
6. **Contributors** — unique Jira assignees, space-separated `@Name`.
7. **Draft narrative** — themed, business-oriented (see [Description](#description-narrative)).
8. **Checkpoint in chat** (required; never skip) — metadata table with full Description in the Description row, Programs warning, issue table, then Slack post draft. Use `(Confluence link — added after draft page is created)` in Slack.

   > Here are the draft **Confluence release notes** and **Slack post** for Release {version}. Review both below.
   >
   > [metadata table → Programs warning → issue table]
   >
   > ---
   >
   > **Slack post (chat only — you post manually):**
   >
   > [Slack post draft]
   >
   > Reply **'looks good'** to create the Confluence draft page, or tell me what to adjust.

9. **File via Atlassian MCP** (`plugin-atlassian-atlassian`) — only on explicit approval:
   - **Existing page** → `updateConfluencePage` (`contentFormat: html`, preserve `data-local-id`)
   - **New page** → `createConfluencePage`:
     - `cloudId: opensupplyhub.atlassian.net`
     - `spaceId: 15859716`, `parentId: 649494530`
     - `title: {version} - {Mon DD YYYY} - Release Notes`
     - `status: draft`, `contentType: page`, `contentFormat: html`
     - `body:` HTML per [Page format](#page-format) below
   - Do not set `status: current` on create. Return draft URL from MCP response.
10. **Return in chat:** Confluence URL, Slack post with real link, Jira/GitHub mismatch notes. Remind: page is **draft** (user publishes); Slack is copy/paste only.

**Hotfixes:** separate Confluence page per deploy (e.g. 2.22.1 and 2.22.2); read only the matching GitHub section.

---

## Page format

Match published pages ([2.25.0](https://opensupplyhub.atlassian.net/wiki/spaces/SD/pages/1329954817) · [2.24.0](https://opensupplyhub.atlassian.net/wiki/spaces/SD/pages/1329004547)). Assemble one HTML string — no markdown pipe tables in `body`.

**Order:** metadata table → Programs warning panel → issue table.

**Metadata table** — first row is Release (not Field/Value); labels in `<th>`, values in `<td>`:

```html
<table data-width="760">
<thead><tr>
  <th><p><strong>Release</strong></p></th>
  <th><p><a href="https://opensupplyhub.atlassian.net/projects/OSDEV/versions/{id}" data-card-appearance="inline">https://opensupplyhub.atlassian.net/projects/OSDEV/versions/{id}</a></p></th>
</tr></thead>
<tbody>
<tr><th><p><strong>Release Date</strong></p></th><td><p><time datetime="YYYY-MM-DD">Month DD, YYYY</time></p></td></tr>
<tr><th><p><strong>Version</strong></p></th><td><p>{version}</p></td></tr>
<tr><th><p><strong>Sprint</strong></p></th><td><p>Sprint {N}</p></td></tr>
<tr><th><p><strong>Contributors</strong></p></th><td><p>@Name @Name …</p></td></tr>
<tr><th><p><strong>Description</strong></p></th><td><!-- narrative --></td></tr>
</tbody></table>
```

| Field | Source |
|---|---|
| Release | Jira Fix Version inline card — full URL, not version number alone |
| Release Date | GitHub Introduction |
| Version | Release version string |
| Sprint | Primary sprint; italic inference note only when spanning sprints |
| Contributors | Unique Jira assignees, `@Name` space-separated |
| Description | Full narrative inside this row — never below the table |

**Programs warning** (exact wording, `panel-warning`):

```html
<div data-type="panel-warning"><p><strong>Programs Team:</strong> Please review tickets marked <strong>include</strong> under <strong>For External Use (Info Site)</strong> and confirm which items should appear on the info-site. These are suggested starting points only.</p></div>
```

**Issue table** — `<p><strong>Issue</strong></p>` heading (not `<h2>`):

```html
<p><strong>Issue</strong></p>
<table data-width="760">
<thead><tr>
  <th><p><strong>Issue</strong></p></th>
  <th><p><strong>For Internal Use (Team Discussions + Slack Post)</strong></p></th>
  <th><p><strong>For External Use (Info Site)</strong></p></th>
</tr></thead>
<tbody><!-- one row per allowlisted ticket --></tbody>
</table>
```

- **Issue column:** `<a href="https://opensupplyhub.atlassian.net/browse/OSDEV-XXXX" data-card-appearance="inline">https://opensupplyhub.atlassian.net/browse/OSDEV-XXXX</a>`
- **Internal column:** always green `HIGHLIGHT`
- **External column:** green `include` or red `don't include` — user/partner-facing features and visible bug fixes → `include`; internal tools, infrastructure, release meta → `don't include`

### Description narrative

1. **Opening summary** — 1–2 sentences, business-oriented.
2. **Themed sections** — group by user impact, not engineering layer:

```
💥 **Theme Name** — One-line theme description.

🔹 **Headline** — Business-friendly explanation. _(OSDEV-XXXX)_
```

**Writing rules:** lead with who benefits; translate GitHub technical bullets into plain language using Jira context; every `🔹` must reference an allowlisted ticket; infrastructure items typically `don't include` externally.

---

## Slack post template

Chat only — never post to Slack. Include all narrative items (no HIGHLIGHT filter).

```
🚀 **Release {version} is live!** ({date})

{1–2 sentence summary}

{emoji} **{Theme}**
• **{Headline}** — {business description}. *(OSDEV-XXXX)*

Thanks all for your contributions! 🙌

📋 Full release notes (internal): {Confluence draft URL}
```

Keep length proportional to release size.

---

## Related skills

- **GitHub engineering release notes:** `.agent/skills/release-notes/SKILL.md`
