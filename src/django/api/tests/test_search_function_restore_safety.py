from contextlib import contextmanager

from django.db import connection
from django.test import TestCase


class SearchFunctionRestoreSafetyTest(TestCase):
    """
    Guards the search helpers of migration 0233 against the empty search path
    pg_dump writes into every dump, which is where their expression indexes
    are rebuilt.
    """

    @contextmanager
    def _empty_search_path(self):
        """
        A cursor running under the empty search path pg_dump sets, restored
        afterwards so later statements in the test see the schemas again. Not
        restored on error: the aborted transaction would turn the RESET into
        an InFailedSqlTransaction that masks the failure this test exists to
        surface, and the rollback discards the SET LOCAL anyway.
        """
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL search_path = ''")
            yield cursor
            cursor.execute("RESET search_path")

    def _fetch_without_search_path(self, statement, params):
        with self._empty_search_path() as cursor:
            cursor.execute(statement, params)
            row = cursor.fetchone()

        return row[0] if row else None

    def test_immutable_unaccent_resolves_without_search_path(self):
        result = self._fetch_without_search_path(
            'SELECT public.immutable_unaccent(%s)', ['Tejeduría']
        )

        self.assertEqual(result, 'Tejeduria')

    def test_search_text_resolves_without_search_path(self):
        result = self._fetch_without_search_path(
            'SELECT public.facility_processing_search_text(%s, %s)',
            [['Final Product Assembly'], ['Tejeduría']],
        )

        self.assertEqual(result, 'final product assembly tejeduria')

    def test_expression_indexes_build_without_search_path(self):
        """
        The restore itself: pg_restore inlines the helpers while creating
        0233's four expression indexes, and an unqualified name in any body
        fails the whole restore rather than just the index. Building the
        lower_varchar_array pair too keeps an edit to that helper, safe today
        only because its body names nothing outside pg_catalog, from breaking
        the next dump unnoticed.
        """
        statements = (
            'CREATE INDEX restore_safety_fp_search_trgm '
            'ON public.api_facilityindex USING gin ('
            'public.facility_processing_search_text('
            'facility_type, processing_type) public.gin_trgm_ops)',
            'CREATE INDEX restore_safety_value_search_trgm '
            'ON public.api_facility_processing_value USING gin ('
            'kind, public.immutable_unaccent(lower(value)) '
            'public.gin_trgm_ops)',
            'CREATE INDEX restore_safety_facility_type_lower_gin '
            'ON public.api_facilityindex USING gin ('
            'public.lower_varchar_array(facility_type))',
            'CREATE INDEX restore_safety_processing_type_lower_gin '
            'ON public.api_facilityindex USING gin ('
            'public.lower_varchar_array(processing_type))',
        )

        with self._empty_search_path() as cursor:
            for statement in statements:
                cursor.execute(statement)

            cursor.execute(
                "SELECT count(*) FROM pg_class "
                "WHERE relname LIKE 'restore_safety_%'"
            )
            self.assertEqual(cursor.fetchone()[0], len(statements))
