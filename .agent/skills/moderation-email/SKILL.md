---
name: moderation-email
description: >-
    Generate the contributor feedback email from a moderator's OWN error
    tags on a ContriBot ~PROCESSED sheet. The moderator reviews row by row
    and fills the error (+ duplicate_pair_id) columns in the spreadsheet
    themselves, then pastes the sheet/tab link; this skill reads their tags
    and produces the finished email (canonical templates fetched at
    runtime, real row examples, HTML for one rich-text paste into Gmail).
    It performs NO moderation judgment: never add, remove, or second-guess
    tags. Use when a moderator asks to draft/generate a moderation or
    list-feedback email from a tagged sheet.
---

# Moderation Email (from the moderator's tags)

Input: a Google Sheets link to the tagged tab of a `~PROCESSED` list
report. Output: the finished contributor email (`email.md` + `email.html`)
in `<output_dir>/<list-id>/`.

## Prerequisites

- **Google Drive access from your agent** (the claude.ai Google Drive
  integration or equivalent) — steps below use `get_file_metadata` /
  `read_file_content` / Drive search. No Drive access? Download the
  tagged sheet as CSV yourself and give the skill the local file path;
  everything from parsing onward works the same.
- `python3` on PATH (the two helper scripts are dependency-free).
- `open` in step 5 is macOS; use your platform's equivalent
  (`xdg-open`, `start`) elsewhere.

## 0. Load the moderator config — required

Read `~/.config/os-hub/moderation-email.json`. If it is missing or
contains placeholder values, STOP and tell the moderator: copy
`config.example.json` from this skill's directory to that path and fill
it from the internal **Data Team Resources** Confluence page. Do not
proceed with defaults — every document ID, policy value, and URL comes
from the config; none of them are stored in this skill.

Config keys used below: `docs.templates_doc_id`, `docs.rules_doc_id`,
`docs.taxonomy_sheet_id` (+ `gid`), `docs.contribot_drive_folder_id`,
`platform.base_url`, `platform.monday_board_url`,
`policy.reject_heuristic_pct` (nullable),
`policy.reject_heuristic_count` (nullable),
`policy.second_rejection_cc`, `output_dir`.

## 1. Read the tagged sheet

- `get_file_metadata` on the file id first: the title
  (`<id>.~PROCESSED.<file-name>`) gives the **list id**.
- **List display name**: newer reports carry a metadata block at the top
  of the Summary sheet (list id / list name / contributor / upload date)
  — use it. Older reports don't; then ask the moderator (it's on their
  Monday item). If still unknown at generation time, write the
  placeholder as `==[ADD LIST NAME]==` — the renderer turns `==...==`
  into a bold yellow highlight that survives the paste into Gmail — and
  say so in the report.
- A bare list id instead of a link → search Drive for
  `title contains '<id>.~PROCESSED'`.
- `read_file_content` returns all tabs concatenated (large workbooks
  arrive as a saved tool-result file — even better). **Parse with the
  skill's parser in ONE call:**

  ```bash
  mkdir -p <output_dir>/<id>
  python3 <skill-dir>/parse_processed.py <dump-file> --csv <output_dir>/<id>/tagged.csv
  ```

  It returns JSON: tagged rows with all columns, the tag ratio, duplicate
  pairs resolved (letters, row-number refs, unpaired rows matched against
  the original tab), free-text pair annotations surfaced, and a pruning
  check. If no table has an `error` column, say so and stop — never
  invent tags.
- Row numbers (`rn`): header = spreadsheet row 1, first data row = 2 —
  the numbering contributors see in their own file and the convention
  ContriBot reports use. Use `rn` in the contributor email. For platform
  actions (removing rows on `<base_url>/lists/<id>`), always give
  `number (facility name)` pairs — names are immune to display-numbering
  drift (see OSDEV-2724 for why this rule exists).

## 2. The tags are the moderator's decisions — treat them as final

- NEVER add, drop, or reinterpret tags. The taxonomy vocabulary lives in
  the sheet at `docs.taxonomy_sheet_id`; if a tag doesn't match it or has
  no section in the templates doc, ask the moderator what they meant —
  don't guess.
- Tagged rows are rows the moderator removed (or will remove) — the
  email presents them as removed-with-fix-instructions per the standard
  flow.

## 3. Pick the template

Fetch the canonical template + per-error copy live from the Error
Message Templates doc (`docs.templates_doc_id`) at run time. No template
text is stored in this skill; the doc is the single source of truth.

