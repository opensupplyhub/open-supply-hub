from django.http import QueryDict
from django.test import SimpleTestCase

from api.facility_processing_query import parse_facility_processing_query
from api.models.facility.facility_manager_index_new import (
    build_fp_match_sql,
    build_fp_relevance_sql,
)


class FacilityProcessingQueryTest(SimpleTestCase):
    def test_removes_blank_values_and_preserves_nonempty_exact_values(self):
        params = QueryDict(
            'facility_type=&facility_type=Office%20%2F%20HQ'
            '&processing_type=%20%20'
            '&processing_type=CAPS'
            '&processing_type_exact='
            '&processing_type_exact=CAPS'
        )

        parsed = parse_facility_processing_query(params)

        self.assertEqual(parsed.facility_types, ['Office / HQ'])
        self.assertEqual(parsed.processing_types, ['CAPS'])
        self.assertEqual(parsed.exact_processing_types, ['CAPS'])

    def test_exact_companion_matches_regular_value_case_insensitively(self):
        params = QueryDict(
            'processing_type=CAPS'
            '&processing_type_exact=Caps'
            '&processing_type_exact=orphan'
        )

        parsed = parse_facility_processing_query(params)

        self.assertEqual(parsed.processing_types, ['CAPS'])
        self.assertEqual(parsed.exact_processing_types, ['Caps'])

    def test_exact_sql_overlaps_the_indexed_lower_cased_array(self):
        """
        The predicate has to match the expression index built by migration
        0233; lower-casing each element inside an unnest instead would read
        every row of api_facilityindex.
        """
        sql, sql_params = build_fp_match_sql(
            [],
            ['CAPS'],
            ['cApS'],
        )

        self.assertIn(
            'lower_varchar_array(processing_type) && %s::text[]',
            sql,
        )
        self.assertNotIn('unnest(processing_type)', sql)
        self.assertEqual(sql_params, [['caps']])

    def test_free_text_sql_prefilters_on_the_trigram_expression(self):
        sql, sql_params = build_fp_match_sql([], ['cement mixing'], [])

        self.assertIn(
            'facility_processing_search_text(facility_type, processing_type)',
            sql,
        )
        self.assertIn('immutable_unaccent(lower(%s))', sql)
        # The containment pattern comes first, then the word-prefix regex for
        # each of the two arrays.
        self.assertEqual(
            sql_params,
            ['cement mixing', r'\mcement\ mixing', r'\mcement\ mixing'],
        )

    def test_free_text_sql_escapes_like_wildcards_in_the_pattern(self):
        _, sql_params = build_fp_match_sql([], ['100%_cotton'], [])

        self.assertEqual(sql_params[0], r'100\%\_cotton')

    def test_relevance_sql_scores_both_tiers_in_one_pass(self):
        sql, sql_params = build_fp_relevance_sql([], ['cement mixing'], [])

        # One aggregate over both arrays rather than an EXISTS per tier and
        # per column, which would run the same regex over the same elements
        # twice.
        self.assertEqual(sql.count('unnest('), 1)
        self.assertEqual(
            sql_params,
            [r'\mcement\ mixing\M', r'\mcement\ mixing'],
        )
