from itertools import count
from unittest.mock import patch

from django.contrib.gis.geos import Point
from django.core.cache import caches
from django.db import connection
from django.test import override_settings
from django.urls import reverse

from api.models import Facility, FacilityListItem, FacilityMatch
from api.models.facility.facility_index import FacilityIndex
from api.services.processing_type_search import MAX_SUGGESTION_LIMIT
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase


class ProcessingTypeSuggestionsAPITest(FacilityAPITestCaseBase):
    def setUp(self):
        super().setUp()
        caches['view_cache'].clear()
        self.url = reverse('processing_type_suggestions')
        self.row_indexes = count(2)

        # api_facility_processing_value follows this write through the
        # facility_index_processing_value_update_trigger.
        FacilityIndex.objects.filter(id=self.facility.id).update(
            facility_type=['Printing, Product Dyeing and Laundering'],
            processing_type=['Dyeing', 'yarn dyeing services', 'null'],
        )

    def _index_processing_types(self, processing_types, locations=1):
        """
        Index the given processing types on locations of their own.

        api_facility_processing_value counts locations, so a value needs one
        location per unit of count. The index rows are written directly:
        going through ExtendedField would exercise the matching code, which
        the typeahead reads the results of rather than depends on.
        """
        facilities = []
        for _ in range(locations):
            row_index = next(self.row_indexes)
            list_item = FacilityListItem.objects.create(
                name=f'Item {row_index}',
                address='Address',
                country_code='US',
                sector=['Apparel'],
                row_index=row_index,
                geocoded_point=Point(row_index, row_index),
                status=FacilityListItem.CONFIRMED_MATCH,
                source=self.source,
            )
            facility = Facility.objects.create(
                name=f'Name {row_index}',
                address='Address',
                country_code='US',
                location=Point(row_index, row_index),
                created_from=list_item,
            )
            FacilityMatch.objects.create(
                status=FacilityMatch.AUTOMATIC,
                facility=facility,
                facility_list_item=list_item,
                confidence=0.85,
                results='',
            )
            list_item.facility = facility
            list_item.save()
            FacilityIndex.objects.filter(id=facility.id).update(
                processing_type=processing_types,
            )
            facilities.append(facility)

        caches['view_cache'].clear()
        return facilities

    @staticmethod
    def _values(response):
        return [row['value'] for row in response.data]

    def test_returns_ranked_suggestions(self):
        response = self.client.get(
            self.url,
            {'q': 'dyeing'},
        )

        self.assertEqual(response.status_code, 200)
        values = self._values(response)
        self.assertEqual(values[0], 'Dyeing')
        self.assertIn('yarn dyeing services', values)
        self.assertNotIn('null', values)

        dyeing = response.data[0]
        self.assertEqual(dyeing['count'], 1)
        self.assertTrue(dyeing['in_taxonomy'])
        self.assertEqual(
            dyeing['facility_types'],
            ['Printing, Product Dyeing and Laundering'],
        )
        self.assertFalse(dyeing['dim'])

    def test_contributor_value_disappears_with_its_last_location(self):
        FacilityIndex.objects.filter(id=self.facility.id).update(
            processing_type=['Dyeing'],
        )
        caches['view_cache'].clear()

        response = self.client.get(
            self.url,
            {'q': 'yarn'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('yarn dyeing services', self._values(response))

    def test_ranks_exact_over_prefix_over_word_prefix_over_substring(self):
        self._index_processing_types([
            'supersonic finishing',
            'seam sealing sonic',
            'ultra sonic bonding',
            'sonic welding',
            'sonic',
        ])

        response = self.client.get(self.url, {'q': 'sonic'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self._values(response),
            [
                'sonic',
                'sonic welding',
                'ultra sonic bonding',
                'seam sealing sonic',
                'supersonic finishing',
            ],
        )

    def test_the_more_common_of_two_equal_matches_ranks_first(self):
        self._index_processing_types(['sonic bonding', 'sonic welding'])
        self._index_processing_types(['sonic welding'])

        response = self.client.get(self.url, {'q': 'sonic'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [(row['value'], row['count']) for row in response.data],
            [('sonic welding', 2), ('sonic bonding', 1)],
        )

    def test_matching_ignores_case_and_accents(self):
        self._index_processing_types(['Sérigraphie'])

        response = self.client.get(self.url, {'q': 'serigraphie'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._values(response), ['Sérigraphie'])

    def test_casing_variants_share_one_distinct_facility_count(self):
        self._index_processing_types(['CAPS'], locations=2)
        self._index_processing_types(['Caps'])
        self._index_processing_types(['CAPS', 'caps'])

        response = self.client.get(self.url, {'q': 'caps'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [(row['value'], row['count']) for row in response.data],
            [('CAPS', 4)],
        )

    def test_canonical_variant_uses_c_collation_to_break_count_ties(self):
        self._index_processing_types(['Zebra'])
        self._index_processing_types(['ZEBRA'])

        response = self.client.get(self.url, {'q': 'zebra'})

        self.assertEqual(
            [(row['value'], row['count']) for row in response.data],
            [('ZEBRA', 2)],
        )

    def test_case_only_update_preserves_logical_count_and_moves_variant(self):
        FacilityIndex.objects.filter(id=self.facility.id).update(
            processing_type=['CAPS'],
        )
        FacilityIndex.objects.filter(id=self.facility.id).update(
            processing_type=['caps'],
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT value, facility_count
                FROM api_facility_processing_value
                WHERE kind = 'processing_type' AND identity = 'caps'
                """
            )
            logical_row = cursor.fetchone()
            cursor.execute(
                """
                SELECT value, facility_count
                FROM api_facility_processing_value_variant
                WHERE kind = 'processing_type' AND identity = 'caps'
                ORDER BY value COLLATE "C"
                """
            )
            variant_rows = cursor.fetchall()

        self.assertEqual(logical_row, ('caps', 1))
        self.assertEqual(variant_rows, [('caps', 1)])

    def test_removing_dominant_variant_switches_canonical_value(self):
        dominant_facilities = self._index_processing_types(
            ['CAPS'],
            locations=2,
        )
        self._index_processing_types(['Caps'])

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT value, facility_count
                FROM api_facility_processing_value
                WHERE kind = 'processing_type' AND identity = 'caps'
                """
            )
            self.assertEqual(cursor.fetchone(), ('CAPS', 3))

        FacilityIndex.objects.filter(
            id__in=[facility.id for facility in dominant_facilities]
        ).update(processing_type=[])

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT value, facility_count
                FROM api_facility_processing_value
                WHERE kind = 'processing_type' AND identity = 'caps'
                """
            )
            logical_row = cursor.fetchone()
            cursor.execute(
                """
                SELECT value, facility_count
                FROM api_facility_processing_value_variant
                WHERE kind = 'processing_type' AND identity = 'caps'
                """
            )
            variant_rows = cursor.fetchall()

        self.assertEqual(logical_row, ('Caps', 1))
        self.assertEqual(variant_rows, [('Caps', 1)])

    def test_recompute_matches_triggered_logical_and_variant_aggregates(self):
        FacilityIndex.objects.filter(id=self.facility.id).update(
            processing_type=['CAPS', 'caps', 'Accent'],
        )
        self._index_processing_types(['Caps', 'accent'])

        def aggregate_rows(cursor, table):
            cursor.execute(
                f"""
                SELECT kind, identity, value, facility_count
                FROM {table}
                ORDER BY kind, identity, value COLLATE "C"
                """
            )
            return cursor.fetchall()

        with connection.cursor() as cursor:
            logical_before = aggregate_rows(
                cursor,
                'api_facility_processing_value',
            )
            variants_before = aggregate_rows(
                cursor,
                'api_facility_processing_value_variant',
            )
            cursor.execute('CALL recompute_facility_processing_values();')
            logical_after = aggregate_rows(
                cursor,
                'api_facility_processing_value',
            )
            variants_after = aggregate_rows(
                cursor,
                'api_facility_processing_value_variant',
            )

        self.assertEqual(logical_after, logical_before)
        self.assertEqual(variants_after, variants_before)
        self.assertIn(
            ('processing_type', 'caps', 'CAPS', 2),
            logical_after,
        )
        self.assertIn(
            ('processing_type', 'accent', 'Accent', 2),
            logical_after,
        )
        self.assertCountEqual(
            [
                row for row in variants_after
                if row[:2] == ('processing_type', 'caps')
            ],
            [
                ('processing_type', 'caps', 'CAPS', 1),
                ('processing_type', 'caps', 'Caps', 1),
                ('processing_type', 'caps', 'caps', 1),
            ],
        )

    def test_punctuation_variants_remain_independently_selectable(self):
        self._index_processing_types(
            ['Warehousing Distribution'],
            locations=2,
        )
        self._index_processing_types(['Warehousing / Distribution'])

        response = self.client.get(self.url, {'q': 'warehousing'})

        self.assertEqual(
            [(row['value'], row['count']) for row in response.data],
            [
                ('Warehousing Distribution', 2),
                ('Warehousing / Distribution', 1),
            ],
        )
        taxonomy_by_value = {
            row['value']: row['in_taxonomy'] for row in response.data
        }
        self.assertFalse(taxonomy_by_value['Warehousing Distribution'])
        self.assertTrue(taxonomy_by_value['Warehousing / Distribution'])

    def test_accents_and_whitespace_remain_separate_identities(self):
        self._index_processing_types([
            'Serigraphie',
            'Sérigraphie',
            'Dyeing',
            ' Dyeing',
        ])

        serigraphie = self.client.get(self.url, {'q': 'serigraphie'})
        dyeing = self.client.get(self.url, {'q': 'dyeing'})

        self.assertCountEqual(
            [(row['value'], row['count']) for row in serigraphie.data],
            [('Serigraphie', 1), ('Sérigraphie', 1)],
        )
        self.assertIn(
            (' Dyeing', 1),
            [(row['value'], row['count']) for row in dyeing.data],
        )

    def test_synthetic_taxonomy_duplicate_does_not_double_count(self):
        self._index_processing_types(['Yarn Dyeing'], locations=2)

        response = self.client.get(self.url, {'q': 'yarn dyeing'})

        yarn_dyeing = next(
            row for row in response.data
            if row['value'] == 'Yarn Dyeing'
        )
        self.assertEqual(yarn_dyeing['count'], 2)
        self.assertEqual(
            sum(
                row['value'] == 'Yarn Dyeing'
                for row in response.data
            ),
            1,
        )

    def test_taxonomy_suggestion_uses_official_casing_and_combined_count(self):
        self._index_processing_types(['DYEING'], locations=2)

        response = self.client.get(self.url, {'q': 'dyeing'})

        dyeing = next(
            row for row in response.data
            if row['value'] == 'Dyeing'
        )
        self.assertEqual(dyeing['value'], 'Dyeing')
        self.assertEqual(dyeing['label'], 'Dyeing')
        self.assertEqual(dyeing['count'], 3)
        self.assertTrue(dyeing['in_taxonomy'])
        self.assertEqual(
            sum(row['value'].lower() == 'dyeing' for row in response.data),
            1,
        )

    def test_facility_type_promotes_its_children_without_dropping_others(self):
        # Prefix matches outrank matches on a later word, so without a
        # facility type "dyeing services" ranks above "Yarn Dyeing".
        self._index_processing_types(['dyeing services'])

        unranked = self.client.get(self.url, {'q': 'dyeing'})
        ranked = self.client.get(
            self.url,
            {
                'q': 'dyeing',
                'facility_type': 'Printing, Product Dyeing and Laundering',
            },
        )

        unranked_values = self._values(unranked)
        self.assertLess(
            unranked_values.index('dyeing services'),
            unranked_values.index('Yarn Dyeing'),
        )

        ranked_values = self._values(ranked)
        self.assertLess(
            ranked_values.index('Yarn Dyeing'),
            ranked_values.index('dyeing services'),
        )
        dimmed = next(
            row for row in ranked.data if row['value'] == 'dyeing services'
        )
        self.assertTrue(dimmed['dim'])

    def test_multi_parent_value_reports_both_facility_types(self):
        response = self.client.get(self.url, {'q': 'embroidery'})

        self.assertEqual(response.status_code, 200)
        embroidery = next(
            row for row in response.data if row['value'] == 'Embroidery'
        )
        self.assertEqual(
            embroidery['facility_types'],
            ['Textile or Material Production', 'Final Product Assembly'],
        )

    def test_placeholder_values_are_never_suggested(self):
        placeholders = [
            'null',
            'none',
            'n/a',
            'na',
            'unknown',
            'other',
            '-',
            '   ',
            'denim services',
            'boarding',
        ]
        self._index_processing_types([*placeholders, 'Dyeing'])

        for placeholder in placeholders:
            with self.subTest(placeholder=placeholder):
                response = self.client.get(
                    self.url,
                    {'q': placeholder.strip()},
                )

                self.assertEqual(response.status_code, 200)
                self.assertNotIn(placeholder, self._values(response))

    def test_facility_types_are_not_suggested_as_processing_types(self):
        FacilityIndex.objects.filter(id=self.facility.id).update(
            facility_type=['warehouse annex'],
            processing_type=['Dyeing'],
        )
        caches['view_cache'].clear()

        response = self.client.get(self.url, {'q': 'annex'})

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('warehouse annex', self._values(response))

    def test_facility_type_dims_non_children(self):
        response = self.client.get(
            self.url,
            {'q': 'dyeing', 'facility_type': 'Final Product Assembly'},
        )

        self.assertEqual(response.status_code, 200)
        dim_by_value = {row['value']: row['dim'] for row in response.data}
        self.assertTrue(dim_by_value['Dyeing'])

    def test_empty_query_returns_top_values(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)

    def test_empty_query_splits_slots_between_taxonomy_and_contributors(self):
        self._index_processing_types([
            'Cutting',
            'Sewing',
            'alpha contributor',
            'beta contributor',
        ])

        response = self.client.get(self.url, {'limit': 5})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self._values(response),
            [
                'Cutting',
                'Dyeing',
                'Sewing',
                'alpha contributor',
                'beta contributor',
            ],
        )
        self.assertEqual(
            sum(row['in_taxonomy'] for row in response.data),
            3,
        )
        self.assertEqual(
            sum(not row['in_taxonomy'] for row in response.data),
            2,
        )
        self.assertLessEqual(len(response.data), 5)

    def test_empty_query_backfills_when_taxonomy_is_sparse(self):
        self._index_processing_types([
            'alpha contributor',
            'beta contributor',
            'gamma contributor',
        ])

        response = self.client.get(self.url, {'limit': 5})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self._values(response),
            [
                'Dyeing',
                'alpha contributor',
                'beta contributor',
                'gamma contributor',
                'yarn dyeing services',
            ],
        )

    def test_empty_query_backfills_when_contributors_are_sparse(self):
        self._index_processing_types([
            'Cutting',
            'Packing',
            'Sewing',
        ])

        response = self.client.get(self.url, {'limit': 5})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self._values(response),
            [
                'Cutting',
                'Dyeing',
                'Packing',
                'Sewing',
                'yarn dyeing services',
            ],
        )

    def test_empty_query_equal_counts_use_deterministic_value_order(self):
        self._index_processing_types([
            'Cutting',
            'alpha contributor',
        ])

        response = self.client.get(self.url, {'limit': 4})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self._values(response),
            [
                'Cutting',
                'Dyeing',
                'alpha contributor',
                'yarn dyeing services',
            ],
        )

    def test_empty_query_limit_one_favors_taxonomy(self):
        response = self.client.get(self.url, {'limit': 1})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertTrue(response.data[0]['in_taxonomy'])

    def test_empty_query_facility_type_boosts_within_taxonomy_quota(self):
        self._index_processing_types(['Dyeing'], locations=2)
        self._index_processing_types(['Sewing'])

        response = self.client.get(
            self.url,
            {
                'facility_type': 'Final Product Assembly',
                'limit': 2,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['value'], 'Sewing')
        self.assertEqual(response.data[0]['count'], 1)
        self.assertFalse(response.data[0]['dim'])
        self.assertFalse(response.data[1]['in_taxonomy'])

    def test_zero_count_taxonomy_is_hidden_empty_but_suggestible_when_typed(
        self,
    ):
        empty_response = self.client.get(self.url)
        typed_response = self.client.get(self.url, {'q': 'headquarters'})

        self.assertNotIn('Headquarters', self._values(empty_response))
        headquarters = next(
            row for row in typed_response.data
            if row['value'] == 'Headquarters'
        )
        self.assertEqual(headquarters['count'], 0)
        self.assertTrue(headquarters['in_taxonomy'])

    def test_limit_is_applied(self):
        response = self.client.get(
            self.url,
            {'limit': 2},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_limit_is_capped(self):
        response = self.client.get(self.url, {'limit': 1000})

        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response.data), MAX_SUGGESTION_LIMIT)

    def test_blank_limit_uses_default(self):
        response = self.client.get(self.url, {'limit': ''})

        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response.data), MAX_SUGGESTION_LIMIT)

    def test_invalid_limit_returns_400(self):
        response = self.client.get(
            self.url,
            {'limit': 'many'},
        )

        self.assertEqual(response.status_code, 400)

    def test_negative_limit_returns_400(self):
        response = self.client.get(
            self.url,
            {'limit': -1},
        )

        self.assertEqual(response.status_code, 400)

    @override_settings(
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            },
            'view_cache': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            },
        },
    )
    @patch(
        'api.views.facility.processing_type_suggestions'
        '.ProcessingTypeSearch.build_suggestions'
    )
    def test_identical_requests_are_served_from_the_cache(self, mock_build):
        mock_build.return_value = [{
            'value': 'Dyeing',
            'label': 'Dyeing',
            'count': 1,
            'in_taxonomy': True,
            'facility_types': ['Printing, Product Dyeing and Laundering'],
            'dim': False,
        }]
        caches['view_cache'].clear()

        first = self.client.get(self.url, {'q': 'dyeing'})
        second = self.client.get(self.url, {'q': 'dyeing'})

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.data, first.data)
        mock_build.assert_called_once()

        self.client.get(
            self.url,
            {'q': 'dyeing', 'facility_type': 'Office / HQ'},
        )

        self.assertEqual(mock_build.call_count, 2)
