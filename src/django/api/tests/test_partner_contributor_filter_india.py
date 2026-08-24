from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Point
from django.test import TestCase

from api.models import Contributor, Polygon, User
from api.models.partner_field import PartnerField
from api.models.facility.facility_index import FacilityIndex
from api.models.facility.partner_contributor_filter import (
    apply_partner_fields_or_filter,
)
from api.partner_fields.india_labour_line_provider import (
    IndiaLabourLineProvider,
)

BOUNDARY_WKT = (
    'POLYGON((76.8 28.4, 76.8 28.9, 77.4 28.9, 77.4 28.4, 76.8 28.4))'
)


class IndiaLabourLinePartnerFilterTest(TestCase):
    """Tests for the polygon-driven branch of the partner search filter."""

    def setUp(self):
        """Create the boundary polygon and in/out facility rows."""
        self.user = User.objects.create(email='test@example.com')
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='Test Contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.polygon = Polygon.objects.create(
            name='helpline_coverage_for_tests',
            description='Helpline coverage boundary for tests.',
            geom=MultiPolygon(GEOSGeometry(BOUNDARY_WKT)),
        )
        self.partner_field, _ = PartnerField.objects \
            .get_all_including_inactive() \
            .get_or_create(
                name=IndiaLabourLineProvider.FIELD_NAME,
                defaults={'type': PartnerField.OBJECT,
                          'system_field': True, 'active': True},
            )
        self.partner_field.polygon = self.polygon
        self.partner_field.save()
        self.inside = self._make_facility('IN2026000INSD', 77.2, 28.6)
        self.outside = self._make_facility('IN2026000OUTS', 75.0, 20.0)

    def _make_facility(self, facility_id, lon, lat, sector=None):
        """Create a FacilityIndex row in India at the given lon/lat."""
        return FacilityIndex.objects.create(
            id=facility_id,
            name='Test Facility',
            address='123 Main St',
            country_code='IN',
            sector=sector or ['Apparel'],
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

    def _filtered_ids(self):
        """Run the partner-fields filter for the helpline field."""
        queryset = apply_partner_fields_or_filter(
            FacilityIndex.objects.all(),
            [IndiaLabourLineProvider.FIELD_NAME],
            [self.contributor.id],
        )
        return set(queryset.values_list('id', flat=True))

    def test_filter_keeps_only_in_boundary_facilities(self):
        """The search filter matches in-polygon locations only."""
        ids = self._filtered_ids()
        self.assertIn(self.inside.id, ids)
        self.assertNotIn(self.outside.id, ids)

    def test_filter_excludes_uncovered_sectors(self):
        """In-boundary locations outside the covered sectors do not
        match the search filter."""
        electronics = self._make_facility(
            'IN2026000ELEC', 77.1, 28.7, sector=['Electronics']
        )
        self.assertNotIn(electronics.id, self._filtered_ids())

    def test_filter_matches_nothing_when_no_polygon_is_linked(self):
        """An unlinked coverage polygon means zero matches, loudly —
        never an unfiltered everything-matches result."""
        self.partner_field.polygon = None
        self.partner_field.save()

        logger_name = 'api.partner_fields.india_labour_line_provider'
        with self.assertLogs(logger_name, level='WARNING'):
            ids = self._filtered_ids()

        self.assertEqual(ids, set())
