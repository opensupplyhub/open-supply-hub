---
name: ship
description: Full ticket pipeline for OS Hub — read a Jira ticket, plan, implement, test, preview, create PR. Use ONLY when the user explicitly invokes the /ship command or asks to "ship a ticket" with an OSDEV key. Do not auto-invoke on general mentions of planning, building, or implementing — /ship is a deliberate multi-step pipeline that requires explicit user trigger.
---

# /ship — OS Hub ticket pipeline

You are the OS Hub ticket pipeline orchestrator. Apply all conventions from `AGENTS.md` (single source of truth for GPS coordinate order, Facility.id, Redux patterns, feature flags, branch naming, commit format, RELEASE-NOTES location, and "never touch" zones).

Working directory: the local OS Hub checkout (typically `~/open-supply-hub`).

**Sub-agents this skill spawns:** `oshub-codebase-expert` for research; generic `general-purpose` Agents for parallel backend/frontend implementation. No others.

**Behavior throughout the run:**
- Surface any assumption before you act on it. If the ticket is ambiguous, ask before planning.
- Minimum work to satisfy the ticket. No extra refactors, no speculative features, no formatting changes to files outside the plan.
- Every checkpoint has a verifiable check — name it, then wait.

---

## Step 0 — Route the entry

Read `$ARGUMENTS`. Decide one of three paths:

- **Empty** → ask: *"Which ticket are we shipping? Give me an OSDEV key (e.g., OSDEV-2316), or describe the idea and I'll help you draft a ticket first."*
- **Matches `OSDEV-####`** → continue to Step 2.
- **Anything else (freeform idea)** → say: *"That looks like an idea, not a ticket. I'll need a Jira ticket to ship against. Should I use the `jira-ticket-writer` skill to draft one from what you wrote? Reply 'yes' to draft, or paste an existing OSDEV key."* If `jira-ticket-writer` does not exist yet, say so honestly and ask the user to create the ticket in Jira manually, then re-invoke `/ship OSDEV-####`.

---

## Step 1 — Confirm experience level (one-time per session)

If unknown from earlier in this session, ask:

> Quick question so I pitch this right:
> 1. First time using Claude Code at OS Hub — explain every term, slow pacing
> 2. Used it a few times — some comfort with git and the workflow
> 3. Engineer — full technical depth, skip the hand-holding
>
> Which fits? (1, 2, or 3)

Calibrate the run:
- **Level 1:** Gloss every git/GitHub term at first appearance. Plain English before every shell command. Slow pacing, confidence-building.
- **Level 2:** Gloss only non-obvious terms (PR, merge). Explain only non-routine commands.
- **Level 3:** No glosses, no narration of routine commands.

**Glosses to reuse** (Levels 1 and 2 only, at first appearance):
- **branch** — your own copy of the code where you can make changes without touching the version everyone else uses
- **commit** — a saved snapshot of your changes on your computer; nothing is visible to anyone else yet
- **push** — uploads your local commits to GitHub so others *could* see them, but doesn't ask anyone to review yet
- **pull request (PR)** — asks your teammates to review your branch and merge it into the shared main version
- **merge** — officially joins your changes into the main version of the code
- **main** — the canonical, shared version of the code everyone works from

---

## Step 2 — Check for a cached plan

Look for `~/.claude/plans/$ARGUMENTS.md` (written by the `/plan` skill).

If it exists, show:

> Cached plan found at ~/.claude/plans/$ARGUMENTS.md.
> - Created: [date]
> - Complexity: [RED / YELLOW / GREEN]
> - Files to change: [count]
> - Tests to write: [count]
>
> Use this plan? Reply 'yes' to skip planning and jump to building, or 'no' to re-plan from scratch.

If yes: skip Steps 3–6 and jump to Step 7.
If no or file missing: continue.

---

## Step 3 — Read the ticket

Fetch the Jira ticket via the Atlassian MCP. The OS Hub Atlassian site is `opensupplyhub.atlassian.net` — use this to identify the workspace when calling the MCP.

Extract: summary, description, acceptance criteria, labels. If anything reads as ambiguous, name it now — don't carry the ambiguity into the plan.

---

## Step 4 — Complexity check

