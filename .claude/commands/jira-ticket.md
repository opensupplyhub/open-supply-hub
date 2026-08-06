---
description: Draft, review, and file Jira Stories or Epics in OS Hub's house style — User Story / Requirements / Given-When-Then Acceptance Criteria, then prompt for parent, priority, labels and other Jira fields before filing in OSDEV.
argument-hint: customer ask / feature request / existing draft / persona+situation / "story" or "epic" / nothing (will ask)
---

Invoke the [`jira-ticket-writer` skill](../../.agent/skills/jira-ticket-writer/SKILL.md) with arguments: $ARGUMENTS

The skill is the source of truth. This command is a thin wrapper for explicit invocation.
