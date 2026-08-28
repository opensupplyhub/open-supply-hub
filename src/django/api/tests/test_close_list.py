from api.close_list import close_list
from api.models import (
    Contributor,
    Facility,
    FacilityActivityReport,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)

from django.contrib.gis.geos import Point
from django.test import TestCase


class CloseListTest(TestCase):
    def setUp(self):
        self.country_code = "US"

        self.user = User.objects.create(email="one@example.com")

        self.contrib = Contributor.objects.create(
            admin=self.user,
            name="contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.list_one = FacilityList.objects.create(
            header="header", file_name="one", name="list 1"
        )

        self.source_one = Source.objects.create(
            source_type=Source.LIST,
            facility_list=self.list_one,
            contributor=self.contrib,
        )

        self.list_item_one = FacilityListItem.objects.create(
            row_index=0,
            source=self.source_one,
            sector=[],
            status=FacilityListItem.MATCHED,
        )

        self.facility_one = Facility.objects.create(
            country_code=self.country_code,
            created_from=self.list_item_one,
            facilitylistitem=self.list_item_one,
            location=Point(0, 0),
            is_closed=False,
        )
        self.list_item_one.facility = self.facility_one
        self.list_item_one.save()

        self.list_item_one_b = FacilityListItem.objects.create(
            row_index=0,
            source=self.source_one,
            sector=[],
            status=FacilityListItem.MATCHED,
        )

        self.facility_one_b = Facility.objects.create(
            country_code=self.country_code,
            created_from=self.list_item_one_b,
            facilitylistitem=self.list_item_one_b,
            location=Point(0, 0),
            is_closed=False,
        )
        self.list_item_one_b.facility = self.facility_one_b
        self.list_item_one_b.save()

        self.list_two = FacilityList.objects.create(
            header="header", file_name="one-b", name="list 2"
        )

        self.source_two = Source.objects.create(
            source_type=Source.LIST,
            facility_list=self.list_two,
            contributor=self.contrib,
        )

        self.list_item_two = FacilityListItem.objects.create(
            row_index=0,
            source=self.source_two,
            sector=[],
            status=FacilityListItem.MATCHED,
        )

        self.facility_two = Facility.objects.create(
            country_code=self.country_code,
            created_from=self.list_item_two,
            facilitylistitem=self.list_item_two,
            location=Point(0, 0),
            is_closed=False,
        )
        self.list_item_two.facility = self.facility_two
        self.list_item_two.save()

    def test_closes_list(self):
        close_list(self.list_one.id, self.user.id)

        f_one = Facility.objects.get(id=self.facility_one.id)
        f_one_b = Facility.objects.get(id=self.facility_one_b.id)
        f_two = Facility.objects.get(id=self.facility_two.id)

        self.assertTrue(f_one.is_closed)
        self.assertTrue(f_one_b.is_closed)
        self.assertFalse(f_two.is_closed)

        activity = FacilityActivityReport.objects.all().count()
        self.assertEqual(2, activity)

    def test_closes_only_rows_matching_status(self):
        self.list_item_one.raw_json = {'name': 'a', 'Status': 'inactive'}
        self.list_item_one.save()
        self.list_item_one_b.raw_json = {'name': 'b', 'Status': 'ACTIVE'}
        self.list_item_one_b.save()

        summary = close_list(self.list_one.id, self.user.id,
                             status_field='status',
                             status_values=['INACTIVE', 'SUSPENDED'])

        self.assertTrue(
            Facility.objects.get(id=self.facility_one.id).is_closed)
        self.assertFalse(
            Facility.objects.get(id=self.facility_one_b.id).is_closed)
        self.assertFalse(
            Facility.objects.get(id=self.facility_two.id).is_closed)
        self.assertEqual(1, summary['closed'])
        self.assertEqual(1, FacilityActivityReport.objects.count())

    def test_active_row_keeps_shared_facility_open(self):
        # Two rows point at the same facility; one INACTIVE, one ACTIVE.
        self.list_item_one.raw_json = {'status': 'INACTIVE'}
        self.list_item_one.save()
        self.list_item_one_b.raw_json = {'status': 'ACTIVE'}
        self.list_item_one_b.facility = self.facility_one
        self.list_item_one_b.save()

        summary = close_list(self.list_one.id, self.user.id,
                             status_field='status',
                             status_values=['INACTIVE'])

        self.assertFalse(
            Facility.objects.get(id=self.facility_one.id).is_closed)
        self.assertEqual(0, summary['closed'])

    def test_dry_run_writes_nothing(self):
        self.list_item_one.raw_json = {'status': 'SUSPENDED'}
        self.list_item_one.save()

        summary = close_list(self.list_one.id, self.user.id,
                             status_field='status',
                             status_values=['INACTIVE', 'SUSPENDED'],
                             dry_run=True)

        self.assertTrue(summary['dry_run'])
        self.assertEqual(1, summary['to_close'])
        self.assertIn(self.facility_one.id, summary['facility_ids'])
        self.assertFalse(
            Facility.objects.get(id=self.facility_one.id).is_closed)
        self.assertEqual(0, FacilityActivityReport.objects.count())

    def test_already_closed_facilities_are_skipped(self):
        self.list_item_one.raw_json = {'status': 'INACTIVE'}
        self.list_item_one.save()
        self.facility_one.is_closed = True
        self.facility_one.save()

        summary = close_list(self.list_one.id, self.user.id,
                             status_field='status',
                             status_values=['INACTIVE'])

        self.assertEqual(0, summary['closed'])
        self.assertEqual(0, FacilityActivityReport.objects.count())