State the complexity in one sentence and what it means:
- **RED** (dedupe pipeline, ECS/Terraform, core DB schema) → *"This touches systems that affect a lot of things — the kind of change where it's worth pairing with a senior engineer before going further. Want to continue solo, or pause and tag someone for guidance first?"*
- **YELLOW** (new Django model, full-stack change, touches search) → *"This is a meaningful change with moderate scope. Want to continue, or pause to align with an engineer first?"*
- **GREEN** (text changes, new field in an existing API, new UI component) → explain why, then continue.

---

## Step 5 — Research the change

*Confidence frame for Levels 1/2:* "Before any code: I gather context from three places — recent similar PRs in GitHub, design specs in Confluence, and a deep read of the codebase by a sub-agent that maps every file the change will touch. Goal is to know exactly what to change before changing anything."

Run in parallel where possible:

- **Confluence** — search the OS Hub Development Home space for the feature name and related specs via the Atlassian MCP. Read any relevant pages.
- **GitHub** — `git log --oneline -20` and `gh pr list --state merged --limit 15 --json title,number,files` for recent similar PRs.
- **Codebase Expert sub-agent** (`oshub-codebase-expert`, run_in_background: true) — give it the ticket summary and description. It returns a structured report under 300 words: architecture, files involved, cross-layer touch points, risks, next steps.

Wait for the sub-agent to finish before moving on.

---

## Step 6 — Show the plan (CHECKPOINT)

Combine all findings into one clear plan. **Order matters** — lead with the proposed approach so the human can react to it in one read:

1. **What the plan is** — 1-2 sentence summary of the proposed approach
2. **What the ticket asks for** — 2 sentences, plain English
3. **What Confluence says** — specs and context, or "nothing found"
4. **What recent PRs show** — patterns to follow
5. **Files to change** — every file with a one-line description
6. **Tests to write**
7. **RELEASE-NOTES entry** — drafted exact text
8. **Risks** — anything that could go wrong

Then:
> Does this plan look right? Reply 'go' to proceed, or tell me what to change.

Do not write code until the user says go.

---

## Step 7 — Create a fresh branch and implement

*Confidence frame for Levels 1/2:* "I'm pulling the latest version of the team's code so you start from a clean copy. Then I'll make a **branch** — your own copy where you can make changes safely."

Automatically:
- Pull main fresh (no stale checkouts)
- Create branch `OSDEV-####-short-description` (derive from the real ticket title; no placeholder text)
- Verify the new branch is checked out before continuing

Implement. If both backend and frontend are needed, launch two generic Agents in parallel (run_in_background: true). Each gets: the approved plan, Confluence context, recent-PR patterns, and AGENTS.md conventions. Each is told: **touch only what the plan calls for. No refactoring of adjacent code. No formatting changes to files outside the plan. Never run git commands.**

If only one layer is needed, use one agent.

Wait for implementation to finish.

---

## Step 8 — Show what changed (CHECKPOINT)

List every file created or modified with a plain-English summary of what changed in each.

> Want to review any file before running tests? Reply 'looks good' to run tests, or name a file to see it.

Wait for the user.

---

## Step 9 — Write tests, run tests, lint

**Future migration:** When the `test-writer` skill exists, this step calls into it. For now, the orchestrator inlines the test-writing logic.

Write tests:
- For each new or modified Django view/model/serializer: write a happy-path test plus one edge case. Place in `src/django/api/tests/test_<feature>.py` following recent PR patterns.
- For each new or modified React component: write a test in `__tests__/components/` exercising the main props.

Run in parallel:
- Django tests: `docker compose exec django python manage.py test`
- React tests: `docker compose exec react yarn test --watchAll=false`
- Django lint: `docker compose run --rm --no-deps django flake8`
- React lint: `docker compose run --rm --no-deps react yarn lint`

Report:

> Tests: [pass] passed, [fail] failed. New tests written: [list].
>
> Coverage:
> - What was tested: [bullets]
> - What was NOT tested: [bullets]
> - Risk if untested parts have bugs: low / medium / high
>
> Lint: clean / [issues]
>
> Reply 'commit' to save these changes locally, or tell me what to fix.

Tests must pass before continuing. Verifiable check: zero failures.

---

## Step 10 — Commit locally and update release notes

