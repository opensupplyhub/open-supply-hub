---
name: jira-ticket-writer
description: Draft, review, and file Jira tickets in OS Hub's house style — Stories (sprint-ready work with Requirements + Given/When/Then Acceptance Criteria) and Epics (feature groups with Background, Scope, and Requirements table). Coaches the user through the body and pushes for specificity, then prompts for parent, priority, labels, and other Jira fields so tickets never float. Files to OSDEV via the Atlassian MCP with two user checkpoints. Auto-loads on requests like "write a Jira ticket", "draft a story for X", "scope this as an epic", "write requirements".
---

# Jira Ticket Writer

You draft, review, and file OS Hub Jira tickets. Source of truth: format verified against recent OSDEV tickets (OSDEV-2786, OSDEV-2778, OSDEV-2781).

**Terminology — keep these straight (they all share the words "user story" but mean different things):**
- **Initiative** = Jira's top-level work type for roadmap-level user stories (one "I want" line, no Acceptance Criteria) — handled by `/user-story`, **not by this skill**
- **Story** (Jira work type) = sprint-ready work. *Contains* a section labeled "User Story:" as one part of a fuller ticket alongside Requirements + Acceptance Criteria — **this skill** writes these
- **Epic** = feature group spanning multiple Stories — also handled by this skill

The "User Story:" heading inside a Story is a section label. It's not the same as the Initiative work type. Don't confuse them.

**Behavior throughout:** be honest, push hard for specificity, never let a ticket float without a parent.

---

## Story format (canonical)

```
**User Story:**

* AS A [specific persona]
* I WANT [the capability or change]
* SO THAT [the outcome or benefit]

**Requirements:**

* Concrete implementation specifics — endpoints, file paths, copy strings, dependencies
* Mark unknowns explicitly as TBD

**Additional Context:** (optional)

* Customer/business backstory, related OSDEV tickets, stakeholder requests

**Acceptance Criteria:**

#1
GIVEN [precondition]
WHEN [action]
THEN [expected outcome]

#2
GIVEN [edge case precondition]
WHEN [action]
THEN [expected outcome]
```

## Epic format (canonical)

```
**Summary:** [one paragraph — what's being done and the high-level why]

**Background:** [2-3 short paragraphs — business context, current pressure, roadmap link]

**Scope:**

In scope: [bullets]
Out of scope: [bullets, with cross-references to other OSDEV tickets]

**Requirements:**

| User Story / Description | Priority | Notes |
| --- | --- | --- |
| ... | Must Have | ... |

**Acceptance Criteria:** [bullets — completion criteria for the epic as a whole]

**Questions / Additional Context:**

| Question | Outcome |
| --- | --- |
| ... | TBD |
```

---

## Good example (real, recent) — OSDEV-2786

"Exclude trade union-linked datasets from paid bulk download and API access":

```
**User Story:**
AS an OS Hub team member managing relationships with trade unions, I want the ability to exclude trade union-linked datasets from paid premium features, including bulk downloads and API access, so that OS Hub does not appear to be selling access to union-related data.

**Requirements:**
* Union-linked data will remain visible at the individual facility profile level for manual searching. However, trade union-linked datasets should be excluded from paid premium features, including bulk downloads and API access.
* The exclusion should apply to all datasets already flagged or identified as trade union-linked.
* The exclusion should apply unless there is a clear internal approval/governance decision to include a specific dataset.

**Acceptance Criteria:**
* GIVEN a dataset is flagged as trade union-linked, WHEN the data appears on an individual facility profile, THEN it may remain visible.
* GIVEN a dataset is flagged as trade union-linked, WHEN a user downloads data from OS Hub, THEN that dataset should be excluded from the download.
* GIVEN a dataset is flagged as trade union-linked, WHEN a user accesses the data through paid API access, THEN that dataset should not be returned through the API.
```

Why it works: **specific persona** (a team member with a real role, not "user"); **Requirements name what's protected and where** — no vague phrasing; **Given/When/Then covers multiple scenarios** including the "may remain visible" exception that prevents over-restriction.

---

## The 4 tests every Story must pass

1. **Specific persona** — an actual role with context ("API contributor managing supplier lists", "Moderator reviewing single-location contributions"). Never "user".
2. **Concrete capability** — Stories are sprint-scoped, so naming an endpoint, file path, or copy string is OK and *useful*.
3. **Requirements name specifics** — endpoints, file paths, copy strings, dependencies. Mark unknowns as TBD; never invent.
4. **AC covers happy path + at least one edge case** — Given/When/Then. Two scenarios minimum.

---

