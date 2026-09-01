# Shared skill files

Not a skill. Files here are used by more than one skill in
`.agent/skills/`, and live outside any single skill so that neither skill
depends on another's directory.

| File | Used by |
| --- | --- |
| `parse_processed.py` | `moderation-email` |
| `md2html.py` | `moderation-email`, `list-review` |
| `config.example.json` | `moderation-email`, `list-review` — both read the same per-moderator config at `~/.config/os-hub/moderation-email.json` |

Referenced from a SKILL.md by repository-relative path, for example:

```bash
python3 .agent/skills/_shared/md2html.py email.md email.html
```

The leading underscore keeps this directory from reading as a skill in the
skills listing.

**Changing anything here affects every skill in the table above** — check
the others before editing, and keep the scripts free of team-specific
values (document ids, board ids, thresholds, contact details), which
belong in the per-moderator config.