*Gloss for Levels 1/2:* "A **commit** is a saved snapshot of your changes on your computer. Nothing is visible to anyone else yet."

- `git add` the changed files
- `git commit -m "[OSDEV-####] [real ticket summary]"`
- **Call the `release-notes` skill** (`.agent/skills/release-notes/SKILL.md`) to update `doc/release/RELEASE-NOTES.md` following OS Hub conventions. Do not write the entry by hand.
- `git commit -m "[OSDEV-####] Update release notes"`

---

## Step 11 — Push to GitHub (CHECKPOINT)

*Gloss for Levels 1/2:* "**Pushing** uploads your local commits to GitHub so others *could* see them, but doesn't ask anyone to review yet."

> Ready to upload your branch to GitHub. This makes it visible online but does NOT create a PR yet. Push? (yes / no)

Wait. Then `git push -u origin HEAD`.

---

## Step 12 — Local preview (CHECKPOINT)

Silent pre-flight checks before involving the user:
1. Local server up (`curl localhost:6543`)
2. Feature flag state if relevant
3. Test account exists if a role is needed
4. Seed data meets any thresholds
5. `docker compose exec django python manage.py migrate` (pulling main often brings new migrations)

Fix pre-flight failures silently. Note any temporary changes to revert before the next commit.

**Never ask the user to use browser DevTools, the console, or the Redux inspector.** Get debug info programmatically.

If local preview cannot run for a structural reason (seed data mismatch, missing test account that can't be created, etc.), say so honestly. Don't claim "looks good" when you couldn't actually verify. Let the user decide whether to skip preview or address the blocker.

Show:
> Preview your change: http://localhost:6543/[path]
> Log in as: [email] / [password]
> What you should see: [plain English description]
> How to verify: [1-2 simple visual checks]
>
> Reply 'looks good' to create the PR, or describe what's wrong.

Two silent debugging attempts before asking the user whether to keep going or skip.

---

## Step 13 — Create the pull request (CHECKPOINT)

*Gloss for Levels 1/2:* "A **pull request (PR)** asks your teammates to review your branch and merge it into the shared main version."

**Generate the PR description by calling the `pr-description` skill** (`.agent/skills/pr-description/SKILL.md`). It produces the body following OS Hub conventions (Summary / How to test / Jira link, correct formatting). Do not write the description from scratch — and do not inline the convention rules here, they live in the skill.

Show:
> PR title: [OSDEV-####] [summary]
> PR description (first 2 lines): [...]
> Files changed: [list]
> Create this PR? (yes / no)

Wait. Then `gh pr create` with the title and the description from `pr-description`.

**Add a top-level PR comment with orchestrator context:**
> /ship orchestrator notes:
> - Plan source: [cached from /plan, dated YYYY-MM-DD] / [generated fresh by this run]
> - Codebase Expert sub-agent report attached below
> - Tests written inline by /ship. When the `test-writer` skill exists, move this logic out of /ship.
> - Risks identified during planning: [bullet list from Step 6 item 8]
>
> [Append the full Codebase Expert structured report]

This comment gives reviewers (and future readers of this PR) the full trail of what /ship did to produce this change.

---

## Step 14 — Handoff

*Gloss for Levels 1/2:* "**Merging** means your changes officially join the main version of the code. That happens after review, not now."

Tell the user:
1. PR link — assign yourself as Assignee in GitHub (right sidebar → Assignees → your username)
2. Wait ~5 minutes for CodeRabbit auto-review
3. Run `/pr-health` to check CodeRabbit comments and CI status
4. Plain-English summary of what was built (3-5 bullets)

End the run.

---

## What this skill does NOT do

- Does not file new Jira tickets — that's `jira-ticket-writer` (called from Step 0 if/when it exists)
- Does not write the PR description from scratch — calls `pr-description`
- Does not write release notes from scratch — calls `release-notes`
- Does not push directly to main — always opens a PR for review
- Does not modify ECS, Terraform, RDS, or production `.env` — out of scope for ticket work
- Does not touch the dedupe pipeline unless the ticket explicitly says so
- Does not merge the PR — that happens after human review
- Does not auto-load on general "planning" or "building" language — must be invoked explicitly via the `/ship` command
