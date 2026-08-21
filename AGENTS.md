# Agents Quick Start Guide

## Repository Structure

Those are the main directories in the project, other ones are not relevant for the agents:

- `doc` - all the documentation for the project, including the architecture
- `scripts` - helper scripts to run specific tasks and commands
- `deployment` - infra configuration and deployment scripts
- `src` - source code for the for different services and parts of the system
    - `anon-tools` - anonymization tools used to anonymize the database for testing and development purposes
    - `django` - Django backend, this our main API Gateway and backend for the system
    - `dedupe-hub` - dedupe hub, this is a tool that helps us deduplicate the data, connects with the Django backend and Kafka for matching and deduplication
    - `e2e` - end to end tests for the system, currently NOT being developed in this repo
    - `logstash` - logstash, this is a tool that helps us index the data into OpenSearch
    - `react` - React frontend, this is the main frontend for the system

## Running the system

IMPORTANT: Use docker compose to run the system, don't run the commands directly.

- To run the system in development mode, you can use the following command:

```bash
docker compose up -d
```

## Testing

- Use docker compose to run the tests. For example, to run the UI tests you can use the following command:

```bash
docker compose exec react yarn test --watchAll=false
```

- To run the tests for the Django backend, you can use the following command:

```bash
docker compose exec django python manage.py test
```

## Data moderation

- To generate a contributor feedback email from a moderator's own error tags on a ContriBot ~PROCESSED sheet, use the [moderation-email](.agent/skills/moderation-email/SKILL.md) skill. It requires a per-moderator config file (see the skill's `config.example.json`) and the Google Drive integration; it never adds or changes tags and never sends email.

## Release notes & PR descriptions

- To write the description for each PR, use the [pr-description](.agent/skills/pr-description/SKILL.md) skill.
- To update the GitHub engineering release notes, use the [release-notes](.agent/skills/release-notes/SKILL.md) skill.
- To create Confluence release notes and a Slack post draft, use the [confluence-release-notes](.agent/skills/confluence-release-notes/SKILL.md) skill.

### Pull request template

IMPORTANT: Every PR body must follow the repository template at [pull_request_template.md](pull_request_template.md). Read that file before drafting a PR description, and reproduce its sections in order with the guidance HTML comments removed:

1. `## Jira Ticket` — link as `[OSDEV-123](https://opensupplyhub.atlassian.net/browse/OSDEV-123)`, derived from the branch name when possible.
2. `## Summary of Changes` — what changed and why, including the root cause found and the approach taken.
3. `## Type of Change` — check every box that applies.
4. `## Testing` — how the change was verified; screenshots or a recording for UI changes, requests/queries for backend changes.
5. `## Known TODO Items` — deferred work, follow-up tickets, known limitations, or `None`.
6. `## Checklist` — keep the Implementation / Testing & Validation / Documentation & Communication / Final Review subsections.

Do not invent, drop, or reorder sections. Leave a section as `N/A` only when it genuinely does not apply. Never check a checklist box on the user's behalf unless the work was actually verified — leave it unchecked and flag it instead.

`pull_request_template.md` is the single source of truth: if it changes, follow the file rather than the summary above.

IMPORTANT: Before creating a PR, always check whether `doc/release/RELEASE-NOTES.md` has been updated on the current branch. If it has not been updated, prompt the user to update it before opening the PR.

IMPORTANT: When the user asks to add, update, or write a release notes entry, always use the [release-notes](.agent/skills/release-notes/SKILL.md) skill.

## Public repository hygiene

This repository is public. Before committing, verify the diff contains no:

- secrets, tokens, or credentials of any kind;
- internal document, spreadsheet, or shared-drive folder identifiers
  (publishing an ID can make a link-shared document effectively public);
- internal project-management identifiers (board or channel names/IDs);
- internal policy thresholds or escalation/routing rules;
- staff names or contact details in code, configuration, or comments.

When a change needs such a value at runtime, externalize it: read it from
an uncommitted per-user configuration file or environment variable, commit
a placeholder `config.example`, and document where teammates obtain the
real values internally. Prefer fetching internal content (e.g. document
text) at runtime over embedding it. When unsure whether something is safe
to publish, ask before committing.
