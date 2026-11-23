#!/usr/bin/env python3
"""Lint Django migrations for missing lock timeouts.

Usage: lint_migrations.py <migration file> [...]

Schema-altering operations (AddField, AlterField, index and constraint
changes, DDL in RunSQL) take ACCESS EXCLUSIVE locks. On a busy table the
ALTER queues behind every open transaction and every later query queues
behind the ALTER, which can stall production for as long as the longest
running query (see OSDEV-3462 review history; the house convention since
0274 is an explicit `SET LOCAL lock_timeout` as the migration's first
operation so the ALTER gives up instead of stalling the site).

A migration that only creates or deletes whole models is exempt: the
lock is on a table no traffic reads yet (or a table being removed).
A migration may opt out with a comment containing `lint: no-lock-timeout`
next to a justification.

Exit status: 0 when every file passes, 1 otherwise. Files that do not
exist (deleted in the diff) are skipped.
"""
import ast
import re
import sys
from pathlib import Path

# Operations that alter an existing table and therefore need a lock
# timeout. CreateModel/DeleteModel/RenameModel and the *state-only*
# operations are deliberately absent.
ALTERING_OPERATIONS = {
    'AddField',
    'RemoveField',
    'AlterField',
    'RenameField',
    'AddIndex',
    'RemoveIndex',
    'RenameIndex',
    'AddConstraint',
    'RemoveConstraint',
    'AlterUniqueTogether',
    'AlterIndexTogether',
    'AlterModelTable',
}

# DDL in raw SQL that takes the same locks.
DDL_PATTERN = re.compile(
    r'\b(ALTER\s+TABLE|CREATE\s+(UNIQUE\s+)?INDEX|DROP\s+INDEX|'
    r'DROP\s+TABLE|ADD\s+CONSTRAINT)\b',
    re.IGNORECASE,
)

OPT_OUT = 'lint: no-lock-timeout'


def call_name(node):
    """Name of a called operation: migrations.AddField(...) -> AddField."""
    func = node.func
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return None


def sql_strings(node):
    """String literals passed to a RunSQL call (positional or sql=)."""
    values = list(node.args)
    values.extend(kw.value for kw in node.keywords if kw.arg == 'sql')
    out = []
    for value in values:
        for sub in ast.walk(value):
            if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                out.append(sub.value)
    return out


def altering_operations(source):
    """Names of schema-altering operations found in the file."""
    tree = ast.parse(source)
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = call_name(node)
        if name in ALTERING_OPERATIONS:
            found.append(name)
        elif name == 'RunSQL':
            for sql in sql_strings(node):
                if DDL_PATTERN.search(sql):
                    found.append('RunSQL (DDL)')
                    break
    return found


def main(paths):
    failures = []
    for raw in paths:
        path = Path(raw)
        if not path.exists():
            continue
        source = path.read_text()
        if OPT_OUT in source:
            continue
        operations = altering_operations(source)
        if operations and 'lock_timeout' not in source:
            failures.append((path, sorted(set(operations))))
    for path, operations in failures:
        print(
            f'{path}: schema-altering operations '
            f'({", ".join(operations)}) without a lock timeout.\n'
            f'  Open the migration with\n'
            f"    migrations.RunSQL(\n"
            f"        sql=\"SET LOCAL lock_timeout = '5s';\",\n"
            f'        reverse_sql=migrations.RunSQL.noop,\n'
            f'    )\n'
            f'  (see 0284_zone_set_last_upload_sha256.py), or justify an\n'
            f'  opt-out with a comment containing "{OPT_OUT}".'
        )
    if failures:
        return 1
    print(f'lint_migrations: {len(paths)} file(s) checked, no findings.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
