from django.contrib.gis.geos import Point
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


class FacilitiesIsic4FilterTest(FacilityAPITestCaseBase):
    def setUp(self):
        super().setUp()

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
            isic_class=['1410', '1411'],
            facility_type=['Final Product Assembly'],
        )
        FacilityIndex.objects.filter(id=self.facility_two.id).update(
            contributors_count=1,
            isic_section=['J'],
            isic_division=['62'],
            isic_group=['620'],
            isic_class=['6201'],
            processing_type=['Batch Dyeing'],
        )

    def test_class_filter_returns_matching_facilities(self):
        response = self.client.get(
            reverse('facility-list'),
            {'isic_4': 'class:1410'},
        )

        self.assertEqual(response.status_code, 200)
        ids = {feature['id'] for feature in response.data['features']}
        self.assertEqual(ids, {self.facility.id})

    def test_section_filter_returns_matching_facilities(self):
        response = self.client.get(
            reverse('facility-list'),
            {'isic_4': ['section:J', 'section:C']},
        )

        self.assertEqual(response.status_code, 200)
        ids = {feature['id'] for feature in response.data['features']}
        self.assertEqual(ids, {self.facility.id, self.facility_two.id})

    def test_group_filter_returns_matching_facilities(self):
        response = self.client.get(
            reverse('facility-list'),
            {'isic_4': 'group:620'},
        )

        self.assertEqual(response.status_code, 200)
        ids = {feature['id'] for feature in response.data['features']}
        self.assertEqual(ids, {self.facility_two.id})

    def test_multiple_class_filters_use_or_semantics(self):
        response = self.client.get(
            reverse('facility-list'),
            {'isic_4': ['class:1410', 'class:6201']},
        )

        self.assertEqual(response.status_code, 200)
        ids = {feature['id'] for feature in response.data['features']}
        self.assertEqual(ids, {self.facility.id, self.facility_two.id})

    def test_facility_processing_and_isic_use_or_semantics_by_default(self):
        response = self.client.get(
            reverse('facility-list'),
            {
                'facility_type': 'Final Product Assembly',
                'isic_4': 'section:J',
            },
        )

        self.assertEqual(response.status_code, 200)
        ids = {feature['id'] for feature in response.data['features']}
        self.assertEqual(ids, {self.facility.id, self.facility_two.id})

    def test_facility_processing_and_isic_use_and_when_requested(self):
        response = self.client.get(
            reverse('facility-list'),
            {
                'facility_type': 'Final Product Assembly',
                'isic_4': 'section:J',
                'combine_facility_processing_isic': 'AND',
            },
        )

        self.assertEqual(response.status_code, 200)
        ids = {feature['id'] for feature in response.data['features']}
        self.assertEqual(ids, set())

    def test_facility_processing_and_isic_and_returns_matching_facility(self):
        response = self.client.get(
            reverse('facility-list'),
            {
                'facility_type': 'Final Product Assembly',
                'isic_4': 'section:C',
                'combine_facility_processing_isic': 'AND',
            },
        )

        self.assertEqual(response.status_code, 200)
        ids = {feature['id'] for feature in response.data['features']}
        self.assertEqual(ids, {self.facility.id})
