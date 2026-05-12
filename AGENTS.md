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

## Agents & skills

| Task | Tool |
|---|---|
| Implement a Jira ticket end-to-end (code + tests + PR description) | [implementer](.cursor/agents/implementer.md) subagent |
| Plan a Jira ticket before implementation | [ticket-planner](.cursor/agents/ticket-planner.md) subagent |
| Scan all codebase layers for a ticket's impact | [codebase-explorer](.cursor/agents/codebase-explorer.md) subagent |
| Write a PR description | [pr-description](.agents/skills/pr-description/SKILL.md) skill |
| Update release notes | [release-notes](.agents/skills/release-notes/SKILL.md) skill |
