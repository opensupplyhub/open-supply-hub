---
name: setup-usage-logging
description: Turn on the optional central usage Sheet for skill/sub-agent/command logging by writing the local .claude/usage-sink.local config from a link the user was given. Use when the user wants to enable, connect, or set up usage logging / the usage sheet. Source of truth for the /setup-usage-logging command.
---

# Set up usage logging (the easy way)

Goal: get a non-technical user connected to the team's central usage Sheet in one
step — they paste the link they were given, you write the local config file for
them. No terminal commands, no file editing on their part.

Background: usage **logging already happens locally** for everyone (no setup). This
only adds the optional POST to the team's Google Sheet, which needs a private URL
that can't live in this public repo. See `.claude/hooks/README.md`.

## Step 1 — Get the link

The link may be passed as an argument. If it's empty or doesn't look like a URL
(`https://script.google.com/...`), ask:

> Paste the usage-logging link you were given (it starts with `https://`). If you
> don't have one, ask whoever owns the team's usage Sheet — until then your usage
> still logs locally, it just won't reach the shared sheet.

If they don't have a link, stop here and reassure them local logging still works.

## Step 2 — Write the config

Write (creating or updating) the file **`.claude/usage-sink.local`** at the repo
root with exactly:

```
OSHUB_USAGE_LOG_URL=<the link they pasted>
```

Notes:
- This file is **gitignored** — it never gets committed. Confirm that to the user.
- A salt is already built in, so the URL is the only value needed. Only add an
  `OSHUB_USAGE_LOG_SALT=...` line if the user explicitly says they were given a
  salt too (advanced; everyone must share the same one).
- If the file already exists, preserve any existing lines and just set/replace the
  `OSHUB_USAGE_LOG_URL` line.

## Step 3 — Confirm (plain language)

Tell the user, simply:

> ✅ Done — usage logging is connected. From now on, when you use a skill,
> command, or sub-agent, it quietly adds to the team's usage sheet. It's
> pseudo-anonymous (your name/email is never stored — just a scrambled tag so we
> can count distinct people), and it never slows anything down. Nothing else to do.

Do **not** echo the full URL back or repeat it anywhere it could be shared — treat
it like a password. Don't suggest committing the file.

## What you do NOT do
- Don't edit `.claude/settings.json` or the hook script — those already work.
- Don't put the URL anywhere except `.claude/usage-sink.local`.
- Don't require the user to open a terminal or run shell commands.
