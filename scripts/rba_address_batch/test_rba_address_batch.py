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
        base_url='https://rba.example.org',
        token='token',
        contributor_id=contributor_id,
        journal=Path(tmpdir) / 'journal.jsonl',
        report=Path(tmpdir) / 'report.csv',
        pause_seconds=0,
    )


def make_response(status_code=200, payload=None, text=''):
    response = MagicMock()
    response.status_code = status_code
    response.text = text
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


class HostGuardTest(unittest.TestCase):
    def test_refuses_the_public_instance(self):
        reason = batch.host_rejection_reason('https://opensupplyhub.org')
        self.assertIsNotNone(reason)
        self.assertIn('public instance', reason)

    def test_refuses_an_unrecognised_host(self):
        self.assertIsNotNone(
            batch.host_rejection_reason('https://example.com')
        )

    def test_allows_a_private_instance(self):
        self.assertIsNone(
            batch.host_rejection_reason('https://rba.example.org')
        )

    def test_allows_local_development(self):
        self.assertIsNone(batch.host_rejection_reason('http://localhost:8000'))

    def test_a_forbidden_marker_wins_over_an_allowed_one(self):
        # A host carrying both an allowed and a forbidden marker must still
        # be refused; the forbidden check is evaluated first for exactly
        # this reason. Built from the constants rather than hardcoding any
        # real host.
        host = 'https://{}.{}'.format(
            batch.ALLOWED_HOST_MARKERS[-1], batch.FORBIDDEN_HOST_MARKERS[0]
        )
        self.assertIsNotNone(batch.host_rejection_reason(host))


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
    def test_the_duplicate_window_raises_a_distinct_error(self):
        # A 422 inside the 15-minute window is a resume artifact, not a
        # failure of the record, and must be distinguishable.
        session = MagicMock()
        session.patch.return_value = make_response(
            status_code=422, text='Duplicate request submitted'
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            config = make_config(tmpdir)
            with self.assertRaises(batch.DuplicateSubmission):
                batch.submit_address(session, config, 'OSID', {
                    'name': 'n', 'address': 'a', 'country': 'US',
                })


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
        session.get.assert_not_called()

    def test_falls_back_to_discovery_when_absent(self):
        session = MagicMock()
        session.get.return_value = make_response(payload={'properties': {
            'matches': [{'match_id': 7, 'list_contributor_id': 42}]
        }})
        match_id = batch.resolve_match_id(session, self.config, 'OSID', {})
        self.assertEqual(7, match_id)
        session.get.assert_called_once()

    def test_discovery_takes_the_newest_of_our_own_matches(self):
        session = MagicMock()
        session.get.return_value = make_response(payload={'properties': {
            'matches': [
                {'match_id': 3, 'list_contributor_id': 42},
                {'match_id': 11, 'list_contributor_id': 42},
                # Another contributor's newer match must be ignored.
                {'match_id': 99, 'list_contributor_id': 7},
            ]
        }})
        self.assertEqual(
            11, batch.discover_match_id(session, self.config, 'OSID')
        )

    def test_discovery_raises_when_none_of_our_matches_are_present(self):
        session = MagicMock()
        session.get.return_value = make_response(payload={'properties': {
            'matches': [{'match_id': 99, 'list_contributor_id': 7}]
        }})
        with self.assertRaises(RuntimeError):
            batch.discover_match_id(session, self.config, 'OSID')


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
            {'row_key': 'C#2', 'step': 'FAILED', 'error': 'boom'},
        ):
            batch.journal_write(self.config, record)

        self.assertEqual({'B#1'}, batch.completed_row_keys(self.config))

    def test_tolerates_blank_lines(self):
        batch.journal_write(self.config, {'row_key': 'B#1',
                                          'step': 'verified'})
        with self.config.journal.open('a') as handle:
            handle.write('\n')
        self.assertEqual({'B#1'}, batch.completed_row_keys(self.config))

    def test_records_are_valid_json_lines(self):
        batch.journal_write(self.config, {'row_key': 'A#0', 'step': 'x'})
        lines = self.config.journal.read_text().splitlines()
        self.assertEqual({'row_key': 'A#0', 'step': 'x'},
                         json.loads(lines[0]))


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

    def test_a_full_record_journals_every_step_and_returns_the_primary(self):
        session = MagicMock()
        session.patch.side_effect = [
            make_response(payload={'moderation_id': 'MOD1'}),
            make_response(payload={'match_id': 55}),
        ]
        session.post.return_value = make_response(payload={})
        session.get.return_value = make_response(payload={'properties': {
            'name': 'Cleaned Name', 'address': 'Cleaned Address',
        }})

        address = batch.process_row(
            session, self.config, 'OSID',
            {'name': 'n', 'address': 'a', 'country': 'US'}, 'OSID#0',
        )

        self.assertEqual('Cleaned Address', address)
        steps = [
            json.loads(line)['step']
            for line in self.config.journal.read_text().splitlines()
        ]
        self.assertEqual(
            ['submitted', 'approved', 'promoted', 'verified'], steps
        )
        # match_id came from the approval, so no discovery call was needed.
        session.get.assert_called_once()


if __name__ == '__main__':
    unittest.main()
