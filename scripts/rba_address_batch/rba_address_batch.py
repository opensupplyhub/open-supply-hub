#!/usr/bin/env python3
"""Bulk-apply address corrections to a private instance and make them primary.

Submitting an address to Open Supply Hub does not change what a production
location displays - a submission is a contribution, and one contribution
has to be *promoted* before its name and address become the location's
primary values. Doing that by hand is four dashboard operations per record.
This tool does it for a CSV of records.

Per record it makes four API calls:

  1. PATCH /api/v1/production-locations/{os_id}/                    submit
  2. PATCH /api/v1/moderation-events/{id}/production-locations/{os_id}/
                                                    approve (superuser)
  3. GET   /api/facilities/{os_id}/split/               find the new match
  4. POST  /api/facilities/{os_id}/promote/            make it primary

Run --dry-run first, then --execute, then read the verification report
before treating the batch as done. See README.md in this directory for
setup, the CSV format, and how to interpret the report.

Scope: this tool is for a single-tenant private instance only. Promoting
one contributor's submissions in bulk on the shared public instance would
override other contributors' data, so the host is checked, not merely
documented.
"""
import argparse
import csv
import json
import os
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import requests

# A private instance, or local development. Anything else is refused.
ALLOWED_HOST_MARKERS = ('localhost', '127.0.0.1', 'rba')
FORBIDDEN_HOST_MARKERS = ('opensupplyhub.org',)

BASE_URL_PLACEHOLDER = '<private-instance-host>'
REQUIRED_COLUMNS = ('os_id', 'name', 'address', 'country')


@dataclass
class Config:
    """Everything the run needs, so nothing is read at import time."""

    base_url: str
    token: str
    contributor_id: int
    journal: Path = field(default_factory=lambda: Path('batch_journal.jsonl'))
    report: Path = field(
        default_factory=lambda: Path('verification_report.csv')
    )
    # Gentle pacing. A thousand records is four thousand calls; there is no
    # deadline on a cleanup batch and the instance is shared with its users.
    pause_seconds: float = 0.25


def config_from_env():
    """Build a Config from the environment, or exit with what is missing."""
    base_url = os.environ.get('RBA_BASE_URL', BASE_URL_PLACEHOLDER)
    token = os.environ.get('RBA_TOKEN', '')
    contributor_id = os.environ.get('RBA_CONTRIBUTOR_ID', '')

    missing = [
        name for name, value in (
            ('RBA_BASE_URL', None if BASE_URL_PLACEHOLDER in base_url
             else base_url),
            ('RBA_TOKEN', token),
            ('RBA_CONTRIBUTOR_ID', contributor_id),
        ) if not value
    ]
    if missing:
        sys.exit(
            'Set these environment variables first: {}. See README.md.'
            .format(', '.join(missing))
        )

    if not contributor_id.isdigit():
        sys.exit('RBA_CONTRIBUTOR_ID must be a number, got: {!r}'
                 .format(contributor_id))

    return Config(
        base_url=base_url.rstrip('/'),
        token=token,
        contributor_id=int(contributor_id),
    )


def host_rejection_reason(base_url):
    """
    Return why this host may not be used, or None when it is allowed.

    Separated from the exit so it can be tested directly.
    """
    host = base_url.split('//', 1)[-1].lower()
    if any(marker in host for marker in FORBIDDEN_HOST_MARKERS):
        return (
            'refusing to run against {}: promoting one contributor\'s '
            'submissions in bulk on the public instance would override '
            'other contributors\' data'.format(host)
        )
    if not any(marker in host for marker in ALLOWED_HOST_MARKERS):
        return (
            'refusing to run against {}: this tool is for a single-tenant '
            'private instance, or local development'.format(host)
        )
    return None


def build_session(config):
    session = requests.Session()
    session.headers.update({'Authorization': 'Token {}'.format(config.token)})
    return session


def load_rows(path):
    """Read the input CSV, or exit explaining which columns are missing."""
    with open(path, newline='') as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        sys.exit('input file has no rows: {}'.format(path))

    missing = sorted(set(REQUIRED_COLUMNS) - set(rows[0].keys()))
    if missing:
        sys.exit('input file is missing columns: {}'.format(missing))

    return rows


