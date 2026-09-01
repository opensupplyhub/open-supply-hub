# Shared skill files

Not a skill. Files here are used by more than one skill in
`.agent/skills/`, and live outside any single skill so that neither skill
depends on another's directory.

| File | Used by |
| --- | --- |
| `parse_processed.py` | `moderation-email` |
| `md2html.py` | `moderation-email`, `list-review` |
| [`config.example.json`](config.example.json) | `moderation-email`, `list-review` — both read the same per-moderator config at `~/.config/os-hub/moderation-email.json` |

## Config keys

Copy [`config.example.json`](config.example.json) to
`~/.config/os-hub/moderation-email.json` and fill it from the internal Data
Team Resources Confluence page. Every value is team-specific and
deliberately absent from this repository.

The example file is the authoritative shape — it is not reproduced here,
so there is only one copy to keep current. The table below says what each
key is for.

| Key | Used by |
| --- | --- |
| `docs.templates_doc_id` | both |
| `docs.rules_doc_id` | both |
| `docs.taxonomy_sheet_id`, `docs.taxonomy_sheet_gid` | both |
| `docs.contribot_drive_folder_id` | `moderation-email` |
| `platform.base_url`, `platform.monday_board_url` | both |
| `policy.reject_heuristic_pct`, `policy.reject_heuristic_count` | both — nullable; leave `null` to report counts with no threshold framing |
| `policy.second_rejection_cc` | both |
| `output_dir` | both |

## Referencing these files

From a SKILL.md, by repository-relative path, for example:

```bash
python3 .agent/skills/_shared/md2html.py email.md email.html
```

The leading underscore keeps this directory from reading as a skill in the
skills listing.

**Changing anything here affects every skill in the table above** — check
the others before editing, and keep the scripts free of team-specific
values (document ids, board ids, thresholds, contact details), which
belong in the per-moderator config.
