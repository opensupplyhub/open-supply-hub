from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase

from api.facility_index_backfill.specs import (
    build_count_sql,
    build_update_sql,
    get_field_spec,
    list_field_names,
)
from api.management.commands.backfill_facility_index import Command


class FacilityIndexBackfillTest(SimpleTestCase):
    def test_list_field_names_includes_contributors(self):
        self.assertIn('contributors', list_field_names())

    def test_get_field_spec_raises_for_unknown_group(self):
        with self.assertRaises(CommandError):
            get_field_spec('unknown_group')

    def test_build_update_sql_includes_contributors_column(self):
        spec = get_field_spec('contributors')
        sql = build_update_sql(spec)

        self.assertIn('contributors =', sql)
        self.assertIn('index_contributors(afi.id)', sql)
        self.assertIn('updated_at = now()', sql)
        self.assertIn('hashtext(afi.id::text)::bigint', sql)

    def test_build_count_sql_applies_contributors_filter(self):
        spec = get_field_spec('contributors')
        sql = build_count_sql(spec)

        self.assertIn('cardinality(COALESCE(contributors', sql)
        self.assertIn('hashtext', sql)
        self.assertIn('hashtext(afi.id::text)::bigint', sql)

    def test_build_count_sql_omits_filter_when_not_configured(self):
        spec = {
            'columns': {'foo': 'bar'},
            'from_clause': 'FROM api_facilityindex afi',
            'id_column': 'afi.id',
        }
        sql = build_count_sql(spec)

        self.assertIn('hashtext', sql)
        self.assertNotIn('cardinality', sql)

    def test_build_update_sql_supports_multiple_columns(self):
        spec = {
            'columns': {
                'alpha': 'alpha_expr',
                'beta': 'beta_expr',
            },
        }
        sql = build_update_sql(spec)

        self.assertIn('alpha = alpha_expr', sql)
        self.assertIn('beta = beta_expr', sql)
        self.assertIn('updated_at = now()', sql)

    def test_requires_at_least_one_field_group(self):
        with self.assertRaises(CommandError):
            call_command('backfill_facility_index', fields='')

    def test_unknown_field_group_via_command(self):
        with self.assertRaises(CommandError) as context:
            call_command('backfill_facility_index', fields='bogus')

        self.assertIn('Unknown field group', str(context.exception))
        self.assertIn('contributors', str(context.exception))

    def test_parses_comma_separated_fields_with_whitespace(self):
        command = Command()
        field_names = command._parse_field_names(
            ' contributors , contributors ',
        )

        self.assertEqual(field_names, ['contributors', 'contributors'])

    def test_parallel_must_be_at_least_one(self):
        with self.assertRaises(CommandError) as context:
            call_command(
                'backfill_facility_index',
                fields='contributors',
                parallel=0,
                dry_run=True,
            )

        self.assertIn('--parallel must be at least 1', str(context.exception))

    def test_batch_size_must_be_at_least_one(self):
        with self.assertRaises(CommandError) as context:
            call_command(
                'backfill_facility_index',
                fields='contributors',
                batch_size=0,
                dry_run=True,
            )

        self.assertIn(
            '--batch-size must be at least 1',
            str(context.exception),
        )

    @patch('api.facility_index_backfill.backfill_worker.connection')
    def test_dry_run_reports_contributors_row_count(self, mock_connection):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (42,)
        mock_connection.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        stdout = StringIO()
        call_command(
            'backfill_facility_index',
            fields='contributors',
            dry_run=True,
            stdout=stdout,
        )

        output = stdout.getvalue()
        self.assertIn('contributors', output)
        self.assertIn('42', output)
        self.assertIn('Backfill dry run', output)
        mock_cursor.execute.assert_called()
