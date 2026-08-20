import json

from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Point
from django.test import TestCase
from waffle.testutils import override_switch

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
    INDIA_LABOUR_LINE_POLYGON_NAMES,
    INDIA_LABOUR_LINE_SWITCH,
    IndiaLabourLineProvider,
)

# A rough box over the Delhi area, used as the helpline boundary.
BOUNDARY_WKT = (
    'POLYGON((76.8 28.4, 76.8 28.9, 77.4 28.9, 77.4 28.4, 76.8 28.4))'
)

# The production JSON schema shape: the helpline number lives in the
# `default` of the phone_number property.
HELPLINE_SCHEMA = {
    'type': 'object',
    'title': 'India Labour Line Helpline',
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
    'properties': {
        'phone_number': {
            'type': 'string',
            'title': 'Phone Number',
            'default': '1-800-833-9020',
        }
    },
}


@override_switch(INDIA_LABOUR_LINE_SWITCH, active=True)
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
        self.partner_field.json_schema = HELPLINE_SCHEMA
        self.partner_field.save()
        self.partner_field.contributor_set.clear()
        self.contributor.partner_fields.add(self.partner_field)

        self.polygon = Polygon.objects.create(
            name=INDIA_LABOUR_LINE_POLYGON_NAMES[0],
            description='Helpline coverage boundary for tests.',
            geom=MultiPolygon(GEOSGeometry(BOUNDARY_WKT)),
        )

        self.provider = IndiaLabourLineProvider()

    def tearDown(self):
        """Detach the contributor but keep the system partner field."""
        self.partner_field.contributor_set.clear()

    def _make_facility(self, lon, lat, country_code='IN'):
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
            sector=['Apparel'],
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

    @override_switch(INDIA_LABOUR_LINE_SWITCH, active=False)
    def test_switch_off_disables_the_provider(self):
        """With the waffle switch off, no location gets the field."""
        facility = self._make_facility(77.2, 28.6)
        self.assertIsNone(self.provider._fetch_raw_data(facility))

    def test_missing_polygon_warns_and_returns_nothing(self):
        """A missing boundary polygon logs loudly instead of failing."""
        facility = self._make_facility(77.2, 28.6)
        self.polygon.delete()

        logger_name = 'api.partner_fields.india_labour_line_provider'
        with self.assertLogs(logger_name, level='WARNING') as logs:
            result = self.provider._fetch_raw_data(facility)

        self.assertIsNone(result)
        self.assertIn(
            INDIA_LABOUR_LINE_POLYGON_NAMES[0], '\n'.join(logs.output)
        )

    def test_phone_number_read_from_string_schema(self):
        """A schema stored as a JSON string is parsed the same way."""
        self.partner_field.json_schema = json.dumps(HELPLINE_SCHEMA)
        self.partner_field.save()
        facility = self._make_facility(77.2, 28.6)

        raw = self.provider._fetch_raw_data(facility)

        self.assertEqual(raw['phone_number'], '1-800-833-9020')

    def test_missing_phone_default_warns_and_returns_nothing(self):
        """A schema without a phone default disables the field loudly."""
        schema = {'type': 'object', 'properties': {}}
        self.partner_field.json_schema = schema
        self.partner_field.save()
        facility = self._make_facility(77.2, 28.6)

        logger_name = 'api.partner_fields.india_labour_line_provider'
        with self.assertLogs(logger_name, level='WARNING'):
            result = self.provider._fetch_raw_data(facility)

        self.assertIsNone(result)
