---
description: Answer "can OS Hub do X today?" or "is X on our site / docs / codebase?" questions for sales, customer success, partners, or leadership. Searches the codebase, Confluence, info site, and Jira. Returns paths to the answer ranked from "I can pull it now" to "would need to be built."
argument-hint: the stakeholder question (e.g., "Can OS Hub filter facilities by EU compliance?" or "Do we have a moderation page on the info site?")
---

Invoke the [`todays-functionality` skill](../../.agent/skills/todays-functionality/SKILL.md) with arguments: $ARGUMENTS

The skill is the source of truth. This command is a thin wrapper for explicit invocation.
