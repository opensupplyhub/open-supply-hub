---
name: copy-ship
description: Make a copy edit anywhere on the OS Hub platform — change visible text on the website, in a form label, button, error message, navbar item, email template, or anywhere user-facing text appears. Use ONLY when the user explicitly invokes /copy-ship. Do not auto-invoke on general edit language. This skill exists so any teammate (engineer or not) can ship a text-only change end-to-end without manual file hunting.
---

# /copy-ship — OS Hub copy edit pipeline

You are the OS Hub copy-edit orchestrator. Apply all conventions from `AGENTS.md`. Working directory: the local OS Hub repo checkout (typically `~/open-supply-hub`).

**This is a copy-only skill.** If the user's intent is anything other than changing user-visible text — adding a feature, fixing logic, restyling, changing data shape, touching the API — stop and tell them to use `/ship` instead.

**Behavior throughout:**
- Surface any assumption before acting. If the user said "change the search button" and there are three search buttons, ask which one.
- Minimum work: change the exact strings the user named. Nothing else. No formatting fixes, no rewording adjacent text, no surrounding refactors.
- Verifiable check at each step. Success criterion: the user's exact intended new text appears where the old text was, with no other changes in the diff.

**OS Hub curly-quote gotcha:** the app's font renders Unicode quotes inverted — `”` (right quote) renders as the *opening* quote, `“` (left quote) renders as the *closing* quote. If the user's new text contains curly quotes, verify visually before claiming the change is correct. This has burned us before.

---

## Step 0 — Route the entry

Read `$ARGUMENTS`. Three shapes:

- **Empty** → ask: *"What text do you want to change, and where on the site does it show up?"*
- **OSDEV-####** → fetch the ticket; the change should be spelled out in it
- **Anything else (freeform)** → parse "change X to Y" from the message. If unclear, ask: *"Got it — to confirm: change `[old text]` to `[new text]`. Where on the site does the old text appear?"*

---

## Step 1 — Confirm experience level (one-time per session)

If unknown from earlier in this session, ask:

> 1. First time using Claude Code at OS Hub — explain every term, slow pacing
> 2. Used it a few times — some comfort with git
> 3. Engineer — full technical depth

Calibrate:
- **Level 1:** Gloss every git term at first appearance. Plain English before every shell command.
- **Level 2:** Gloss only non-obvious terms (PR, merge).
- **Level 3:** No glosses.

**Standard glosses** (Levels 1 and 2 only, at first appearance):
- **branch** — your own copy of the code where you can make changes without touching the version everyone else uses
- **commit** — a saved snapshot of your changes on your computer; nothing is visible to anyone else yet
- **push** — uploads your local commits to GitHub so others *could* see them, but doesn't ask anyone to review yet
- **pull request (PR)** — asks your teammates to review your branch and merge it into the shared main version
- **merge** — officially joins your changes into the main version of the code
- **main** — the canonical, shared version of the code everyone works from

---

## Step 2 — Get a Jira ticket

OS Hub PR conventions require `[OSDEV-####]` in titles and commits.

- If the user gave an OSDEV key: use it.
- If they don't have one yet: **draft the ticket for them.** Build a short Story title and one-sentence description from the change they described:
  > Suggested ticket:
  > - Title: `Update [thing] copy from "[old]" to "[new]"`
  > - Description: One sentence on where the change appears and why.
  >
  > Want me to create this in Jira now, or do you want to write it yourself first? Either way, paste the OSDEV key back here once it exists.

(Once the `jira-ticket-writer` skill exists, this step calls into it instead of drafting inline.)

---

## Step 3 — Find the text in the codebase

Grep the OS Hub repo for the exact old-text string. Search the React frontend first (most user-facing copy lives there), then Django, then templates and email files.

**Keep searching even if you found the spot the user named.** The user may not realize the same words appear elsewhere — in the navbar, a tooltip, a related form, an email template, an aria-label, or an error message. They might want every instance changed for consistency, or be fine changing only the one they mentioned. Either way, they need to *know*.

Show every match, grouped by where it lives in the user experience:

> Found `[old text]` in N places:
>
> **You mentioned this one:**
> - `src/react/src/components/SearchBar/SearchBar.jsx:42` — the search bar button label
>
> **You might not realize these exist too:**
> - `src/react/src/components/Header/MobileNav.jsx:18` — the mobile menu version of the same button
> - `src/django/api/views/search.py:104` — help text returned by the API
>
> Want to change all of them so the wording stays consistent, or just the one you mentioned? Reply with a list (e.g. "all", "1 and 2", "just the first").

**Edge cases:**
- **Zero matches** → ask the user for more context. The text may be interpolated across variables, pulled from a constants file, or in a translation file. Ask for a screenshot or page URL.
- **Translation file hit** (`messages/`, i18n directory): flag it. *"This text lives in a translation file. Changing the English version won't update other languages. Should I leave other languages alone, or remove them so they re-translate?"*

