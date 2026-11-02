from django.contrib.gis.geos import Point
from django.urls import reverse

from api.models import (
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
)
from api.isic_taxonomy import revisions
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
            isic_division=['14'],
            isic_group=['141'],
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

    def test_unparseable_isic_values_match_nothing(self):
        # AC4: unmatched input must not fall back to every location.
        for values in (['300'], ['bogus:123'], ['class:'], ['dressing']):
            with self.subTest(values=values):
                response = self.client.get(
                    reverse('facility-list'), {'isic_4': values},
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data['features'], [])

    def test_one_valid_value_still_matches(self):
        response = self.client.get(
            reverse('facility-list'),
            {'isic_4': ['bogus:123', 'class:1410']},
        )

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

    def test_division_filter_returns_descendant_classes(self):
        response = self.client.get(
            reverse('facility-list'),
            {'isic_4': 'division:14'},
        )

        self.assertEqual(response.status_code, 200)
        ids = {feature['id'] for feature in response.data['features']}
        self.assertEqual(ids, {self.facility.id})

    def test_multiple_class_filters_use_or_semantics(self):
        response = self.client.get(
            reverse('facility-list'),
            {'isic_4': ['class:1410', 'class:6201']},
        )

        self.assertEqual(response.status_code, 200)
        ids = {feature['id'] for feature in response.data['features']}
        self.assertEqual(ids, {self.facility.id, self.facility_two.id})

    def test_facility_type_and_isic_use_and_semantics(self):
        response = self.client.get(
            reverse('facility-list'),
            {
                'facility_type': 'Final Product Assembly',
                'isic_4': 'section:J',
            },
        )

        self.assertEqual(response.status_code, 200)
        ids = {feature['id'] for feature in response.data['features']}
        self.assertEqual(ids, set())

    def _set_isic5(self, facility, class_code):
        path = revisions.chain(class_code, '5')
        FacilityIndex.objects.filter(id=facility.id).update(**{
            f'isic5_{level}': [code]
            for level, code in zip(
                ('section', 'division', 'group', 'class'), path,
            )
        })

    def _ids(self, params):
        response = self.client.get(reverse('facility-list'), params)
        self.assertEqual(response.status_code, 200)
        return {feature['id'] for feature in response.data['features']}

    def test_isic_5_filter_returns_isic_5_values(self):
        self._set_isic5(self.facility_two, '6310')

        self.assertEqual(
            self._ids({'isic_5': 'group:631'}), {self.facility_two.id},
        )

    def test_isic_4_filter_finds_values_uploaded_as_isic_5(self):
        # ISIC 5 6310 corresponds to ISIC 4 6311.
        self._set_isic5(self.facility_two, '6310')

        self.assertEqual(
            self._ids({'isic_4': 'class:6311'}), {self.facility_two.id},
        )

    def test_isic_5_filter_finds_values_uploaded_as_isic_4(self):
        # A group selection covers its classes, translated.
        self.assertEqual(
            self._ids({'isic_5': 'group:141'}), {self.facility.id},
        )

    def test_a_code_is_read_in_its_own_revision(self):
        # ISIC 5 1104 is malt; ISIC 4 1104 (soft drinks) does not match it.
        FacilityIndex.objects.filter(id=self.facility.id).update(
            isic_section=['C'], isic_division=['11'],
            isic_group=['110'], isic_class=['1104'],
        )

        self.assertEqual(self._ids({'isic_5': 'class:1104'}), set())
        self.assertEqual(
            self._ids({'isic_4': 'class:1104'}), {self.facility.id},
        )

    def test_isic_4_and_isic_5_combine_with_or(self):
        self._set_isic5(self.facility_two, '6310')

        self.assertEqual(
            self._ids({'isic_4': 'class:1410', 'isic_5': 'class:6310'}),
            {self.facility.id, self.facility_two.id},
        )
