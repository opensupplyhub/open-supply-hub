from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Point
from django.test import TestCase

from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Polygon,
    Source,
    User,
)
from api.models.partner_field import PartnerField
from api.partner_fields.india_labour_line_provider import (
    INDIA_LABOUR_LINE_SECTORS,
    IndiaLabourLineProvider,
)

# A rough box over the Delhi area, used as the helpline boundary.
BOUNDARY_WKT = (
    'POLYGON((76.8 28.4, 76.8 28.9, 77.4 28.9, 77.4 28.4, 76.8 28.4))'
)


class IndiaLabourLineProviderTest(TestCase):
    """Tests for the India Labour Line system partner field provider."""

    def setUp(self):
        """Create the partner field, boundary polygon, and a facility."""
        self.user = User.objects.create(email='test@example.com')
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='India Labour Line',
            contrib_type=Contributor.CONTRIB_TYPE_CHOICES[0][0],
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
                defaults={
                    'type': PartnerField.OBJECT,
                    'label': 'India Labour Line Helpline',
                    'system_field': True,
                    'active': True,
                },
            )
        # The number lives in display_text (admin-editable even on
        # protected system fields); coverage is a database link.
        self.partner_field.display_text = '1-800-833-9020'
        self.partner_field.polygon = self.polygon
        self.partner_field.save()
        self.partner_field.contributor_set.clear()
        self.contributor.partner_fields.add(self.partner_field)

        self.provider = IndiaLabourLineProvider()

    def tearDown(self):
        """Detach the contributor but keep the system partner field."""
        self.partner_field.contributor_set.clear()

    def _make_facility(self, lon, lat, country_code='IN',
                       sector=None):
        """Create a Facility (with its list/source chain) at lon/lat."""
        location = Point(lon, lat, srid=4326)
        facility_list = FacilityList.objects.create(
            header='header', file_name='test', name='Test List'
        )
        source = Source.objects.create(
            facility_list=facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        list_item = FacilityListItem.objects.create(
            name='Test Facility',
            address='123 Test St',
            country_code=country_code,
            sector=sector or ['Apparel'],
            row_index=0,
            geocoded_point=location,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )
        facility = Facility.objects.create(
            name='Test Facility',
            address='123 Test St',
            country_code=country_code,
            location=location,
            created_from=list_item,
        )
        FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=facility,
            results='',
            facility_list_item=list_item,
        )
        list_item.facility = facility
        list_item.save()
        return facility

    def test_get_field_name(self):
        """The provider names the production partner field exactly."""
        self.assertEqual(
            self.provider._get_field_name(), 'india_labour_line_helpline'
        )

    def test_in_boundary_location_gets_the_helpline(self):
        """A location inside the boundary gets the schema's number."""
        facility = self._make_facility(77.2, 28.6)

        data = self.provider.fetch_data(facility)

        self.assertIsNotNone(data)
        self.assertEqual(
            data['value']['raw_values'], {'phone_number': '1-800-833-9020'}
        )
        self.assertEqual(data['field_name'], 'india_labour_line_helpline')
        self.assertEqual(data['contributor']['name'], 'India Labour Line')

    def test_outside_boundary_location_gets_nothing(self):
        """An Indian location outside the boundary gets no field."""
        facility = self._make_facility(75.0, 20.0)
        self.assertIsNone(self.provider._fetch_raw_data(facility))

    def test_non_india_location_gets_nothing(self):
        """The country check skips non-Indian locations cheaply."""
        facility = self._make_facility(77.2, 28.6, country_code='US')
        self.assertIsNone(self.provider._fetch_raw_data(facility))

    def test_unlinked_polygon_warns_and_returns_nothing(self):
        """With no coverage polygon linked, the field stays dormant
        and says so loudly in the logs."""
        facility = self._make_facility(77.2, 28.6)
        self.partner_field.polygon = None
        self.partner_field.save()

        logger_name = 'api.partner_fields.india_labour_line_provider'
        with self.assertLogs(logger_name, level='WARNING') as logs:
            result = self.provider._fetch_raw_data(facility)

        self.assertIsNone(result)
        self.assertIn('no coverage polygon', '\n'.join(logs.output))

    def test_linked_polygon_cannot_be_deleted(self):
        """The database blocks deleting a polygon a field points at."""
        from django.db.models import ProtectedError
        with self.assertRaises(ProtectedError):
            self.polygon.delete()

    def test_phone_number_read_from_display_text(self):
        """The number comes from display_text, the admin-editable
        column, so staff can change it with no deploy."""
        self.partner_field.display_text = '1-800-000-0000'
        self.partner_field.save()
        facility = self._make_facility(77.2, 28.6)

        raw = self.provider._fetch_raw_data(facility)

        self.assertEqual(raw['phone_number'], '1-800-000-0000')

    def test_blank_display_text_warns_and_returns_nothing(self):
        """A blank helpline number disables the field loudly."""
        self.partner_field.display_text = ''
        self.partner_field.save()
        facility = self._make_facility(77.2, 28.6)

        logger_name = 'api.partner_fields.india_labour_line_provider'
        with self.assertLogs(logger_name, level='WARNING'):
            result = self.provider._fetch_raw_data(facility)

        self.assertIsNone(result)

    def test_uncovered_sector_gets_nothing(self):
        """An in-boundary location in a non-covered sector is skipped."""
        facility = self._make_facility(77.2, 28.6, sector=['Electronics'])
        self.assertIsNone(self.provider._fetch_raw_data(facility))

    def test_every_covered_sector_qualifies(self):
        """Each covered sector, on its own, is enough to qualify."""
        for sector in INDIA_LABOUR_LINE_SECTORS:
            facility = self._make_facility(77.2, 28.6, sector=[sector])
            self.assertIsNotNone(
                self.provider._fetch_raw_data(facility), sector
            )
