# Usage-sink Google Sheet — one-time owner setup

This is the **admin/owner** task to stand up the central usage Sheet. Regular
contributors don't need this — they just point at the resulting URL (see
`README.md`). Done once.

## Steps

1. In the target Google Sheet: **Extensions → Apps Script**, paste the code below, save.
2. **Deploy → New deployment → Web app**; *Execute as:* Me, *Who has access:* Anyone
   (the URL itself is the capability secret).
3. Share the web-app **URL out of band** (e.g. 1Password / DM) — never commit it.
   Contributors run `/setup-usage-logging` and paste it (it lands in their
   gitignored `.claude/usage-sink.local`). The URL is all they need — each user's
   identity is a random token generated automatically, so there's no salt to share.

## Apps Script

Aggregate upsert — stores counts + a dedup token set, never identities. Maintains
one row per `(kind, id)`:

| kind | id | uses | distinct_users | last_used | user_tokens (hidden) |
| --- | --- | --- | --- | --- | --- |

```javascript
const SHEET_NAME = 'usage';

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    const d = JSON.parse(e.postData.contents);
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(['kind', 'id', 'uses', 'distinct_users', 'last_used', 'user_tokens']);
    }
    const kind = d.kind || '', id = d.id || '', tok = d.user_token || '';
    const rows = sheet.getDataRange().getValues();
    let r = -1;
    for (let i = 1; i < rows.length; i++) {
      if (rows[i][0] === kind && rows[i][1] === id) { r = i + 1; break; }
    }
    if (r === -1) {
      sheet.appendRow([kind, id, 1, tok ? 1 : 0, d.ts || '', tok]);
    } else {
      const uses = Number(sheet.getRange(r, 3).getValue()) + 1;
      const tokens = String(sheet.getRange(r, 6).getValue() || '').split(',').filter(Boolean);
      let distinct = Number(sheet.getRange(r, 4).getValue());
      if (tok && tokens.indexOf(tok) === -1) { tokens.push(tok); distinct += 1; }
      sheet.getRange(r, 3, 1, 4).setValues([[uses, distinct, d.ts || '', tokens.join(',')]]);
    }
    return ContentService.createTextOutput('ok');
  } finally {
    lock.releaseLock();
  }
}
```

> Hide the `user_tokens` column — it exists only so the script can dedup distinct
> users. It holds the random per-user tokens (never names or emails).

## Onboarding

Add the contributor `cp .claude/usage-sink.local.example .claude/usage-sink.local`
step (from `README.md`) to the OS Hub local-setup guide alongside the existing
`.env` step, so new devs opt in during setup without extra friction.
