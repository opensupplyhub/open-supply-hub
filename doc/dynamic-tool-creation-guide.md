# Automated Data Sync with GitHub Actions

A guide for building tools that automatically pull live data from an external source, update a file in a GitHub repository, and redeploy — on a recurring schedule, with no manual intervention.

> ### Important: GitHub Pages
>
> GitHub Pages is a great way to host an automated tool as a live, publicly accessible webpage — and it's free. However, **GitHub Pages supports only one published site per repository**, which means only one tool can be hosted via GitHub Pages from any single repository.
>
> **The `opensupplyhub/open-supply-hub` repository's GitHub Pages slot is already taken.** The OS Hub Product Delivery Roadmap is currently hosted here:
> `https://opensupplyhub.github.io/open-supply-hub/`
> It is deployed automatically via `.github/workflows/deploy-roadmap.yml` whenever a change is pushed to the `roadmap-delivery` branch.
>
> **Do not add a new GitHub Pages deployment workflow to this repository.** Adding one will conflict with the existing roadmap deployment and could break the live roadmap site. If you want to host a new tool using GitHub Pages, create a separate repository — each repository gets its own free Pages site. See the [Choosing How to Publish Your Tool](#choosing-how-to-publish-your-tool) section below for guidance.

---

## Choosing How to Publish Your Tool

Before building, answer one question: **does your tool need to be a rendered webpage (a dashboard), or does it just need to expose data?** The answer determines where it should live.

### If you need a rendered dashboard (HTML that a browser displays)

Use a **separate GitHub repository** with its own GitHub Pages site.

- Every GitHub repository gets a free Pages site at `https://opensupplyhub.github.io/<repo-name>/`
- There is no limit on the number of repos, so no limit on the number of Pages sites
- Example: create `opensupplyhub/os-hub-dashboards` → its Pages URL is `opensupplyhub.github.io/os-hub-dashboards/`
- Your sync workflow in *this* repo still runs the script and commits the updated file — the deploy step at the end just pushes the output to the separate repo instead of deploying from this one

This keeps dashboards isolated, independently deployable, and avoids any conflict with the existing roadmap Pages site.

### If you just need to share data (JSON, CSV, markdown)

Use the **raw GitHub URL** — no separate repo or hosting needed.

When the sync workflow commits an updated file to this repo, it is immediately accessible at:
```
https://raw.githubusercontent.com/opensupplyhub/open-supply-hub/<branch>/path/to/file.json
```

Anyone can fetch that URL and always get the latest version. This works well when:
- The output feeds into another tool, script, or API that consumes structured data
- You want to share a markdown report or CSV that someone opens directly
- A downstream dashboard (built elsewhere) pulls from this URL as its data source

**Raw URLs do not render HTML** — GitHub serves them as plain text. Only use this path for data files, not for webpages.

### Decision guide

| What you're building | Recommended approach |
|---|---|
| Dashboard / rendered webpage | New GitHub repo with its own Pages site |
| Data file consumed by another tool | Raw GitHub URL in this repo |
| Markdown report read in GitHub UI | Commit to this repo, link to the GitHub blob URL |

---

## What This Pattern Does

You have a file (HTML, JSON, markdown, etc.) that displays data sourced from an external system — a project tracker, a database, a CRM, an API. Instead of manually updating the file every time the source changes, you write a script that does the update automatically, and wire it to a GitHub Actions workflow that runs on a schedule.

The result: the file stays current, every change is tracked in git history, and no one has to remember to do anything.

---

## Real Example: OS Hub Delivery Roadmap

The OS Hub delivery roadmap (`doc/roadmap/delivery-roadmap.html`) is a standalone HTML file that displays the status, health, dates, owners, and execution updates for ~21 Jira epics. It was being updated manually by pulling data from Jira and editing the file by hand.

The automated version:
1. A Python script (`scripts/sync-roadmap.py`) fetches the current state of every epic from the Jira REST API
2. It diffs the fetched data against what is currently in the HTML file
3. If anything changed, it updates the file in place
4. A GitHub Actions workflow (`sync-roadmap.yml`) runs this script Monday–Friday at 7 AM UTC
5. If the file changed, the workflow commits and pushes the update
6. That push triggers a second workflow (`deploy-roadmap.yml`) which redeploys the file to GitHub Pages

The net effect: the roadmap on GitHub Pages is always within 24 hours of Jira reality, automatically.

---

## Architecture Overview

```
External API (Jira, etc.)
        │
        │  HTTP request with API token
        ▼
  Python sync script
        │
        │  reads current file, diffs, writes changes
        ▼
  Repository file (HTML/JSON/MD)
        │
        │  git commit + push (only if changed)
        ▼
  GitHub Actions (scheduled workflow)
        │
        │  triggers downstream workflow on push
        ▼
  Deployment (GitHub Pages, S3, etc.)
```

---

## The Two Files You Need to Build

### 1. The Sync Script (`scripts/sync-<tool>.py`)

A Python script that:
- Authenticates with the external API using credentials from environment variables
- Fetches the current data
- Reads the target file
- Compares new data to current file content and applies updates
- Writes the file back only if something changed
- Prints a clear summary of what changed (useful for CI logs)

**Key design rules:**
- Credentials come **only** from environment variables — never hardcoded
- The script exits cleanly with no writes if nothing changed (so git stays clean)
- Use regex or structured parsing to find and replace specific fields — do not regenerate the entire file, because that would overwrite any manually maintained content
- Fields that require human judgment (narrative summaries, manually curated text) should be left untouched

### 2. The Workflow (`workflows/sync-<tool>.yml`)

A GitHub Actions workflow that:
- Runs on a cron schedule (and also supports manual trigger via `workflow_dispatch`)
- Checks out the correct branch
- Installs Python dependencies
- Runs the sync script with secrets injected as environment variables
- Commits and pushes only if the file changed (checked with `git diff --cached --quiet`)

---

## Step-by-Step: Build a Sync Tool for a New Data Source

### Step 1 — Identify the data source and its API

You need:
- The base URL of the API
- The authentication method (most APIs use Basic Auth with an API token, or Bearer token)
- The specific endpoint(s) that return the data you want to display
- The field names or IDs for the data you care about

For Jira specifically:
- Base URL: `https://your-org.atlassian.net`
- Auth: Basic Auth with `email:api_token` (Base64 encoded by the `requests` library automatically)
- Search endpoint: `POST https://your-org.atlassian.net/rest/api/3/search/jql`
- Custom fields: look these up by fetching one issue and inspecting all `customfield_XXXXX` keys

### Step 2 — Map the data to your file format

For each field you want to keep in sync, figure out:
- What it's called in the API response
- How it appears in your file (the regex pattern needed to find and replace it)
- Whether it is safe to auto-update or whether a human should control it

Fields safe to auto-update: status, dates, boolean flags, numeric counts, owner names, simple list values.

Fields to leave alone: narrative summaries, AI-generated text, manually curated comments, anything that gets edited in the file directly.

### Step 3 — Write the sync script

Here is the general structure of any sync script following this pattern:

```python
#!/usr/bin/env python3
import os, re, sys, requests
from datetime import date

SOURCE_API = "https://api.example.com"
TARGET_FILE = "path/to/your/file"

def fetch_data(api_key: str) -> dict:
    """Call the external API and return normalized data."""
    r = requests.get(
        f"{SOURCE_API}/endpoint",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=30,
    )
    r.raise_for_status()
    # normalize to a dict keyed however makes sense for your file
    return {item["id"]: item for item in r.json()["items"]}

def apply_updates(content: str, data: dict) -> tuple[str, list]:
    """Apply data changes to file content. Returns (new_content, list_of_changes)."""
    changes = []
    # Use regex to find and replace fields
    # e.g. for a field like status:"OldValue" → status:"NewValue":
    for key, values in data.items():
        pattern = rf'id:"{re.escape(key)}".*?status:"([^"]*)"'
        # ... apply substitution and record changes
    return content, changes

def main():
    api_key = os.environ.get("API_KEY", "").strip()
    if not api_key:
        print("ERROR: set API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    data = fetch_data(api_key)

    with open(TARGET_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    new_content, changes = apply_updates(content, data)

    if not changes:
        print("No changes.")
        return

    for c in changes:
        print(f"  • {c}")

    with open(TARGET_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

if __name__ == "__main__":
    main()
```

### Step 4 — Write the workflow file

```yaml
name: Sync <Tool> from <Source>

on:
  schedule:
    - cron: '0 7 * * 1-5'   # adjust time and days as needed
  workflow_dispatch:          # always include this for manual runs

permissions:
  contents: write             # required to push commits

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: your-branch-name  # specify branch if not main

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - run: pip install requests

      - name: Run sync script
        env:
          API_KEY: ${{ secrets.API_KEY }}
        run: python scripts/sync-tool.py

      - name: Commit and push if changed
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add path/to/your/file
          if git diff --cached --quiet; then
            echo "Nothing to commit."
          else
            git commit -m "Auto sync $(date -u +%Y-%m-%d)"
            git push origin your-branch-name
          fi
```

### Step 5 — Store credentials as GitHub Secrets

1. In your GitHub repo, go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret** for each credential the script needs
3. Name them in ALL_CAPS (e.g. `JIRA_EMAIL`, `JIRA_API_TOKEN`)
4. Reference them in the workflow as `${{ secrets.SECRET_NAME }}`

**Never put API tokens, passwords, or email addresses directly in the workflow file or the script.** They are committed to git and visible to anyone with repo access.

### Step 6 — Test the script locally before pushing

```bash
export API_KEY="your-real-token"
python scripts/sync-tool.py
```

If it runs cleanly and prints "No changes" (or a valid list of changes), it is ready. If the workflow uses the same environment variable names, local testing and CI testing are equivalent.

### Step 7 — Trigger a manual run to verify end-to-end

After pushing, go to **GitHub → Actions → your workflow → Run workflow**. Watch the log output to confirm it fetches data, correctly diffs, and either commits or prints "Nothing to commit."

---

## Cron Schedule Reference

GitHub Actions cron runs in UTC. Some useful schedules:

| Schedule | Cron expression |
|---|---|
| Every weekday at 7 AM UTC | `0 7 * * 1-5` |
| Every day at midnight UTC | `0 0 * * *` |
| Every Monday at 9 AM UTC | `0 9 * * 1` |
| Every hour | `0 * * * *` |
| Every 6 hours | `0 */6 * * *` |

Cron expression format: `minute hour day-of-month month day-of-week`

Note: GitHub may delay scheduled workflows by up to 15 minutes during high load.

---

## How the Jira Sync Script Works (Technical Detail)

This section is the implementation-specific detail for the OS Hub roadmap sync. An AI assistant reading this file can use it as a reference when building a similar tool for a different data source.

### API endpoint

```
POST https://opensupplyhub.atlassian.net/rest/api/3/search/jql
Authorization: Basic base64(email:api_token)
Content-Type: application/json

{
  "jql": "key in (OSDEV-2566, OSDEV-2554, ...)",
  "fields": ["status", "duedate", "customfield_10498", ...],
  "maxResults": 50
}
```

### Jira custom field IDs (specific to opensupplyhub.atlassian.net)

| Field name in roadmap | Jira field ID |
|---|---|
| `health` | `customfield_10499` (select field, `.value`) |
| `execUpdate` | `customfield_10498` (ADF document, needs text extraction) |
| `startDate` | `customfield_10015` (date string) |
| `funding` | `customfield_10245` (array of select options, `.value`) |
| `teamMembers` | `customfield_10465` (array of user objects, `.displayName`) |
| `status` | `fields.status.name` (standard field) |
| `dueDate` | `fields.duedate` (standard date field) |
| `lastCommentDate` | `fields.comment.comments[-1].created[:10]` |

### ADF (Atlassian Document Format) to plain text

Jira stores rich text fields as a nested JSON tree (ADF). To convert to plain text for the roadmap:

```python
def adf_to_text(node) -> str:
    if isinstance(node, str):
        return node
    if not isinstance(node, dict):
        return ""
    node_type = node.get("type", "")
    text = node.get("text", "")
    children = node.get("content", [])
    result = text + "".join(adf_to_text(c) for c in children)
    if node_type == "paragraph":
        result = result.rstrip("\n") + "\n"
    elif node_type == "listItem":
        result = "• " + result
    elif node_type == "hardBreak":
        result = "\n"
    return result
```

### Regex patterns for updating JS object literals in the HTML

The roadmap data is stored as a JavaScript array of objects (not JSON). The regex patterns that safely update individual fields:

```python
# Match a JS string value or null
JS_STR_OR_NULL = r'(?:"(?:[^"\\]|\\.)*"|null)'
# Match a JS array of strings
JS_STR_ARRAY   = r'\[(?:"(?:[^"\\]|\\.)*"(?:,"(?:[^"\\]|\\.)*")*)?\]'

# Escape a Python string for embedding in a JS double-quoted string
def js_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "")

# Update a string field in a JS object line
def set_str_field(line, field, value):
    replacement = "null" if value is None else f'"{js_escape(value)}"'
    return re.sub(rf'{re.escape(field)}:{JS_STR_OR_NULL}', f'{field}:{replacement}', line)

# Update an array field in a JS object line
def set_array_field(line, field, values):
    inner = ",".join(f'"{js_escape(v)}"' for v in values)
    return re.sub(rf'{re.escape(field)}:{JS_STR_ARRAY}', f'{field}:[{inner}]', line)
```

### Fields deliberately left unsynced

These fields exist in the HTML but are not touched by the automated sync, because they require human judgment or are generated separately:

| Field | Reason |
|---|---|
| `aiSummary` | AI-generated narrative, manually reviewed |
| `epicSummary` | Written description, manually maintained |
| `backlogDone` / `backlogTotal` | Requires querying child tickets separately |
| `priority` | Set deliberately during quarterly planning |
| `quarter` | Set deliberately during quarterly planning |
| `owner` | Same as Jira assignee but formatted differently |

---

## Prompting an AI Assistant to Build This for a New Tool

If you want an AI assistant to build a version of this pattern for a different data source (e.g. Notion, Linear, Airtable, a REST API you own), give it this file as context and then describe your specific situation:

> "I have a [file type] at [path] that displays data from [source]. The file is updated by hand right now. The data fields I want to keep in sync automatically are [list]. The [source] API uses [auth method]. Here is an example API response: [paste example]. Build me a sync script following the pattern in the automated-sync-guide.md file, and a GitHub Actions workflow to run it daily."

The more specific you are about:
- Which fields to sync vs. which to leave alone
- The format of the file (JSON, HTML with embedded JS, markdown, etc.)
- The exact API endpoint and response shape
- The schedule you want (daily, weekdays only, hourly, etc.)

...the better the output will be. Paste or link this guide file so the assistant understands the architecture and can follow the same conventions.

---

## Files in This Repository

| File | Purpose |
|---|---|
| `scripts/sync-roadmap.py` | The Jira sync script for the OS Hub delivery roadmap |
| `.github/workflows/sync-roadmap.yml` | Scheduled workflow: runs Mon–Fri 7 AM UTC |
| `.github/workflows/deploy-roadmap.yml` | Deployment workflow: triggers on push to `roadmap-delivery`, deploys to GitHub Pages |
| `doc/roadmap/delivery-roadmap.html` | The roadmap file that gets updated |
