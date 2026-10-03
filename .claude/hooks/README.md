# Skill / sub-agent / command usage logging

Logs which Claude Code **skills**, **sub-agents**, and **slash commands** get used,
so we can see what's actually valuable. Wired up via `.claude/settings.json` hooks
that call `log_usage.py`.

> **Scope: Claude Code sessions only.** These are Claude Code hooks, so they fire
> only inside Claude Code sessions running in this repo (CLI / IDE extension /
> desktop app), for users who've pulled a checkout that has them. They capture
> *nothing* for developers not using Claude Code — and that's inherent, since
> skills / sub-agents / commands only exist within Claude Code. So the numbers
> reflect the **Claude Code user population**, not all OS Hub devs.

## What gets logged

| Event | Hook | Captured |
| --- | --- | --- |
| Skill | `PreToolUse` (matcher `Skill`) | skill name |
| Sub-agent | `PreToolUse` (matcher `Agent`/`Task`) | sub-agent type |
| Slash command | `UserPromptSubmit` | command name (raw `/cmd`) |

Each event becomes one JSON line:

```json
{"ts":"2026-06-18T...Z","kind":"skill","id":"code-review","user_token":"3f9c1a7b8d2e45061b2c3d4e5f607189","session_id":"..."}
```

- `kind` ∈ `skill` | `subagent` | `command`
- `id` — the skill / sub-agent / command name
- `user_token` — a **random** per-user token, minted once and reused forever
  (128-bit, stored locally at `~/.claude/oshub-usage-uid`). It is **not** derived from
  your name/email, so there's nothing to reverse — genuinely anonymous, while still
  letting us count *distinct users*. No salt, no setup; the only thing you ever
  provide is the URL.

**Deliberately not captured:** names, emails, file paths/`cwd`, prompt text, or
arguments — only the items above. Keeps it anonymous end-to-end.

The hook **never blocks**: it writes locally, optionally fires a detached POST,
prints nothing, and always exits 0.

## Two destinations

### 1. Local file (always on, zero setup)
Appends to `.claude/usage-log.jsonl` (gitignored, per-developer). Aggregate any time:

```bash
# uses + distinct users per item
jq -r '[.kind,.id] | @tsv' .claude/usage-log.jsonl | sort | uniq -c        # uses
jq -r '[.kind,.id,.user_token] | @tsv' .claude/usage-log.jsonl | sort -u \
  | cut -f1,2 | uniq -c                                                     # distinct users
```

### 2. Central Google Sheet (optional, team-wide aggregate)
If a sink URL is configured, each line is also POSTed (backgrounded, fail-soft)
to a Google Apps Script web app that maintains an **aggregate** sheet — counts only,
no per-event identity:

| kind | id | uses | distinct_users | last_used |
| --- | --- | --- | --- | --- |

**The URL is never committed** (this repo is public). The hook reads it from, in
order: (1) the `OSHUB_USAGE_LOG_URL` env var, then (2) a gitignored
**`.claude/usage-sink.local`** file. If neither is present, logging stays
**local-only** — nothing breaks, you just don't contribute to the central sheet.

**Enable it — easiest, no terminal.** In Claude Code, paste the link right into the
command:

```
/setup-usage-logging https://script.google.com/macros/s/XXXX/exec
```

The agent writes the (gitignored) config for you and confirms — that's the whole
setup. (You can also run it bare — `/setup-usage-logging` — and it'll ask for the
link.) The **link is the only thing you need** — your logging identity is a random
token generated automatically.

**Or do it by hand:**

```bash
cp .claude/usage-sink.local.example .claude/usage-sink.local
# paste the link into OSHUB_USAGE_LOG_URL
```

(Or `export OSHUB_USAGE_LOG_URL=...` in your shell — env vars win over the file.)

Don't have a link yet? Ask whoever owns the usage Sheet — until then logging stays
**local-only** (nothing breaks). Setting up the Sheet is a one-time admin task —
see `sheet-owner-setup.md`.

## Privacy & security (assessed)

We reviewed this for compliance/SOC 2 and rated it **low risk**:

- **Anonymous & minimal** — only the tool/skill/command name + a random per-user
  token + timestamp are recorded. Never names, emails, file paths, prompt text, or
  arguments.
- **Write-only sink** — the Sheet endpoint only accepts writes (`doPost` returns
  `ok`); there is no read path, so nothing can be read back or extracted through it.
- **Non-sensitive data** — internal tool-adoption metrics, not customer data, not a
  system of record, not a control.
- **Residual risk = integrity, low-consequence** — the endpoint is deployed public
  ("Anyone"), so in principle the counts could be spammed/skewed. For an internal
  metric that's minor, and it's mitigated by rotating the URL if it's ever abused.
  It can be tightened to org-only later (that would require authenticating the hook).
- **Opt-in & local-first** — central posting only happens if a user supplies the URL;
  otherwise everything stays in the local, gitignored file and never leaves the machine.
- Recorded in the data-flow inventory.

## Notes
- No secret is committed: the sink URL comes only from the env var or the gitignored
  `.claude/usage-sink.local`.
- Hooks in a project `.claude/settings.json` run without per-use approval; the
  hook's working dir is the project root (`$CLAUDE_PROJECT_DIR`).
- Disable locally by removing the env var (drops to local-only) or by removing
  the hooks block from `.claude/settings.json`.
