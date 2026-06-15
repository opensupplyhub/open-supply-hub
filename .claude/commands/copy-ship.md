---
description: OS Hub copy edit pipeline — change visible text on the website end-to-end. For text-only changes (button labels, form text, navbar items, error messages, etc.). For anything functional, use /ship instead.
argument-hint: OSDEV-#### (or describe the copy change in plain English)
---

Invoke the [`copy-ship` skill](../../.agent/skills/copy-ship/SKILL.md) with arguments: $ARGUMENTS

The skill is the source of truth. This command is a thin wrapper so Claude Code users can trigger it via `/copy-ship`.
