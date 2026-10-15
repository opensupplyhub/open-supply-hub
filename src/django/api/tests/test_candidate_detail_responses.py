import json
import unittest.mock

from django.contrib.gis.geos import GEOSGeometry, Point
from django.db.models.signals import post_delete
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import (
    Contributor,
    Facility,
    FacilityCandidateVote,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.models.extended_field import ExtendedField
from api.models.facility.facility_index import FacilityIndex
from api.serializers.facility.facility_index_details_serializer import (
    FacilityIndexDetailsSerializer,
)
from api.serializers.v1.candidates_bbox_query_param_serializer import (
    CandidatesBboxQueryParamSerializer,
)
from api.services.candidate_retirement import (
    RETIRED_DETAIL,
    retire_candidate,
)
from api.services.candidate_validation import (
    DISPUTED,
    UNVERIFIED,
    cast_vote,
)
from api.signals import location_post_delete_handler_for_opensearch

OPEN_SEARCH_SERVICE = 'api.views.v1.production_locations.OpenSearchService'
CANDIDATE_POLYGON_WKT = 'POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))'
FAR_POLYGON_WKT = 'POLYGON((5 5, 5 6, 6 6, 6 5, 5 5))'
YES = FacilityCandidateVote.Vote.CONFIRMED.value
NO = FacilityCandidateVote.Vote.NOT_A_FACILITY.value
ZERO_TALLY = {'confirmed': 0, 'not_a_facility': 0}
CANDIDATE_KEYS = ('is_candidate', 'candidate', 'validation')

# Pinned so the derived states below do not drift with a local .env.
PILOT_THRESHOLDS = dict(
    CANDIDATE_VOTE_THRESHOLD=3,
    CANDIDATE_CONFIRM_MARGIN=0.6,
    CANDIDATE_RETIRE_MARGIN=0.75,
    CANDIDATE_AUTO_RETIRE=False,
)


@override_settings(**PILOT_THRESHOLDS)
class CandidateDetailResponsesTest(APITestCase):
    """
    OSDEV-3249: candidate-aware detail responses.

    Fixture mirrors test_candidate_votes: one confirmed facility at (0, 0)
    and three candidates built the way ingest builds them -- one with a
    polygon around the confirmed facility, one point-only candidate inside
    that polygon and one far away.
    """

    def setUp(self):
        post_delete.disconnect(
            location_post_delete_handler_for_opensearch, Facility
        )
        self.addCleanup(
            post_delete.connect,
            location_post_delete_handler_for_opensearch,
            Facility,
        )
        self.search_mock = unittest.mock.patch(OPEN_SEARCH_SERVICE).start()
        self.addCleanup(unittest.mock.patch.stopall)
        self.search_index_mock = self.search_mock.return_value.search_index
        self.search_index_mock.return_value = {}

        self.user = User.objects.create(email='one@example.com')
        self.voters = [
            User.objects.create(email=f'voter{i}@example.com')
            for i in range(4)
        ]
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
        self.candidate_source = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            create=True,
            contributor=self.contributor,
        )
        self.next_row_index = 0

        self.facility = self._create_facility(
            self.list_source, name='Confirmed'
        )
        self.candidate = self._create_candidate(
            'eg-facility-0001',
            polygon=GEOSGeometry(CANDIDATE_POLYGON_WKT, srid=4326),
            location=Point(0, 0),
        )
        self.point_candidate = self._create_candidate(
            'eg-facility-0002', polygon=None, location=Point(0.5, 0.5)
        )
        self.far_candidate = self._create_candidate(
            'eg-facility-0003',
            polygon=GEOSGeometry(FAR_POLYGON_WKT, srid=4326),
            location=Point(5.5, 5.5),
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
        FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=facility,
            facility_list_item=item,
            confidence=1.0,
            results={},
        )
        return facility

    def _create_candidate(self, external_id, **kwargs):
        return self._create_facility(
            self.candidate_source,
            name='',
            address='',
            is_candidate=True,
            confidence=0.87,
            external_id=external_id,
            source='earth_genome',
            **kwargs,
        )

    def _make_disputed(self, candidate):
        """
        2 yes / 2 no reaches the threshold with no consensus. The "no"
        votes go first: 1-2 at the threshold is already disputed, whereas
        2-1 would be confirmed (0.667 >= 0.6) and close voting.
        """
        for voter, vote in zip(self.voters, (NO, NO, YES, YES)):
            cast_vote(candidate, voter, vote)
        return {'confirmed': 2, 'not_a_facility': 2}

    @staticmethod
    def _v1_url(os_id):
        return f'/api/v1/production-locations/{os_id}/'

    @staticmethod
    def _legacy_url(os_id):
        return f'/api/facilities/{os_id}/'

    @staticmethod
    def _bbox_url(bbox=None, **params):
        if bbox is not None:
            params['bbox'] = bbox
        query = '&'.join(f'{k}={v}' for k, v in params.items())
        return f'/api/v1/production-locations/candidates/?{query}'

    def _assert_candidate_headers(self, response):
        self.assertEqual('noindex', response['X-Robots-Tag'])
        self.assertIn('private', response['Cache-Control'])

    def _assert_no_candidate_headers(self, response):
        self.assertFalse(response.has_header('X-Robots-Tag'))

    # --- v1 detail -----------------------------------------------------

    def test_v1_candidate_detail_is_labeled(self):
        response = self.client.get(self._v1_url(self.candidate.id))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self._assert_candidate_headers(response)
        body = response.data
        self.assertEqual(
            [
                'os_id', 'is_candidate', 'name', 'address', 'country',
                'coordinates', 'source', 'external_id', 'confidence',
                'polygon', 'created_at', 'updated_at', 'validation',
                'suggested_matches',
            ],
            list(body.keys()),
        )
        self.assertEqual(self.candidate.id, body['os_id'])
        self.assertIs(True, body['is_candidate'])
        self.assertEqual('', body['name'])
        self.assertEqual('', body['address'])
        self.assertEqual(
            {'alpha_2': 'US', 'name': 'United States'}, body['country']
        )
        self.assertEqual({'lat': 0.0, 'lng': 0.0}, body['coordinates'])
        self.assertEqual('earth_genome', body['source'])
        self.assertEqual('eg-facility-0001', body['external_id'])
        self.assertEqual(0.87, body['confidence'])
        self.assertEqual('Polygon', body['polygon']['type'])
        self.assertEqual(
            [[[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]],
            body['polygon']['coordinates'],
        )
        self.assertTrue(body['created_at'])
        self.assertTrue(body['updated_at'])
        self.assertEqual(
            {
                'state': UNVERIFIED,
                'tally': ZERO_TALLY,
                'your_vote': None,
                'voting_open': True,
            },
            body['validation'],
        )
        self.assertEqual(
            [{
                'os_id': self.facility.id,
                'name': 'Confirmed',
                'address': 'Address',
                'distance_m': 0.0,
            }],
            body['suggested_matches'],
        )

    def test_v1_point_only_candidate_has_null_polygon(self):
        response = self.client.get(self._v1_url(self.point_candidate.id))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIsNone(response.data['polygon'])
        self.assertEqual(
            {'lat': 0.5, 'lng': 0.5}, response.data['coordinates']
        )

    def test_v1_disputed_candidate_carries_state_and_split_tally(self):
        expected_tally = self._make_disputed(self.candidate)

        response = self.client.get(self._v1_url(self.candidate.id))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        validation = response.data['validation']
        self.assertEqual(DISPUTED, validation['state'])
        self.assertEqual(expected_tally, validation['tally'])
        self.assertTrue(validation['voting_open'])

    def test_v1_confirmed_candidate_closes_voting(self):
        for voter in self.voters[:3]:
            cast_vote(self.candidate, voter, YES)

        response = self.client.get(self._v1_url(self.candidate.id))

        self.assertEqual('confirmed', response.data['validation']['state'])
        self.assertFalse(response.data['validation']['voting_open'])

    def test_v1_your_vote_for_authenticated_and_anonymous(self):
        cast_vote(self.candidate, self.user, YES)

        response = self.client.get(self._v1_url(self.candidate.id))
        self.assertIsNone(response.data['validation']['your_vote'])

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self._v1_url(self.candidate.id))
        self.assertEqual(YES, response.data['validation']['your_vote'])

        self.client.force_authenticate(user=self.voters[0])
        response = self.client.get(self._v1_url(self.candidate.id))
        self.assertIsNone(response.data['validation']['your_vote'])

    def test_v1_confirmed_facility_response_is_unchanged(self):
        document = {
            'os_id': self.facility.id,
            'name': 'Confirmed',
            'address': 'Address',
            'country': {'alpha_2': 'US', 'name': 'United States'},
            'coordinates': {'lat': 0.0, 'lng': 0.0},
        }
        self.search_index_mock.return_value = {'count': 1, 'data': [document]}

        response = self.client.get(self._v1_url(self.facility.id))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(document, response.data)
        for key in CANDIDATE_KEYS:
            self.assertNotIn(key, response.data)
        self._assert_no_candidate_headers(response)

    def test_v1_confirmed_facility_missing_from_opensearch_is_still_404(
        self
    ):
        # The fallback is for candidates only: an indexing gap on a
        # confirmed facility keeps its pre-existing 404.
        response = self.client.get(self._v1_url(self.facility.id))

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self._assert_no_candidate_headers(response)

    def test_v1_retired_candidate_is_still_410_and_unknown_404(self):
        os_id = self.candidate.id
        retire_candidate(self.candidate, {'confirmed': 0, 'not_a_facility': 3})

        response = self.client.get(self._v1_url(os_id))
        self.assertEqual(status.HTTP_410_GONE, response.status_code)
        self.assertEqual(RETIRED_DETAIL, response.data['detail'])

        response = self.client.get(self._v1_url('US1234567ABCDEF'))
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    # --- legacy detail -------------------------------------------------

    def test_legacy_candidate_detail_is_a_labeled_feature(self):
        response = self.client.get(self._legacy_url(self.candidate.id))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self._assert_candidate_headers(response)
        body = json.loads(response.content)
        self.assertEqual(self.candidate.id, body['id'])
        self.assertEqual('Feature', body['type'])
        self.assertEqual(
            {'type': 'Point', 'coordinates': [0.0, 0.0]}, body['geometry']
        )
        props = body['properties']
        self.assertIs(True, props['is_candidate'])
        self.assertEqual('', props['name'])
        self.assertEqual('', props['address'])
        self.assertEqual('US', props['country_code'])
        self.assertEqual('United States', props['country_name'])
        self.assertEqual(self.candidate.id, props['os_id'])

        candidate = props['candidate']
        self.assertEqual(
            [
                'state', 'tally', 'your_vote', 'voting_open', 'source',
                'external_id', 'confidence', 'polygon', 'suggested_matches',
            ],
            list(candidate.keys()),
        )
        self.assertEqual(UNVERIFIED, candidate['state'])
        self.assertEqual(ZERO_TALLY, candidate['tally'])
        self.assertIsNone(candidate['your_vote'])
        self.assertTrue(candidate['voting_open'])
        self.assertEqual('earth_genome', candidate['source'])
        self.assertEqual('eg-facility-0001', candidate['external_id'])
        self.assertEqual(0.87, candidate['confidence'])
        self.assertEqual('Polygon', candidate['polygon']['type'])
        self.assertEqual(
            self.facility.id, candidate['suggested_matches'][0]['os_id']
        )

        # Every key the confirmed-facility serializer emits is present
        # with a safe empty, so the existing detail page renders.
        expected_keys = set(FacilityIndexDetailsSerializer.Meta.fields)
        expected_keys -= {'id', 'location'}
        expected_keys |= {'is_candidate', 'candidate'}
        self.assertEqual(expected_keys, set(props.keys()))
        self.assertEqual([], props['contributors'])
        self.assertIsNone(props['claim_info'])
        self.assertIsNone(props['is_closed'])
        self.assertIsNone(props['new_os_id'])
        self.assertEqual([], props['activity_reports'])
        self.assertEqual([], props['other_locations'])
        self.assertEqual([], props['sector'])
        self.assertEqual({}, props['partner_fields'])
        self.assertIs(False, props['is_claimed'])
        self.assertIs(False, props['is_data_center'])
        self.assertIs(False, props['has_inexact_coordinates'])
        self.assertEqual(
            {name for name, _ in ExtendedField.FIELD_CHOICES},
            set(props['extended_fields'].keys()),
        )
        self.assertTrue(
            all(v == [] for v in props['extended_fields'].values())
        )
        self.assertEqual('Earth Genome', props['created_from']['contributor'])
        self.assertTrue(props['created_from']['created_at'])

    def test_legacy_disputed_candidate_carries_split_tally(self):
        expected_tally = self._make_disputed(self.candidate)

        response = self.client.get(self._legacy_url(self.candidate.id))

        candidate = json.loads(response.content)['properties']['candidate']
        self.assertEqual(DISPUTED, candidate['state'])
        self.assertEqual(expected_tally, candidate['tally'])

    def test_legacy_your_vote_is_per_caller_not_cached_across_users(self):
        cast_vote(self.candidate, self.user, YES)
        url = self._legacy_url(self.candidate.id)

        def your_vote():
            return json.loads(
                self.client.get(url).content
            )['properties']['candidate']['your_vote']

        self.client.force_authenticate(user=self.user)
        self.assertEqual(YES, your_vote())
        self.client.force_authenticate(user=self.voters[0])
        self.assertIsNone(your_vote())
        self.client.force_authenticate(user=None)
        self.assertIsNone(your_vote())

    def test_legacy_confirmed_facility_response_is_unchanged(self):
        self.assertTrue(
            FacilityIndex.objects.filter(id=self.facility.id).exists()
        )

        response = self.client.get(self._legacy_url(self.facility.id))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self._assert_no_candidate_headers(response)
        body = json.loads(response.content)
        props = body['properties']
        # Exactly the pre-existing serializer's key set, nothing added.
        expected_keys = set(FacilityIndexDetailsSerializer.Meta.fields)
        expected_keys -= {'id', 'location'}
        self.assertEqual(expected_keys, set(props.keys()))
        for key in CANDIDATE_KEYS:
            self.assertNotIn(key, props)
        self.assertEqual('Confirmed', props['name'])
        self.assertEqual(self.facility.id, body['id'])

    def test_legacy_retired_candidate_is_still_410_and_unknown_404(self):
        os_id = self.candidate.id
        retire_candidate(self.candidate, {'confirmed': 0, 'not_a_facility': 3})

        response = self.client.get(self._legacy_url(os_id))
        self.assertEqual(status.HTTP_410_GONE, response.status_code)

        response = self.client.get(self._legacy_url('US1234567ABCDEF'))
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    # --- bbox endpoint -------------------------------------------------

    def test_bbox_returns_intersecting_candidates_only(self):
        response = self.client.get(self._bbox_url('-0.5,-0.5,1.5,1.5'))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('noindex', response['X-Robots-Tag'])
        body = response.data
        self.assertEqual('FeatureCollection', body['type'])
        self.assertEqual(
            sorted([self.candidate.id, self.point_candidate.id]),
            [feature['id'] for feature in body['features']],
        )
        by_id = {feature['id']: feature for feature in body['features']}
        self.assertNotIn(self.facility.id, by_id)
        self.assertNotIn(self.far_candidate.id, by_id)

        polygon_feature = by_id[self.candidate.id]
        self.assertEqual('Feature', polygon_feature['type'])
        self.assertEqual('Polygon', polygon_feature['geometry']['type'])
        self.assertEqual(
            {
                'os_id': self.candidate.id,
                'confidence': 0.87,
                'source': 'earth_genome',
                'state': UNVERIFIED,
                'tally': ZERO_TALLY,
                'centroid': {'lat': 0.0, 'lng': 0.0},
            },
            polygon_feature['properties'],
        )
        point_feature = by_id[self.point_candidate.id]
        self.assertEqual(
            {'type': 'Point', 'coordinates': [0.5, 0.5]},
            point_feature['geometry'],
        )
        self.assertEqual(
            {'lat': 0.5, 'lng': 0.5},
            point_feature['properties']['centroid'],
        )

    def test_bbox_touching_polygon_edge_counts_as_intersecting(self):
        # The far candidate's polygon starts at (5, 5); a box ending there
        # touches it, a box ending just short of it does not.
        response = self.client.get(self._bbox_url('4,4,5,5'))
        self.assertEqual(
            [self.far_candidate.id],
            [f['id'] for f in response.data['features']],
        )
        response = self.client.get(self._bbox_url('4,4,4.9,4.9'))
        self.assertEqual([], response.data['features'])

    def test_bbox_never_includes_non_candidates(self):
        # A confirmed facility with a polygon-shaped footprint would still
        # be excluded: the filter is on is_candidate, not geometry.
        Facility.objects.filter(pk=self.facility.pk).update(
            polygon=GEOSGeometry(CANDIDATE_POLYGON_WKT, srid=4326)
        )

        response = self.client.get(self._bbox_url('-0.5,-0.5,1.5,1.5'))

        ids = {feature['id'] for feature in response.data['features']}
        self.assertNotIn(self.facility.id, ids)
        self.assertEqual(2, len(ids))

    def test_bbox_state_and_tally_reflect_votes(self):
        expected_tally = self._make_disputed(self.candidate)

        response = self.client.get(self._bbox_url('-0.5,-0.5,1.5,1.5'))

        by_id = {f['id']: f['properties'] for f in response.data['features']}
        self.assertEqual(DISPUTED, by_id[self.candidate.id]['state'])
        self.assertEqual(expected_tally, by_id[self.candidate.id]['tally'])
        self.assertEqual(UNVERIFIED, by_id[self.point_candidate.id]['state'])
        self.assertEqual(ZERO_TALLY, by_id[self.point_candidate.id]['tally'])

    def test_bbox_limit_is_applied_and_capped(self):
        response = self.client.get(
            self._bbox_url('-0.5,-0.5,1.5,1.5', limit=1)
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data['features']))

        # Over the cap is clamped, not rejected.
        response = self.client.get(
            self._bbox_url('-0.5,-0.5,1.5,1.5', limit=9999)
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data['features']))

        params = CandidatesBboxQueryParamSerializer(
            data={'bbox': '0,0,1,1', 'limit': '9999'}
        )
        self.assertTrue(params.is_valid(), params.errors)
        self.assertEqual(500, params.validated_data['limit'])
        params = CandidatesBboxQueryParamSerializer(data={'bbox': '0,0,1,1'})
        self.assertTrue(params.is_valid(), params.errors)
        self.assertEqual(200, params.validated_data['limit'])

    def test_bbox_bad_requests_are_400(self):
        cases = {
            'missing bbox': self._bbox_url(),
            'three numbers': self._bbox_url('0,0,1'),
            'not numeric': self._bbox_url('a,b,c,d'),
            'nan': self._bbox_url('nan,0,1,1'),
            'inverted': self._bbox_url('1,1,0,0'),
            'out of range': self._bbox_url('-181,0,1,1'),
            'too wide': self._bbox_url('0,0,2.5,1'),
            'too tall': self._bbox_url('0,0,1,2.5'),
            'limit zero': self._bbox_url('0,0,1,1', limit=0),
            'limit text': self._bbox_url('0,0,1,1', limit='abc'),
        }
        for label, url in cases.items():
            with self.subTest(label):
                response = self.client.get(url)
                self.assertEqual(
                    status.HTTP_400_BAD_REQUEST, response.status_code
                )
                self.assertEqual(
                    'The request query is invalid.', response.data['detail']
                )
                self.assertIn(
                    response.data['errors'][0]['field'], ('bbox', 'limit')
                )
                self.assertTrue(response.data['errors'][0]['detail'])

    def test_bbox_too_large_message_is_clear(self):
        response = self.client.get(self._bbox_url('0,0,3,1'))

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual('bbox', response.data['errors'][0]['field'])
        self.assertIn(
            'at most 2 degrees', response.data['errors'][0]['detail']
        )

    def test_bbox_route_is_not_shadowed_by_detail_lookup(self):
        # 'candidates' must resolve to the collection action, not to a
        # retrieve of an OS ID literally named "candidates".
        response = self.client.get('/api/v1/production-locations/candidates/')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual('bbox', response.data['errors'][0]['field'])
