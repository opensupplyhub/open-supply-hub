from unittest.mock import patch

from django.contrib.gis.geos import Point
from django.core.cache import caches
from django.test import override_settings
from django.urls import reverse

from api.models import (
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
)
from api.models.facility.facility_index import FacilityIndex
from api.taxonomy_counts import FACILITY_PROCESSING_CACHE_KEY
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase


class TaxonomyCountsAPITest(FacilityAPITestCaseBase):
    def setUp(self):
        super().setUp()
        caches['view_cache'].clear()

        self.list_two = FacilityList.objects.create(
            header='header',
            file_name='two',
            name='Second List',
        )
        self.source_two = Source.objects.create(
            facility_list=self.list_two,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        self.list_item_two = FacilityListItem.objects.create(
            name='Item Two',
            address='Address Two',
            country_code='US',
            sector=['Apparel'],
            row_index=1,
            geocoded_point=Point(5, 5),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source_two,
        )
        self.facility_two = Facility.objects.create(
            name='Name Two',
            address='Address Two',
            country_code='US',
            location=Point(5, 5),
            created_from=self.list_item_two,
        )
        self.match_two = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility_two,
            facility_list_item=self.list_item_two,
            confidence=0.85,
            results='',
        )
        self.list_item_two.facility = self.facility_two
        self.list_item_two.save()

        FacilityIndex.objects.filter(id=self.facility.id).update(
            contributors_count=2,
            facility_type=['Final Product Assembly'],
            processing_type=['Assembly', 'Cutting'],
            isic_section=['C'],
            isic_division=['14'],
            isic_group=['141'],
            isic_class=['1410'],
        )
        FacilityIndex.objects.filter(id=self.facility_two.id).update(
            contributors_count=1,
            facility_type=['Office / HQ'],
            processing_type=['Office'],
            isic_section=['J'],
            isic_class=['620'],
        )

    def test_facility_processing_counts_match_index(self):
        response = self.client.get(
            reverse('taxonomy_counts'),
            {'kind': 'facility_processing'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['facility_type:Final Product Assembly'],
            1,
        )
        self.assertEqual(response.data['processing_type:Assembly'], 1)
        self.assertEqual(response.data['processing_type:Cutting'], 1)
        self.assertEqual(response.data['facility_type:Office / HQ'], 1)
        self.assertEqual(response.data['processing_type:Office'], 1)

    def test_facility_processing_counts_separate_colliding_labels(self):
        shared_label = 'Printing, Product Dyeing and Laundering'
        FacilityIndex.objects.filter(id=self.facility.id).update(
            facility_type=[shared_label],
            processing_type=['Dyeing'],
        )
        FacilityIndex.objects.filter(id=self.facility_two.id).update(
            facility_type=['Final Product Assembly'],
            processing_type=[shared_label],
        )
        caches['view_cache'].clear()

        response = self.client.get(
            reverse('taxonomy_counts'),
            {'kind': 'facility_processing'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data[f'facility_type:{shared_label}'],
            1,
        )
        self.assertEqual(
            response.data[f'processing_type:{shared_label}'],
            1,
        )

    def test_isic4_counts_match_index(self):
        response = self.client.get(
            reverse('taxonomy_counts'),
            {'kind': 'isic4'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['section:C'], 1)
        self.assertEqual(response.data['section:J'], 1)
        self.assertEqual(response.data['division:14'], 1)
        self.assertEqual(response.data['group:141'], 1)
        self.assertEqual(response.data['class:1410'], 1)
        self.assertEqual(response.data['class:620'], 1)

    def test_invalid_kind_returns_400(self):
        response = self.client.get(
            reverse('taxonomy_counts'),
            {'kind': 'unknown'},
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
    @patch('api.taxonomy_counts.compute_facility_processing_counts')
    def test_facility_processing_counts_use_one_hour_cache(
        self,
        mock_compute,
    ):
        from api.taxonomy_counts import get_facility_processing_counts

        mock_compute.return_value = {'processing_type:Assembly': 99}
        cache = caches['view_cache']

        first = get_facility_processing_counts()
        second = get_facility_processing_counts()

        self.assertEqual(first, {'processing_type:Assembly': 99})
        self.assertEqual(second, {'processing_type:Assembly': 99})
        mock_compute.assert_called_once()
        self.assertEqual(
            cache.get(FACILITY_PROCESSING_CACHE_KEY),
            {'processing_type:Assembly': 99},
        )
