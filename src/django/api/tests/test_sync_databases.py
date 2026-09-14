from unittest.mock import patch

from django.core.management.base import CommandError
from django.test import SimpleTestCase, override_settings

from api.constants import OriginSource
from api.reassert_rba_promotions import after_database_sync


class AfterDatabaseSyncTest(SimpleTestCase):
    '''
    After a successful sync on the RBA instance, promotions the overwrite
    reverted have to be restored. These tests cover that post-sync hook
    without importing sync_databases, whose synchronizer has no unit tests
    and must not enter the coverage report as a side effect.
    '''

    databases = []

    @override_settings(INSTANCE_SOURCE=OriginSource.RBA)
    @patch('api.reassert_rba_promotions.call_command')
    def test_reasserts_promotions_after_an_error_free_sync(
            self, nested_call_command):
        after_database_sync(error_count=0, dry_run=False)

        nested_call_command.assert_called_once_with(
            'reassert_rba_promotions',
            dry_run=False,
        )

    @override_settings(INSTANCE_SOURCE=OriginSource.RBA)
    @patch('api.reassert_rba_promotions.call_command')
    def test_passes_dry_run_through_to_the_reassert(
            self, nested_call_command):
        after_database_sync(error_count=0, dry_run=True)

        nested_call_command.assert_called_once_with(
            'reassert_rba_promotions',
            dry_run=True,
        )

    @override_settings(INSTANCE_SOURCE=OriginSource.OSHUB)
    @patch('api.reassert_rba_promotions.call_command')
    def test_skips_reassert_outside_the_rba_instance(
            self, nested_call_command):
        after_database_sync(error_count=0)

        nested_call_command.assert_not_called()

    @override_settings(INSTANCE_SOURCE=OriginSource.RBA)
    @patch('api.reassert_rba_promotions.call_command')
    def test_does_not_reassert_after_a_partial_sync(
            self, nested_call_command):
        with self.assertRaises(CommandError) as context:
            after_database_sync(error_count=2)

        self.assertIn('2 error(s)', str(context.exception))
        nested_call_command.assert_not_called()
