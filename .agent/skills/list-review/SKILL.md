---
name: list-review
description: >-
    Review a contributor facility-list upload end-to-end: annotate the
    ContriBot ~PROCESSED report with taxonomy error tags, apply the team's
    moderation bar, compute the error ratio against the reject threshold,
    and generate the finished contributor email (template merged, HTML for
    a single rich-text paste into Gmail). Replaces the manual chain of
    annotate → copy columns to sheet → notebook → merge template. Every tag
    it applies is a SUGGESTION the moderator reviews and can overrule. Use
    when a moderator asks to review a list or moderate an upload, or gives
    a list id / ~PROCESSED file / Drive link in a moderation context.
---

# List Review

You produce three artifacts for one uploaded facility list, in
`<output_dir>/<list-id>/`, each in BOTH markdown/CSV (the record) and HTML
(the readable view), rendered with the skill's own script:

```bash
python3 .agent/skills/_shared/md2html.py <in.md|in.csv> <out.html>
```

1. `tagged.csv` + `tagged.html` — **tagged rows only** (rows with a
   non-empty `error` or `duplicate_pair_id`), keyed by `rn` back to the
   source sheet. Do NOT transcribe untagged rows — on large lists that
   dominates the runtime for zero information; the full data lives in the
   source sheet. Review every row; record only the findings.
2. `summary.md` + `summary.html` — stats, ratio vs threshold,
   recommendation, checklist
3. `email.md` + `email.html` — the finished contributor email

**Your tags are suggestions, not decisions.** The moderator reviews every
one and removes the rows on the platform themselves. Say so in the report,
and flag anything you were unsure about rather than quietly resolving it.

## 0. Load the moderator config — required

Read `~/.config/os-hub/moderation-email.json` (shared with the
`moderation-email` skill). If it is missing or still contains placeholder
values, STOP and tell the moderator: copy
`.agent/skills/_shared/config.example.json` to that path and fill it from
the internal **Data Team Resources** Confluence page. Do not proceed with defaults — every document
ID, policy value and URL comes from the config; none are stored here.

Config keys used below: `docs.templates_doc_id`, `docs.rules_doc_id`,
`docs.taxonomy_sheet_id` (+ `gid`), `platform.base_url`,
`platform.monday_board_url`, `policy.reject_heuristic_pct` (nullable),
`policy.reject_heuristic_count` (nullable), `policy.second_rejection_cc`,
`output_dir`.

## 1. Get the data

Accept any of: a local CSV path, a Google Drive link/file id, or a bare
list id.

**Always establish the list id AND the list display name** (the name shown
on `<base_url>/lists/<id>` and in the Monday item) before generating the
email — the name fills `{List Name}` and the id names the output folder.
If either isn't derivable from the input, ask the moderator up front, in
the same message as any tab-access fallback question (one round-trip).

- Bare list id → search Drive for `title contains '<id>.~PROCESSED'`.
- Drive link/file id → call `get_file_metadata` FIRST: the file title
  (`<id>.~PROCESSED.<original-file-name>`) yields the list id without
  asking. Only ask for what the title doesn't give (usually just the
  display name).
- Drive spreadsheet → try `download_file_content` first (may return the
  full workbook); if you only get one tab and it isn't the data tab
  (Summary is usually first — you need the row-level Findings/data sheet),
  fall back to `read_file_content`, and if still blocked ask for the CSV or
  the specific tab. Never silently review the Summary tab as if it were
  rows.
- The workbook may have five sheets: Summary / Findings / Similarities /
  original / ~Fixes. Row numbers (`rn`) refer to the original spreadsheet
  rows (header = row 1, first data row = 2) — use these in contributor
  emails; the platform list page shows the same numbers. Anywhere the
  moderator is told to remove rows on the platform, give
  `number (facility name)` — names are immune to display-numbering drift.

## 2. Tag rows — taxonomy vocabulary

Tag the `error` column with comma-separated bare tags (no prefixes).
Canonical vocabulary and format live in the taxonomy sheet
(`docs.taxonomy_sheet_id`); that sheet wins over the summary below.

