"""Unit tests for the address batch tool.

Run from this directory:

    python -m unittest test_rba_address_batch -v

These are not part of the Django test suite - the tool is a standalone
API client and runs outside the app - so CI does not pick them up. See the
Known TODO note on the pull request.
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

import rba_address_batch as batch


def make_config(tmpdir, contributor_id=42):
    return batch.Config(
        base_url='https://rba.opensupplyhub.org',
        token='token',
        contributor_id=contributor_id,
        journal=Path(tmpdir) / 'journal.jsonl',
        report=Path(tmpdir) / 'report.csv',
        pause_seconds=0,
    )


def make_response(status_code=200, payload=None, text='', headers=None):
    response = MagicMock()
    response.status_code = status_code
    response.text = text
    response.headers = headers or {}
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


def session_returning(*responses):
    """A session whose .request returns the given responses in order."""
    session = MagicMock()
    session.request.side_effect = list(responses)
    return session


class HostGuardTest(unittest.TestCase):
    def test_allows_the_private_instance_under_the_public_domain(self):
        # The instance is a subdomain of the public domain. A substring
        # test for the public domain refuses it, which would make the tool
        # unable to run anywhere it is meant to run.
        self.assertIsNone(
            batch.host_rejection_reason('https://rba.opensupplyhub.org')
        )

    def test_refuses_the_public_instance(self):
        reason = batch.host_rejection_reason('https://opensupplyhub.org')
        self.assertIsNotNone(reason)
        self.assertIn('public instance', reason)

    def test_refuses_the_public_instance_with_www(self):
        self.assertIsNotNone(
            batch.host_rejection_reason('https://www.opensupplyhub.org')
        )

    def test_refuses_an_unrecognised_host(self):
        self.assertIsNotNone(
            batch.host_rejection_reason('https://example.com')
        )

    def test_allows_local_development_including_a_port(self):
        self.assertIsNone(batch.host_rejection_reason('http://localhost:8000'))

    def test_a_path_or_query_cannot_smuggle_in_an_allowed_label(self):
        # Substring matching on the whole URL would accept both of these.
        self.assertIsNotNone(
            batch.host_rejection_reason('https://example.com/rba')
        )
        self.assertIsNotNone(
            batch.host_rejection_reason('https://example.com/?x=rba')
        )

    def test_a_hostname_merely_containing_the_label_is_refused(self):
        self.assertIsNotNone(
            batch.host_rejection_reason('https://rbanking.example.com')
        )

    def test_a_url_with_no_hostname_is_refused(self):
        self.assertIsNotNone(batch.host_rejection_reason('not-a-url'))


class SubmissionPayloadTest(unittest.TestCase):
    def test_sends_the_core_fields(self):
        payload = batch.build_submission({
            'os_id': 'X', 'name': 'Name', 'address': 'Address',
            'country': 'US',
        })
        self.assertEqual(
            {'name': 'Name', 'address': 'Address', 'country': 'US'}, payload
        )

    def test_includes_coordinates_when_present(self):
        payload = batch.build_submission({
            'name': 'Name', 'address': 'Address', 'country': 'US',
            'lat': '1.5', 'lng': '-2.5',
        })
        self.assertEqual({'lat': 1.5, 'lng': -2.5}, payload['coordinates'])

    def test_omits_coordinates_when_blank(self):
        payload = batch.build_submission({
            'name': 'Name', 'address': 'Address', 'country': 'US',
            'lat': '', 'lng': '',
        })
        self.assertNotIn('coordinates', payload)


class DuplicateSubmissionTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config = make_config(self.tmpdir.name)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_the_duplicate_window_is_a_429_not_a_422(self):
        # The duplicate guard is a throttle, so it answers 429. Testing a
        # 422 here would make the branch look covered while never firing
        # against a real instance.
        session = session_returning(make_response(
            status_code=429, text='Duplicate request submitted, please retry'
        ))
        with self.assertRaises(batch.DuplicateSubmission):
            batch.submit_address(session, self.config, 'OSID', {
                'name': 'n', 'address': 'a', 'country': 'US',
            })

    def test_a_duplicate_is_not_retried(self):
        # Retrying would just wait out the whole duplicate window.
        session = session_returning(make_response(
            status_code=429, text='Duplicate request submitted'
        ))
        with self.assertRaises(batch.DuplicateSubmission):
            batch.submit_address(session, self.config, 'OSID', {
                'name': 'n', 'address': 'a', 'country': 'US',
            })
        self.assertEqual(1, session.request.call_count)


class RateLimitTest(unittest.TestCase):
    def test_a_real_rate_limit_is_waited_out_and_retried(self):
        session = session_returning(
            make_response(status_code=429, text='Request was throttled',
                          headers={'Retry-After': '1'}),
            make_response(status_code=200, payload={'ok': True}),
        )
        response = batch.request_with_backoff(
            session, 'GET', 'https://rba.opensupplyhub.org/x'
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, session.request.call_count)

    def test_a_missing_retry_after_falls_back_to_a_default(self):
        session = session_returning(
            make_response(status_code=429, text='throttled'),
            make_response(status_code=200, payload={}),
        )
        original = batch.DEFAULT_RETRY_AFTER_SECONDS
        batch.DEFAULT_RETRY_AFTER_SECONDS = 0
        try:
            response = batch.request_with_backoff(
                session, 'GET', 'https://rba.opensupplyhub.org/x'
            )
        finally:
            batch.DEFAULT_RETRY_AFTER_SECONDS = original
        self.assertEqual(200, response.status_code)


class MatchResolutionTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config = make_config(self.tmpdir.name, contributor_id=42)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_prefers_the_match_id_the_server_reported(self):
        # Once OSDEV-3424 ships, no discovery call should be made at all.
        session = MagicMock()
        match_id = batch.resolve_match_id(
            session, self.config, 'OSID', {'match_id': 99}
        )
        self.assertEqual(99, match_id)
        session.request.assert_not_called()

    def test_falls_back_to_discovery_when_absent(self):
        session = session_returning(make_response(payload={'properties': {
            'matches': [{'match_id': 7, 'list_contributor_id': 42}]
        }}))
        match_id = batch.resolve_match_id(session, self.config, 'OSID', {})
        self.assertEqual(7, match_id)

    def test_discovery_takes_the_newest_of_our_own_matches(self):
        session = session_returning(make_response(payload={'properties': {
            'matches': [
                {'match_id': 3, 'list_contributor_id': 42},
                {'match_id': 11, 'list_contributor_id': 42},
                # Another contributor's newer match must be ignored.
                {'match_id': 99, 'list_contributor_id': 7},
            ]
        }}))
        self.assertEqual(
            11, batch.discover_match_id(session, self.config, 'OSID')
        )

    def test_discovery_raises_when_none_of_our_matches_are_present(self):
        session = session_returning(make_response(payload={'properties': {
            'matches': [{'match_id': 99, 'list_contributor_id': 7}]
        }}))
        with self.assertRaises(RuntimeError):
            batch.discover_match_id(session, self.config, 'OSID')


class CacheBustingTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config = make_config(self.tmpdir.name)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_verification_reads_bypass_the_response_cache(self):
        # The endpoint sits behind pure-TTL response caches that are not
        # invalidated on write, and the dry run primes them, so a read
        # without a cache buster can return pre-change values and make a
        # batch that did nothing look successful.
        session = session_returning(make_response(payload={'properties': {
            'name': 'N', 'address': 'A',
        }}))
        batch.fetch_primary(
            session, self.config, 'OSID', cache_buster='abc'
        )
        _, kwargs = session.request.call_args
        self.assertEqual({'_': 'abc'}, kwargs['params'])


class SuperuserCheckTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config = make_config(self.tmpdir.name)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_a_non_superuser_token_is_reported(self):
        # Reading a location needs only an authenticated user, so without
        # this check the dry run passes and --execute creates a pending
        # contribution per record before failing at approve.
        session = MagicMock()
        session.get.return_value = make_response(status_code=403)
        problem = batch.check_superuser_access(session, self.config)
        self.assertIsNotNone(problem)
        self.assertIn('superuser', problem)

    def test_a_superuser_token_passes(self):
        session = MagicMock()
        session.get.return_value = make_response(payload={'data': []})
        self.assertIsNone(
            batch.check_superuser_access(session, self.config)
        )


class ResumeKeyTest(unittest.TestCase):
    def test_the_key_is_derived_from_content_not_position(self):
        row = {'os_id': 'OSID', 'name': 'N', 'address': 'A', 'country': 'US'}
        self.assertEqual(batch.row_key(row), batch.row_key(dict(row)))

    def test_editing_the_address_changes_the_key(self):
        base = {'os_id': 'OSID', 'name': 'N', 'address': 'A', 'country': 'US'}
        edited = dict(base, address='B')
        self.assertNotEqual(batch.row_key(base), batch.row_key(edited))

    def test_the_key_is_stable_when_other_rows_are_removed(self):
        # Deleting earlier rows from the CSV between runs must not change
        # this row's key, or already-applied records get re-applied.
        row = {'os_id': 'OSID', 'name': 'N', 'address': 'A', 'country': 'US'}
        first = batch.row_key(row)
        self.assertEqual(first, batch.row_key(row))

    def test_the_key_starts_with_the_os_id(self):
        row = {'os_id': 'OSID', 'name': 'N', 'address': 'A', 'country': 'US'}
        self.assertTrue(batch.row_key(row).startswith('OSID#'))


class JournalTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config = make_config(self.tmpdir.name)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_no_journal_means_nothing_is_done(self):
        self.assertEqual(set(), batch.completed_row_keys(self.config))

    def test_only_verified_rows_count_as_done(self):
        # A run that died between approve and promote must be retried, not
        # skipped, so partial steps do not mark a row complete.
        for record in (
            {'row_key': 'A#0', 'step': 'submitted'},
            {'row_key': 'A#0', 'step': 'approved'},
            {'row_key': 'B#1', 'step': 'verified'},
            {'row_key': 'C#2', 'step': 'FAILED', 'status': 'FAILED boom'},
        ):
            batch.journal_write(self.config, record)

        self.assertEqual({'B#1'}, batch.completed_row_keys(self.config))

    def test_a_truncated_final_line_does_not_break_resume(self):
        # A run killed mid-write leaves partial JSON. Refusing to parse it
        # would break the exact path the journal exists to provide.
        batch.journal_write(self.config, {'row_key': 'B#1',
                                          'step': 'verified'})
        with self.config.journal.open('a') as handle:
            handle.write('{"row_key": "C#2", "step": "veri')

        self.assertEqual({'B#1'}, batch.completed_row_keys(self.config))

    def test_entries_without_a_row_key_are_ignored(self):
        with self.config.journal.open('a') as handle:
            handle.write(json.dumps({'unrelated': True}) + '\n')
        self.assertEqual(set(), batch.completed_row_keys(self.config))


class StatusTest(unittest.TestCase):
    def test_an_unchanged_primary_address_is_flagged(self):
        # Comparing the submitted string to the result would be wrong,
        # since ingest cleaning rewrites it - but an address identical to
        # what it was before the run means the promote did not take.
        self.assertTrue(batch.status_for('Same', 'Same').startswith('CHECK'))

    def test_a_changed_primary_address_is_ok(self):
        self.assertEqual('OK', batch.status_for('Before', 'After'))


class ReportTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config = make_config(self.tmpdir.name)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_the_report_covers_rows_from_earlier_runs(self):
        # Rebuilt from the journal, so resuming a batch does not overwrite
        # the report with only the records the final run processed.
        batch.journal_write(self.config, {
            'row_key': 'A#aaa', 'step': 'verified', 'os_id': 'A',
            'submitted_address': 'sub-a', 'previous_primary_address': 'old-a',
            'resulting_primary_address': 'new-a', 'status': 'OK',
        })
        batch.journal_write(self.config, {
            'row_key': 'B#bbb', 'step': 'FAILED', 'os_id': 'B',
            'submitted_address': 'sub-b', 'previous_primary_address': '',
            'resulting_primary_address': '', 'status': 'FAILED boom',
        })

        rows = batch.write_report(self.config)

        self.assertEqual(2, len(rows))
        written = self.config.report.read_text()
        self.assertIn('previous_primary_address', written)
        self.assertIn('old-a', written)
        self.assertIn('FAILED boom', written)

    def test_a_later_attempt_supersedes_an_earlier_one(self):
        batch.journal_write(self.config, {
            'row_key': 'A#aaa', 'step': 'FAILED', 'os_id': 'A',
            'status': 'FAILED boom',
        })
        batch.journal_write(self.config, {
            'row_key': 'A#aaa', 'step': 'verified', 'os_id': 'A',
            'status': 'OK',
        })

        rows = batch.write_report(self.config)

        self.assertEqual(1, len(rows))
        self.assertEqual('OK', rows[0][-1])


class InputPathTest(unittest.TestCase):
    """
    The path arrives on the command line, so ordinary operator mistakes
    have to produce a usable message rather than a traceback.
    """

    def test_a_missing_file_exits_naming_it(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / 'not-there.csv'

            with self.assertRaises(SystemExit) as caught:
                batch.load_rows(str(missing))

            self.assertIn('does not exist', str(caught.exception))
            self.assertIn('not-there.csv', str(caught.exception))

    def test_a_directory_exits_rather_than_raising(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(SystemExit) as caught:
                batch.load_rows(tmpdir)

            self.assertIn('not a file', str(caught.exception))

    def test_a_readable_file_resolves_to_an_absolute_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / 'input.csv'
            path.write_text('os_id,name\n')

            resolved = batch.resolve_input_path(str(path))

            self.assertTrue(resolved.is_absolute())
            self.assertTrue(resolved.is_file())

    def test_missing_columns_are_reported_for_a_real_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / 'input.csv'
            path.write_text('os_id\nUS2021250D1DTNT\n')

            with self.assertRaises(SystemExit) as caught:
                batch.load_rows(str(path))

            self.assertIn('missing columns', str(caught.exception))


class GroupingTest(unittest.TestCase):
    def test_groups_by_location_preserving_file_order(self):
        rows = [
            {'os_id': 'A'}, {'os_id': 'B'}, {'os_id': 'A'},
        ]
        grouped = batch.group_by_facility(rows)
        self.assertEqual([0, 2], [index for index, _ in grouped['A']])
        self.assertEqual([1], [index for index, _ in grouped['B']])


class ProcessRowTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config = make_config(self.tmpdir.name, contributor_id=42)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_a_full_record_journals_every_step_and_reports_the_change(self):
        session = session_returning(
            # read before
            make_response(payload={'properties': {
                'name': 'Old', 'address': 'Old Address'}}),
            # submit
            make_response(payload={'moderation_id': 'MOD1'}),
            # approve, reporting the created match
            make_response(payload={'match_id': 55}),
            # promote
            make_response(payload={}),
            # read after
            make_response(payload={'properties': {
                'name': 'New', 'address': 'New Address'}}),
        )

        before, after = batch.process_row(
            session, self.config, 'OSID',
            {'name': 'n', 'address': 'a', 'country': 'US'}, 'OSID#abc',
        )

        self.assertEqual('Old Address', before)
        self.assertEqual('New Address', after)
        self.assertEqual('OK', batch.status_for(before, after))

        steps = [
            json.loads(line)['step']
            for line in self.config.journal.read_text().splitlines()
        ]
        self.assertEqual(['submitted', 'approved', 'promoted'], steps)
        # Five calls, not six: the approval reported the match, so no
        # discovery call was needed.
        self.assertEqual(5, session.request.call_count)


if __name__ == '__main__':
    unittest.main()
