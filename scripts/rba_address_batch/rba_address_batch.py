#!/usr/bin/env python3
"""Bulk-apply address corrections to a private instance and make them primary.

Submitting an address to Open Supply Hub does not change what a production
location displays - a submission is a contribution, and one contribution
has to be *promoted* before its name and address become the location's
primary values. Doing that by hand is four dashboard operations per record.
This tool does it for a CSV of records.

Per record it makes these API calls:

  1. GET   /api/facilities/{os_id}/                     read current primary
  2. PATCH /api/v1/production-locations/{os_id}/                    submit
  3. PATCH /api/v1/moderation-events/{id}/production-locations/{os_id}/
                                                    approve (superuser)
  4. GET   /api/facilities/{os_id}/split/     find the new match, if needed
  5. POST  /api/facilities/{os_id}/promote/            make it primary
  6. GET   /api/facilities/{os_id}/                     read it back

Step 4 is skipped when the approval response reports the match it created.

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
import hashlib
import json
import os
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

import requests

# The shared public instance. Never a valid target: bulk-promoting one
# contributor's submissions there would override other contributors' data.
PUBLIC_HOSTNAMES = frozenset({
    'opensupplyhub.org',
    'www.opensupplyhub.org',
})

LOCAL_HOSTNAMES = frozenset({'localhost', '127.0.0.1', '::1'})

# A private instance is identified by its first host label, so
# rba.opensupplyhub.org is allowed while opensupplyhub.org is not. Matching
# on labels rather than substrings is the point: 'opensupplyhub.org' as a
# substring test also matches every private instance hosted under it.
PRIVATE_INSTANCE_LABELS = frozenset({'rba'})

BASE_URL_PLACEHOLDER = '<private-instance-host>'
REQUIRED_COLUMNS = ('os_id', 'name', 'address', 'country')

# The duplicate-submission guard is a throttle, so it answers 429 like any
# other rate limit. This text is what distinguishes it from a real one.
DUPLICATE_DETAIL_MARKER = 'Duplicate request'

RATE_LIMIT_STATUS = 429
MAX_RATE_LIMIT_RETRIES = 5
DEFAULT_RETRY_AFTER_SECONDS = 30


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
    # Gentle pacing. A thousand records is several thousand calls; there is
    # no deadline on a cleanup batch and the instance is shared with its
    # users. The submit endpoint is throttled per contributor, so this also
    # keeps the run under that ceiling.
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

    Compares host labels rather than searching for substrings, so a private
    instance hosted under the public domain is allowed while the public
    instance itself is not.
    """
    hostname = (urlsplit(base_url).hostname or '').lower()
    if not hostname:
        return 'could not read a hostname from {!r}'.format(base_url)

    if hostname in PUBLIC_HOSTNAMES:
        return (
            'refusing to run against {}: promoting one contributor\'s '
            'submissions in bulk on the public instance would override '
            'other contributors\' data'.format(hostname)
        )

    if hostname in LOCAL_HOSTNAMES:
        return None

    first_label = hostname.split('.')[0]
    if first_label in PRIVATE_INSTANCE_LABELS:
        return None

    return (
        'refusing to run against {}: this tool is for a single-tenant '
        'private instance ({}), or local development'.format(
            hostname, ', '.join(sorted(PRIVATE_INSTANCE_LABELS))
        )
    )


def build_session(config):
    session = requests.Session()
    session.headers.update({'Authorization': 'Token {}'.format(config.token)})
    return session


def is_duplicate_submission(response):
    return (
        response.status_code == RATE_LIMIT_STATUS
        and DUPLICATE_DETAIL_MARKER in response.text
    )


def request_with_backoff(session, method, url, **kwargs):
    """
    Make a request, waiting out rate limits rather than failing the record.

    The submit endpoint is throttled per contributor, so a long batch will
    meet the ceiling. Without this, every remaining record in the window
    fails and is reported as if the data were at fault.

    A duplicate-submission response also arrives as 429 but is not a rate
    limit, so it is returned to the caller rather than retried - retrying
    would just wait out the whole duplicate window.
    """
    for attempt in range(MAX_RATE_LIMIT_RETRIES):
        response = session.request(method, url, **kwargs)

        if response.status_code != RATE_LIMIT_STATUS:
            return response
        if is_duplicate_submission(response):
            return response

        try:
            wait = int(response.headers.get('Retry-After', ''))
        except ValueError:
            wait = DEFAULT_RETRY_AFTER_SECONDS

        wait = max(wait, 1)
        print(
            '  rate limited, waiting {}s (attempt {} of {})'.format(
                wait, attempt + 1, MAX_RATE_LIMIT_RETRIES
            )
        )
        time.sleep(wait)

    return response


def resolve_input_path(path):
    """
    Resolve the operator's input path, or exit explaining what is wrong.

    The path arrives on the command line, so the failures to catch are
    ordinary operator mistakes - a typo, a directory, a file that is not
    there - which would otherwise surface as a traceback. Resolving before
    opening also means every later message names the file actually read
    rather than whatever relative path was typed.
    """
    resolved = Path(path).expanduser().resolve()

    if not resolved.exists():
        sys.exit('input file does not exist: {}'.format(resolved))
    if not resolved.is_file():
        sys.exit('input path is not a file: {}'.format(resolved))

    return resolved


