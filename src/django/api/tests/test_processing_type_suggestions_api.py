from itertools import count
from unittest.mock import patch

from django.contrib.gis.geos import Point
from django.core.cache import caches
from django.test import override_settings
from django.urls import reverse

from api.models import Facility, FacilityListItem, FacilityMatch
from api.models.facility.facility_index import FacilityIndex
from api.processing_type_search import MAX_SUGGESTION_LIMIT
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

        caches['view_cache'].clear()

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

    def test_casing_variants_collapse_into_one_suggestion(self):
        self._index_processing_types(['sonic welding'], locations=2)
        self._index_processing_types(['Sonic Welding'])

        response = self.client.get(self.url, {'q': 'sonic'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [(row['value'], row['count']) for row in response.data],
            [('sonic welding', 2)],
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
        self.assertEqual(len(response.data), MAX_SUGGESTION_LIMIT)

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
        '.search_processing_types'
    )
    def test_identical_requests_are_served_from_the_cache(self, mock_search):
        mock_search.return_value = [{
            'value': 'Dyeing',
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
        mock_search.assert_called_once()

        self.client.get(
            self.url,
            {'q': 'dyeing', 'facility_type': 'Office / HQ'},
        )

        self.assertEqual(mock_search.call_count, 2)
