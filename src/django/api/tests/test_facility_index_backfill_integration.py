from django.contrib.gis.geos import Point
from django.db import connection
from django.test import TestCase

from api.facility_index_backfill.specs import build_count_sql, get_field_spec
from api.models import Contributor, User
from api.models.facility.facility_index import FacilityIndex


class FacilityIndexBackfillIntegrationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='backfill-test@example.com')
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='Backfill Test Contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

    def _create_facility_index(self, facility_id, contributors):
        return FacilityIndex.objects.create(
            id=facility_id,
            name='Test Facility',
            address='123 Main St',
            country_code='US',
            location=Point(0, 0),
            contributors_count=1 if contributors else 0,
            contributors_id=[self.contributor.id] if contributors else [],
            contributors=contributors,
            contrib_types=[Contributor.OTHER_CONTRIB_TYPE],
            facility_addresses=[{'address': '123 Main St'}],
            extended_fields=[],
            lists=[],
            approved_claim_ids=[],
            facility_names=[],
        )

    def _count_rows_for_worker(self, workers, worker_id):
        spec = get_field_spec('contributors')
        count_sql = build_count_sql(spec)
        with connection.cursor() as cursor:
            cursor.execute(
                count_sql,
                {'workers': workers, 'worker_id': worker_id},
            )
            return cursor.fetchone()[0]

    def test_count_sql_skips_empty_contributors(self):
        self._create_facility_index('US2021250EMPTY1', [])
        self._create_facility_index(
            'US2021250FILLED1',
            [{'id': self.contributor.id, 'name': 'Test'}],
        )

        count = self._count_rows_for_worker(workers=1, worker_id=0)

        self.assertEqual(count, 1)

    def test_partition_counts_are_disjoint_and_complete(self):
        facility_ids = [
            'US2021250PART01',
            'US2021250PART02',
            'US2021250PART03',
            'US2021250PART04',
            'US2021250PART05',
        ]
        contributor = {'id': self.contributor.id, 'name': 'Test'}
        for facility_id in facility_ids:
            self._create_facility_index(facility_id, [contributor])

        workers = 2
        total = sum(
            self._count_rows_for_worker(workers=workers, worker_id=worker_id)
            for worker_id in range(workers)
        )

        self.assertEqual(total, len(facility_ids))
