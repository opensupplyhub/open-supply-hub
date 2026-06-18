# Skill / sub-agent / command usage logging

Logs which Claude Code **skills**, **sub-agents**, and **slash commands** get used,
so we can see what's actually valuable. Wired up via `.claude/settings.json` hooks
that call `log_usage.py`.

## What gets logged

| Event | Hook | Captured |
| --- | --- | --- |
| Skill | `PreToolUse` (matcher `Skill`) | skill name |
| Sub-agent | `PreToolUse` (matcher `Agent`/`Task`) | sub-agent type |
| Slash command | `UserPromptSubmit` | command name (raw `/cmd`) |

Each event becomes one JSON line:

```json
{"ts":"2026-06-18T...Z","kind":"skill","id":"code-review","user_hash":"a1b2c3d4e5f6a7b8","session_id":"...","cwd":"..."}
```

- `kind` ∈ `skill` | `subagent` | `command`
- `id` — the skill / sub-agent / command name
- `user_hash` — **pseudonymous**: `sha256(SALT+identity)[:16]`, where `identity`
  is git `user.email` → git `user.name` → OS username (first one available). Lets us
  count *distinct users* without storing identities. A default `SALT` is built in
  (so setup needs only the URL); it's committed, so for stronger re-identification
  resistance on a small, known team, override it with a shared `OSHUB_USAGE_LOG_SALT`.

The hook **never blocks**: it writes locally, optionally fires a detached POST,
prints nothing, and always exits 0.

## Two destinations

### 1. Local file (always on, zero setup)
Appends to `.claude/usage-log.jsonl` (gitignored, per-developer). Aggregate any time:

```bash
# uses + distinct users per item
jq -r '[.kind,.id] | @tsv' .claude/usage-log.jsonl | sort | uniq -c        # uses
jq -r '[.kind,.id,.user_hash] | @tsv' .claude/usage-log.jsonl | sort -u \
  | cut -f1,2 | uniq -c                                                     # distinct users
```

### 2. Central Google Sheet (optional, team-wide aggregate)
If a sink URL is configured, each line is also POSTed (backgrounded, fail-soft)
to a Google Apps Script web app that maintains an **aggregate** sheet — counts only,
no per-event identity:

| kind | id | uses | distinct_users | last_used | user_hashes (hidden) |
| --- | --- | --- | --- | --- | --- |

**The URL is never committed** (this repo is public). The hook reads the URL + salt
from, in order: (1) the `OSHUB_USAGE_LOG_URL` / `OSHUB_USAGE_LOG_SALT` env vars, then
(2) a gitignored **`.claude/usage-sink.local`** file. If neither is present, logging
stays **local-only** — nothing breaks, you just don't contribute to the central sheet.

**Enable it — easiest, no terminal.** In Claude Code, run:

```
/setup-usage-logging
```

Paste the link you were given when it asks. The agent writes the (gitignored)
config for you and confirms — that's the whole setup. A salt is built in, so the
**link is the only thing you need.**

**Or do it by hand:**

```bash
cp .claude/usage-sink.local.example .claude/usage-sink.local
# paste the link into OSHUB_USAGE_LOG_URL
```

(Or `export OSHUB_USAGE_LOG_URL=...` in your shell — env vars win over the file.)

Don't have a link yet? Ask whoever owns the usage Sheet — until then logging stays
**local-only** (nothing breaks). Setting up the Sheet is a one-time admin task —
see `sheet-owner-setup.md`.

## Notes
- No secret is committed: the sink URL and salt come only from the env vars or the
  gitignored `.claude/usage-sink.local`.
- Hooks in a project `.claude/settings.json` run without per-use approval; the
  hook's working dir is the project root (`$CLAUDE_PROJECT_DIR`).
- Disable locally by removing the env var (drops to local-only) or by removing
  the hooks block from `.claude/settings.json`.
