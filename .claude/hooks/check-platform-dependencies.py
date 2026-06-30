#!/usr/bin/env python3
"""Analyze git changes for cross-cutting platform dependency risk.

Hook mode (stdin JSON from Claude Code):
  Used automatically before `git push` via .claude/settings.json
  (PreToolUse hook on the Bash tool).

Manual mode:
  .claude/hooks/check-platform-dependencies.py --manual [--base main]
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path(__file__).resolve().parent / "platform-dependencies.json"


@dataclass
class AreaMatch:
    area: dict
    matched_files: set[str] = field(default_factory=set)
    matched_keywords: set[str] = field(default_factory=set)


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def resolve_base_ref(explicit_base: str | None) -> str | None:
    if explicit_base:
        return explicit_base

    upstream = run_git(["rev-parse", "--abbrev-ref", "@{upstream}"])
    if upstream and run_git(["rev-parse", "--verify", upstream]):
        return upstream

    for candidate in ("origin/main", "main", "origin/master", "master"):
        if run_git(["rev-parse", "--verify", candidate]):
            return candidate
    return None


def collect_changed_files(base_ref: str | None, include_worktree: bool = True) -> list[str]:
    files: set[str] = set()

    if include_worktree:
        for args in (
            ["diff", "--name-only", "--diff-filter=ACMRT"],
            ["diff", "--name-only", "--cached", "--diff-filter=ACMRT"],
        ):
            output = run_git(args)
            if output:
                files.update(line.strip() for line in output.splitlines() if line.strip())

    if base_ref and run_git(["rev-parse", "--verify", base_ref]):
        output = run_git(["diff", "--name-only", f"{base_ref}...HEAD"])
        if output:
            files.update(line.strip() for line in output.splitlines() if line.strip())

    return sorted(files)


def load_diff_text(base_ref: str | None, include_worktree: bool = True) -> str:
    chunks: list[str] = []

    if include_worktree:
        for args in (
            ["diff", "--unified=0"],
            ["diff", "--cached", "--unified=0"],
        ):
            chunks.append(run_git(args))

    if base_ref and run_git(["rev-parse", "--verify", base_ref]):
        chunks.append(run_git(["diff", f"{base_ref}...HEAD", "--unified=0"]))

    return "\n".join(chunk for chunk in chunks if chunk)


def path_matches_pattern(path: str, pattern: str) -> bool:
    normalized = path.replace("\\", "/")
    if fnmatch.fnmatch(normalized, pattern):
        return True
    if "**" in pattern:
        regex = "^" + re.escape(pattern).replace(r"\*\*", ".*").replace(r"\*", "[^/]*") + "$"
        return re.match(regex, normalized) is not None
    return False


def find_area_matches(changed_files: Iterable[str], diff_text: str, areas: list[dict]) -> list[AreaMatch]:
    matches: list[AreaMatch] = []
    changed_list = list(changed_files)

    for area in areas:
        area_match = AreaMatch(area=area)

        for path in changed_list:
            for pattern in area.get("patterns", []):
                if path_matches_pattern(path, pattern):
                    area_match.matched_files.add(path)
                    break

        for keyword in area.get("keywords", []):
            if re.search(re.escape(keyword), diff_text, re.IGNORECASE):
                area_match.matched_keywords.add(keyword)

        if area_match.matched_files or area_match.matched_keywords:
            matches.append(area_match)

    return matches


def format_manual_report(matches: list[AreaMatch], changed_files: list[str], base_ref: str | None) -> str:
    lines = [
        "# Platform dependency check",
        "",
        f"Repository: {ROOT.name}",
        f"Base ref: {base_ref or '(working tree only)'}",
        f"Changed files: {len(changed_files)}",
        "",
    ]

    if not changed_files:
        lines.extend(
            [
                "No changed files detected.",
                "",
                "Tip: commit or stage changes, or pass `--base main` to compare against a branch.",
            ]
        )
        return "\n".join(lines)

    if not matches:
        lines.extend(
            [
                "No cross-cutting platform dependency areas were triggered.",
                "",
                "Changed files:",
                *[f"- {path}" for path in changed_files],
            ]
        )
        return "\n".join(lines)

    lines.append(f"Triggered areas: {len(matches)}")
    lines.append("")

    for match in matches:
        area = match.area
        lines.append(f"## {area['name']} ({area['id']})")
        lines.append(area["summary"])
        lines.append("")

        if match.matched_files:
            lines.append("Matched files:")
            for path in sorted(match.matched_files):
                lines.append(f"- {path}")
            lines.append("")

        if match.matched_keywords:
            lines.append("Matched diff keywords:")
            for keyword in sorted(match.matched_keywords):
                lines.append(f"- {keyword}")
            lines.append("")

        lines.append("Review checklist:")
        for question in area.get("review_questions", []):
            lines.append(f"- [ ] {question}")
        lines.append("")

        related_tests = area.get("related_tests", [])
        if related_tests:
            lines.append("Suggested tests:")
            for test_path in related_tests:
                lines.append(f"- `{test_path}`")
            lines.append("")

        related_jira = area.get("related_jira", [])
        if related_jira:
            lines.append("Related Jira bugs:")
            for key in related_jira:
                lines.append(f"- {key}: https://opensupplyhub.atlassian.net/browse/{key}")
            lines.append("")

    lines.extend(
        [
            "## All changed files",
            *[f"- {path}" for path in changed_files],
        ]
    )
    return "\n".join(lines)


def format_hook_messages(matches: list[AreaMatch], changed_files: list[str]) -> tuple[str, str]:
    area_names = ", ".join(match.area["name"] for match in matches)
    user_message = (
        f"Platform dependency check: {len(matches)} area(s) may be affected "
        f"({area_names}). Review the checklist before pushing."
    )

    agent_lines = [
        "Run the platform dependency review before pushing.",
        "",
        f"Changed files ({len(changed_files)}): " + ", ".join(changed_files[:20])
        + (" ..." if len(changed_files) > 20 else ""),
        "",
    ]

    for match in matches:
        area = match.area
        agent_lines.append(f"### {area['name']}")
        agent_lines.append(area["summary"])
        if match.matched_files:
            agent_lines.append("Matched files: " + ", ".join(sorted(match.matched_files)))
        if match.matched_keywords:
            agent_lines.append("Matched keywords: " + ", ".join(sorted(match.matched_keywords)))
        agent_lines.append("Checklist:")
        for question in area.get("review_questions", []):
            agent_lines.append(f"- {question}")
        tests = area.get("related_tests", [])
        if tests:
            agent_lines.append("Suggested tests: " + ", ".join(tests))
        jira = area.get("related_jira", [])
        if jira:
            agent_lines.append("Related Jira: " + ", ".join(jira))
        agent_lines.append("")

    agent_lines.extend(
        [
            "Manual rerun:",
            ".claude/hooks/check-platform-dependencies.py --manual",
            "",
            "If checklist items are addressed or not applicable, proceed with the push.",
        ]
    )
    return user_message, "\n".join(agent_lines)


def load_config() -> dict:
    with CONFIG_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def analyze(base_ref: str | None, include_worktree: bool = True) -> tuple[list[str], list[AreaMatch]]:
    config = load_config()
    changed_files = collect_changed_files(base_ref, include_worktree=include_worktree)
    diff_text = load_diff_text(base_ref, include_worktree=include_worktree)
    matches = find_area_matches(changed_files, diff_text, config["areas"])
    return changed_files, matches


def is_git_push(command: str) -> bool:
    return re.search(r"\bgit\s+push\b", command) is not None


def hook_mode(base_ref: str | None) -> int:
    command = ""
    try:
        stdin_data = sys.stdin.read().strip()
        if stdin_data:
            payload = json.loads(stdin_data)
            command = (payload.get("tool_input") or {}).get("command", "") or ""
    except (json.JSONDecodeError, AttributeError):
        pass

    # Only weigh in on `git push`; stay silent (no decision) for everything else
    # so normal Claude Code permission handling is untouched.
    if command and not is_git_push(command):
        return 0

    # Pre-push review must reflect only what is actually being pushed:
    # the outgoing commits from base_ref to HEAD. Dirty/staged worktree
    # files are intentionally excluded so they do not trigger the check.
    changed_files, matches = analyze(base_ref, include_worktree=False)

    if not matches:
        return 0

    user_message, agent_message = format_hook_messages(matches, changed_files)
    reason = f"{user_message}\n\n{agent_message}"
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    return 0


def manual_mode(base_ref: str | None) -> int:
    changed_files, matches = analyze(base_ref)
    print(format_manual_report(matches, changed_files, base_ref))
    return 1 if matches else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manual",
        action="store_true",
        help="Print a human-readable report instead of hook JSON.",
    )
    parser.add_argument(
        "--base",
        help="Git ref to compare against (default: upstream or origin/main).",
    )
    args = parser.parse_args()

    base_ref = resolve_base_ref(args.base)

    if args.manual or not sys.stdin.isatty():
        if args.manual:
            return manual_mode(base_ref)
        return hook_mode(base_ref)

    return manual_mode(base_ref)


if __name__ == "__main__":
    raise SystemExit(main())