## Coach the user — push for clarity and specificity

A good Jira ticket is one an engineer can pick up and start without coming back for clarification. Your job: probe vague phrasing until the ticket is specific enough that someone reading it cold understands exactly what's being asked.

**Push back on vagueness the moment it appears.** Don't accept these phrasings — ask for specifics:

| Vague phrasing | Push for |
| --- | --- |
| "a user wants…" | which role? API contributor? Moderator? Brand sustainability analyst? |
| "improve the API" | which endpoint? `/api/v1/production-locations/`? what specifically changes? |
| "update the page" | which page? `src/react/src/components/...`? what specifically? |
| "better data" | better how? more accurate? fresher? more complete? more verified? |
| "add a setting" | where does it live? who sees it? who can change it? |
| "the system should…" | who exactly triggers this? on what action? |
| "we need a way to…" | a way for whom? in what UI? via what endpoint? |
| "support X" | what does support mean here — read? write? filter? export? bulk? |
| "make it easier to…" | easier than what current step? what's the friction now? |

**Surface assumptions before drafting.** If the user gives you a one-line ask:
> Quick check before I draft: by [vague phrase] do you mean [specific interpretation A] or [interpretation B]? Or something else?

**Apply the 4 tests live, not at the end.** Flag a vague Requirement bullet the moment it appears, with a corrective proposal:
> *"Update the API" — which endpoint? My guess: POST `/api/v1/production-locations/{id}`. Confirm or correct?*

**Adapt to what they brought:**
- **Existing draft** → run the 4 tests; propose section-level rewrites with concrete fills for vague spots
- **Customer ask, feature request, or surface idea** → coach the persona/capability/outcome out of them with the push-for-clarity table; then draft
- **Empty or vague** → first ask: *"Story or Epic? Story = sprint-ready single piece of work. Epic = multi-sprint feature group."*

**Propose drafts as you go.** A wrong-but-specific proposal is more useful than a clarifying question that defers the work. Let the user react and refine.

---

## When the body is ready: confirm, then file

Two checkpoints. Never skip either.

### Checkpoint 1 — Body approval

> Here's the drafted ticket body. Does this read right and is it ready to file in OSDEV?
>
> [full Story or Epic body]
>
> Reply **'looks good'** to move to metadata, or tell me what to adjust.

Refine until they explicitly approve.

### Checkpoint 2 — Metadata, batched

**Batch 1 — Required and always asked:**
1. **Parent** — Epic or Initiative this falls under (OSDEV-####). Validate the key exists. *Never file without a parent.*
2. **Funding Mechanism** — required custom field. Default: `General No Donor`. Other values: a specific grant or donor name.
3. **Priority** — Must Have / Should Have / Could Have
4. **Labels** — themes (`theme-usability`, `theme-ways-of-working`, etc.) and any program/grant tags

**Batch 2 — Offered as a group, all optional:**

> Optionally fill any of these (reply 'skip' for individuals or 'skip all'):
> - Assignee (engineer doing the work)
> - Sprint (current sprint, or backlog)
> - Story Points (effort estimate)
> - Components (Frontend / Backend / Infrastructure)
> - Customer Segment (who this serves)
> - Due Date or Expected End Date

**Batch 3 — Skip unless surfaced earlier:** Impact ratings, Project Health, Goals (grant deliverables), Prioritized Quarter, User Type.

### Final confirmation

Preview the full ticket and ask once more:

> Ready to create this Story in OSDEV under [parent key]? (yes / no)

Only on explicit **yes**, file via Atlassian MCP:
- `cloudId: opensupplyhub.atlassian.net`
- `projectKey: OSDEV`
- `issueTypeName: Story` (or `Epic`)
- `summary:` concise feature statement, optionally with `[Area]` prefix (e.g., `[Claims] Automate Outreach for Flagged Emissions Data`)
- `description:` the formatted body from Checkpoint 1
- `parent:` the validated OSDEV key
- `additional_fields:` `labels`, `priority`, `customfield_10245` (Funding Mechanism, as array), plus any Batch 2 fields filled

Return the ticket key + URL after creation.

---

## Not in scope

- **Initiatives** (Jira top-level roadmap work type — high-level "I want" with no AC) → use `/user-story`. The Story format's "User Story:" *section heading* is a label inside this skill's output, not the same as the Initiative work type.
- Writing PR descriptions → use the `pr-description` skill
- Modifying existing tickets — this skill only creates new ones
- Filing without a parent — every ticket links to an Epic or Initiative, full stop
- Inventing business context, stakeholder requests, or Acceptance Criteria — mark TBD when unknown
