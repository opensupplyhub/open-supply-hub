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
- `user_hash` — **pseudonymous**: `sha256((SALT)+git user.email)[:16]`. Lets us
  count *distinct users* without storing identities. Not strong anonymity for a
  small, known email set — set `OSHUB_USAGE_LOG_SALT` (shared across the team) to
  make re-identification harder.

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

Setup (once, by the Sheet owner):

1. In the target Sheet: **Extensions → Apps Script**, paste the code below, save.
2. **Deploy → New deployment → Web app**; *Execute as:* Me, *Who has access:* Anyone (the URL is the capability secret).
3. Share the web-app URL + salt **out of band** — do NOT commit them.

Setup (once, per contributor — recommended, no shell editing):

```bash
cp .claude/usage-sink.local.example .claude/usage-sink.local
# edit .claude/usage-sink.local and paste the URL + salt you were given
```

That file is gitignored, so the secret never reaches the repo. (Alternatively,
export `OSHUB_USAGE_LOG_URL` / `OSHUB_USAGE_LOG_SALT` in your shell — env vars win
over the file.) **Use the same salt as everyone else**, or distinct-user counts break.

> Onboarding: add the `cp …` step above to the local-setup guide alongside the
> existing `.env` step, so new devs opt in during setup without extra friction.

```javascript
// Apps Script — aggregate upsert: stores counts + a dedup hash set, not identities.
const SHEET_NAME = 'usage';

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    const d = JSON.parse(e.postData.contents);
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(['kind', 'id', 'uses', 'distinct_users', 'last_used', 'user_hashes']);
    }
    const kind = d.kind || '', id = d.id || '', uh = d.user_hash || '';
    const rows = sheet.getDataRange().getValues();
    let r = -1;
    for (let i = 1; i < rows.length; i++) {
      if (rows[i][0] === kind && rows[i][1] === id) { r = i + 1; break; }
    }
    if (r === -1) {
      sheet.appendRow([kind, id, 1, uh ? 1 : 0, d.ts || '', uh]);
    } else {
      const uses = Number(sheet.getRange(r, 3).getValue()) + 1;
      const hashes = String(sheet.getRange(r, 6).getValue() || '').split(',').filter(Boolean);
      let distinct = Number(sheet.getRange(r, 4).getValue());
      if (uh && hashes.indexOf(uh) === -1) { hashes.push(uh); distinct += 1; }
      sheet.getRange(r, 3, 1, 4).setValues([[uses, distinct, d.ts || '', hashes.join(',')]]);
    }
    return ContentService.createTextOutput('ok');
  } finally {
    lock.releaseLock();
  }
}
```

> You can hide the `user_hashes` column — it exists only so the script can dedup
> distinct users. It holds pseudonymous hashes, never emails.

## Notes
- No secret is committed: the sink URL and salt come only from env vars.
- Hooks in a project `.claude/settings.json` run without per-use approval; the
  hook's working dir is the project root (`$CLAUDE_PROJECT_DIR`).
- Disable locally by removing the env var (drops to local-only) or by removing
  the hooks block from `.claude/settings.json`.
