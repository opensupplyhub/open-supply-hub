"""
OSDEV-3250: end-to-end lifecycle of Earth Genome candidate facilities.

One module walks a detections file through every Phase 1 PR in the
order a staging run would: ingest (OSDEV-3244) -> hidden from the
confirmed surfaces (OSDEV-3380 / 3378 / 3243) -> labeled detail and bbox
payloads (OSDEV-3249) -> votes and derived state (OSDEV-3245, D6) ->
moderator-gated retirement with tombstone (OSDEV-3246, D3 / D5) ->
re-ingest suppression (D5). A second test covers the
``CANDIDATE_AUTO_RETIRE`` edge, and a regression test proves that
candidates sitting in the database do not change the legacy
``POST /api/facilities/`` flow for a confirmed facility.

The detections file is the prototype JSON list format
(``nc_candidates.json``) because it is the only input shape that can
carry a point-only detection (``polygon: null`` with a centroid). The
Earth Genome GeoJSON export has polygons or ``null`` only; a Feature
with a ``Point`` geometry is a parse error there by design, which
``IngestSatelliteDetectionsTest`` already pins.

Thresholds are pinned to the pilot defaults so the derived states below
do not drift with a local ``.env``.
"""
import json
import os
import tempfile
from io import StringIO
from unittest.mock import Mock, patch

from django.contrib import auth
from django.contrib.gis.geos import Point
from django.core.cache import caches
from django.core.management import call_command
from django.test import override_settings
from django.urls import reverse
from opensearchpy.exceptions import NotFoundError
from rest_framework import status
from rest_framework.test import APITestCase