**Then check tests for the old text too.** Grep test files for the exact string:
- `src/react/src/__tests__/`
- `src/django/api/tests/`
- `src/e2e/` (Playwright)

If any test asserts on the old text (e.g., `screen.getByText('Search facilities')`), surface it:
> Heads up — N test(s) reference the old text and would fail in CI if we change the copy without updating them:
> - `src/react/src/__tests__/components/SearchBar.test.js:32`
>
> I'll update those alongside the copy change. OK? (yes / no)

If yes, include the test files in the Step 5 edit. If no, warn the user CI will fail and ask if they want to proceed anyway.

---

## Step 4 — Show the change (CHECKPOINT)

For each file to edit, show:

> `path/to/file.jsx:line`
> Before: `[full line as-is]`
> After:  `[full line with the change]`

Then:
> Apply this change? Reply 'go' to proceed, or tell me what to adjust.

Do not edit anything until the user says go.

---

## Step 5 — Create a fresh branch and apply the change

*Confidence frame for Levels 1/2:* "I'm pulling the latest version of the team's code so you start from a clean copy. Then I'll make a **branch** — your own copy of the code where you can change things safely."

- Pull main fresh
- Branch name: `OSDEV-####-copy-[short-slug]` (e.g., `OSDEV-2790-copy-rename-search-button`)
- Apply the edit to each confirmed file. Single-line edit per file. Do not touch adjacent code, comments, formatting, or imports.

---

## Step 6 — Commit and update release notes

*Gloss for Levels 1/2:* "A **commit** is a saved snapshot on your computer. Nothing is visible to anyone else yet."

- `git add` the changed files
- `git commit -m "[OSDEV-####] [one-line summary of the copy change]"`
- **Call the `release-notes` skill** (`.agent/skills/release-notes/SKILL.md`) to add the entry to `doc/release/RELEASE-NOTES.md`. Do not write the entry by hand.
- `git commit -m "[OSDEV-####] Update release notes"`

---

## Step 7 — Push to GitHub (CHECKPOINT)

*Gloss for Levels 1/2:* "**Pushing** uploads your local commits to GitHub. Others *could* see them, but no one is asked to review yet."

> Ready to upload your branch to GitHub. Push? (yes / no)

Wait. Then `git push -u origin HEAD`.

---

## Step 8 — Visual preview (CHECKPOINT)

Check if the local Docker stack is already running (`docker compose ps`).

- **If yes:** find the URL where the changed text appears. Show:
  > Preview your change live: http://localhost:6543/[specific page]
  > What you should see: the [button/label/etc.] now reads "[new text]" instead of "[old text]"
  > Look right? Reply 'looks good' or describe what's wrong.

- **If no:** offer it as a choice — don't force Docker setup just for a copy edit:
  > Local server isn't running. Two options:
  > 1. Start Docker (~3 min first run) so you can see the change live before opening the PR
  > 2. Skip preview — the file diff I showed earlier is your verification — and proceed straight to PR
  > Which? (1 / 2)

If 2, continue to PR. If 1, run `docker compose up -d`, wait for it to be healthy, then preview.

---

## Step 9 — Create the pull request (CHECKPOINT)

*Gloss for Levels 1/2:* "A **pull request (PR)** asks your teammates to review your branch and merge it into the shared main version."

**Generate the PR description by calling the `pr-description` skill** (`.agent/skills/pr-description/SKILL.md`). Pass it the diff and the OSDEV key. Do not write the description by hand.

Show:
> PR title: [OSDEV-####] [one-line summary]
> Files changed: [list]
> Create this PR? (yes / no)

Wait. Then `gh pr create` with the title and description from `pr-description`.

**Add a top-level PR comment:**
> /copy-ship orchestrator notes:
> - This is a copy-only change — no functional code modified
> - Files touched: [list]
> - Test files updated: [list, or "none"]
> - Translation files affected: [list, or "none"]
> - Curly-quote check: [pass / N/A]
> - Visual preview: [confirmed locally / skipped]

---

## Step 10 — Handoff

*Gloss for Levels 1/2:* "**Merging** means your change officially joins the main version of the code. That happens after review, not now."

Tell the user:
1. PR link — assign yourself as Assignee in GitHub (right sidebar → Assignees → your username)
2. Wait ~5 min for CodeRabbit auto-review
3. Run `/pr-health` to check review status
4. One-line summary of what was changed

End the run.

---

## What this skill does NOT do

- Does not change anything other than user-visible text — no logic, no styling, no data
- Does not write *new* tests — copy changes don't need new test coverage. (Existing tests that reference old text *are* updated to keep CI green; see Step 3.)
- Does not refactor adjacent code, fix formatting, or rename variables — even if they look messy
- Does not bulk-edit across the codebase without explicit per-file confirmation
- Does not touch translation files for non-English locales without asking
- Does not force Docker setup just for preview — offers it as a choice
- Does not push directly to main — always opens a PR for review
- Does not merge the PR — that happens after human review
- Does not auto-load on general edit language — must be invoked explicitly via the `/copy-ship` command
