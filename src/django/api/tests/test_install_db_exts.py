from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase


class InstallDbExtsTest(SimpleTestCase):
    '''
    A failing CREATE EXTENSION must not leave the command exiting zero: the
    release procedure treats a successful run as proof that the extensions
    (pgaudit in particular) are installed. See OSDEV-2997.
    '''

    def _mock_connection(self, failing_extensions):
        def execute(sql):
            for extension_name in failing_extensions:
                if f'IF NOT EXISTS {extension_name};' in sql:
                    raise Exception(
                        f'{extension_name} must be loaded via '
                        'shared_preload_libraries'
                    )

        cursor = MagicMock()
        cursor.execute.side_effect = execute
        connection = MagicMock()
        connection.cursor.return_value.__enter__.return_value = cursor
        return connection, cursor

    def test_raises_when_an_extension_fails(self):
        connection, _ = self._mock_connection(['pgaudit'])

        with patch('api.management.commands.install_db_exts.connection',
                   connection):
            with self.assertRaises(CommandError) as context:
                call_command('install_db_exts')

        self.assertIn('pgaudit', str(context.exception))

    def test_attempts_every_extension_before_failing(self):
        connection, cursor = self._mock_connection(['btree_gin'])

        with patch('api.management.commands.install_db_exts.connection',
                   connection):
            with self.assertRaises(CommandError):
                call_command('install_db_exts')

        # The first extension fails, but the rest are still attempted.
        self.assertEqual(cursor.execute.call_count, 6)

    def test_succeeds_when_every_extension_installs(self):
        connection, cursor = self._mock_connection([])

        with patch('api.management.commands.install_db_exts.connection',
                   connection):
            call_command('install_db_exts')

        self.assertEqual(cursor.execute.call_count, 6)
