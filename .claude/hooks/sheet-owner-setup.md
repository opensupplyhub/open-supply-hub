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
   gitignored `.claude/usage-sink.local`).
4. (Optional) A default salt is built into the logger, so the URL is all
   contributors need. Only pick + share a custom `OSHUB_USAGE_LOG_SALT` if you want
   stronger re-identification resistance — and then everyone must use the same one.

## Apps Script

Aggregate upsert — stores counts + a dedup hash set, never identities. Maintains
one row per `(kind, id)`:

| kind | id | uses | distinct_users | last_used | user_hashes (hidden) |
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

> Hide the `user_hashes` column — it exists only so the script can dedup distinct
> users. It holds pseudonymous hashes, never emails.

## Onboarding

Add the contributor `cp .claude/usage-sink.local.example .claude/usage-sink.local`
step (from `README.md`) to the OS Hub local-setup guide alongside the existing
`.env` step, so new devs opt in during setup without extra friction.