def load_rows(path):
    """Read the input CSV, or exit explaining which columns are missing."""
    resolved = resolve_input_path(path)

    with resolved.open(newline='') as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        sys.exit('input file has no rows: {}'.format(resolved))

    missing = sorted(set(REQUIRED_COLUMNS) - set(rows[0].keys()))
    if missing:
        sys.exit('input file is missing columns: {}'.format(missing))

    return rows


def row_key(row):
    """
    A resume key derived from the row's content, not its position.

    Keying on the row's offset in the file would mean an operator who
    edits the CSV between runs - deleting rows that already applied, or
    correcting one that failed - shifts every later key and re-applies
    records that were already correct.
    """
    canonical = '|'.join(
        str(row.get(column, '')).strip()
        for column in ('os_id', 'name', 'address', 'country', 'lat', 'lng')
    )
    digest = hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:12]
    return '{}#{}'.format(row['os_id'], digest)


def journal_write(config, record):
    with config.journal.open('a') as handle:
        handle.write(json.dumps(record) + '\n')


def read_journal(config):
    """
    Every readable entry in the journal.

    Tolerates a malformed final line: a run killed mid-write, or a full
    disk, leaves partial JSON, and refusing to parse it would break the
    resume path this journal exists to provide.
    """
    entries = []
    if not config.journal.exists():
        return entries

    for number, line in enumerate(
        config.journal.read_text().splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except ValueError:
            print(
                '  ignoring unreadable journal line {} (probably a run that '
                'was killed mid-write)'.format(number)
            )
            continue
        if isinstance(entry, dict) and 'row_key' in entry:
            entries.append(entry)

    return entries


def completed_row_keys(config):
    """
    Row keys already carried all the way through to verification.

    Only a 'verified' entry counts as done, so a run interrupted between
    approve and promote is retried rather than silently skipped.
    """
    return {
        entry['row_key'] for entry in read_journal(config)
        if entry.get('step') == 'verified'
    }


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
    """Raised when the duplicate-submission window is hit."""


def submit_address(session, config, os_id, row):
    response = request_with_backoff(
        session,
        'PATCH',
        '{}/api/v1/production-locations/{}/'.format(config.base_url, os_id),
        json=build_submission(row),
        timeout=30,
    )
    if is_duplicate_submission(response):
        raise DuplicateSubmission(
            'identical payload resubmitted inside the duplicate-request '
            'window - usually a resume shortly after a crash. Wait for the '
            'window to pass and re-run; the journal will skip the records '
            'that already finished.'
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
    response = request_with_backoff(
        session,
        'PATCH',
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


def discover_match_id(session, config, os_id):
    """
    Find the match the approval just created.

    Filtered to our own contributor and taking the highest id, because the
    approval runs submissions through ingest cleaning - the stored strings
    drift from what was submitted, so matching on name or address is
    unreliable. This is only correct while nothing else is writing to the
    same location; see the concurrency note in README.md.
    """
    response = request_with_backoff(
        session,
        'GET',
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


def resolve_match_id(session, config, os_id, approval):
    """Prefer the id the server reported; fall back to discovering it."""
    match_id = approval.get('match_id')
    if match_id is not None:
        return match_id
    return discover_match_id(session, config, os_id)


def promote_match(session, config, os_id, match_id):
    response = request_with_backoff(
        session,
        'POST',
        '{}/api/facilities/{}/promote/'.format(config.base_url, os_id),
        json={'match_id': match_id},
        timeout=30,
    )
    response.raise_for_status()


def fetch_primary(session, config, os_id, cache_buster=None):
    """
    Read the location's current primary name and address.

    Uses the legacy facility endpoint, which is Postgres-backed and
    reflects a promote immediately. Do not verify through /api/v1/ - that
    reads a search index and lags by the indexing cycle, so a correct
    promote looks like a failure for several minutes.

    That endpoint sits behind two response caches which are pure TTL and
    are not invalidated on write, so a cache-busting parameter is required.
    Without it the dry run primes the cache and every read during the
    execute run can return the values from before the change - which would
    make a batch that did nothing look like a batch that worked.
    """
    params = {}
    if cache_buster is not None:
        params['_'] = cache_buster

    response = request_with_backoff(
        session,
        'GET',
        '{}/api/facilities/{}/'.format(config.base_url, os_id),
        params=params,
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


def check_superuser_access(session, config):
    """
    Confirm the token can do what the batch needs, not merely read.

    Reading a location needs only an authenticated user, while approve and
    promote are superuser-only. Without this check a valid non-superuser
    token passes the dry run, and the execute run then creates a real
    pending contribution for every record before failing at approve -
    leaving the instance's moderation queue full of unapproved events.
    """
    response = session.get(
        '{}/api/v1/moderation-events/'.format(config.base_url),
        params={'size': 1},
        timeout=30,
    )
    if response.status_code in (401, 403):
        return (
            'the token is valid but not a superuser: {} returned HTTP {}. '
            'Approving and promoting both require a superuser account, so '
            '--execute would submit every record and then fail.'.format(
                '/api/v1/moderation-events/', response.status_code
            )
        )
    if response.status_code != 200:
        return (
            'could not confirm superuser access: '
            '/api/v1/moderation-events/ returned HTTP {}'.format(
                response.status_code
            )
        )
    return None


def dry_run(session, config, rows):
    """Read-only: confirm the token can do the job and locations exist."""
    grouped = group_by_facility(rows)
    print('dry run: {} rows across {} locations'.format(
        len(rows), len(grouped)
    ))

    problems = 0

    access_problem = check_superuser_access(session, config)
    if access_problem:
        print('  PROBLEM {}'.format(access_problem))
        problems += 1

    repeated = sorted(
        os_id for os_id, indexes in grouped.items() if len(indexes) > 1
    )
    if repeated:
        shown = repeated[:5]
        print(
            '  NOTE {} locations appear more than once. They are processed '
            'in file order, so the last row for a location wins its primary '
            'address. Showing {} of {}: {}'.format(
                len(repeated), len(shown), len(repeated), shown
            )
        )

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


def process_row(session, config, os_id, row, key):
    """Run one record all the way through, journaling each step."""
    # Read before and after so the report can say whether anything
    # actually changed. Both reads bypass the response cache.
    _, before = fetch_primary(session, config, os_id, cache_buster=key)

    moderation_id = submit_address(session, config, os_id, row)
    journal_write(config, {'row_key': key, 'step': 'submitted',
                           'moderation_id': moderation_id})

    approval = approve_event(session, config, moderation_id, os_id)
    journal_write(config, {'row_key': key, 'step': 'approved'})

    match_id = resolve_match_id(session, config, os_id, approval)
    promote_match(session, config, os_id, match_id)
    journal_write(config, {'row_key': key, 'step': 'promoted',
                           'match_id': match_id})

    _, after = fetch_primary(
        session, config, os_id, cache_buster='{}-after'.format(key)
    )
    return before, after


def status_for(before, after):
    """
    Whether the promote visibly changed the location's primary address.

    Comparing the submitted string to the result would be wrong - ingest
    cleaning legitimately rewrites it - but "the primary address is exactly
    what it was before the run" is a real signal that the promote did not
    take, and it used to be thrown away.
    """
    if after != before:
        return 'OK'
    return 'CHECK unchanged'


def execute(session, config, rows):
    done = completed_row_keys(config)
    processed = 0

    for os_id, facility_rows in group_by_facility(rows).items():
        for _, row in facility_rows:
            key = row_key(row)
            if key in done:
                continue
            processed += 1
            try:
                before, after = process_row(
                    session, config, os_id, row, key
                )
                journal_write(config, {
                    'row_key': key,
                    'step': 'verified',
                    'os_id': os_id,
                    'submitted_address': row['address'],
                    'previous_primary_address': before,
                    'resulting_primary_address': after,
                    'status': status_for(before, after),
                })
            except Exception as err:
                # One bad record must not end the batch. It is journaled as
                # FAILED, reported, and picked up by the next run.
                journal_write(config, {
                    'row_key': key,
                    'step': 'FAILED',
                    'os_id': os_id,
                    'submitted_address': row['address'],
                    'previous_primary_address': '',
                    'resulting_primary_address': '',
                    'status': 'FAILED {}'.format(err),
                })
            time.sleep(config.pause_seconds)

    report_rows = write_report(config)
    failures = sum(
        1 for row in report_rows if row[-1].startswith('FAILED')
    )
    unchanged = sum(1 for row in report_rows if row[-1].startswith('CHECK'))
    print(
        'processed {} rows this run; {} in the report, {} failures, {} '
        'unchanged. Review {} before treating the batch as done - '
        'addresses are cleaned on ingest, so a submitted string and the '
        'resulting primary string differ legitimately and need a human '
        'eye.'.format(
            processed, len(report_rows), failures, unchanged, config.report
        )
    )
    return failures


def write_report(config):
    """
    Rebuild the report from the journal.

    Built from the journal rather than from this run's results so that
    resuming an interrupted batch produces a report covering every record,
    not only the ones the final run happened to process.
    """
    latest = {}
    for entry in read_journal(config):
        if entry.get('step') in ('verified', 'FAILED'):
            # A later attempt supersedes an earlier one for the same row.
            latest[entry['row_key']] = entry

    report_rows = [
        [
            entry.get('os_id', ''),
            entry.get('submitted_address', ''),
            entry.get('previous_primary_address', ''),
            entry.get('resulting_primary_address', ''),
            entry.get('status', ''),
        ]
        for entry in latest.values()
    ]

    with config.report.open('w', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow([
            'os_id', 'submitted_address', 'previous_primary_address',
            'resulting_primary_address', 'status',
        ])
        writer.writerows(report_rows)

    return report_rows


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
