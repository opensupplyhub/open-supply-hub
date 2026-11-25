from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    Sector,
    Source,
    User,
)

from django.contrib.gis.geos import Point
from django.db import connection
from django.test import TestCase

from importlib import import_module


migration = import_module(
    'api.migrations.0285_split_composite_sectors'
)


class SplitCompositeSectorsTest(TestCase):
    """
    The backfill splits only what is safe to split.

    A comma in a stored sector does not prove it is a composite: a
    contributor phrase can contain one, and a composite longer than the
    field limit was truncated mid-word. Both must survive untouched, or
    the backfill invents sectors that never existed. See OSDEV-3923.
    """

    TAXONOMY = (
        'Apparel',
        'Manufacturing',
        'Textiles',
        'Packaging',
        'Technical and Scientific Activities',
    )

    def setUp(self):
        for name in self.TAXONOMY:
            Sector.objects.get_or_create(name=name)

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
        self.row_index = 0

    def make_item(self, sector):
        list_item = FacilityListItem.objects.create(
            name='Facility {}'.format(self.row_index),
            address='address',
            country_code='US',
            sector=sector,
            row_index=self.row_index,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )
        facility = Facility.objects.create(
            name=list_item.name,
            address='Address',
            country_code='US',
            location=Point(0, 0),
            created_from=list_item,
        )
        list_item.facility = facility
        list_item.save()
        self.row_index += 1
        return list_item

    def run_migration(self):
        with connection.schema_editor() as schema_editor:
            migration.split_composite_sectors(None, schema_editor)

    def sector_of(self, list_item):
        list_item.refresh_from_db()
        return sorted(list_item.sector)

    def test_splits_when_every_part_is_a_sector(self):
        item = self.make_item(['Apparel,Manufacturing,Textiles'])
        self.run_migration()
        self.assertEqual(
            ['Apparel', 'Manufacturing', 'Textiles'],
            self.sector_of(item),
        )

    def test_leaves_contributor_text_that_contains_a_comma(self):
        # One phrase, not two sectors: neither half is in the taxonomy,
        # so splitting would invent both.
        phrase = 'Professional, scientific and technical activities'
        item = self.make_item([phrase])
        self.run_migration()
        self.assertEqual([phrase], self.sector_of(item))

    def test_leaves_a_truncated_composite(self):
        # Cut at the field limit mid-word; "Manufactu" is not a sector
        # and no split can repair it.
        truncated = 'Apparel,Textiles,Manufactu'
        item = self.make_item([truncated])
        self.run_migration()
        self.assertEqual([truncated], self.sector_of(item))

    def test_rewrites_a_case_only_mismatch(self):
        item = self.make_item(['packaging'])
        self.run_migration()
        self.assertEqual(['Packaging'], self.sector_of(item))

    def test_leaves_correct_rows_alone(self):
        item = self.make_item(['Apparel', 'Textiles'])
        self.run_migration()
        self.assertEqual(['Apparel', 'Textiles'], self.sector_of(item))

    def test_no_location_loses_a_sector(self):
        item = self.make_item(
            ['Apparel,Manufacturing', 'Technical and Scientific Activities']
        )
        self.run_migration()
        self.assertEqual(
            [
                'Apparel',
                'Manufacturing',
                'Technical and Scientific Activities',
            ],
            self.sector_of(item),
        )

    def test_running_twice_changes_nothing_further(self):
        item = self.make_item(['Apparel,Manufacturing,Textiles'])
        self.run_migration()
        once = self.sector_of(item)
        self.run_migration()
        self.assertEqual(once, self.sector_of(item))
