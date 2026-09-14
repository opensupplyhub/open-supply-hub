from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, override_settings

from api.constants import OriginSource


SYNC_ARGS = [
    '--source-host', 'source.example',
    '--source-name', 'oshub',
    '--source-user', 'sync',
    '--source-password', 'secret',
]


class SyncDatabasesReassertHookTest(SimpleTestCase):
    '''
    After a successful sync on the RBA instance, promotions the overwrite
    reverted have to be restored in the same job. These tests cover that
    hook without running the synchronizer.
    '''

    def _run(self, extra_args=None):
        args = list(SYNC_ARGS)
        if extra_args:
            args.extend(extra_args)
        call_command('sync_databases', *args, stdout=StringIO())

    @override_settings(INSTANCE_SOURCE=OriginSource.RBA)
    @patch('api.management.commands.sync_databases.call_command')
    @patch('api.management.commands.sync_databases.DatabaseSynchronizer')
    def test_reasserts_promotions_after_a_successful_sync_on_rba(
            self, synchronizer_cls, nested_call_command):
        self._run()

        synchronizer_cls.return_value.sync_all.assert_called_once()
        nested_call_command.assert_called_once_with(
            'reassert_rba_promotions',
            dry_run=False,
        )

    @override_settings(INSTANCE_SOURCE=OriginSource.RBA)
    @patch('api.management.commands.sync_databases.call_command')
    @patch('api.management.commands.sync_databases.DatabaseSynchronizer')
    def test_passes_dry_run_through_to_the_reassert(
            self, synchronizer_cls, nested_call_command):
        self._run(['--dry-run'])

        nested_call_command.assert_called_once_with(
            'reassert_rba_promotions',
            dry_run=True,
        )

    @override_settings(INSTANCE_SOURCE=OriginSource.OSHUB)
    @patch('api.management.commands.sync_databases.call_command')
    @patch('api.management.commands.sync_databases.DatabaseSynchronizer')
    def test_skips_reassert_outside_the_rba_instance(
            self, synchronizer_cls, nested_call_command):
        self._run()

        synchronizer_cls.return_value.sync_all.assert_called_once()
        nested_call_command.assert_not_called()

    @override_settings(INSTANCE_SOURCE=OriginSource.RBA)
    @patch('api.management.commands.sync_databases.call_command')
    @patch('api.management.commands.sync_databases.DatabaseSynchronizer')
    def test_does_not_reassert_when_the_sync_fails(
            self, synchronizer_cls, nested_call_command):
        synchronizer_cls.return_value.sync_all.side_effect = RuntimeError(
            'source unreachable'
        )

        with self.assertRaises(CommandError) as context:
            self._run()

        self.assertIn('Synchronization failed', str(context.exception))
        nested_call_command.assert_not_called()

    @override_settings(INSTANCE_SOURCE=OriginSource.RBA)
    @patch('api.management.commands.sync_databases.call_command')
    @patch('api.management.commands.sync_databases.DatabaseSynchronizer')
    def test_reassert_failure_is_not_relabelled_a_sync_failure(
            self, synchronizer_cls, nested_call_command):
        nested_call_command.side_effect = CommandError(
            '2 promotion(s) could not be re-asserted. See the log for details.'
        )

        with self.assertRaises(CommandError) as context:
            self._run()

        self.assertNotIn('Synchronization failed', str(context.exception))
        self.assertIn('could not be re-asserted', str(context.exception))
