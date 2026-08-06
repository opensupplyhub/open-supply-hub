#!/usr/bin/env python3
"""Analyze git changes for cross-cutting platform dependency risk.

Hook mode (stdin JSON from Claude Code):
  Used automatically before `git push` via .claude/settings.json
  (PreToolUse hook on the Bash tool).

Manual mode:
  .claude/hooks/check-platform-dependencies.py --manual [--base main]

The migration DB-indexation checks are STATIC ONLY: they read migration file
text and match patterns. They never import, run, or apply migrations, and they
are skipped entirely unless a migration file is part of the pushed commits.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path(__file__).resolve().parent / "platform-dependencies.json"
MIGRATION_FILE_RE = re.compile(r"src/django/.+/migrations/\d{4}_[^/]+\.py$")
MIGRATION_INDEXATION_AREA_ID = "migration_db_indexation"


@dataclass
class AreaMatch:
    area: dict
    matched_files: set[str] = field(default_factory=set)
    matched_keywords: set[str] = field(default_factory=set)


@dataclass
class MigrationWarning:
    severity: str
    file: str
    message: str


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

    if not any(ch in pattern for ch in "*?"):
        return normalized == pattern

    # Build a slash-aware regex so `*` and `?` stay within a single path
    # segment while `**` is the only token allowed to cross directories.
    regex = re.escape(pattern)
    regex = regex.replace(r"\*\*/", "(?:.*/)?")
    regex = regex.replace(r"\*\*", ".*")
    regex = regex.replace(r"\*", "[^/]*")
    regex = regex.replace(r"\?", "[^/]")
    return re.fullmatch(regex, normalized) is not None


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


# ---------------------------------------------------------------------------
# Migration DB-indexation checks (static; migration-gated)
# ---------------------------------------------------------------------------


def migration_files_from(changed_files: Iterable[str]) -> list[str]:
    return sorted(
        path
        for path in changed_files
        if MIGRATION_FILE_RE.match(path.replace("\\", "/"))
    )


def read_migration_text(relative_path: str) -> str:
    """Read migration file text without executing anything.

    Prefers the working-tree copy; falls back to the committed HEAD blob.
    """
    absolute_path = ROOT / relative_path
    if absolute_path.is_file():
        return absolute_path.read_text(encoding="utf-8")
    return run_git(["show", f"HEAD:{relative_path}"])


def table_has_write_signal(content: str, table: str, models: list[str]) -> bool:
    """Return True only when the migration physically writes to the table.

    A metadata-only ``AlterField`` (help_text/verbose_name/choices) does not
    rewrite rows and does not fire the per-row indexing trigger, so it must not
    be flagged. Write signals are, purely by static text matching:

    - raw SQL DML/DDL against the physical table
      (``ALTER TABLE`` / ``UPDATE`` / ``INSERT INTO`` / ``DELETE FROM``);
    - Django operations that add, remove, or rename a physical column;
    - a data migration (``RunPython``) that references the model.
    """
    sql_signals = (
        rf"ALTER\s+TABLE\s+(?:ONLY\s+)?{re.escape(table)}\b",
        rf"UPDATE\s+{re.escape(table)}\b",
        rf"INSERT\s+INTO\s+{re.escape(table)}\b",
        rf"DELETE\s+FROM\s+{re.escape(table)}\b",
    )
    for pattern in sql_signals:
        if re.search(pattern, content, re.IGNORECASE):
            return True

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return False

    model_names = {model.casefold() for model in models}
    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if not isinstance(node.func.value, ast.Name) or node.func.value.id != "migrations":
            continue

        if node.func.attr in {"AddField", "RemoveField", "RenameField"}:
            model_name = next(
                (
                    keyword.value.value
                    for keyword in node.keywords
                    if keyword.arg == "model_name"
                    and isinstance(keyword.value, ast.Constant)
                    and isinstance(keyword.value.value, str)
                ),
                None,
            )
            if model_name is not None and model_name.casefold() in model_names:
                return True

        if node.func.attr == "RunPython":
            callback = (
                node.args[0]
                if node.args
                else next(
                    (
                        keyword.value
                        for keyword in node.keywords
                        if keyword.arg == "code"
                    ),
                    None,
                )
            )
            if callback is None:
                continue
            if isinstance(callback, ast.Name):
                callback = functions.get(callback.id, callback)
            for call in ast.walk(callback):
                if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute):
                    continue
                if call.func.attr != "get_model":
                    continue
                model_name = (
                    call.args[1]
                    if len(call.args) >= 2
                    else next(
                        (
                            keyword.value
                            for keyword in call.keywords
                            if keyword.arg == "model_name"
                        ),
                        None,
                    )
                )
                if (
                    isinstance(model_name, ast.Constant)
                    and isinstance(model_name.value, str)
                    and model_name.value.casefold() in model_names
                ):
                    return True

    return False


def trigger_lifecycle_ok(content: str, trigger_name: str) -> bool:
    drop_match = re.search(
        rf"DROP\s+TRIGGER(?:\s+IF\s+EXISTS)?\s+{re.escape(trigger_name)}\b",
        content,
        re.IGNORECASE,
    )
    create_match = re.search(
        rf"CREATE\s+TRIGGER\s+{re.escape(trigger_name)}\b",
        content,
        re.IGNORECASE,
    )
    if not drop_match or not create_match:
        return False
    return drop_match.start() < create_match.start()


def migration_indexation_reference(config: dict) -> tuple[str, str]:
    reference = next(
        (
            area.get("reference", {})
            for area in config.get("areas", [])
            if area.get("id") == MIGRATION_INDEXATION_AREA_ID
        ),
        {},
    )
    example_migration = reference.get(
        "example_migration",
        "src/django/api/migrations/0219_add_contributor_anonymise_in_paid_products.py",
    )
    pr_url = reference.get(
        "pr",
        "https://github.com/opensupplyhub/open-supply-hub/pull/1123",
    )
    return example_migration, pr_url


def analyze_migration_indexation(
    migration_files: list[str],
    config: dict,
) -> list[MigrationWarning]:
    indexed_tables = config.get("migration_indexation", {}).get("indexed_tables", {})
    if not indexed_tables or not migration_files:
        return []

    example_migration, pr_url = migration_indexation_reference(config)
    warnings: list[MigrationWarning] = []

    for relative_path in migration_files:
        content = read_migration_text(relative_path)
        if not content:
            continue

        written_tables = [
            table
            for table, table_config in indexed_tables.items()
            if table_has_write_signal(content, table, table_config.get("models", []))
        ]

        for table in sorted(written_tables):
            trigger_name = indexed_tables[table]["insert_update_trigger"]
            if not trigger_lifecycle_ok(content, trigger_name):
                warnings.append(
                    MigrationWarning(
                        severity="high",
                        file=relative_path,
                        message=(
                            f"Writes to indexed table `{table}` but does not drop and "
                            f"recreate `{trigger_name}` around the schema change. "
                            f"Without this, INSERT/UPDATE triggers can fire per-row "
                            f"reindexing during migration. Follow {example_migration} "
                            f"and {pr_url}."
                        ),
                    )
                )

        if re.search(r"UPDATE\s+api_[a-z_]+\s+SET\b", content, re.IGNORECASE):
            warnings.append(
                MigrationWarning(
                    severity="high",
                    file=relative_path,
                    message=(
                        "Contains a full-table `UPDATE ... SET` on an api_* table. "
                        "Prefer `ADD COLUMN ... NOT NULL DEFAULT <value>` (PostgreSQL 11+) "
                        f"to avoid rewriting every row. See {pr_url}."
                    ),
                )
            )

        for statement in re.finditer(r"ADD\s+COLUMN[\s\S]*?;", content, re.IGNORECASE):
            text = statement.group(0)
            if re.search(r"NOT\s+NULL", text, re.IGNORECASE) and not re.search(
                r"DEFAULT", text, re.IGNORECASE
            ):
                warnings.append(
                    MigrationWarning(
                        severity="high",
                        file=relative_path,
                        message=(
                            "Adds a `NOT NULL` column without a `DEFAULT`. This fails "
                            "on already-populated tables. Use `ADD COLUMN ... NOT NULL "
                            f"DEFAULT <value>` (metadata-only on PostgreSQL 11+). See "
                            f"{example_migration}."
                        ),
                    )
                )
                break

        if re.search(
            r"ALTER\s+COLUMN[\s\S]{0,120}SET\s+NOT\s+NULL",
            content,
            re.IGNORECASE,
        ) and re.search(r"UPDATE\s+api_[a-z_]+\s+SET\b", content, re.IGNORECASE):
            warnings.append(
                MigrationWarning(
                    severity="high",
                    file=relative_path,
                    message=(
                        "Uses nullable column + UPDATE backfill + SET NOT NULL pattern. "
                        "Replace with a single metadata-only `ADD COLUMN ... NOT NULL DEFAULT`. "
                        f"See {pr_url}."
                    ),
                )
            )

    return warnings


def attach_migration_indexation_area(
    matches: list[AreaMatch],
    migration_files: list[str],
    migration_warnings: list[MigrationWarning],
    config: dict,
) -> list[AreaMatch]:
    """Surface the indexation area only when a migration is being pushed."""
    if not migration_files:
        return matches

    area = next(
        (
            item
            for item in config.get("areas", [])
            if item.get("id") == MIGRATION_INDEXATION_AREA_ID
        ),
        None,
    )
    if area is None:
        return matches

    area_match = AreaMatch(area=area)
    area_match.matched_files.update(migration_files)
    for warning in migration_warnings:
        area_match.matched_files.add(warning.file)
    return [*matches, area_match]


def format_migration_warnings(warnings: list[MigrationWarning]) -> list[str]:
    if not warnings:
        return []

    lines = ["## Automated migration indexation checks", ""]
    for warning in warnings:
        lines.append(f"- **[{warning.severity}]** `{warning.file}`: {warning.message}")
    lines.append("")
    return lines


def format_manual_report(
    matches: list[AreaMatch],
    changed_files: list[str],
    base_ref: str | None,
    migration_warnings: list[MigrationWarning],
) -> str:
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

    if not matches and not migration_warnings:
        lines.extend(
            [
                "No cross-cutting platform dependency areas were triggered.",
                "",
                "Changed files:",
                *[f"- {path}" for path in changed_files],
            ]
        )
        return "\n".join(lines)

    if migration_warnings:
        lines.extend(format_migration_warnings(migration_warnings))

    if matches:
        lines.append(f"Triggered areas: {len(matches)}")
        lines.append("")

    for match in matches:
        area = match.area
        lines.append(f"## {area['name']} ({area['id']})")
        lines.append(area["summary"])
        lines.append("")

        reference = area.get("reference")
        if reference:
            if reference.get("pr"):
                lines.append(f"Reference PR: {reference['pr']}")
            if reference.get("example_migration"):
                lines.append(f"Example migration: `{reference['example_migration']}`")
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


def format_hook_messages(
    matches: list[AreaMatch],
    changed_files: list[str],
    migration_warnings: list[MigrationWarning],
) -> tuple[str, str]:
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

    if migration_warnings:
        agent_lines.append("### Automated migration indexation checks")
        for warning in migration_warnings:
            agent_lines.append(f"- [{warning.severity}] {warning.file}: {warning.message}")
        agent_lines.append("")

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


def analyze(
    base_ref: str | None,
    include_worktree: bool = True,
) -> tuple[list[str], list[AreaMatch], list[MigrationWarning]]:
    config = load_config()
    changed_files = collect_changed_files(base_ref, include_worktree=include_worktree)
    diff_text = load_diff_text(base_ref, include_worktree=include_worktree)
    matches = find_area_matches(changed_files, diff_text, config["areas"])

    # Indexation checks run ONLY when a migration file is part of the changes.
    migration_files = migration_files_from(changed_files)
    migration_warnings: list[MigrationWarning] = []
    if migration_files:
        migration_warnings = analyze_migration_indexation(migration_files, config)
        matches = attach_migration_indexation_area(
            matches, migration_files, migration_warnings, config
        )

    return changed_files, matches, migration_warnings


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
    changed_files, matches, migration_warnings = analyze(base_ref, include_worktree=False)

    if not matches:
        return 0

    user_message, agent_message = format_hook_messages(
        matches, changed_files, migration_warnings
    )
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
    changed_files, matches, migration_warnings = analyze(base_ref)
    print(format_manual_report(matches, changed_files, base_ref, migration_warnings))
    has_high_severity = any(warning.severity == "high" for warning in migration_warnings)
    return 1 if has_high_severity else 0


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
