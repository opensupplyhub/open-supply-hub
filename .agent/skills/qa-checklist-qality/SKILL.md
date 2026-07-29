---
name: qa-checklist-qality
description: >-
  Build compact QA checklists from Jira stories and GitHub PRs (format: what to
  test? — expected result) and update linked QAlity Test issues in opensupplyhub
  Jira. Use when the user asks for a QA checklist, test steps, QAlity test case
  content, or change-list QA for OSDEV tickets.
---

# QA Checklist & QAlity Test Case

Generate a compact QA checklist from Jira + PR context, then push it into the linked **QAlity Test** issue when requested.

## When to use

- User shares a Jira story and/or GitHub PR(s) and wants a **QA checklist**
- User wants each item as **what to test? — expected result**
- User asks to update a **QAlity Test** issue (`issuetype: QAlity Test`) with test steps
- User mentions **change list**, **OSDEV-####**, or **test cycle** (Passes/Failed/Blocked)

## Inputs to collect

| Input | Required | Example |
|-------|----------|---------|
| Jira story key/URL | Yes | `OSDEV-1149` |
| GitHub PR URL(s) | If available | `opensupplyhub/open-supply-hub#1094` |
| QAlity Test key/URL | If updating Jira | `OSDEV-3013` |
| Environment notes | Optional | reindex required, Test vs Staging |

## Workflow

### 1. Gather context

**Jira story** (Atlassian MCP):

```
getJiraIssue
  cloudId: ce4a9d75-c0aa-460b-92fa-28cb0a11baa6
  issueIdOrKey: <STORY_KEY>
  fields: summary, description, comment, issuelinks
  responseContentFormat: markdown
```

Read: user story, acceptance criteria, dev QA notes in comments, linked QAlity Test (`tests` link).

**GitHub PR(s)**:

- Prefer `gh pr view <num> --repo opensupplyhub/open-supply-hub --json title,body`
- If `gh` is unavailable, use `WebFetch` on the PR URL

Extract: functional changes, deploy/release steps, null semantics, out-of-scope follow-ups.

### 2. Write the QA checklist

Use this structure:

1. **Prerequisites** — data/env setup before testing
2. **AC coverage** — one row per acceptance criterion
3. **Regression** — existing behaviour unchanged
4. **Out of scope** — informational; do not block release

**Item format (required):**

```text
what to test? — expected result
```

In Jira/QAlity fields:

- **Test Step** ← what to test?
- **Expected Result** ← expected result

Keep items **actionable** (concrete endpoint, UI path, or data condition). Reference legacy APIs or admin UI when they are the source of truth.

### 3. Update the QAlity Test issue (if requested)

Find the linked test case via `issuelinks` on the story, or use the key the user provides.

**Standard QAlity Test description header** (keep or append):

```markdown
Follow the checklist steps presented below _and_ the main ticket description for testing [STORY_KEY](https://opensupplyhub.atlassian.net/browse/STORY_KEY).

Change the status in the test cycle: _Passes/Failed/Blocked_, not the status of the current ticket.

If the testing has passed successfully, move this QAlity ticket to the **Done** status.
```

**Also set label:** `qality-change-list-item`

#### Update methods (try in order)

| Method | Tool | Works? |
|--------|------|--------|
| QAlity Test Steps panel | Playwright MCP | Yes, **only after user logs into Atlassian in the Playwright browser** |
| Jira comments with steps | `addCommentToJiraIssue` | Yes — reliable fallback |
| Short description (intro + prereqs) | `editJiraIssue` | Yes — keep short |
| QAlity REST `/rest/qality/1.0/...` | — | No — needs QAlity API token |
| Jira API → Test Steps panel | — | No — plugin data, not standard fields |

**Playwright prerequisite:** navigating to the issue shows `Log in to continue` until the user signs in manually in the Playwright-controlled browser. Do not enter passwords.

**`editJiraIssue` pitfall:** long descriptions containing `{curly_braces}` (e.g. `{os_id}`) can break JSON parsing. Prefer comments for the full step list, or write `by os_id` instead of `{os_id}`.

### 4. Report back

Tell the user:

- Checklist (in chat or Jira)
- What was updated in Jira (description, labels, comments, QAlity steps)
- What still needs manual action (Playwright login, copy steps into QAlity panel)

