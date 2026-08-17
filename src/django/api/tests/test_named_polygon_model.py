from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Point
from django.test import TestCase

from api.models import Contributor, NamedPolygon, User
from api.models.facility.facility_index import FacilityIndex

SQUARE_WKT = 'POLYGON((0 0, 0 10, 10 10, 10 0, 0 0))'
SQUARE_WITH_HOLE_WKT = (
    'POLYGON((0 0, 0 10, 10 10, 10 0, 0 0), (2 2, 2 4, 4 4, 4 2, 2 2))'
)
OTHER_SQUARE_WKT = 'POLYGON((20 20, 20 30, 30 30, 30 20, 20 20))'


class NamedPolygonModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@example.com')
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='Test Contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

    def _make_facility(self, facility_id, lon, lat):
        return FacilityIndex.objects.create(
            id=facility_id,
            name='Test Facility',
            address='123 Main St',
            country_code='US',
            location=Point(lon, lat),
            contributors_count=1,
            contributors_id=[self.contributor.id],
            contributors=[{'id': self.contributor.id, 'name': 'Test'}],
            contrib_types=[Contributor.OTHER_CONTRIB_TYPE],
            facility_addresses=[{'address': '123 Main St'}],
            extended_fields=[],
            lists=[],
            approved_claim_ids=[],
            facility_names=[],
        )

    def test_facilities_respects_holes(self):
        polygon = NamedPolygon.objects.create(
            name='Square with hole',
            description='A square boundary with a hole cut out.',
            geom=MultiPolygon(GEOSGeometry(SQUARE_WITH_HOLE_WKT)),
        )
        inside = self._make_facility('US1000000INSD', 1, 1)
        in_hole = self._make_facility('US1000000HOLE', 3, 3)
        outside = self._make_facility('US1000000OUTS', 50, 50)

        result_ids = set(polygon.facilities().values_list('id', flat=True))

        self.assertIn(inside.id, result_ids)
        self.assertNotIn(in_hole.id, result_ids)
        self.assertNotIn(outside.id, result_ids)

    def test_facilities_matches_any_part_of_a_multipolygon(self):
        polygon = NamedPolygon.objects.create(
            name='Two disjoint squares',
            description='A multipolygon made of two separate squares.',
            geom=MultiPolygon(
                GEOSGeometry(SQUARE_WKT), GEOSGeometry(OTHER_SQUARE_WKT)
            ),
        )
        in_first = self._make_facility('US1000000FRST', 1, 1)
        in_second = self._make_facility('US1000000SCND', 25, 25)
        outside = self._make_facility('US1000000OUTS', 50, 50)

        result_ids = set(polygon.facilities().values_list('id', flat=True))

        self.assertIn(in_first.id, result_ids)
        self.assertIn(in_second.id, result_ids)
        self.assertNotIn(outside.id, result_ids)
