---
description: Full OS Hub ticket pipeline — read ticket, plan (or use cached plan), implement, write tests, preview locally, open PR
argument-hint: OSDEV-#### (or paste a freeform idea — I'll route to ticket creation)
---

Invoke the [`ship` skill](../../.agent/skills/ship/SKILL.md) with arguments: $ARGUMENTS

The skill is the source of truth. This command is a thin wrapper so Claude Code users can trigger it via `/ship`.