def journal_write(config, record):
    with config.journal.open('a') as handle:
        handle.write(json.dumps(record) + '\n')


def completed_row_keys(config):
    """
    Row keys already carried all the way through to verification.

    Only a 'verified' entry counts as done, so a run interrupted between
    approve and promote is retried rather than silently skipped.
    """
    done = set()
    if not config.journal.exists():
        return done

    for line in config.journal.read_text().splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        if entry.get('step') == 'verified':
            done.add(entry['row_key'])
    return done


def build_submission(row):
    payload = {
        'name': row['name'],
        'address': row['address'],
        'country': row['country'],
    }
    if row.get('lat') and row.get('lng'):
        # Submissions are geocoded server-side and rejected when geocoding
        # fails. Explicit coordinates bypass geocoding entirely, so include
        # them whenever the input file carries them.
        payload['coordinates'] = {
            'lat': float(row['lat']),
            'lng': float(row['lng']),
        }
    return payload


class DuplicateSubmission(RuntimeError):
    """Raised when the 15-minute duplicate-request window is hit."""


def submit_address(session, config, os_id, row):
    response = session.patch(
        '{}/api/v1/production-locations/{}/'.format(config.base_url, os_id),
        json=build_submission(row),
        timeout=30,
    )
    if response.status_code == 422 and 'Duplicate request' in response.text:
        raise DuplicateSubmission(
            'identical payload resubmitted inside the 15-minute '
            'duplicate-request window - usually a resume after a crash. '
            'Wait for the window to pass and re-run; the journal will skip '
            'the records that already finished.'
        )
    response.raise_for_status()
    return response.json()['moderation_id']


def approve_event(session, config, moderation_id, os_id):
    """
    Approve the submission and return whatever the response tells us.

    The response carries only os_id today, which is why the match has to be
    discovered separately. OSDEV-3424 adds the created match_id here; when
    it is present we use it, because the server knows the answer and does
    not have to infer it. Reading it opportunistically means this tool is
    correct whichever order the two changes ship in, and gets safer the
    moment 3424 deploys without needing a change here.
    """
    response = session.patch(
        '{}/api/v1/moderation-events/{}/production-locations/{}/'.format(
            config.base_url, moderation_id, os_id
        ),
        timeout=60,
    )
    response.raise_for_status()
    try:
        return response.json() or {}
    except ValueError:
        return {}


def resolve_match_id(session, config, os_id, approval):
    """Prefer the id the server reported; fall back to discovering it."""
    match_id = approval.get('match_id')
    if match_id is not None:
        return match_id
    return discover_match_id(session, config, os_id)


def discover_match_id(session, config, os_id):
    """
    Find the match the approval just created.

    Filtered to our own contributor and taking the highest id, because the
    approval runs submissions through ingest cleaning - the stored strings
    drift from what was submitted, so matching on name or address is
    unreliable. This is only correct while nothing else is writing to the
    same location; see the concurrency note in README.md.
    """
    response = session.get(
        '{}/api/facilities/{}/split/'.format(config.base_url, os_id),
        timeout=30,
    )
    response.raise_for_status()

    matches = response.json()['properties']['matches']
    ours = [
        match for match in matches
        if match['list_contributor_id'] == config.contributor_id
    ]
    if not ours:
        raise RuntimeError(
            '{}: the approval reported success but no match for contributor '
            '{} is present, so there is nothing to promote'.format(
                os_id, config.contributor_id
            )
        )
    return max(match['match_id'] for match in ours)


def promote_match(session, config, os_id, match_id):
    response = session.post(
        '{}/api/facilities/{}/promote/'.format(config.base_url, os_id),
        json={'match_id': match_id},
        timeout=30,
    )
    response.raise_for_status()


def fetch_primary(session, config, os_id):
    """
    Read the resulting primary values.

    Uses the legacy facility endpoint, which is Postgres-backed and
    reflects the promote immediately. Do not verify through /api/v1/ - that
    reads OpenSearch and lags by the indexing cycle, so a correct promote
    looks like a failure for several minutes.
    """
    response = session.get(
        '{}/api/facilities/{}/'.format(config.base_url, os_id),
        timeout=30,
    )
    response.raise_for_status()
    properties = response.json()['properties']
    return properties['name'], properties['address']


