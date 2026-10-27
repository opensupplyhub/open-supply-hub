from django.db import connection
from django.test import TestCase


class SearchFunctionRestoreSafetyTest(TestCase):
    """
    Guards the search helpers of migration 0233 against the empty search path
    pg_dump writes into every dump, which is where their expression indexes
    are rebuilt.
    """

    def _fetch_without_search_path(self, statement, params=None):
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL search_path = ''")
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
        The restore itself: pg_restore inlines both helpers while creating
        these indexes, and an unqualified name in either body fails the whole
        restore rather than just the index.
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
        )

        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL search_path = ''")
            for statement in statements:
                cursor.execute(statement)
