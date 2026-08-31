from django.contrib.gis.geos import Point
from django.core.cache import caches
from django.urls import reverse

from api.models import (
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
)
from api.models.facility.facility_index import FacilityIndex
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
            isic_section=['C'],
            isic_division=['14'],
            isic_group=['141'],
            isic_class=['1410'],
        )
        FacilityIndex.objects.filter(id=self.facility_two.id).update(
            contributors_count=1,
            isic_section=['J'],
            isic_class=['620'],
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
            {'kind': 'facility_processing'},
        )

        self.assertEqual(response.status_code, 400)
