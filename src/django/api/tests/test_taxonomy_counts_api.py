from django.contrib.gis.geos import Point
from django.core.cache import caches
from django.urls import reverse
from waffle.testutils import override_switch

from api.models import (
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
)
from api.models.facility.facility_index import FacilityIndex
from api.taxonomy_counts import compute_isic4_counts
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase


@override_switch('enable_isic_taxonomy', active=True)
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

    def test_unknown_param_returns_400(self):
        # The response cache keys on every param; an unknown one would
        # force a full count on each request.
        response = self.client.get(
            reverse('taxonomy_counts'),
            {'kind': 'isic4', 'cache_buster': '1'},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('cache_buster', response.data)

    def test_repeated_param_returns_400(self):
        response = self.client.get(
            reverse('taxonomy_counts'),
            {'kind': ['isic4', 'isic4']},
        )

        self.assertEqual(response.status_code, 400)

    @override_switch('enable_isic_taxonomy', active=False)
    def test_switch_off_returns_404_that_is_not_cached(self):
        response = self.client.get(
            reverse('taxonomy_counts'),
            {'kind': 'isic4'},
        )
        self.assertEqual(response.status_code, 404)

        # Turning the switch on shows counts at once, not after the cache.
        with override_switch('enable_isic_taxonomy', active=True):
            response = self.client.get(
                reverse('taxonomy_counts'),
                {'kind': 'isic4'},
            )
        self.assertEqual(response.data['section:C'], 1)

        # Back off: not answered from the counts cached while it was on.
        response = self.client.get(
            reverse('taxonomy_counts'),
            {'kind': 'isic4'},
        )
        self.assertEqual(response.status_code, 404)

    def test_invalid_kind_returns_400(self):
        response = self.client.get(
            reverse('taxonomy_counts'),
            {'kind': 'facility_processing'},
        )

        self.assertEqual(response.status_code, 400)

    def test_counts_match_a_brute_force_count(self):
        FacilityIndex.objects.filter(id=self.facility.id).update(
            isic_mapped_section=['C', 'H'],
            isic_mapped_division=['14', '52'],
            isic_mapped_group=['141', '521'],
            isic_mapped_class=['1410', '5210'],
        )
        FacilityIndex.objects.filter(id=self.facility_two.id).update(
            isic_mapped_section=['C'],
            isic_mapped_class=['1410'],
        )

        for include_mapped in (False, True):
            expected = {}
            for index in FacilityIndex.objects.all():
                for level in ('section', 'division', 'group', 'class'):
                    codes = set(getattr(index, f'isic_{level}'))
                    if include_mapped:
                        codes |= set(getattr(index, f'isic_mapped_{level}'))
                    for code in codes:
                        key = f'{level}:{code}'
                        expected[key] = expected.get(key, 0) + 1
            with self.subTest(include_mapped=include_mapped):
                self.assertEqual(
                    compute_isic4_counts(include_mapped=include_mapped),
                    expected,
                )
