from django.contrib.gis.geos import Point
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from api.models import (
    Contributor,
    CountrySectorStats,
    CountryStats,
    Facility,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)
from api.models.facility.facility_index import FacilityIndex


class CountrySectorStatsTest(TestCase):
    """
    The country x sector cube behind the sector-filtered country map.

    Shading the map for one sector live means grouping the whole of
    api_facilityindex by country, which costs seconds for a broad sector
    such as Apparel. The cube turns that into a lookup, which only holds if
    it is built from the same open-locations definition as the unfiltered
    rollup: a cube counting closed locations would shade a country the
    filtered map says has none. See OSDEV-3802.
    """

    # name, country code, sectors, closed
    FACILITIES = (
        ('Aerospace Parts Company', 'US', ['Aerospace'], False),
        ('Mixed Operations Site', 'US', ['Aerospace', 'Mining'], False),
        ('Garment Factory', 'IN', ['Apparel'], False),
        ('Shuttered Aerospace Plant', 'US', ['Aerospace'], True),
    )

    def setUp(self):
        self.user = User.objects.create(email='example@example.com')
        self.user.set_password('password')
        self.user.save()

        self.contrib = Contributor.objects.create(
            admin=self.user,
            name='contributor name',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.list = FacilityList.objects.create(
            header='header', file_name='one', name='list_one'
        )

        self.source = Source.objects.create(
            facility_list=self.list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contrib,
        )

        for row_index, facility in enumerate(self.FACILITIES):
            self.__create_facility(row_index, *facility)

        # Partner-field presence is the slow half of the rebuild and has
        # nothing to do with the cube, so it stays out of these runs.
        call_command('compute_country_stats', '--skip-partner-fields')

    def __create_facility(self, row_index, name, country_code,
                          sectors, is_closed):
        list_item = FacilityListItem.objects.create(
            name=name,
            address='address',
            country_code=country_code,
            sector=sectors,
            row_index=row_index,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )
        facility = Facility.objects.create(
            name=name,
            address='Address',
            country_code=country_code,
            location=Point(0, 0),
            created_from=list_item,
            is_closed=is_closed,
        )
        # FacilityIndex.sector is denormalized from the list items attached
        # to the facility, so without this link the indexed row carries an
        # empty sector and the rebuild counts nothing.
        list_item.facility = facility
        list_item.save()
        return facility

    @staticmethod
    def __cube():
        return {
            (row.sector, row.country_code): row.location_count
            for row in CountrySectorStats.objects.all()
        }

    def __countries(self, response):
        return {
            country['country_code']: country['location_count']
            for country in response.json()['countries']
        }

    def __get(self, **params):
        return self.client.get(reverse('country-stats-list'), params)

    def test_cube_counts_locations_per_country_and_sector(self):
        self.assertEqual(
            {
                ('Aerospace', 'US'): 2,
                ('Mining', 'US'): 1,
                ('Apparel', 'IN'): 1,
            },
            self.__cube(),
        )

    def test_multi_sector_location_counts_once_per_sector(self):
        # `sector` is an array, so one location contributes to each sector
        # it reports. The cube therefore sums to more than the rollup.
        self.assertEqual(
            sum(self.__cube().values()) - 1,
            sum(
                CountryStats.objects
                .values_list('location_count', flat=True)
            ),
        )

    def test_closed_locations_are_excluded(self):
        # Guards the premise of the test rather than the code under test:
        # if the index stopped carrying is_closed, every assertion below
        # would pass while counting the closed plant.
        self.assertTrue(
            FacilityIndex.objects
            .filter(name='Shuttered Aerospace Plant', is_closed=True)
            .exists()
        )

        # Three US locations report Aerospace; the shuttered one is not
        # counted, matching the unfiltered rollup's own definition.
        self.assertEqual(2, self.__cube()[('Aerospace', 'US')])

    def test_rebuild_replaces_the_whole_cube(self):
        stale = CountrySectorStats.objects.create(
            country_code='ZZ',
            sector='Aerospace',
            location_count=99,
            computed_at=CountryStats.objects.first().computed_at,
        )

        call_command('compute_country_stats', '--skip-partner-fields')

        self.assertFalse(
            CountrySectorStats.objects.filter(pk=stale.pk).exists()
        )
        self.assertNotIn(('Aerospace', 'ZZ'), self.__cube())

    def test_endpoint_returns_the_countries_for_a_sector(self):
        response = self.__get(sector='Aerospace')

        self.assertEqual(200, response.status_code)
        self.assertEqual({'US': 2}, self.__countries(response))
        self.assertEqual(1, response.json()['count'])

    def test_endpoint_counts_a_sector_the_location_also_shares(self):
        # The mixed site reports both sectors, so it shades the map for
        # Mining as well as for Aerospace.
        self.assertEqual({'US': 1}, self.__countries(self.__get(
            sector='Mining'
        )))
        self.assertEqual({'IN': 1}, self.__countries(self.__get(
            sector='Apparel'
        )))

    def test_unknown_sector_returns_no_countries(self):
        response = self.__get(sector='Shipbuilding')

        self.assertEqual(200, response.status_code)
        self.assertEqual([], response.json()['countries'])
        self.assertEqual(0, response.json()['count'])
        # A sector we hold nothing for is an empty answer, not a stale one:
        # a null timestamp here would read as a rebuild that never ran.
        self.assertIsNotNone(response.json()['computed_at'])

    def test_no_sector_param_returns_the_unfiltered_list(self):
        response = self.__get()

        self.assertEqual(200, response.status_code)
        self.assertEqual({'US': 2, 'IN': 1}, self.__countries(response))
        self.assertEqual(2, response.json()['count'])

    def test_filtered_and_unfiltered_responses_share_a_shape(self):
        self.assertEqual(
            sorted(self.__get().json().keys()),
            sorted(self.__get(sector='Aerospace').json().keys()),
        )

    def test_filtered_response_is_cacheable_for_an_hour(self):
        # The cache is a Cache-Control header, so the sector separates
        # entries by itself: a shared cache keys on the whole URL.
        self.assertIn(
            'max-age=3600',
            self.__get(sector='Aerospace')['Cache-Control'],
        )