## Checklist template

```markdown
### Prerequisites
- [ ] <setup step> — <expected state>

### AC#N — <short title>
- [ ] <what to test?> — <expected result>

### Regression
- [ ] <what to test?> — <expected result>

### Out of scope (informational)
- [ ] <item> — <why not blocking>
```

## Reference example (OSDEV-1149)

**Story:** Add `is_closed` to `GET /api/v1/production-locations/`

**Prerequisite:** `production-locations` OpenSearch reindex (~4h, `[Release] Deploy` → `clear-opensearch-target` = `production-locations`) OR facility edited post-deploy. Legacy `GET /api/facilities/{os_id}/` is source of truth.

**Sample steps:**

| # | Test Step | Expected Result |
|---|-----------|-----------------|
| 5 | `GET /api/v1/production-locations/?q=<closed location>` | `"is_closed": true` in matching result |
| 9 | `GET /api/v1/production-locations/{os_id}/` for location with no closure status | `is_closed` key absent (not `null`) |
| 12 | Check `is_closed` value type in v1 response | Boolean `true`/`false`, not string |

**Out of scope:** UI "Closed" label (OSDEV-1202 / OSDEV-1597); API docs AC#2 (OSDEV-2951).

## Usage examples

### Example 1 — Checklist only (chat)

**User:**

> Check PR https://github.com/opensupplyhub/open-supply-hub/pull/1094 and task OSDEV-1149. Give a compact QA checklist: what to test? — expected result.

**Agent:**

1. Fetch PR #1094 and Jira OSDEV-1149
2. Return checklist in chat (Prerequisites → AC → Regression → Out of scope)
3. Do not touch Jira unless asked

---

### Example 2 — Checklist + update QAlity issue via Jira API

**User:**

> Build QA steps for OSDEV-1149 and put them in QAlity task OSDEV-3013 (Test Step / Expected Result).

**Agent:**

1. Fetch OSDEV-1149 and PR context; draft 10–15 steps
2. `editJiraIssue` OSDEV-3013: short description + label `qality-change-list-item`
3. `addCommentToJiraIssue` OSDEV-3013: full step list (`Test Step: … | Expected: …`)
4. Say QAlity panel was not filled via API; steps are in comments for copy/paste

---

### Example 3 — Playwright fill (user must log in first)

**User:**

> Update QAlity test steps in OSDEV-3013 via Playwright.

**Agent:**

1. `navigate` to `https://opensupplyhub.atlassian.net/browse/OSDEV-3013`
2. If snapshot shows **Log in to continue** → ask user to log in to Atlassian in the Playwright browser, then say "continue"
3. After login: find QAlity **Test Steps** section, add rows with Test Step + Expected Result, save
4. If Playwright unavailable, fall back to Example 2

---

### Example 4 — Multiple PRs, one story

**User:**

> PR 1094 and 1115, story OSDEV-1149 — QA checklist for release 2.27.

**Agent:**

1. PR #1094 = functional changes; PR #1115 = docs-only (note, do not add fake test steps for docs)
2. Merge deploy notes (reindex) into Prerequisites
3. Single checklist tied to story AC, not per-PR

---

### Example 5 — Change-list test case from scratch

**User:**

> Create QA content for the QAlity test linked to OSDEV-2960.

**Agent:**

1. `getJiraIssue` OSDEV-2960 → find `is tested by` QAlity Test key
2. If no QAlity issue exists, tell user to create one in Jira (do not create unless asked)
3. Apply standard description header + checklist + `qality-change-list-item` label

## Jira constants (opensupplyhub)

| Field | Value |
|-------|-------|
| Cloud ID | `ce4a9d75-c0aa-460b-92fa-28cb0a11baa6` |
| Site | `https://opensupplyhub.atlassian.net` |
| QAlity issue type | `QAlity Test` (id `10012`) |
| Change-list label | `qality-change-list-item` |
| Test cycle statuses | Passes / Failed / Blocked (not the issue workflow status) |

## Do not

- Block QA on out-of-scope items (UI follow-ups, separate doc tickets) unless the user asks to include them
- Commit or push the skill file unless the user requests it
- Force-push or amend commits when only updating Jira content
- Assume Playwright is logged in — always check accessibility snapshot first
