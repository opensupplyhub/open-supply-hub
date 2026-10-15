"""
OSDEV-3627: the ``earth_genome_candidates`` waffle switch turns the
candidate pilot off per environment. With the switch inactive every
candidate-facing surface answers as it did before the pilot; the
exclusions and the contributor guard are untouched.
"""
import os
import json
import tempfile
import unittest.mock

from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.models.facility.facility_candidate_retirement_request import (
    FacilityCandidateRetirementRequest,
)
from api.services.candidate_retirement import retire_candidate
from api.services.candidate_switch import SWITCH_NAME, candidates_enabled
from api.signals import location_post_delete_handler_for_opensearch
from django.contrib.gis.geos import GEOSGeometry, Point
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db.models.signals import post_delete
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from waffle.models import Switch
from waffle.testutils import override_switch

OPEN_SEARCH_SERVICE = (
    'api.views.v1.production_locations.OpenSearchService'
)
CANDIDATE_POLYGON_WKT = (
    'POLYGON((-0.01 -0.01, -0.01 0.01, 0.01 0.01, 0.01 -0.01, -0.01 -0.01))'
)


class CandidatePilotSwitchTest(APITestCase):
    def setUp(self):
        post_delete.disconnect(
            location_post_delete_handler_for_opensearch, Facility
        )
        self.addCleanup(
            post_delete.connect,
            location_post_delete_handler_for_opensearch,
            Facility,
        )
        search_mock = unittest.mock.patch(OPEN_SEARCH_SERVICE).start()
        self.addCleanup(unittest.mock.patch.stopall)
        search_mock.return_value.search_index.return_value = {}

        self.user = User.objects.create(email='one@example.com')
        self.superuser = User.objects.create_superuser(
            email='super@example.com', password='example123'
        )
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='Earth Genome',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        guard_settings = override_settings(
            EARTH_GENOME_CONTRIBUTOR_ID=self.contributor.id
        )
        guard_settings.enable()
        self.addCleanup(guard_settings.disable)

        facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='First List'
        )
        self.list_source = Source.objects.create(
            facility_list=facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        self.candidate_source = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            create=True,
            contributor=self.contributor,
        )
        self.next_row_index = 0
        self.candidate = self._create_facility(
            self.candidate_source,
            name='',
            address='',
            is_candidate=True,
            polygon=GEOSGeometry(CANDIDATE_POLYGON_WKT, srid=4326),
            confidence=0.87,
            external_id='eg-facility-0001',
            source='earth_genome',
        )

    # --- fixtures ---------------------------------------------------------

    def _create_facility(self, item_source, **kwargs):
        self.next_row_index += 1
        item = FacilityListItem.objects.create(
            name='Item',
            address='Address',
            country_code='US',
            sector=['Apparel'],
            row_index=self.next_row_index,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.MATCHED,
            source=item_source,
        )
        defaults = {
            'name': 'Name',
            'address': 'Address',
            'country_code': 'US',
            'location': Point(0, 0),
            'created_from': item,
        }
        defaults.update(kwargs)
        facility = Facility.including_candidates.create(**defaults)
        item.facility = facility
        item.save()
        FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=facility,
            facility_list_item=item,
            confidence=1.0,
            results={},
        )
        return facility

    def _v1_url(self, os_id):
        return f'/api/v1/production-locations/{os_id}/'

    def _votes_url(self, os_id):
        return f'/api/v1/production-locations/{os_id}/candidate-votes/'

    # --- the switch itself ---------------------------------------------

    def test_migration_created_the_switch_inactive(self):
        switch = Switch.objects.get(name=SWITCH_NAME)
        self.assertFalse(switch.active)
        self.assertFalse(candidates_enabled())

    def test_feature_flags_endpoint_exposes_the_switch(self):
        response = self.client.get('/api-feature-flags/')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIs(False, response.data[SWITCH_NAME])
        with override_switch(SWITCH_NAME, active=True):
            response = self.client.get('/api-feature-flags/')
        self.assertIs(True, response.data[SWITCH_NAME])

    # --- switch off: every candidate surface is not found ----------------

    @override_switch(SWITCH_NAME, active=False)
    def test_v1_candidate_detail_is_404_when_off(self):
        response = self.client.get(self._v1_url(self.candidate.id))
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertNotIn('is_candidate', json.dumps(response.data))

    @override_switch(SWITCH_NAME, active=False)
    def test_legacy_candidate_detail_is_404_when_off(self):
        response = self.client.get(f'/api/facilities/{self.candidate.id}/')
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    @override_switch(SWITCH_NAME, active=False)
    def test_retired_os_id_is_still_410_when_off(self):
        os_id = self.candidate.id
        retire_candidate(self.candidate, {'confirmed': 0, 'not_a_facility': 3})

        self.assertEqual(
            status.HTTP_410_GONE,
            self.client.get(self._v1_url(os_id)).status_code,
        )
        self.assertEqual(
            status.HTTP_410_GONE,
            self.client.get(f'/api/facilities/{os_id}/').status_code,
        )

    @override_switch(SWITCH_NAME, active=False)
    def test_votes_are_404_and_write_nothing_when_off(self):
        response = self.client.get(self._votes_url(self.candidate.id))
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self._votes_url(self.candidate.id),
            {'vote': 'confirmed'},
            format='json',
        )
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(
            0, self.candidate.candidate_votes.count()
        )

    @override_switch(SWITCH_NAME, active=False)
    def test_bbox_is_404_when_off(self):
        response = self.client.get(
            '/api/v1/production-locations/candidates/',
            {'bbox': '-1,-1,1,1'},
        )
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    @override_switch(SWITCH_NAME, active=False)
    def test_retirement_requests_are_404_for_moderators_when_off(self):
        request = FacilityCandidateRetirementRequest.objects.create(
            facility=self.candidate,
            tally={'confirmed': 0, 'not_a_facility': 3},
        )
        self.client.force_authenticate(user=self.superuser)

        response = self.client.get('/api/v1/candidate-retirement-requests/')
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

        response = self.client.post(
            f'/api/v1/candidate-retirement-requests/{request.id}/approve/'
        )
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertTrue(
            Facility.including_candidates.filter(
                pk=self.candidate.id
            ).exists()
        )

    @override_switch(SWITCH_NAME, active=False)
    def test_ingest_refuses_to_run_when_off(self):
        handle, path = tempfile.mkstemp(suffix='.geojson')
        os.close(handle)
        self.addCleanup(os.unlink, path)
        with open(path, 'w') as out:
            json.dump({'type': 'FeatureCollection', 'features': []}, out)

        with self.assertRaises(CommandError) as ctx:
            call_command('ingest_satellite_detections', '--file', path)

        self.assertIn(SWITCH_NAME, str(ctx.exception))
        self.assertIn('switched off', str(ctx.exception))

    # --- switch on: the pilot surfaces answer -------------------------------

    @override_switch(SWITCH_NAME, active=True)
    def test_candidate_surfaces_answer_when_on(self):
        response = self.client.get(self._v1_url(self.candidate.id))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(response.data['is_candidate'])

        response = self.client.get(f'/api/facilities/{self.candidate.id}/')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        response = self.client.get(self._votes_url(self.candidate.id))
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        response = self.client.get(
            '/api/v1/production-locations/candidates/',
            {'bbox': '-1,-1,1,1'},
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data['features']))

        self.client.force_authenticate(user=self.superuser)
        response = self.client.get('/api/v1/candidate-retirement-requests/')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
