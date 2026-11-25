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

# The timeout itself, recognised only in SQL a RunSQL operation
# actually executes - never in a comment or docstring.
TIMEOUT_PATTERN = re.compile(
    r'SET\s+LOCAL\s+lock_timeout', re.IGNORECASE
)

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


def module_strings(tree):
    """Module-level NAME = "..." assignments, so RunSQL(sql=SQL) resolves.

    Without this, SQL held in a constant is invisible and its DDL is
    never matched.
    """
    out = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not (isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                out[target.id] = node.value.value
    return out


def sql_arguments(node):
    """The `sql` arguments of a RunSQL call: positional first, or sql=.

    reverse_sql is deliberately excluded: it runs on the way back, so
    its DDL is not what the forward migration takes a lock for.
    """
    values = []
    if node.args:
        values.append(node.args[0])
    values.extend(kw.value for kw in node.keywords if kw.arg == 'sql')
    return values


def resolve_sql(values, constants):
    """(literal SQL strings, True if any argument could not be resolved)."""
    texts = []
    unresolved = False
    for value in values:
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            texts.append(value.value)
        elif isinstance(value, ast.Name) and value.id in constants:
            texts.append(constants[value.id])
        elif isinstance(value, (ast.List, ast.Tuple)):
            for element in value.elts:
                if (isinstance(element, ast.Constant)
                        and isinstance(element.value, str)):
                    texts.append(element.value)
                else:
                    unresolved = True
        else:
            unresolved = True
    return texts, unresolved


def operations_list(tree):
    """The elements of the Migration class's `operations = [...]`."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for statement in node.body:
            if not isinstance(statement, ast.Assign):
                continue
            targets = [
                t.id for t in statement.targets if isinstance(t, ast.Name)
            ]
            if 'operations' in targets and isinstance(statement.value,
                                                      ast.List):
                return statement.value.elts
    return None


def classify_operations(source):
    """Classify the migration's operations, in declaration order.

    Returns (sequence, unresolved) where sequence is a list of
    ('timeout' | 'altering', label) pairs in the order the operations
    run, and unresolved lists RunSQL calls whose SQL could not be read
    as literal text.
    """
    tree = ast.parse(source)
    constants = module_strings(tree)
    elements = operations_list(tree)
    if elements is None:
        return None, []

    sequence = []
    unresolved = []
    for element in elements:
        if not isinstance(element, ast.Call):
            continue
        name = call_name(element)
        if name in ALTERING_OPERATIONS:
            sequence.append(('altering', name))
        elif name == 'RunSQL':
            texts, could_not_read = resolve_sql(
                sql_arguments(element), constants
            )
            if could_not_read:
                unresolved.append(f'RunSQL at line {element.lineno}')
            if any(TIMEOUT_PATTERN.search(sql) for sql in texts):
                sequence.append(('timeout', 'SET LOCAL lock_timeout'))
            elif any(DDL_PATTERN.search(sql) for sql in texts):
                sequence.append(('altering', 'RunSQL (DDL)'))
    return sequence, unresolved


def migration_path(raw):
    """Resolve one argument to a migration file inside the repository.

    Arguments come from the command line (CI passes a git diff listing),
    so anything outside the working tree or not shaped like a Django
    migration module is rejected rather than read.
    """
    resolved = Path(raw).resolve()
    if not resolved.is_relative_to(Path.cwd().resolve()):
        raise SystemExit(f'{raw}: outside the working tree, refusing to read')
    if resolved.suffix != '.py' or 'migrations' not in resolved.parts:
        raise SystemExit(f'{raw}: not a migration file, refusing to read')
    return resolved


def check(source):
    """Reasons the migration fails the lock-timeout convention."""
    sequence, unresolved = classify_operations(source)
    problems = []
    if sequence is None:
        return problems, unresolved

    altering = [label for kind, label in sequence if kind == 'altering']
    if not altering:
        return problems, unresolved

    # The timeout only protects operations that run after it, so the
    # test is positional: a SET LOCAL lock_timeout must come before the
    # first schema-altering operation. A mention in a docstring or
    # comment is not an operation and never satisfies this.
    first_altering = next(
        i for i, (kind, _) in enumerate(sequence) if kind == 'altering'
    )
    has_timeout_first = any(
        kind == 'timeout' for kind, _ in sequence[:first_altering]
    )
    if not has_timeout_first:
        problems.append(
            'schema-altering operations ('
            + ', '.join(sorted(set(altering)))
            + ') with no SET LOCAL lock_timeout before the first one'
        )
    return problems, unresolved


def main(paths):
    failures = []
    for raw in paths:
        path = migration_path(raw)
        if not path.exists():
            continue
        source = path.read_text()
        if OPT_OUT in source:
            continue
        problems, unresolved = check(source)
        if unresolved:
            problems.append(
                'SQL that could not be read as literal text, so its DDL '
                'was not checked: ' + ', '.join(unresolved)
            )
        if problems:
            failures.append((path, problems))
    for path, problems in failures:
        print(f'{path}:')
        for problem in problems:
            print(f'  - {problem}')
        print(
            '  Open the migration with\n'
            "    migrations.RunSQL(\n"
            "        sql=\"SET LOCAL lock_timeout = '5s';\",\n"
            '        reverse_sql=migrations.RunSQL.noop,\n'
            '    )\n'
            '  as its FIRST operation (see '
            '0284_zone_set_last_upload_sha256.py), or justify an\n'
            f'  opt-out with a comment containing "{OPT_OUT}".'
        )
    if failures:
        return 1
    print(f'lint_migrations: {len(paths)} file(s) checked, no findings.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
