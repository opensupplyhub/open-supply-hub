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

    def test_a_remote_host_over_plain_http_is_refused(self):
        # Every request carries a superuser token in a header, so this
        # would put it on the wire in the clear.
        reason = batch.host_rejection_reason('http://rba.opensupplyhub.org')
        self.assertIsNotNone(reason)
        self.assertIn('https', reason)

    def test_the_public_instance_is_refused_as_the_public_instance(self):
        # Not as a scheme problem: the most dangerous target keeps the
        # message that says why it is dangerous.
        reason = batch.host_rejection_reason('http://opensupplyhub.org')
        self.assertIn('public instance', reason)

    def test_local_development_over_http_is_still_allowed(self):
        # No TLS locally, and nothing on the wire to intercept.
        self.assertIsNone(batch.host_rejection_reason('http://127.0.0.1:8000'))


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
        session = session_returning(make_response(status_code=403))
        problem = batch.check_superuser_access(session, self.config)
        self.assertIsNotNone(problem)
        self.assertIn('not a superuser', problem)

    def test_a_superuser_token_passes(self):
        session = session_returning(make_response(payload={'data': []}))
        self.assertIsNone(
            batch.check_superuser_access(session, self.config)
        )

    def test_a_rate_limited_check_is_waited_out_not_reported(self):
        # The check used to read the response directly. A large dry run can
        # meet the rate limit on its own, and a 429 read straight off would
        # be reported as 'could not confirm superuser access' - sending the
        # operator to fix a token that is perfectly fine.
        session = session_returning(
            make_response(status_code=429, headers={'Retry-After': '1'}),
            make_response(payload={'data': []}),
        )
        self.assertIsNone(
            batch.check_superuser_access(session, self.config)
        )
        self.assertEqual(2, session.request.call_count)


class DryRunTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config = make_config(self.tmpdir.name)
        self.rows = [
            {'os_id': 'OSID1', 'name': 'n', 'address': 'a', 'country': 'US'},
        ]

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_a_rate_limited_location_read_is_waited_out(self):
        # One GET per location over a large file is exactly where the rate
        # limit is met. Reported as a problem, a 429 reads as 'this location
        # does not exist', which is the misreading the dry run exists to
        # prevent.
        session = session_returning(
            # superuser check
            make_response(payload={'data': []}),
            # the location read, rate limited then served
            make_response(status_code=429, headers={'Retry-After': '1'}),
            make_response(payload={'properties': {}}),
        )
        self.assertEqual(0, batch.dry_run(session, self.config, self.rows))

    def test_a_genuinely_missing_location_is_still_reported(self):
        session = session_returning(
            make_response(payload={'data': []}),
            make_response(status_code=404),
        )
        self.assertEqual(1, batch.dry_run(session, self.config, self.rows))


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


class ApplyRowTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config = make_config(self.tmpdir.name, contributor_id=42)
        self.row = {'name': 'n', 'address': 'a', 'country': 'US'}

    def tearDown(self):
        self.tmpdir.cleanup()

    def steps(self):
        return [
            json.loads(line)['step']
            for line in self.config.journal.read_text().splitlines()
        ]

    def test_a_fresh_record_runs_and_journals_every_step(self):
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
        )

        before = batch.apply_row(
            session, self.config, 'OSID', self.row, 'OSID#abc'
        )

        self.assertEqual('Old Address', before)
        self.assertEqual(
            ['started', 'submitted', 'approved', 'resolved', 'promoted'],
            self.steps(),
        )
        # Four calls, not five: the approval reported the match, so no
        # discovery call was needed.
        self.assertEqual(4, session.request.call_count)

    def test_the_match_is_journaled_before_the_promote_is_attempted(self):
        # So an attempt that dies waiting for the promote response knows
        # which match to re-promote, instead of running discovery again
        # against a location it has already changed.
        session = session_returning(
            make_response(payload={'properties': {
                'name': 'Old', 'address': 'Old Address'}}),
            make_response(payload={'moderation_id': 'MOD1'}),
            make_response(payload={'match_id': 55}),
            ConnectionError('promote never answered'),
        )

        with self.assertRaises(ConnectionError):
            batch.apply_row(
                session, self.config, 'OSID', self.row, 'OSID#abc'
            )

        self.assertIn('resolved', self.steps())
        facts = batch.row_progress(self.config)['OSID#abc']
        self.assertEqual(55, facts['match_id'])

    def test_a_record_already_promoted_repeats_no_writes(self):
        # The case that used to submit a second contribution for a location
        # that was already correct: everything landed, and only the
        # confirming read failed.
        facts = {
            'reached': {'started', 'submitted', 'approved', 'resolved',
                        'promoted'},
            'previous_primary_address': 'Old Address',
            'moderation_id': 'MOD1',
            'match_id': 55,
        }
        session = session_returning()

        before = batch.apply_row(
            session, self.config, 'OSID', self.row, 'OSID#abc', facts
        )

        self.assertEqual('Old Address', before)
        self.assertEqual(0, session.request.call_count)
        self.assertFalse(self.config.journal.exists())

    def test_a_record_resumes_from_its_journaled_submission(self):
        # A run that died between submit and promote used to leave its
        # submission pending forever and start a brand new one. The
        # moderation id is on record, so it is approved instead.
        facts = {
            'reached': {'started', 'submitted'},
            'previous_primary_address': 'Old Address',
            'moderation_id': 'MOD1',
        }
        session = session_returning(
            make_response(payload={'match_id': 55}),
            make_response(payload={}),
        )

        before = batch.apply_row(
            session, self.config, 'OSID', self.row, 'OSID#abc', facts
        )

        self.assertEqual('Old Address', before)
        self.assertEqual(['approved', 'resolved', 'promoted'], self.steps())
        self.assertEqual(2, session.request.call_count)
        approve_url = session.request.call_args_list[0][0][1]
        self.assertIn('MOD1', approve_url)

    def test_a_resume_re_promotes_the_match_it_recorded(self):
        facts = {
            'reached': {'started', 'submitted', 'approved', 'resolved'},
            'previous_primary_address': 'Old Address',
            'moderation_id': 'MOD1',
            'match_id': 55,
        }
        session = session_returning(make_response(payload={}))

        batch.apply_row(
            session, self.config, 'OSID', self.row, 'OSID#abc', facts
        )

        # No discovery call - the match was already known.
        self.assertEqual(1, session.request.call_count)
        self.assertEqual({'match_id': 55},
                         session.request.call_args_list[0][1]['json'])

    def test_a_step_without_the_id_it_produced_stops_the_record(self):
        facts = {'reached': {'started', 'submitted'},
                 'previous_primary_address': 'Old Address'}
        with self.assertRaises(batch.ResumeAmbiguity):
            batch.apply_row(
                session_returning(), self.config, 'OSID', self.row,
                'OSID#abc', facts,
            )