| Tag | Meaning |
| --- | --- |
| address_too_many / address_too_few | address over-detailed / under-detailed (under ~25 chars is suspect) |
| address_po_box | PO Box / Post Office in address — include "Post Box"/"POST BOX" variants (the pipeline's PO-box check misses these; catch them by eye) |
| multiple_addresses | more than one address in one row |
| country_address_mismatch | country value ≠ country in address (watch Macao/Hong Kong/Taiwan vs China) |
| name_incomplete / name_too_many | generic name ("Factory 1") / name stuffed with parent company etc. |
| multiple_names / repeated_names | two names in one cell / same name on multiple rows |
| pii_name / pii_address / pii_parent_company | personal names or contact details |
| dupe_upload / dupe_remove | duplicate pair: the row kept gets dupe_upload, the row to drop gets dupe_remove; both get the same letter in `duplicate_pair_id` (A, B, C…). If keep/remove is ambiguous, mark the pair and ask. |
| non_roman_characters_name/_address/_spt/_ftpt/_parent_company | non-Latin or mis-encoded characters, column-specific |
| missing_separators | missing vertical-bar/comma separators in spt / ftpt |
| spt_ftpt_values | values in the wrong column or not in the sector taxonomy |
| spelling_name/_address/_spt/_ftpt/_parent_company | spelling/typo issues |
| filler_text_spt/_ftpt/_now/_parent_company/_address | "N/A", "None", zeros-as-postal-code, other placeholders |
| number_of_workers | symbols (+, >, <), commas, or invalid/backwards ranges |

Check sector values against `api_sector` via the local anonymized dump when
unsure (`docker compose dbshell`) — the visible product wording is often
not a sector. facility_type/processing_type taxonomy:
`src/django/api/facility_type_processing_type.py`.

## 3. Judgment bar (apply, don't ask)

**Default posture: err on the side of removing or asking.** When a row is
borderline, tag it (= propose removal) or put it in the report's
ask-bucket with a recommendation — never silently dismiss. A false removal
costs a contributor a re-upload; a false accept puts bad data on the public
map and seeds duplicate OS IDs. Prefer the first failure mode.

**Core semantics: a row-level tag IS a proposed removal.** The
Remove-and-Approve email lists rows that were removed; there is no "kept
with feedback" lane for row errors. The judgment happens at tagging time:
don't tag trivial issues; once tagged, the row comes out and the email
tells the contributor how to fix and re-upload it. List-wide guidance (e.g.
a sector-column recommendation applying to every row) may ride along in the
email without implying those rows were removed — say so explicitly.

**The acceptance test for addresses:** accept when reasonably confident the
address is complete enough to give a definite and incontrovertible
location. Complete = street number and name, city/town, province/state,
postal code — with country-specific standards. Consult the rules doc's
per-country sections before tagging `address_too_few`; it covers Türkiye,
Europe/LatAm, India, Japan, Bangladesh and China, and those standards
differ enough that guessing produces wrong tags.

- Plus Codes (e.g. `9G8F+6W`) → not accepted as the address; tag unless
  street-level information accompanies the code.
- **Coordinates override the address test.** When every row carries valid
  latitude/longitude (plausible and in-country — verify), city-level
  "CITY, STATE" addresses are ACCEPTABLE, because coordinates override
  geocoding and the location is definite. Don't tag `address_too_few` on
  such rows; include a soft "add street addresses where available"
  enrichment line in the email instead. General rule: if it can be
  geocoded, or coordinates are supplied, it can be accepted.

**Specific rules:**

- PO Box in the address → remove, even if the rest is complete.
- Backwards or invalid worker ranges (e.g. `2101-2100`) → remove, don't
  guess.
- `spelling_name` / `spelling_address` → REMOVE. Spelling variants survive
  cleaning and won't auto-match, producing duplicate OS IDs. When unsure
  whether a variant is a typo or a legitimate local spelling, ask.
- `spelling_spt` / `spelling_ftpt` → list-wide feedback. These only fail
  taxonomy matching and carry no phantom-facility risk. Spell out
  abbreviations (RMG → Ready Made Garment).
- **Formulas in the file: inspect the contributor's ORIGINAL upload, not
  the ~PROCESSED report.** Uncached formulas render as BLANK in the report
  tabs while the platform ingests the raw formula text, so a review that
  reads only the report can pass a file whose formula fragments then reach
  public profiles. Check the contributor template sheet too.
- If `policy.reject_heuristic_pct` is set and the tagged-row share meets or
  exceeds it, OR `policy.reject_heuristic_count` is set and the absolute
  number of tagged rows meets or exceeds it, flag it and raise whole-list
  REJECT as the likely call. Either trigger alone is enough — the count
  floor catches large lists sitting under the percentage bar. These are
  **heuristics, not rules**: severity and kind of errors matter more than
  the count, and the moderator decides. If both are null, report the count
  with no threshold framing.
- Same-company multi-unit rows ("Plant 1 and 2", "Unit 4 & 5" in the name,
  one address) → KEEP, acceptable as-is, no tag and no split request. One
  company at distinct plots on separate rows is the CORRECT pattern, never
  a duplicate.
- TWO DIFFERENT company names in one name cell (slash-separated, "X Co Ltd
  / Y Co") → REMOVE, tag `multiple_names`; email copy = the templates doc's
  multiple-names block, pick-primary-or-split. Distinguish carefully from
  unit annotations of ONE company, which stay.
- Sector-only product-type rows → list-wide feedback, not removal.
- The cleaning step already fixes formatting silently (accents,
  punctuation, whitespace, comma spacing) — don't tag what it normalized.
- **Completeness sweep (ALWAYS, even when tagging from pipeline
  findings):** scan ALL rows for blank required cells (name, address,
  country). Pipeline findings are not exhaustive and have no missing-name
  check, so a findings-driven review inherits that blind spot.

## 4. Summary + recommendation

`summary.md` contains: rows, tagged rows, error ratio, scenario
(**Approved** = no errors / **Remove and approve** = some rows removed /
**Rejected (Feedback Phase)** = over the threshold or structural failure),
duplicate pairs table, and this checklist:

- [ ] Current moderation-pause guidance — confirm before approving or
      rejecting.
- [ ] Is this the contributor's **second rejection**? → cc
      `<policy.second_rejection_cc>`. This is about contributors who are
      struggling, not a literal lifetime count: check the dates, since old
      rejections followed by clean approvals are not a pattern.
- [ ] Update the Monday board entry (`<platform.monday_board_url>`) — the
      queue of record.
- [ ] Remove tagged rows on the list page before clicking Approve.
- [ ] After approval: work the Confirm/Reject queue for potential matches
      that could not be resolved automatically — move PENDING entries to
      their final state.

## 5. Generate the email

Fetch the canonical template text live from the Error Message Templates doc
(`docs.templates_doc_id`) so wording stays current. No template text is
stored in this skill.

- Scenario **Remove and approve** and scenario **Rejected (Feedback
  Phase)** each have their own subject line and body in that doc — use them
  verbatim.
- Body = the scenario's general template with `{List Name}` filled and
  `{error details}` replaced by one section per tag present, using the
  doc's per-error copy with real examples substituted (`Row {rn}:
  {actual value}` — 2–3 examples per error type, real rows from the list).
- Order error sections by severity/count (duplicates and address issues
  first).
- **Removed vs kept must be unmistakable.** When some tagged rows were
  KEPT, split the body: "Here is the error that led to a removal:" (only
  rows actually removed, each marked "(removed)"), then "The rest of your
  list is live as uploaded" introducing keep-tier suggestions with no
  `Error:` prefix. Never present a kept row under removal framing.
- **Rejecting on the platform needs a reason string too** — the reject
  action writes `status_change_reason`, separate from this email. The short
  canonical blurbs are in the rules doc (`docs.rules_doc_id`).
- Write `email.md` and render `email.html` with the skill's script so one
  browser copy pastes into Gmail with formatting intact.

## 6. Report back

In chat: scenario + tag count (threshold framing only if configured), the
checklist with any flags raised, and anything ambiguous for the moderator
to rule on (unfamiliar error patterns, borderline duplicates, PII judgment
calls). **Never send email or change list state yourself** — the moderator
reviews, pastes, sends, and clicks Approve/Reject on the platform.

**Artifact links (always, as the report's last section):** list every
created file as an absolute path, one per line, and auto-open the email for
the rich-text copy:

```bash
open <output_dir>/<id>/summary.html <output_dir>/<id>/email.html
open <output_dir>/<id>/
```

Include the list URL (`<base_url>/lists/<id>`) and the source Drive link
alongside the file paths.

### Canonical sources — two docs, know both

Both ids come from the config; neither is stored here.

1. **Error Message Templates** (`docs.templates_doc_id`) — the per-error
   email copy blocks and the two scenario templates.
2. **Moderation rules / templates doc** (`docs.rules_doc_id`) — duplicates
   the templates, and uniquely carries the summary scenario table (numbered
   error rows, which moderators cite by number), the short platform
   **rejection-reason blurbs**, and per-country address moderation
   practice.

**When fetching either doc, ask for an ordered list of headings first,**
then request the blocks you need. Asking only "does it cover X?" hides
everything outside your hypothesis.
