import json
import unittest.mock

from django.contrib.gis.geos import Point
from django.core.cache import cache
from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
    ZoneSet,
)
from api.models.facility.facility_index import FacilityIndex
from api.models.partner_field import PartnerField
from api.partner_fields.registry import system_partner_field_registry
from api.partner_fields.zone_set_provider import ZoneSetProvider
from api.serializers import FacilityIndexDetailsSerializer
from api.helpers.geojson_zones import parse_zone_features

OPEN_SEARCH_SERVICE = "api.views.v1.production_locations.OpenSearchService"

# Two touching bands over the Delhi area, plus one band that overlaps
# the first so the tie-break rule can be exercised.
WEST = [[[76.8, 28.4], [76.8, 28.9], [77.1, 28.9], [77.1, 28.4],
         [76.8, 28.4]]]
EAST = [[[77.1, 28.4], [77.1, 28.9], [77.4, 28.9], [77.4, 28.4],
         [77.1, 28.4]]]
OVERLAPPING_WEST = [[[76.9, 28.5], [76.9, 28.8], [77.0, 28.8],
                     [77.0, 28.5], [76.9, 28.5]]]


def feature(coordinates, properties):
    return {
        'type': 'Feature',
        'properties': properties,
        'geometry': {'type': 'Polygon', 'coordinates': coordinates},
    }


def zone_records(*features, value_property='bws_label'):
    raw = json.dumps({'type': 'FeatureCollection', 'features': features})
    return parse_zone_features(raw, value_property)