class AlreadyAppliedTest(unittest.TestCase):
    """The two responses that mean 'an earlier attempt already did this'."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config = make_config(self.tmpdir.name)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_promoting_an_already_primary_match_is_success(self):
        # The state this call is trying to reach. Failing the record here
        # would send the whole sequence round again.
        session = session_returning(make_response(
            status_code=400,
            text='{"detail":"Facility is created from item."}',
        ))
        batch.promote_match(session, self.config, 'OSID', 55)

    def test_a_different_bad_request_still_fails(self):
        response = make_response(
            status_code=400, text='{"detail":"Match is not to facility"}'
        )
        response.raise_for_status.side_effect = RuntimeError('400')
        with self.assertRaises(RuntimeError):
            batch.promote_match(
                session_returning(response), self.config, 'OSID', 55
            )

    def test_approving_a_non_pending_event_stops_the_record_loudly(self):
        # Approved-then-interrupted and rejected look the same from here,
        # and the event list lags because it is served from the search
        # index. Guessing 'approved' would promote whatever our newest
        # earlier match happens to be over this location.
        session = session_returning(make_response(
            status_code=410,
            text='{"detail":"The moderation event should be in PENDING '
                 'status."}',
        ))
        with self.assertRaises(batch.ResumeAmbiguity) as caught:
            batch.approve_event(session, self.config, 'MOD1', 'OSID')
        self.assertIn('MOD1', str(caught.exception))
        self.assertIn('moderation queue', str(caught.exception))


class VerificationTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config = make_config(self.tmpdir.name)
        self.row = {'os_id': 'OSID', 'name': 'n', 'address': 'a',
                    'country': 'US'}

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_a_failed_read_back_still_counts_the_record_as_done(self):
        # The writes have all landed by this point. Marking the record
        # FAILED because a pure read failed hands the next run a record to
        # redo, and redoing it means a second contribution and a second
        # promote against a location that is already correct.
        session = session_returning(ConnectionError('read timed out'))

        entry = batch.verification_entry(
            session, self.config, 'OSID', self.row, 'OSID#abc', 'Old Address'
        )

        self.assertEqual('verified', entry['step'])
        self.assertTrue(entry['status'].startswith('CHECK'))
        self.assertIn('only the confirming read failed', entry['status'])

        batch.journal_write(self.config, entry)
        self.assertIn('OSID#abc', batch.completed_row_keys(self.config))

    def test_a_successful_read_back_reports_the_change(self):
        session = session_returning(make_response(payload={'properties': {
            'name': 'New', 'address': 'New Address'}}))

        entry = batch.verification_entry(
            session, self.config, 'OSID', self.row, 'OSID#abc', 'Old Address'
        )

        self.assertEqual('New Address', entry['resulting_primary_address'])
        self.assertEqual('OK', entry['status'])


class RowProgressTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config = make_config(self.tmpdir.name)

    def tearDown(self):
        self.tmpdir.cleanup()

    def write(self, *entries):
        for entry in entries:
            batch.journal_write(self.config, entry)

    def test_facts_survive_an_attempt_that_later_failed(self):
        # A promote that happened stays happened even though the attempt
        # carrying it ended in failure.
        self.write(
            {'row_key': 'K', 'step': 'started', 'os_id': 'OSID',
             'submitted_address': 'a', 'previous_primary_address': 'Old'},
            {'row_key': 'K', 'step': 'submitted', 'moderation_id': 'MOD1'},
            {'row_key': 'K', 'step': 'approved'},
            {'row_key': 'K', 'step': 'resolved', 'match_id': 55},
            {'row_key': 'K', 'step': 'promoted', 'match_id': 55},
            {'row_key': 'K', 'step': 'FAILED', 'os_id': 'OSID',
             'previous_primary_address': '', 'status': 'FAILED read'},
        )

        facts = batch.row_progress(self.config)['K']
        self.assertEqual('promoted', batch.furthest_step(facts))
        self.assertEqual('MOD1', facts['moderation_id'])
        self.assertEqual(55, facts['match_id'])
        # Not blanked by the FAILED entry, which records an outcome rather
        # than a step the record reached.
        self.assertEqual('Old', facts['previous_primary_address'])

    def test_an_untouched_record_has_no_progress(self):
        self.assertEqual({}, dict(batch.row_progress(self.config)))

    def test_the_report_surfaces_a_record_that_never_terminated(self):
        # A run killed outright writes no FAILED entry for the record it
        # was in the middle of, so without this its half-applied state
        # appears nowhere at all.
        self.write(
            {'row_key': 'K', 'step': 'started', 'os_id': 'OSID',
             'submitted_address': 'a', 'previous_primary_address': 'Old'},
            {'row_key': 'K', 'step': 'submitted', 'moderation_id': 'MOD1'},
        )

        rows = batch.write_report(self.config)

        self.assertEqual(1, len(rows))
        self.assertEqual('OSID', rows[0][0])
        self.assertTrue(rows[0][-1].startswith('INCOMPLETE'))
        self.assertIn('submitted', rows[0][-1])

    def test_a_finished_record_is_not_also_reported_incomplete(self):
        self.write(
            {'row_key': 'K', 'step': 'started', 'os_id': 'OSID',
             'submitted_address': 'a', 'previous_primary_address': 'Old'},
            {'row_key': 'K', 'step': 'verified', 'os_id': 'OSID',
             'submitted_address': 'a', 'previous_primary_address': 'Old',
             'resulting_primary_address': 'New', 'status': 'OK'},
        )

        rows = batch.write_report(self.config)
        self.assertEqual(1, len(rows))
        self.assertEqual('OK', rows[0][-1])


if __name__ == '__main__':
    unittest.main()