There is a **second** doc (`docs.rules_doc_id`) that duplicates the
templates but carries several things nothing else does — read
[Canonical sources](#canonical-sources--two-docs-know-both) before
assuming the templates doc has what you need.

- Default scenario: **REMOVE AND APPROVE**.
- If `policy.reject_heuristic_pct` is set and the tagged-row share meets
  or exceeds it, OR `policy.reject_heuristic_count` is set and the
  absolute number of tagged rows meets or exceeds it, raise the
  possibility of **REJECTED (Feedback Phase)**. Either trigger alone is
  enough — the count floor exists because on a very large list a serious
  problem can sit well under the percentage bar. The thresholds are
  **heuristics, not rules**: they prompt the question, never decide it —
  severity and kind of errors matter more than the count, and the
  moderator's call is final in both directions. If the config leaves
  both null, report the count with no threshold framing.
- The moderator can always state the scenario directly — that wins.

## 4. Build the email

**Always start email.md with the internal scenario banner** — a `:::`
block the renderer turns into a loud color-coded box ABOVE the email
(red for reject, green for remove-and-approve) with a
copy-below-this-line divider:

```text
:::reject
- **[Open list <id> on OS Hub](<base_url>/lists/<id>)** → set it to **REJECT** — do NOT remove rows or Approve
- Rejection reason to paste: "<short blurb from the rules doc>"
- <N>/<total> rows tagged (<pct>%)
- Second rejection for this contributor? cc <policy.second_rejection_cc>
- Update the Monday entry to Rejected (<platform.monday_board_url>)
:::
```

(`:::approve` variant: remove the tagged rows — listed as
`number (facility name)` pairs — then click Approve; update Monday to
Approved; work the post-approval Confirm/Reject queue.)

- `{List Name}` filled; `{error details}` = one section per tag present,
  using the templates doc's copy with real examples substituted
  (`Row {rn}: {actual value}`, 2–3 per type; note "and rows X, Y, Z"
  when more).
- Duplicate pairs use the uploaded-facility / removed-facility format
  from the templates doc's duplicates section.
- Order sections by count/severity (dupes and address issues first).
- **Removed vs kept must be unmistakable.** The template's "Here are the
  errors we found" preamble makes every section read as an explanation of
  a removal. When some tagged rows were KEPT, split the body: "Here is
  the error that led to a removal:" (only rows actually removed, each
  marked "(removed)"), then "The rest of your list is live as uploaded"
  introducing keep-tier suggestions with no `Error:` prefix. Never
  present a kept row under removal framing — the contributor will
  believe live rows were deleted.
- **Rejecting on the platform needs a reason string too.** The reject
  action writes `status_change_reason`, which is separate from this
  email. The short canonical blurbs are in the rules doc
  (`docs.rules_doc_id`) under its rejection-message section — put the
  right one in the `:::reject` banner so the moderator has it at click
  time rather than hunting for it mid-action.
- **The second-rejection cc rule is about contributors who are
  struggling, not a lifetime count.** Check the dates before flagging it:
  old rejections followed by clean approvals are not a pattern and should
  not trigger a cc.
- **Address precision is usually a keep, not an error.** Check whether
  the address geocodes first (platform history, or the geocoder); one
  that resolves to ward or district level is a KEEP with optional
  precision feedback. Only tag it when the moderator did.
- Write `<output_dir>/<id>/email.md`, render with the skill's script so
  one browser copy pastes into Gmail with formatting intact:

  ```bash
  python3 <skill-dir>/md2html.py <output_dir>/<id>/email.md <output_dir>/<id>/email.html
  ```

## 5. Report

- One line: scenario + tag count (threshold framing only if configured).
- Reminders (informational, never blocking): second-rejection cc;
  Monday update.
- Auto-open the artifacts and list every path plus the list URL and
  source sheet link:

  ```bash
  open <output_dir>/<id>/email.html   # one-copy rich-text paste
  open <output_dir>/<id>/             # folder
  ```

Never send the email or change any list state — the moderator reviews,
pastes, sends, and clicks Approve/Reject on the platform.

## Canonical sources — two docs, know both

Both ids come from the config; neither is stored here.

1. **Error Message Templates** (`docs.templates_doc_id`) — the per-error
   email copy blocks and the two scenario templates.
2. **Moderation rules / templates doc** (`docs.rules_doc_id`) —
   duplicates the templates, and uniquely carries the summary scenario
   table (numbered error rows, which moderators cite by number), the
   short platform **rejection-reason blurbs**, and per-country address
   moderation practice.

**When fetching either doc, ask for an ordered list of headings first,**
then request the blocks you need. Asking only "does it cover X?" hides
everything outside your hypothesis — that is how the rejection-reason
blurbs stayed unnoticed through several list reviews.
