#!/usr/bin/env python3
"""
Sync delivery-roadmap.html with current Jira data.

Updates per-epic fields from Jira: status, health, dueDate, startDate,
execUpdate, teamMembers, funding, lastCommentDate.
Also updates LAST_SYNC to today's date.

Leaves untouched: aiSummary, epicSummary, backlogDone, backlogTotal,
priority, quarter, owner, title — these require human judgment.

Usage:
    JIRA_EMAIL=you@example.com JIRA_API_TOKEN=xxx python scripts/sync-roadmap.py
"""

import os
import re
import sys
from datetime import date

import requests

JIRA_BASE = "https://opensupplyhub.atlassian.net"
ROADMAP_PATH = "doc/roadmap/delivery-roadmap.html"

EPIC_KEYS = [
    "OSDEV-2566", "OSDEV-2554", "OSDEV-2568", "OSDEV-2628",
    "OSDEV-2661", "OSDEV-2638", "OSDEV-2555", "OSDEV-2559",
    "OSDEV-2546", "OSDEV-2677", "OSDEV-2675", "OSDEV-2553",
    "OSDEV-2548", "OSDEV-2673", "OSDEV-2543", "OSDEV-2270",
    "OSDEV-2676", "OSDEV-2653", "OSDEV-2655", "OSDEV-2656",
    "OSDEV-392",
]

JIRA_FIELDS = [
    "summary", "status", "assignee", "duedate",
    "customfield_10015",  # startDate
    "customfield_10498",  # Product Execution Update
    "customfield_10499",  # Project Health
    "customfield_10245",  # Funder
    "customfield_10465",  # Team Members
    "comment",
]

# Matches JS string values (handles escaped characters) or null
JS_STR_OR_NULL = r'(?:"(?:[^"\\]|\\.)*"|null)'
# Matches JS arrays of strings
JS_STR_ARRAY = r'\[(?:"(?:[^"\\]|\\.)*"(?:,"(?:[^"\\]|\\.)*")*)?\]'


def adf_to_text(node) -> str:
    """Convert Atlassian Document Format node to plain text."""
    if isinstance(node, str):
        return node
    if not isinstance(node, dict):
        return ""
    node_type = node.get("type", "")
    text = node.get("text", "")
    children = node.get("content", [])
    result = text + "".join(adf_to_text(c) for c in children)
    if node_type in ("paragraph",):
        result = result.rstrip("\n") + "\n"
    elif node_type == "listItem":
        result = "• " + result
    elif node_type == "hardBreak":
        result = "\n"
    return result


def js_escape(s: str) -> str:
    """Escape a plain string for embedding in a JS double-quoted string literal."""
    return (
        s.replace("\\", "\\\\")
         .replace('"', '\\"')
         .replace("\n", "\\n")
         .replace("\r", "")
    )


def fetch_jira(email: str, token: str) -> dict:
    """Return a dict keyed by epic key with the latest Jira field values."""
    jql = f"key in ({','.join(EPIC_KEYS)})"
    r = requests.post(
        f"{JIRA_BASE}/rest/api/3/search/jql",
        auth=(email, token),
        json={"jql": jql, "fields": JIRA_FIELDS, "maxResults": 50},
        timeout=30,
    )
    r.raise_for_status()

    result = {}
    for iss in r.json().get("issues", []):
        key = iss["key"]
        f = iss["fields"]

        health_obj = f.get("customfield_10499")
        exec_obj = f.get("customfield_10498")
        comments = (f.get("comment") or {}).get("comments", [])

        result[key] = {
            "status":          (f.get("status") or {}).get("name", ""),
            "health":          health_obj.get("value", "") if health_obj else "",
            "dueDate":         f.get("duedate") or None,
            "startDate":       f.get("customfield_10015") or None,
            "execUpdate":      adf_to_text(exec_obj).strip() if exec_obj else None,
            "teamMembers":     [m.get("displayName", "") for m in (f.get("customfield_10465") or [])],
            "funding":         [v.get("value", "") for v in (f.get("customfield_10245") or [])],
            "lastCommentDate": comments[-1]["created"][:10] if comments else None,
        }
    return result