class ZoneSetProviderTest(APITestCase):
    """Tests for serving a zone set as a Spotlight partner field, on
    the provider itself, the registry, and both public surfaces."""

    def setUp(self):
        cache.clear()
        self.search_mock = unittest.mock.patch(OPEN_SEARCH_SERVICE).start()
        self.addCleanup(unittest.mock.patch.stopall)

        self.user = User.objects.create(email='aqueduct@example.com')
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='WRI Aqueduct',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.partner_field = PartnerField.objects.create(
            name='aqueduct_water_stress',
            type=PartnerField.STRING,
            label='Baseline water stress',
            source_by='<p>WRI Aqueduct 4.0</p>',
            base_url='https://www.wri.org/aqueduct',
            display_text='View on Aqueduct',
        )
        self.contributor.partner_fields.add(self.partner_field)

        self.zone_set = ZoneSet.objects.create(
            name='aqueduct_bws',
            description='Baseline water stress bands.',
            partner_field=self.partner_field,
            value_property='bws_label',
        )
        self.zone_set.replace_zones(zone_records(
            feature(WEST, {'bws_label': 'Extremely High'}),
            feature(EAST, {'bws_label': 'Low'}),
            feature(OVERLAPPING_WEST, {'bws_label': 'Medium'}),
        ))
        self.provider = ZoneSetProvider(self.zone_set)

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

    # --- provider -------------------------------------------------

    def test_field_name_is_the_linked_partner_field(self):
        self.assertEqual(
            self.provider._get_field_name(), 'aqueduct_water_stress'
        )

    def test_location_inside_a_zone_gets_its_label(self):
        facility = self._make_facility(77.3, 28.6)

        data = self.provider.fetch_data(facility)

        self.assertIsNotNone(data)
        self.assertEqual(data['value'], {'raw_value': 'Low'})
        self.assertEqual(data['field_name'], 'aqueduct_water_stress')
        self.assertEqual(data['contributor']['name'], 'WRI Aqueduct')
        self.assertTrue(data['should_display_association'])

    def test_location_outside_every_zone_gets_nothing(self):
        facility = self._make_facility(80.0, 20.0)
        self.assertIsNone(self.provider.fetch_data(facility))

    def test_location_without_coordinates_gets_nothing(self):
        facility = self._make_facility(77.3, 28.6)
        facility.location = None
        self.assertIsNone(self.provider._fetch_raw_data(facility))

    def test_overlap_resolves_to_the_first_feature_in_the_file(self):
        """The point sits in both the west band (feature 0) and the
        overlapping band (feature 2); the lower index wins."""
        facility = self._make_facility(76.95, 28.65)

        data = self.provider.fetch_data(facility)

        self.assertEqual(data['value'], {'raw_value': 'Extremely High'})

    def test_no_contributor_means_no_field(self):
        """Mirrors the other system providers: a field nobody holds is
        not shown."""
        self.contributor.partner_fields.clear()
        facility = self._make_facility(77.3, 28.6)
        self.assertIsNone(self.provider.fetch_data(facility))

    def test_linked_partner_field_cannot_be_deleted(self):
        with self.assertRaises(ProtectedError):
            self.partner_field.delete()

    # --- registry -------------------------------------------------

    def _registered_zone_set_fields(self):
        return [
            provider._get_field_name()
            for provider in system_partner_field_registry.providers
            if isinstance(provider, ZoneSetProvider)
        ]

    def test_registry_lists_active_linked_zone_sets(self):
        self.assertEqual(
            self._registered_zone_set_fields(), ['aqueduct_water_stress']
        )

    def test_registry_keeps_the_hard_wired_providers(self):
        names = [
            provider._get_field_name()
            for provider in system_partner_field_registry.providers
        ]
        self.assertIn('mit_living_wage', names)
        self.assertIn('wage_indicator', names)
        self.assertIn('india_labour_line_helpline', names)

    def test_inactive_zone_set_is_not_registered(self):
        self.zone_set.active = False
        self.zone_set.save()
        self.assertEqual(self._registered_zone_set_fields(), [])

    def test_unlinked_zone_set_is_not_registered(self):
        self.zone_set.partner_field = None
        self.zone_set.save()
        self.assertEqual(self._registered_zone_set_fields(), [])

    # --- details endpoint serializer (location page) --------------

    def test_details_serializer_shows_title_value_and_attribution(self):
        """AC #1 on the location page: the Spotlight entry carries the
        field's label, the zone's value, and the source attribution,
        with no front-end change needed."""
        facility = self._make_facility(77.3, 28.6)
        facility_index = FacilityIndex.objects.get(id=facility.id)

        data = FacilityIndexDetailsSerializer(facility_index).data

        entries = data['properties']['partner_fields']['aqueduct_water_stress']
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry['value'], {'raw_value': 'Low'})
        self.assertEqual(entry['label'], 'Baseline water stress')
        self.assertEqual(entry['source_by'], '<p>WRI Aqueduct 4.0</p>')
        self.assertEqual(entry['base_url'], 'https://www.wri.org/aqueduct')
        self.assertEqual(entry['display_text'], 'View on Aqueduct')
        self.assertEqual(entry['field_name'], 'aqueduct_water_stress')

    def test_details_serializer_omits_field_outside_zones(self):
        """AC #2: no empty or placeholder entry for a location that
        falls in no zone."""
        facility = self._make_facility(80.0, 20.0)
        facility_index = FacilityIndex.objects.get(id=facility.id)

        data = FacilityIndexDetailsSerializer(facility_index).data

        self.assertNotIn(
            'aqueduct_water_stress', data['properties']['partner_fields']
        )

    def test_newly_created_location_resolves_on_first_view(self):
        """AC #3: no backfill — a location created after the zones
        were uploaded gets its value straight away."""
        facility = self._make_facility(76.85, 28.45)
        facility_index = FacilityIndex.objects.get(id=facility.id)

        data = FacilityIndexDetailsSerializer(facility_index).data

        entries = data['properties']['partner_fields']['aqueduct_water_stress']
        self.assertEqual(entries[0]['value'], {'raw_value': 'Extremely High'})

    # --- v1 production-locations endpoint -------------------------

    def test_v1_endpoint_includes_the_zone_value(self):
        """AC #1 on the v1 endpoint: the value arrives as a plain
        string under the field's name."""
        facility = self._make_facility(77.3, 28.6)
        self.search_mock.return_value.search_index.return_value = {
            'count': 1,
            'data': [{'os_id': facility.id, 'name': 'Test Facility'}],
        }

        response = self.client.get(
            f'/api/v1/production-locations/{facility.id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['aqueduct_water_stress'], 'Low')

    def test_v1_endpoint_omits_field_outside_zones(self):
        facility = self._make_facility(80.0, 20.0)
        self.search_mock.return_value.search_index.return_value = {
            'count': 1,
            'data': [{'os_id': facility.id, 'name': 'Test Facility'}],
        }

        response = self.client.get(
            f'/api/v1/production-locations/{facility.id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('aqueduct_water_stress', response.data)