from api.constants import FeatureGroups
from api.models import (
    Contributor,
    Facility,
    FacilityAlias,
    FacilityCandidateRetirementRequest,
    FacilityCandidateVote,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.models.facility.facility_index import FacilityIndex
from api.services.candidate_retirement import RETIRED_DETAIL
from api.services.candidate_validation import (
    CONFIRMED,
    DISPUTED,
    RETIRED,
    RETIREMENT_PENDING,
    UNVERIFIED,
)
from api.tests.test_data import geocoding_data

V1_OPEN_SEARCH_SERVICE = 'api.views.v1.production_locations.OpenSearchService'
SIGNALS_OPEN_SEARCH_CONNECTION = 'api.signals.OpenSearchServiceConnection'
SIGNALS_ERROR_NOTIFIER = 'api.signals.signal_error_notifier'
KAFKA_PRODUCER = (
    'api.facility_actions.processing_facility_api'
    '.produce_message_match_process'
)
GEOCODER = 'api.geocoding.requests.get'
ASYNCIO_IN_PROCESSING = 'api.facility_actions.processing_facility_api.asyncio'

SOURCE = 'earth_genome'
# A detection site in North Carolina; the other detections step east.
SITE_LNG = -78.6400
SITE_LAT = 35.7800
# Covers all three detections (and nothing else) within the 2-degree cap.
SITE_BBOX = '-78.7,35.7,-78.1,35.9'

YES = FacilityCandidateVote.Vote.CONFIRMED.value
NO = FacilityCandidateVote.Vote.NOT_A_FACILITY.value

PILOT_THRESHOLDS = dict(
    CANDIDATE_VOTE_THRESHOLD=3,
    CANDIDATE_CONFIRM_MARGIN=0.6,
    CANDIDATE_RETIRE_MARGIN=0.75,
    CANDIDATE_AUTO_RETIRE=False,
)


def _square(lng, lat, half=0.001):
    return {
        'type': 'Polygon',
        'coordinates': [[
            [lng - half, lat - half],
            [lng - half, lat + half],
            [lng + half, lat + half],
            [lng + half, lat - half],
            [lng - half, lat - half],
        ]],
    }


def _record(eg_id, lng, lat, confidence, polygon=True, centroid=True):
    return {
        'eg_id': eg_id,
        'polygon': _square(lng, lat) if polygon else None,
        'centroid_lat': lat if centroid else None,
        'centroid_lng': lng if centroid else None,
        'point_only': not polygon,
        'probable_facility_type': 'poultry',
        'confidence_score': confidence,
        'eg_model_version': 'MLP64-16',
    }


# Two valid polygons, one point-only detection, one with no geometry at
# all (skipped by ingest).
DETECTIONS = [
    _record('EG-A', SITE_LNG, SITE_LAT, 0.95),
    _record('EG-B', SITE_LNG + 0.2, SITE_LAT, 0.80),
    _record('EG-C', SITE_LNG + 0.4, SITE_LAT, 0.70, polygon=False),
    _record('EG-D', SITE_LNG + 0.6, SITE_LAT, 0.60,
            polygon=False, centroid=False),
]


@override_settings(**PILOT_THRESHOLDS)
class CandidateLifecycleE2ETest(APITestCase):
    fixtures = ['sectors']

    def setUp(self):
        # v1 detail/list go to OpenSearch first; nothing is indexed in a
        # unit test, so every lookup misses and falls through to the
        # candidate / tombstone / 404 branches under test.
        search_mock = patch(V1_OPEN_SEARCH_SERVICE).start()
        search_mock.return_value.search_index.return_value = {
            'count': 0, 'data': []
        }
        # The post_delete signal stays connected: a retired candidate has
        # no OpenSearch document, and the handler must swallow the 404
        # without reporting an inconsistency.
        self.opensearch_connection = patch(
            SIGNALS_OPEN_SEARCH_CONNECTION
        ).start()
        self.opensearch_connection.return_value.client.delete.side_effect = (
            NotFoundError(404, 'not_found', {})
        )
        self.error_notifier = patch(SIGNALS_ERROR_NOTIFIER).start()
        self.addCleanup(patch.stopall)
        # The anonymous burst throttle (100/minute, keyed on the test
        # client's IP) lives in the shared 'api_throttling' cache, which
        # outlives a test and a module. These tests make many anonymous
        # reads in a few seconds, so the budget is reset at the start of
        # each step and left clean for the modules that run after.
        self._reset_throttles()
        self.addCleanup(self._reset_throttles)

        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.detections_path = os.path.join(
            self.tmpdir.name, 'detections.json'
        )
        with open(self.detections_path, 'w') as handle:
            json.dump(DETECTIONS, handle)

        self.eg_user = User.objects.create(email='earth-genome@example.com')
        self.eg_contributor = Contributor.objects.create(
            admin=self.eg_user,
            name='Earth Genome',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        guard_settings = override_settings(
            EARTH_GENOME_CONTRIBUTOR_ID=self.eg_contributor.id
        )
        guard_settings.enable()
        self.addCleanup(guard_settings.disable)

        self.voters = [
            User.objects.create(email=f'voter{i}@example.com')
            for i in range(5)
        ]
        self.superuser = User.objects.create_superuser(
            email='super@example.com', password='example123'
        )

        # One ordinary contributor with one confirmed facility, so the
        # confirmed surfaces have something to show while candidates hide.
        self.submitter_password = 'example123'
        self.submitter = User.objects.create(email='submitter@example.com')
        self.submitter.set_password(self.submitter_password)
        self.submitter.save()
        self.contributor = Contributor.objects.create(
            admin=self.submitter,
            name='Ordinary contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='First List'
        )
        list_source = Source.objects.create(
            facility_list=facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        item = FacilityListItem.objects.create(
            name='Confirmed Plant',
            address='1 Main Street',
            country_code='US',
            sector=['Apparel'],
            row_index=1,
            geocoded_point=Point(-80.0, 36.0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=list_source,
        )
        self.confirmed = Facility.objects.create(
            name='Confirmed Plant',
            address='1 Main Street',
            country_code='US',
            location=Point(-80.0, 36.0),
            created_from=item,
        )
        FacilityMatch.objects.create(
            facility=self.confirmed,
            facility_list_item=item,
            status=FacilityMatch.CONFIRMED,
            confidence=1.0,
            results={},
        )
        item.facility = self.confirmed
        item.save()

    # --- helpers --------------------------------------------------------

    @staticmethod
    def _reset_throttles():
        caches['api_throttling'].clear()

    def _ingest(self):
        out, err = StringIO(), StringIO()
        call_command(
            'ingest_satellite_detections',
            '--file', self.detections_path,
            stdout=out, stderr=err,
        )
        return out.getvalue()

    @staticmethod
    def _candidates():
        return Facility.including_candidates.filter(source=SOURCE)

    def _candidate(self, external_id):
        return self._candidates().get(external_id=external_id)

    def _detection_exists(self, external_id):
        return self._candidates().filter(external_id=external_id).exists()

    @staticmethod
    def _exists(os_id):
        return Facility.including_candidates.filter(id=os_id).exists()

    @staticmethod
    def _votes_url(os_id):
        return f'/api/v1/production-locations/{os_id}/candidate-votes/'

    def _vote(self, user, os_id, vote):
        self.client.force_authenticate(user=user)
        try:
            return self.client.post(
                self._votes_url(os_id), {'vote': vote}, format='json'
            )
        finally:
            self.client.force_authenticate(user=None)

    def _legacy_detail(self, os_id):
        return self.client.get(f'/api/facilities/{os_id}/')

    def _v1_detail(self, os_id):
        return self.client.get(f'/api/v1/production-locations/{os_id}/')

    def _bbox_features(self):
        response = self.client.get(
            f'/api/v1/production-locations/candidates/?bbox={SITE_BBOX}'
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        return {f['id']: f for f in response.data['features']}

    def _list_ids(self, **params):
        response = self.client.get(reverse('facility-list'), params)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        return sorted(f['id'] for f in response.data['features'])

    def _count(self):
        response = self.client.get('/api/facilities/count/')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        return response.data['count']

    def _download_ids(self, **params):
        self.client.force_authenticate(user=self.superuser)
        try:
            response = self.client.get('/api/facilities-downloads/', params)
        finally:
            self.client.force_authenticate(user=None)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        results = response.data['results']
        column = results['headers'].index('os_id')
        return sorted(row[column] for row in results['rows'])

    def _assert_hidden_from_confirmed_surfaces(self, confirmed_ids):
        """Every FacilityIndex / Facility.objects surface shows exactly
        ``confirmed_ids`` and never a candidate."""
        self._reset_throttles()
        confirmed_ids = sorted(confirmed_ids)
        self.assertEqual(confirmed_ids, self._list_ids())
        self.assertEqual(len(confirmed_ids), self._count())
        self.assertEqual(confirmed_ids, self._download_ids())
        self.assertEqual(
            confirmed_ids,
            sorted(FacilityIndex.objects.values_list('id', flat=True)),
        )
        for candidate in self._candidates():
            self.assertEqual([], self._list_ids(q=candidate.id))
            self.assertEqual([], self._download_ids(q=candidate.id))

    def _assert_gone(self, os_id):
        self._reset_throttles()
        for response in (self._legacy_detail(os_id), self._v1_detail(os_id)):
            self.assertEqual(status.HTTP_410_GONE, response.status_code)
            body = json.loads(response.content)
            self.assertEqual(RETIRED_DETAIL, body['detail'])
            self.assertEqual(os_id, body['os_id'])
            self.assertTrue(body['retired_at'])
        self.assertEqual(
            status.HTTP_410_GONE,
            self.client.get(self._votes_url(os_id)).status_code,
        )

    def _force_index_row(self, facility):
        """A stale api_facilityindex row, as rows indexed before 0246
        shipped would be; retirement must clear it."""
        FacilityIndex.objects.get_or_create(
            id=facility.id,
            defaults={
                'name': facility.name,
                'address': facility.address,
                'country_code': facility.country_code,
                'location': facility.location,
                'contributors_count': 1,
                'contributors_id': [self.eg_contributor.id],
                'contributors': [{
                    'id': self.eg_contributor.id,
                    'name': self.eg_contributor.name,
                }],
                'contrib_types': [self.eg_contributor.contrib_type],
                'facility_addresses': [{'address': facility.address}],
                'extended_fields': [],
                'lists': [],
                'approved_claim_ids': [],
                'facility_names': [],
                'sector': ['Agriculture'],
            },
        )
        self.assertTrue(FacilityIndex.objects.filter(id=facility.id).exists())

    def _graph_ids(self, facility):
        item = facility.created_from
        match = FacilityMatch.objects.get(facility=facility)
        return item.source_id, item.id, match.id

    def _assert_graph_gone(self, graph_ids):
        source_id, item_id, match_id = graph_ids
        self.assertFalse(Source.objects.filter(id=source_id).exists())
        self.assertFalse(FacilityListItem.objects.filter(id=item_id).exists())
        self.assertFalse(FacilityMatch.objects.filter(id=match_id).exists())

    def _graph_counts(self):
        return (
            Source.objects.count(),
            FacilityListItem.objects.count(),
            FacilityMatch.objects.count(),
        )

    # --- the lifecycle ----------------------------------------------------

    def test_ingest_vote_retire_and_reingest(self):
        # 1. Ingest: 3 candidates with OS IDs, the no-geometry record skipped.
        out = self._ingest()

        self.assertIn('created=3 updated=0', out)
        self.assertIn('skipped_no_geometry=1', out)
        self.assertEqual(3, self._candidates().count())
        a, b, c = (self._candidate(x) for x in ('EG-A', 'EG-B', 'EG-C'))
        for candidate in (a, b, c):
            self.assertTrue(candidate.is_candidate)
            self.assertTrue(candidate.id.startswith('US'), candidate.id)
            self.assertEqual(15, len(candidate.id))
            self.assertEqual('', candidate.name)
            self.assertEqual(
                self.eg_contributor.id,
                candidate.created_from.source.contributor_id,
            )
        self.assertEqual(3, len({a.id, b.id, c.id}))
        self.assertIsNotNone(a.polygon)
        self.assertIsNotNone(b.polygon)
        self.assertIsNone(c.polygon)

        # 2. Hidden from every confirmed surface, with no stale index rows.
        self._assert_hidden_from_confirmed_surfaces([self.confirmed.id])

        # 3. Present in the bbox endpoint, labeled unverified.
        self._reset_throttles()
        features = self._bbox_features()
        self.assertEqual({a.id, b.id, c.id}, set(features))
        self.assertEqual('Polygon', features[a.id]['geometry']['type'])
        self.assertEqual('Polygon', features[b.id]['geometry']['type'])
        self.assertEqual('Point', features[c.id]['geometry']['type'])
        for os_id in (a.id, b.id, c.id):
            properties = features[os_id]['properties']
            self.assertEqual(UNVERIFIED, properties['state'])
            self.assertEqual(SOURCE, properties['source'])

        # 4. Direct lookups serve the labeled candidate payloads.
        response = self._v1_detail(a.id)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIs(True, response.data['is_candidate'])
        self.assertEqual(a.id, response.data['os_id'])
        self.assertEqual('EG-A', response.data['external_id'])
        self.assertEqual(0.95, response.data['confidence'])
        self.assertEqual('Polygon', response.data['polygon']['type'])
        self.assertEqual(UNVERIFIED, response.data['validation']['state'])
        self.assertTrue(response.data['validation']['voting_open'])
        self.assertEqual('noindex', response['X-Robots-Tag'])

        response = self._legacy_detail(a.id)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        props = json.loads(response.content)['properties']
        self.assertIs(True, props['is_candidate'])
        self.assertEqual(UNVERIFIED, props['candidate']['state'])
        self.assertEqual('Earth Genome', props['created_from']['contributor'])

        # 5. Candidate A: three voters split -> disputed, voting stays
        #    open; two more "yes" votes reach consensus-yes -> confirmed,
        #    voting closes (D6). With the pilot margins a 2-1 split is
        #    already confirmed (0.667 >= 0.6), so the "no" votes go first.
        self._reset_throttles()
        self._vote(self.voters[0], a.id, NO)
        self._vote(self.voters[1], a.id, NO)
        response = self._vote(self.voters[2], a.id, YES)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(DISPUTED, response.data['state'])
        self.assertEqual(
            {'confirmed': 1, 'not_a_facility': 2}, response.data['tally']
        )
        for payload in (
            self._v1_detail(a.id).data['validation'],
            json.loads(self._legacy_detail(a.id).content)
            ['properties']['candidate'],
            self._bbox_features()[a.id]['properties'],
        ):
            self.assertEqual(DISPUTED, payload['state'])
            self.assertEqual(
                {'confirmed': 1, 'not_a_facility': 2}, payload['tally']
            )
        self.assertFalse(FacilityCandidateRetirementRequest.objects.exists())

        response = self._vote(self.voters[3], a.id, YES)
        self.assertEqual(DISPUTED, response.data['state'])
        response = self._vote(self.voters[4], a.id, YES)
        self.assertEqual(CONFIRMED, response.data['state'])
        self.assertEqual(
            {'confirmed': 3, 'not_a_facility': 2}, response.data['tally']
        )
        self.assertFalse(
            self._v1_detail(a.id).data['validation']['voting_open']
        )

        response = self._vote(self.eg_user, a.id, NO)
        self.assertEqual(status.HTTP_409_CONFLICT, response.status_code)
        response = self._vote(self.voters[0], a.id, YES)   # change of mind
        self.assertEqual(status.HTTP_409_CONFLICT, response.status_code)
        self.assertEqual(
            5, FacilityCandidateVote.objects.filter(facility=a).count()
        )
        # Confirmed is a derived state: the row stays a candidate, so it
        # remains off the confirmed surfaces and is never tombstoned.
        a.refresh_from_db()
        self.assertTrue(a.is_candidate)
        self.assertFalse(FacilityAlias.objects.filter(os_id=a.id).exists())
        self._assert_hidden_from_confirmed_surfaces([self.confirmed.id])

        # 6. Candidate B: consensus-no under the moderation gate opens a
        #    retirement request; nothing is deleted yet.
        self._reset_throttles()
        self._vote(self.voters[0], b.id, NO)
        self._vote(self.voters[1], b.id, NO)
        response = self._vote(self.voters[2], b.id, NO)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(RETIREMENT_PENDING, response.data['state'])
        request = FacilityCandidateRetirementRequest.objects.get()
        self.assertEqual(b.id, request.facility_id)
        self.assertEqual({'confirmed': 0, 'not_a_facility': 3}, request.tally)
        self.assertTrue(self._exists(b.id))
        self.assertFalse(FacilityAlias.objects.filter(os_id=b.id).exists())
        self.assertEqual(
            RETIREMENT_PENDING,
            self._v1_detail(b.id).data['validation']['state'],
        )
        self.assertEqual(
            RETIREMENT_PENDING,
            self._bbox_features()[b.id]['properties']['state'],
        )

        # 7. Moderator approval retires B: hard delete + tombstone.
        self._reset_throttles()
        self._force_index_row(b)
        b_graph = self._graph_ids(b)
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(
            f'/api/v1/candidate-retirement-requests/{request.id}/approve/'
        )
        self.client.force_authenticate(user=None)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(b.id, response.data['os_id'])
        self.assertEqual(RETIRED, response.data['state'])

        self.assertFalse(self._exists(b.id))
        self._assert_gone(b.id)
        tombstone = FacilityAlias.objects.get(os_id=b.id)
        self.assertEqual(FacilityAlias.NOT_A_FACILITY, tombstone.reason)
        self.assertIsNone(tombstone.facility)
        self.assertEqual(SOURCE, tombstone.retired_source)
        self.assertEqual('EG-B', tombstone.retired_external_id)
        self.assertEqual(0, tombstone.retirement_tally['confirmed'])
        self.assertEqual(3, tombstone.retirement_tally['not_a_facility'])
        self.assertEqual(
            self.superuser.id, tombstone.retirement_tally['retired_by']
        )
        self.assertTrue(tombstone.retirement_tally['retired_at'])

        self.assertFalse(FacilityIndex.objects.filter(id=b.id).exists())
        self._assert_graph_gone(b_graph)
        self.assertFalse(
            FacilityCandidateVote.objects.filter(facility_id=b.id).exists()
        )
        self.assertFalse(FacilityCandidateRetirementRequest.objects.exists())
        # The OpenSearch delete was attempted, the 404 tolerated, and no
        # inconsistency was reported for the never-indexed candidate.
        delete = self.opensearch_connection.return_value.client.delete
        delete.assert_called_once()
        self.assertEqual(b.id, delete.call_args.kwargs['id'])
        self.error_notifier.assert_not_called()

        self.assertEqual({a.id, c.id}, set(self._bbox_features()))
        self.assertTrue(Facility.objects.filter(id=self.confirmed.id).exists())
        self._assert_hidden_from_confirmed_surfaces([self.confirmed.id])

        # 8. Re-ingest the same file: B stays retired, A and C update in
        #    place with the same OS IDs, no new synthetic records.
        self._reset_throttles()
        counts_before = self._graph_counts()
        out = self._ingest()

        self.assertIn('created=0 updated=2', out)
        self.assertIn('skipped_retired=1', out)
        self.assertIn('skipped_no_geometry=1', out)
        self.assertEqual(
            {'EG-A': a.id, 'EG-C': c.id},
            dict(self._candidates().values_list('external_id', 'id')),
        )
        self.assertFalse(self._detection_exists('EG-B'))
        self.assertEqual(counts_before, self._graph_counts())
        self.assertTrue(FacilityAlias.objects.filter(os_id=b.id).exists())
        self._assert_gone(b.id)
        # A's votes and derived state survive the refresh.
        self.assertEqual(
            CONFIRMED, self._v1_detail(a.id).data['validation']['state']
        )
        self.assertEqual(
            5, FacilityCandidateVote.objects.filter(facility=a).count()
        )
        self._assert_hidden_from_confirmed_surfaces([self.confirmed.id])

    @override_settings(CANDIDATE_AUTO_RETIRE=True)
    def test_auto_retire_makes_consensus_no_an_immediate_410(self):
        self._ingest()
        c = self._candidate('EG-C')
        c_graph = self._graph_ids(c)
        self._reset_throttles()
        self._force_index_row(c)

        self._vote(self.voters[0], c.id, NO)
        response = self._vote(self.voters[1], c.id, NO)
        self.assertEqual(UNVERIFIED, response.data['state'])
        self.assertTrue(self._exists(c.id))

        response = self._vote(self.voters[2], c.id, NO)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(RETIRED, response.data['state'])
        self.assertEqual(
            {'confirmed': 0, 'not_a_facility': 3}, response.data['tally']
        )
        self.assertFalse(self._exists(c.id))
        self.assertFalse(FacilityCandidateRetirementRequest.objects.exists())
        self.assertFalse(FacilityIndex.objects.filter(id=c.id).exists())
        self._assert_graph_gone(c_graph)
        self._assert_gone(c.id)
        tombstone = FacilityAlias.objects.get(os_id=c.id)
        self.assertEqual('EG-C', tombstone.retired_external_id)
        self.assertEqual(
            self.voters[2].id, tombstone.retirement_tally['retired_by']
        )
        self.error_notifier.assert_not_called()

        # The other two candidates and the confirmed facility are untouched,
        # and a re-ingest does not bring C back.
        self.assertEqual(2, self._candidates().count())
        self.assertTrue(Facility.objects.filter(id=self.confirmed.id).exists())
        out = self._ingest()
        self.assertIn('created=0 updated=2', out)
        self.assertIn('skipped_retired=1', out)
        self.assertFalse(self._detection_exists('EG-C'))
        self._assert_hidden_from_confirmed_surfaces([self.confirmed.id])

    # --- regression: confirmed flows with candidates present ----------------

    @patch(KAFKA_PRODUCER, new_callable=Mock)
    @patch(GEOCODER)
    def test_candidates_present_do_not_change_confirmed_facility_flows(
        self, mock_geocoder, mock_producer
    ):
        """
        The legacy ``POST /api/facilities/`` path creates a confirmed
        facility the normal way while three candidates sit in the
        database, and every confirmed surface then behaves exactly as it
        would in a candidate-free database.

        Dedupe Hub is an external service reached through
        ``asyncio.run(produce_message_match_process(source_id))``. That
        call is the boundary replaced here: a stand-in does what Dedupe
        Hub does for a new facility (Facility + AUTOMATIC match, item
        MATCHED) on the test connection, and the view's own result
        handling then runs unmodified. (The work cannot live inside an
        async side effect: a task started by ``asyncio.run`` gets its own
        database connection and cannot see the test transaction.)
        """
        mock_geocoder.return_value = Mock(ok=True, status_code=200)
        mock_geocoder.return_value.json.return_value = geocoding_data

        def dedupe_hub_creates_new_facility(_awaitable):
            (source_id,), _ = mock_producer.call_args
            item = FacilityListItem.objects.get(source_id=source_id)
            facility = Facility.objects.create(
                name=item.name,
                address=item.address,
                country_code=item.country_code,
                location=item.geocoded_point,
                created_from=item,
            )
            FacilityMatch.objects.create(
                facility=facility,
                facility_list_item=item,
                status=FacilityMatch.AUTOMATIC,
                confidence=1.0,
                results={'match_type': 'single_gazetteer_match'},
            )
            item.facility = facility
            item.status = FacilityListItem.MATCHED
            item.save()

        fake_asyncio = Mock()
        fake_asyncio.run.side_effect = dedupe_hub_creates_new_facility
        patch(ASYNCIO_IN_PROCESSING, fake_asyncio).start()

        self._ingest()
        self.assertEqual(3, self._candidates().count())
        candidate_ids = set(self._candidates().values_list('id', flat=True))
        self._assert_hidden_from_confirmed_surfaces([self.confirmed.id])

        group = auth.models.Group.objects.get(
            name=FeatureGroups.CAN_SUBMIT_FACILITY
        )
        self.submitter.groups.set([group.id])
        self.client.login(
            email=self.submitter.email, password=self.submitter_password
        )
        response = self.client.post(
            reverse('facility-list'),
            json.dumps({
                'country': 'US',
                'name': 'Towel Factory 42',
                'address': '42 Dolphin St',
                'sector': 'Apparel',
            }),
            content_type='application/json',
        )
        self.client.logout()

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(
            FacilityListItem.NEW_FACILITY, response.data['status']
        )
        new_os_id = response.data['os_id']
        self.assertNotIn(new_os_id, candidate_ids)
        mock_producer.assert_called_once()
        new_facility = Facility.objects.get(id=new_os_id)
        self.assertFalse(new_facility.is_candidate)
        self.assertEqual('Towel Factory 42', new_facility.name)
        self.assertEqual(
            self.contributor.id,
            new_facility.created_from.source.contributor_id,
        )

        self._reset_throttles()
        response = self._legacy_detail(new_os_id)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertFalse(response.has_header('X-Robots-Tag'))
        body = json.loads(response.content)
        self.assertEqual(new_os_id, body['id'])
        self.assertEqual('Towel Factory 42', body['properties']['name'])
        self.assertNotIn('is_candidate', body['properties'])
        self.assertNotIn('candidate', body['properties'])
        self.assertEqual(
            [self.contributor.name],
            [c['name'] for c in body['properties']['contributors']],
        )

        # Exactly the two confirmed facilities everywhere; the candidates
        # change nothing.
        self._assert_hidden_from_confirmed_surfaces(
            [self.confirmed.id, new_os_id]
        )
        self.assertEqual([new_os_id], self._list_ids(q='Towel Factory'))
        self.assertEqual([new_os_id], self._download_ids(q=new_os_id))
        self.assertEqual(3, self._candidates().count())
        self.assertEqual(
            UNVERIFIED, self._v1_detail(sorted(candidate_ids)[0])
            .data['validation']['state'],
        )
