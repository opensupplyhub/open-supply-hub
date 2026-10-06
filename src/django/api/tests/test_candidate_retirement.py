import json
from unittest.mock import patch

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, Point
from django.db.models.signals import post_delete
from django.test import override_settings
from django.urls import reverse
from opensearchpy.exceptions import NotFoundError
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.facility.facility_index import FacilityIndex
from api.models import (
    Contributor,
    ExtendedField,
    Facility,
    FacilityAlias,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.services.candidate_retirement import (
    NotACandidateError,
    RETIRED_DETAIL,
    get_tombstone,
    is_retired_detection,
    retire_candidate,
    tombstone_payload,
)
from api.signals import location_post_delete_handler_for_opensearch

CANDIDATE_POLYGON_WKT = 'POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))'
V1_OPEN_SEARCH_SERVICE = 'api.views.v1.production_locations.OpenSearchService'


class CandidateRetirementTest(APITestCase):
    """
    OSDEV-3246: retire a candidate OS ID as NOT_A_FACILITY.

    Fixture: one confirmed facility (list source) and one candidate built
    the way ingest (OSDEV-3244) builds it, a synthetic SINGLE Source ->
    FacilityListItem -> FacilityMatch graph with the candidate columns set.
    """

    def setUp(self):
        # Same as test_facility_delete: OpenSearch propagation is outside
        # Django unit testing. Reconnected in tearDown so the signal test
        # below and other modules see the normal wiring.
        post_delete.disconnect(
            location_post_delete_handler_for_opensearch, Facility
        )

        self.user = User.objects.create(email='one@example.com')
        self.user.set_password('example123')
        self.user.save()
        self.superuser = User.objects.create_superuser(
            email='super@example.com', password='example123'
        )
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='test contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        guard_settings = override_settings(
            EARTH_GENOME_CONTRIBUTOR_ID=self.contributor.id
        )
        guard_settings.enable()
        self.addCleanup(guard_settings.disable)
        self.list = FacilityList.objects.create(
            header='header', file_name='one', name='First List'
        )
        self.list_source = Source.objects.create(
            facility_list=self.list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        self.next_row_index = 0

        self.facility = self._create_facility(
            self.list_source, name='Confirmed'
        )
        self.facility_match = self._create_match(self.facility)

        self.candidate_source = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            create=True,
            contributor=self.contributor,
        )
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
        self.candidate_item = self.candidate.created_from
        self.candidate_match = self._create_match(self.candidate)
        self.tally = {'confirmed': 1, 'not_a_facility': 5}

    def tearDown(self):
        post_delete.connect(
            location_post_delete_handler_for_opensearch, Facility
        )

    # --- fixture helpers ----------------------------------------------

    def _create_list_item(self, item_source):
        self.next_row_index += 1
        return FacilityListItem.objects.create(
            name='Item',
            address='Address',
            country_code='US',
            sector=['Apparel'],
            row_index=self.next_row_index,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.MATCHED,
            source=item_source,
        )

    def _create_facility(self, item_source, **kwargs):
        item = self._create_list_item(item_source)
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
        return facility

    def _create_match(self, facility):
        return FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=facility,
            facility_list_item=facility.created_from,
            confidence=1.0,
            results={},
        )

    def _retire(self, **kwargs):
        return retire_candidate(
            self.candidate, self.tally, retired_by=self.user, **kwargs
        )

    # --- AC 3: tombstone holds the tally, graph and index row are gone -

    def test_retire_creates_tombstone_with_tally_and_detection_key(self):
        os_id = self.candidate.id

        tombstone = self._retire()

        self.assertEqual(os_id, tombstone.os_id)
        self.assertIsNone(tombstone.facility)
        self.assertEqual(FacilityAlias.NOT_A_FACILITY, tombstone.reason)
        self.assertEqual('earth_genome', tombstone.retired_source)
        self.assertEqual('eg-facility-0001', tombstone.retired_external_id)
        self.assertTrue(tombstone.is_tombstone)

        tally = tombstone.retirement_tally
        self.assertEqual(1, tally['confirmed'])
        self.assertEqual(5, tally['not_a_facility'])
        self.assertEqual(self.user.id, tally['retired_by'])
        self.assertIsNotNone(tally['retired_at'])

        stored = FacilityAlias.objects.get(os_id=os_id)
        self.assertEqual(tombstone.retirement_tally, stored.retirement_tally)

    def test_retire_hard_deletes_facility_graph_and_index_row(self):
        os_id = self.candidate.id
        item_id = self.candidate_item.id
        match_id = self.candidate_match.id
        source_id = self.candidate_source.id
        # OSDEV-3243 keeps candidates out of api_facilityindex at the
        # trigger, so force a row here: retirement must still clear one
        # that exists (e.g. rows indexed before that change shipped).
        FacilityIndex.objects.get_or_create(
            id=os_id,
            defaults={
                'name': self.candidate.name,
                'address': self.candidate.address,
                'country_code': self.candidate.country_code,
                'location': self.candidate.location,
                'contributors_count': 1,
                'contributors_id': [self.contributor.id],
                'contributors': [
                    {'id': self.contributor.id, 'name': self.contributor.name}
                ],
                'contrib_types': [self.contributor.contrib_type],
                'facility_addresses': [{'address': self.candidate.address}],
                'extended_fields': [],
                'lists': [],
                'approved_claim_ids': [],
                'facility_names': [],
                'sector': ['Agriculture'],
            },
        )
        self.assertTrue(FacilityIndex.objects.filter(id=os_id).exists())

        self._retire()

        self.assertFalse(
            Facility.including_candidates.filter(id=os_id).exists()
        )
        self.assertFalse(FacilityIndex.objects.filter(id=os_id).exists())
        self.assertFalse(FacilityMatch.objects.filter(id=match_id).exists())
        self.assertFalse(
            FacilityListItem.objects.filter(id=item_id).exists()
        )
        self.assertFalse(Source.objects.filter(id=source_id).exists())

        # The confirmed facility and its graph are untouched.
        self.assertTrue(Facility.objects.filter(id=self.facility.id).exists())
        self.assertTrue(
            FacilityMatch.objects.filter(id=self.facility_match.id).exists()
        )

    def test_retire_keeps_a_source_shared_with_other_items(self):
        other_item = self._create_list_item(self.candidate_source)

        self._retire()

        self.assertTrue(
            Source.objects.filter(id=self.candidate_source.id).exists()
        )
        self.assertTrue(
            FacilityListItem.objects.filter(id=other_item.id).exists()
        )

    def test_retire_removes_extended_fields_of_the_candidate_item(self):
        ExtendedField.objects.create(
            contributor=self.contributor,
            facility=self.candidate,
            facility_list_item=self.candidate_item,
            field_name=ExtendedField.NAME,
            value={'raw_value': 'x'},
        )

        self._retire()

        self.assertFalse(
            ExtendedField.objects.filter(
                facility_list_item_id=self.candidate_item.id
            ).exists()
        )

    def test_retire_stamps_retired_at_only_when_missing(self):
        tombstone = retire_candidate(
            self.candidate,
            {'confirmed': 0, 'not_a_facility': 3,
             'retired_at': '2026-10-01T00:00:00+00:00'},
        )

        tally = tombstone.retirement_tally
        self.assertEqual('2026-10-01T00:00:00+00:00', tally['retired_at'])
        self.assertIsNone(tally['retired_by'])

    def test_retire_does_not_mutate_the_callers_tally(self):
        self._retire()

        self.assertEqual({'confirmed': 1, 'not_a_facility': 5}, self.tally)

    # --- AC 4: non-candidates are refused, nothing changes -------------

    def test_retire_refuses_a_non_candidate_and_changes_nothing(self):
        with self.assertRaises(NotACandidateError) as ctx:
            retire_candidate(self.facility, self.tally, retired_by=self.user)

        self.assertIn(self.facility.id, str(ctx.exception))
        self.assertIn('not a candidate', str(ctx.exception))
        self.assertTrue(Facility.objects.filter(id=self.facility.id).exists())
        self.assertTrue(
            FacilityMatch.objects.filter(id=self.facility_match.id).exists()
        )
        self.assertTrue(
            FacilityListItem.objects.filter(
                id=self.facility.created_from.id, facility=self.facility
            ).exists()
        )
        self.assertFalse(FacilityAlias.objects.exists())

    # --- AC 2: ingest can detect a retired detection -------------------

    def test_is_retired_detection(self):
        self.assertFalse(
            is_retired_detection('earth_genome', 'eg-facility-0001')
        )

        self._retire()

        self.assertTrue(
            is_retired_detection('earth_genome', 'eg-facility-0001')
        )
        self.assertFalse(
            is_retired_detection('earth_genome', 'eg-facility-0002')
        )
        self.assertFalse(
            is_retired_detection('other_source', 'eg-facility-0001')
        )
        self.assertFalse(is_retired_detection('', None))

    def test_is_retired_detection_ignores_redirect_aliases(self):
        FacilityAlias.objects.create(
            os_id='US1234567ABCDEF',
            facility=self.facility,
            reason=FacilityAlias.MERGE,
            retired_source='earth_genome',
            retired_external_id='eg-facility-0001',
        )

        self.assertFalse(
            is_retired_detection('earth_genome', 'eg-facility-0001')
        )

    # --- AC 1: retired OS ID answers 410 Gone --------------------------

    def test_retrieve_retired_os_id_returns_410(self):
        os_id = self.candidate.id
        tombstone = self._retire()

        response = self.client.get(f'/api/facilities/{os_id}/')

        self.assertEqual(status.HTTP_410_GONE, response.status_code)
        body = json.loads(response.content)
        self.assertEqual(RETIRED_DETAIL, body['detail'])
        self.assertEqual(os_id, body['os_id'])
        self.assertEqual(
            tombstone.retirement_tally['retired_at'], body['retired_at']
        )

    def test_retrieve_unknown_os_id_still_404s(self):
        response = self.client.get('/api/facilities/US1234567ABCDEF/')

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_retrieve_redirect_alias_still_redirects(self):
        """A tombstone alongside a redirect alias leaves redirects intact."""
        self._retire()
        FacilityAlias.objects.create(
            os_id='US1234567ABCDEF',
            facility=self.facility,
            reason=FacilityAlias.MERGE,
        )

        response = self.client.get('/api/facilities/US1234567ABCDEF/')

        self.assertEqual(status.HTTP_302_FOUND, response.status_code)
        self.assertEqual(
            f'/api/facilities/{self.facility.id}/', response.url
        )

    def test_search_by_retired_os_id_matches_nothing(self):
        os_id = self.candidate.id
        self._retire()
        base_url = reverse('facility-list')

        for url in (f'{base_url}?q={os_id}', f'{base_url}?id={os_id}'):
            response = self.client.get(url)

            self.assertEqual(status.HTTP_200_OK, response.status_code, url)
            self.assertEqual(
                0, len(json.loads(response.content)['features']), url
            )

    def test_search_by_redirect_alias_still_resolves(self):
        self._retire()
        FacilityAlias.objects.create(
            os_id='US1234567ABCDEF',
            facility=self.facility,
            reason=FacilityAlias.MERGE,
        )

        response = self.client.get(
            f"{reverse('facility-list')}?q=US1234567ABCDEF"
        )

        features = json.loads(response.content)['features']
        self.assertEqual(1, len(features))
        self.assertEqual(self.facility.id, features[0]['id'])

    def test_v1_production_location_retired_os_id_returns_410(self):
        os_id = self.candidate.id
        self._retire()
        with patch(V1_OPEN_SEARCH_SERVICE) as search_mock:
            search_mock.return_value.search_index.return_value = {
                'count': 0, 'data': []
            }

            response = self.client.get(
                f'/api/v1/production-locations/{os_id}/'
            )

        self.assertEqual(status.HTTP_410_GONE, response.status_code)
        self.assertEqual(RETIRED_DETAIL, response.data['detail'])
        self.assertEqual(os_id, response.data['os_id'])

    def test_v1_production_location_unknown_os_id_still_404s(self):
        with patch(V1_OPEN_SEARCH_SERVICE) as search_mock:
            search_mock.return_value.search_index.return_value = {
                'count': 0, 'data': []
            }

            response = self.client.get(
                '/api/v1/production-locations/US1234567ABCDEF/'
            )

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    # --- Tombstone helpers and rendering -------------------------------

    def test_get_tombstone_and_payload(self):
        os_id = self.candidate.id
        self.assertIsNone(get_tombstone(os_id))

        tombstone = self._retire()

        self.assertEqual(tombstone, get_tombstone(os_id))
        self.assertEqual(
            {
                'detail': RETIRED_DETAIL,
                'os_id': os_id,
                'retired_at': tombstone.retirement_tally['retired_at'],
            },
            tombstone_payload(tombstone),
        )

    def test_tombstone_str_does_not_dereference_facility(self):
        tombstone = self._retire()

        self.assertEqual(
            f'{tombstone.os_id} -> retired (NOT_A_FACILITY)', str(tombstone)
        )

    def test_admin_renders_tombstone_with_null_facility(self):
        tombstone = self._retire()
        self.client.login(email='super@example.com', password='example123')
        # The test runner has no collected static manifest; the admin
        # templates only need a storage that can build a URL.
        storages = {
            **settings.STORAGES,
            'staticfiles': {
                'BACKEND':
                'django.contrib.staticfiles.storage.StaticFilesStorage',
            },
        }

        for url in (
            '/admin/api/facilityalias/',
            f'/admin/api/facilityalias/{tombstone.os_id}/change/',
            f'/admin/api/facilityalias/{tombstone.os_id}/history/',
        ):
            with override_settings(STORAGES=storages):
                response = self.client.get(url)

            self.assertEqual(status.HTTP_200_OK, response.status_code, url)
            self.assertContains(response, tombstone.os_id)

    # --- OpenSearch post_delete signal -----------------------------------

    def test_retire_survives_missing_opensearch_document(self):
        """The signal must not abort retirement of a never-indexed doc."""
        post_delete.connect(
            location_post_delete_handler_for_opensearch, Facility
        )
        os_id = self.candidate.id

        with patch('api.signals.OpenSearchServiceConnection') as conn, \
                patch('api.signals.signal_error_notifier') as notifier:
            conn.return_value.client.delete.side_effect = NotFoundError(
                404, 'not_found', {}
            )

            tombstone = self._retire()

            conn.return_value.client.delete.assert_called_once()
            notifier.assert_not_called()

        self.assertEqual(os_id, tombstone.os_id)
        self.assertFalse(
            Facility.including_candidates.filter(id=os_id).exists()
        )

    def test_missing_opensearch_document_still_reported_for_facilities(self):
        post_delete.connect(
            location_post_delete_handler_for_opensearch, Facility
        )

        with patch('api.signals.OpenSearchServiceConnection') as conn, \
                patch('api.signals.signal_error_notifier') as notifier:
            conn.return_value.client.delete.side_effect = NotFoundError(
                404, 'not_found', {}
            )

            location_post_delete_handler_for_opensearch(self.facility)

            notifier.assert_called_once()
