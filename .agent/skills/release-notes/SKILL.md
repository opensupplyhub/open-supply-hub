---
name: release-notes
description: >-
    Update release notes entries in doc/release/RELEASE-NOTES.md.
    Use when the user asks to write, draft, add, or update release notes,
    or when preparing a new release entry.
---

# Writing Release Notes

## Gathering Context

Before writing the note, run these commands in parallel to understand the full scope of changes:

- `git log --oneline <base-branch>..HEAD`
- `git diff <base-branch>..HEAD --stat`
- `git diff <base-branch>..HEAD`
- `git log <base-branch>..HEAD --format="%B---"`

## File Location

- Release notes: `doc/release/RELEASE-NOTES.md`
- Template: `doc/release/RELEASE-NOTES-TEMPLATE.md`

New entries go at the **top** of the file, directly after the header block (lines 1–4).

## Steps

1. **Read the current release notes** to find the latest version number.
2. **Determine the new version** using semver:
    - Major feature release → bump minor (e.g. `2.19.0` → `2.20.0`)
    - Hotfix → bump patch (e.g. `2.18.0` → `2.18.1`)
3. **Gather changes** — ask the user for, or derive from git log / PR history:
    - New migrations and schema changes
    - Code/API changes
    - Architecture/environment changes
    - Bug fixes
    - New user-facing features
    - Required post-deployment commands
4. **Write the entry** following the format below.
5. **Make then concise.** Each bullet should include only the most important information, avoiding unnecessary details.
6. **Insert** the new entry after line 4 of `RELEASE-NOTES.md` (after the header), with a blank line before the next release.

## Entry Format

```markdown
## Release X.Y.Z

## Introduction

- Product name: Open Supply Hub
- Release date: _Provide release date_

### Database changes

#### Migrations

- <filename>.py - <What the migration does>.

#### Schema changes

- [OSDEV-XXXX](https://opensupplyhub.atlassian.net/browse/OSDEV-XXXX) - <Describe model/table changes>.

### Code/API changes

- [OSDEV-XXXX](https://opensupplyhub.atlassian.net/browse/OSDEV-XXXX) - <Describe code or API changes>.

### Architecture/Environment changes

- [OSDEV-XXXX](https://opensupplyhub.atlassian.net/browse/OSDEV-XXXX) - <Describe infra/devops changes>.

### Bugfix

- [OSDEV-XXXX](https://opensupplyhub.atlassian.net/browse/OSDEV-XXXX) - <Describe the fix>.

### What's new

- [OSDEV-XXXX](https://opensupplyhub.atlassian.net/browse/OSDEV-XXXX) - <Describe user-facing feature or change>.

### Release instructions

- Ensure that the following commands are included in the `post_deployment` command:
    - `migrate`
    - `reindex_database`
```

## Writing Rules

1. **Omit empty sections.** Only include sections that have content. Hotfix releases often only have `Bugfix` and `Release instructions`.
2. **Link Jira tickets** using `[OSDEV-XXXX](https://opensupplyhub.atlassian.net/browse/OSDEV-XXXX)` format.
3. **Prefix tags** when applicable:
    - `[Hotfix]` — for hotfix-specific items.
    - `[Follow-up]` — for follow-up work from a previous release.
4. **Migration entries** use the format: `* <filename>.py - <description>.`
5. **Be detailed.** Each bullet should explain _what_ changed and _why_, including endpoint paths, model names, field names, and behavioral effects.
6. **Release instructions** always include at minimum `migrate` and `reindex_database`. Add other commands (e.g. `reindex_locations_with_approved_claim`) only when the release requires them.
7. **Release date** — use the actual date if known, otherwise leave as `*Provide release date*`.
8. **Separate releases** with two blank lines between entries.