def group_by_facility(rows):
    """
    Group input rows by location, preserving file order within each.

    Each location is processed to completion before the next row for that
    same location starts, so two rows for one location cannot interleave.
    """
    grouped = defaultdict(list)
    for index, row in enumerate(rows):
        grouped[row['os_id']].append((index, row))
    return grouped


def dry_run(session, config, rows):
    """Read-only: confirm the token works and every location exists."""
    grouped = group_by_facility(rows)
    print('dry run: {} rows across {} locations'.format(
        len(rows), len(grouped)
    ))

    repeated = {
        os_id: indexes for os_id, indexes in grouped.items()
        if len(indexes) > 1
    }
    if repeated:
        print(
            '  NOTE {} locations appear more than once. They are processed '
            'in file order, so the last row for a location wins its primary '
            'address: {}'.format(len(repeated), sorted(repeated)[:5])
        )

    problems = 0
    for os_id in grouped:
        response = session.get(
            '{}/api/facilities/{}/'.format(config.base_url, os_id),
            timeout=30,
        )
        if response.status_code != 200:
            print('  PROBLEM {}: HTTP {}'.format(os_id, response.status_code))
            problems += 1
        time.sleep(config.pause_seconds)

    print('dry run finished: {} problems. Fix these before --execute.'
          .format(problems))
    return problems


def process_row(session, config, os_id, row, row_key):
    """Run one record all the way through, journaling each step."""
    moderation_id = submit_address(session, config, os_id, row)
    journal_write(config, {'row_key': row_key, 'step': 'submitted',
                           'moderation_id': moderation_id})

    approval = approve_event(session, config, moderation_id, os_id)
    journal_write(config, {'row_key': row_key, 'step': 'approved'})

    match_id = resolve_match_id(session, config, os_id, approval)
    promote_match(session, config, os_id, match_id)
    journal_write(config, {'row_key': row_key, 'step': 'promoted',
                           'match_id': match_id})

    name, address = fetch_primary(session, config, os_id)
    journal_write(config, {'row_key': row_key, 'step': 'verified'})
    return address


def execute(session, config, rows):
    done = completed_row_keys(config)
    report_rows = []

    for os_id, facility_rows in group_by_facility(rows).items():
        for index, row in facility_rows:
            row_key = '{}#{}'.format(os_id, index)
            if row_key in done:
                continue
            try:
                address = process_row(session, config, os_id, row, row_key)
                report_rows.append([
                    os_id, row['address'], address,
                    'OK' if address else 'CHECK',
                ])
            except Exception as err:
                # One bad record must not end the batch. It is journaled as
                # FAILED, reported, and picked up by the next run.
                journal_write(config, {'row_key': row_key, 'step': 'FAILED',
                                       'error': str(err)})
                report_rows.append([
                    os_id, row['address'], '', 'FAILED {}'.format(err),
                ])
            time.sleep(config.pause_seconds)

    write_report(config, report_rows)
    failures = sum(1 for row in report_rows if row[3].startswith('FAILED'))
    print(
        'executed {} rows, {} failures. Review {} before treating the batch '
        'as done - addresses are cleaned on ingest, so a submitted string '
        'and the resulting primary string differ legitimately and need a '
        'human eye.'.format(len(report_rows), failures, config.report)
    )
    return failures


def write_report(config, report_rows):
    with config.report.open('w', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow([
            'os_id', 'submitted_address', 'resulting_primary_address',
            'status',
        ])
        writer.writerows(report_rows)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Bulk-apply address corrections and promote them to '
                    'primary on a private instance.'
    )
    parser.add_argument('input_csv')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run', action='store_true',
                      help='read-only checks; creates and changes nothing')
    mode.add_argument('--execute', action='store_true',
                      help='apply the changes')
    args = parser.parse_args(argv)

    config = config_from_env()

    rejection = host_rejection_reason(config.base_url)
    if rejection:
        sys.exit(rejection)

    rows = load_rows(args.input_csv)
    session = build_session(config)

    if args.dry_run:
        return 1 if dry_run(session, config, rows) else 0
    return 1 if execute(session, config, rows) else 0


if __name__ == '__main__':
    sys.exit(main())
