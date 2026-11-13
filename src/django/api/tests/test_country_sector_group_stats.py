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
    Sector,
    Source,
    User,
)
from api.models.facility.facility_index import FacilityIndex
from api.models.sector_group import SectorGroup


class CountrySectorGroupStatsTest(TestCase):
    """
    The sector rollup behind the country card.

    Raw sector names are too many and too redundant to read: India reports
    141 of them, with "Agriculture", "Food" and "Food Industry" in the top
    three and all meaning the same thing. The card therefore lists sector
    groups, which only holds if a group is counted as distinct locations
    rather than as the sum of its member sectors' counts: a location
    reporting both "Food" and "Food Industry" must count once.

    See OSDEV-3802.
    """

    # name, country code, sectors, closed
    FACILITIES = (
        # Two sectors in the one group: must count once for it.
        ('Cannery', 'IN', ['Food', 'Food Industry'], False),
        # A sector in two groups: must count for both.
        ('Component Plant', 'IN', ['Food Manufacturing'], False),
        # A sector in neither, plus the no-sector sentinel.
        ('Shipyard', 'IN', ['Shipbuilding'], False),
        ('Unknown Site', 'IN', [Sector.DEFAULT_SECTOR_NAME], False),
        ('Shuttered Cannery', 'IN', ['Food', 'Food Industry'], True),
        ('Steel Mill', 'US', ['Metal Manufacturing'], False),
    )

    GROUPS = {
        'Agriculture, Food & Beverage': [
            'Food',
            'Food Industry',
            'Food Manufacturing',
        ],
        'Manufacturing': ['Food Manufacturing', 'Metal Manufacturing'],
        # The taxonomy files "Unspecified" under "Other". The rollup has to
        # keep it out, because the card pins it last and dims it by that
        # exact name.
        'Other': [Sector.DEFAULT_SECTOR_NAME],
    }

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

        self.__create_taxonomy()

        for row_index, facility in enumerate(self.FACILITIES):
            self.__create_facility(row_index, *facility)

        # Partner-field presence is the slow half of the rebuild and has
        # nothing to do with the rollup, so it stays out of these runs.
        call_command('compute_country_stats', '--skip-partner-fields')

    def __create_taxonomy(self):
        # Migration 0154 seeds the real taxonomy into the test database, so
        # without this the fixtures below would quietly inherit its group
        # memberships and the expected counts would depend on it.
        SectorGroup.objects.all().delete()
        Sector.objects.all().delete()

        for group_name, sector_names in self.GROUPS.items():
            group, _ = SectorGroup.objects.get_or_create(name=group_name)
            for sector_name in sector_names:
                sector, _ = Sector.objects.get_or_create(name=sector_name)
                sector.groups.add(group)

        # Deliberately grouped by nothing, to exercise the fallback.
        Sector.objects.get_or_create(name='Shipbuilding')

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
    def __rollup(country_code):
        row = CountryStats.objects.get(country_code=country_code)
        return {entry['sector']: entry['count'] for entry in row.sectors}

    def test_two_sectors_in_one_group_count_once(self):
        # The cannery reports "Food" and "Food Industry". Summing the two
        # member sectors would count it twice in the one group.
        self.assertEqual(2, self.__rollup('IN')[
            'Agriculture, Food & Beverage'
        ])

    def test_a_sector_in_two_groups_counts_for_both(self):
        # The component plant reports only "Food Manufacturing", which the
        # taxonomy files under both groups. Counting it twice across two
        # groups is correct; counting it twice within one is not.
        rollup = self.__rollup('IN')
        self.assertEqual(1, rollup['Manufacturing'])
        self.assertIn('Agriculture, Food & Beverage', rollup)

    def test_sector_with_no_group_falls_to_unspecified(self):
        # The shipyard's sector is in no group and the unknown site reports
        # no sector at all. Both land in the bucket the card pins last,
        # rather than appearing as a group of their own.
        self.assertEqual(2, self.__rollup('IN')[Sector.DEFAULT_SECTOR_NAME])

    def test_unspecified_is_not_rolled_into_its_taxonomy_group(self):
        # The taxonomy files "Unspecified" under "Other". Following that
        # here would hide a pile of missing data inside a real group and
        # lose the card's ordering and dimming, both keyed on the name.
        self.assertNotIn('Other', self.__rollup('IN'))

    def test_closed_locations_are_excluded(self):
        # Guards the premise rather than the code under test: if the index
        # stopped carrying is_closed, the assertion below would pass while
        # counting the shuttered cannery.
        self.assertTrue(
            FacilityIndex.objects
            .filter(name='Shuttered Cannery', is_closed=True)
            .exists()
        )

        # Two open Indian locations report a sector in the food group; the
        # shuttered one is not among them.
        self.assertEqual(2, self.__rollup('IN')[
            'Agriculture, Food & Beverage'
        ])

    def test_whole_rollup_for_a_country(self):
        self.assertEqual(
            {
                'Agriculture, Food & Beverage': 2,
                'Manufacturing': 1,
                Sector.DEFAULT_SECTOR_NAME: 2,
            },
            self.__rollup('IN'),
        )

    def test_stored_shape_is_unchanged(self):
        # The card reads {"sector": ..., "count": ...} and is not changing,
        # so the rollup has to keep writing that shape even though the
        # value is now a group name.
        for row in CountryStats.objects.all():
            self.assertTrue(row.sectors)
            for entry in row.sectors:
                self.assertEqual({'sector', 'count'}, set(entry))
                self.assertIsInstance(entry['sector'], str)
                self.assertIsInstance(entry['count'], int)

    def test_entries_are_ordered_by_count_descending(self):
        counts = [
            entry['count']
            for entry in CountryStats.objects
            .get(country_code='IN').sectors
        ]
        self.assertEqual(sorted(counts, reverse=True), counts)

    def test_group_counts_may_exceed_the_location_count(self):
        # A sector belongs to several groups, so the breakdown still sums
        # to more than the country's locations. The card already says so.
        row = CountryStats.objects.get(country_code='IN')
        self.assertEqual(4, row.location_count)
        self.assertEqual(
            5, sum(entry['count'] for entry in row.sectors)
        )

    def test_detail_endpoint_serves_the_groups(self):
        response = self.client.get(
            reverse('country-stats-detail', args=['IN'])
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            {
                'Agriculture, Food & Beverage': 2,
                'Manufacturing': 1,
                Sector.DEFAULT_SECTOR_NAME: 2,
            },
            {
                entry['sector']: entry['count']
                for entry in response.json()['sectors']
            },
        )

    def test_cube_still_holds_raw_sector_names(self):
        # The country x sector cube drives the search page's sector filter,
        # which filters on raw sectors. It must not follow the card's
        # rollup to groups.
        cube = {
            (row.sector, row.country_code): row.location_count
            for row in CountrySectorStats.objects.all()
        }

        self.assertEqual(1, cube[('Food', 'IN')])
        self.assertEqual(1, cube[('Food Industry', 'IN')])
        self.assertEqual(1, cube[('Metal Manufacturing', 'US')])
        self.assertNotIn(('Agriculture, Food & Beverage', 'IN'), cube)

    def test_filtered_map_endpoint_still_takes_a_raw_sector(self):
        response = self.client.get(
            reverse('country-stats-list'), {'sector': 'Food Industry'}
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            {'IN': 1},
            {
                country['country_code']: country['location_count']
                for country in response.json()['countries']
            },
        )