def set_str_field(line: str, field: str, value) -> str:
    """Replace field:<JS string or null> in a JS object line."""
    replacement = f'null' if value is None else f'"{js_escape(value)}"'
    return re.sub(
        rf'{re.escape(field)}:{JS_STR_OR_NULL}',
        f'{field}:{replacement}',
        line,
    )


def set_array_field(line: str, field: str, values: list) -> str:
    """Replace field:[...] in a JS object line."""
    inner = ",".join(f'"{js_escape(v)}"' for v in values)
    return re.sub(
        rf'{re.escape(field)}:{JS_STR_ARRAY}',
        f'{field}:[{inner}]',
        line,
    )


def main():
    email = os.environ.get("JIRA_EMAIL", "").strip()
    token = os.environ.get("JIRA_API_TOKEN", "").strip()
    if not email or not token:
        print("ERROR: set JIRA_EMAIL and JIRA_API_TOKEN environment variables.", file=sys.stderr)
        sys.exit(1)

    print("Fetching Jira data...")
    jira = fetch_jira(email, token)
    print(f"  {len(jira)} epics fetched.")

    with open(ROADMAP_PATH, "r", encoding="utf-8") as fh:
        html = fh.read()

    today = date.today().isoformat()
    changes = []

    # --- LAST_SYNC ---
    sync_match = re.search(r'let LAST_SYNC = "([^"]+)"', html)
    if sync_match and sync_match.group(1) != today:
        html = re.sub(r'let LAST_SYNC = "[^"]+"', f'let LAST_SYNC = "{today}"', html)
        changes.append(f"LAST_SYNC: {sync_match.group(1)} → {today}")

    # --- Per-epic fields ---
    lines = html.split("\n")
    new_lines = []
    for line in lines:
        updated = line
        for key in EPIC_KEYS:
            if f'key:"{key}"' not in line:
                continue
            data = jira.get(key)
            if not data:
                break

            str_fields = [
                ("status",          data["status"] or None),
                ("health",          data["health"] or None),
                ("dueDate",         data["dueDate"]),
                ("startDate",       data["startDate"]),
                ("lastCommentDate", data["lastCommentDate"]),
                ("execUpdate",      data["execUpdate"]),
            ]
            for field_name, new_val in str_fields:
                # Extract current raw value from the JS line for change detection
                m = re.search(rf'{re.escape(field_name)}:({JS_STR_OR_NULL})', updated)
                if not m:
                    continue
                current_raw = m.group(1)
                new_raw = "null" if new_val is None else f'"{js_escape(new_val)}"'
                if current_raw != new_raw:
                    updated = set_str_field(updated, field_name, new_val)
                    changes.append(f"{key}.{field_name}: {current_raw[:60]} → {new_raw[:60]}")

            for field_name, new_vals in [("teamMembers", data["teamMembers"]),
                                          ("funding",     data["funding"])]:
                m = re.search(rf'{re.escape(field_name)}:({JS_STR_ARRAY})', updated)
                if not m:
                    continue
                current_raw = m.group(1)
                new_raw = "[" + ",".join(f'"{js_escape(v)}"' for v in new_vals) + "]"
                if current_raw != new_raw:
                    updated = set_array_field(updated, field_name, new_vals)
                    changes.append(f"{key}.{field_name} updated")
            break

        new_lines.append(updated)

    html = "\n".join(new_lines)

    if not changes:
        print("No changes — roadmap is already up to date.")
        return

    print(f"\n{len(changes)} change(s):")
    for c in changes:
        print(f"  • {c}")

    with open(ROADMAP_PATH, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"\nWrote {ROADMAP_PATH}")


if __name__ == "__main__":
    main()
