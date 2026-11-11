import unittest.mock
from datetime import timedelta

from django.contrib.gis.geos import GEOSGeometry, Point
from django.core.cache import caches
from django.db.models.signals import post_delete
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

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
from api.services.candidate_listing import (
    ORDER_CACHE_ALIAS,
    _order_cache_key,
)
from api.services.candidate_retirement import retire_candidate
from api.services.candidate_validation import (
    CONFIRMED,
    DISPUTED,
    RETIREMENT_PENDING,
    UNVERIFIED,
    cast_vote,
)
from api.signals import location_post_delete_handler_for_opensearch

OPEN_SEARCH_SERVICE = 'api.views.v1.production_locations.OpenSearchService'
URL = '/api/v1/production-locations/candidates/'
YES = FacilityCandidateVote.Vote.CONFIRMED.value
NO = FacilityCandidateVote.Vote.NOT_A_FACILITY.value
ZERO_TALLY = {'confirmed': 0, 'not_a_facility': 0}
# 0.003485 degrees of longitude on the equator is ~388 m on the sphere
# PostGIS uses for ST_DistanceSphere.
NEAR_OFFSET_DEG = 0.003485

PILOT_THRESHOLDS = dict(
    CANDIDATE_VOTE_THRESHOLD=3,
    CANDIDATE_CONFIRM_MARGIN=0.6,
    CANDIDATE_RETIRE_MARGIN=0.75,
    CANDIDATE_AUTO_RETIRE=False,
    CANDIDATE_SUGGESTION_RADIUS_M=500,
)


@override_settings(**PILOT_THRESHOLDS)
@override_switch('earth_genome_candidates', active=True)
class CandidatesListEndpointTest(APITestCase):
    """
    OSDEV-3754: the paged list mode of the candidates endpoint.

    Fixture: two confirmed facilities, one at (0, 0) and one 388 m east
    of (3, 0); four candidates, built the way ingest builds them:

      * ``c_near_zero``  polygon around (0, 0): 1 confirmed within 500 m
                         (distance 0), confidence 0.40, US
      * ``c_alone``      point at (0.5, 0.5): nothing nearby, 0.87, US
      * ``c_near_three`` point at (3, 0): 1 confirmed 388 m away, 0.95, US
      * ``c_mexico``     point at (5.5, 5.5): nothing nearby, 0.60, MX,
                         source 'other_source'
    """

    def setUp(self):
        caches[ORDER_CACHE_ALIAS].clear()
        self.addCleanup(caches[ORDER_CACHE_ALIAS].clear)
        post_delete.disconnect(
            location_post_delete_handler_for_opensearch, Facility
        )
        self.addCleanup(
            post_delete.connect,
            location_post_delete_handler_for_opensearch,
            Facility,
        )
        unittest.mock.patch(OPEN_SEARCH_SERVICE).start()
        # The anonymous burst throttle (100/minute per IP) is counted in
        # the shared memcached; this module alone makes most of that in a
        # second, so it is switched off here rather than letting the run
        # order of the candidate modules decide which test sees a 429.
        for throttle in ('BurstRateThrottle', 'SustainedRateThrottle'):
            unittest.mock.patch(
                f'api.throttles.{throttle}.allow_request', return_value=True
            ).start()
        self.addCleanup(unittest.mock.patch.stopall)

        self.user = User.objects.create(email='one@example.com')
        self.voters = [
            User.objects.create(email=f'voter{i}@example.com')
            for i in range(4)
        ]
        # Nearby sorts and filters need a login (see
        # candidate_listing.needs_whole_set_nearby); the anonymous cases
        # below log out explicitly.
        self.client.force_authenticate(user=self.voters[0])
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

        self.facility_zero = self._create_facility(
            self.list_source, name='Confirmed at zero'
        )
        self.facility_three = self._create_facility(
            self.list_source,
            name='Confirmed near three',
            location=Point(3 + NEAR_OFFSET_DEG, 0),
        )
        self.c_near_zero = self._create_candidate(
            'eg-0001',
            polygon=GEOSGeometry(
                'POLYGON((-0.01 -0.01, -0.01 0.01, 0.01 0.01, '
                '0.01 -0.01, -0.01 -0.01))',
                srid=4326,
            ),
            location=Point(0, 0),
            confidence=0.40,
        )
        self.c_alone = self._create_candidate(
            'eg-0002', polygon=None, location=Point(0.5, 0.5),
            confidence=0.87,
        )
        self.c_near_three = self._create_candidate(
            'eg-0003', polygon=None, location=Point(3, 0), confidence=0.95,
        )
        self.c_mexico = self._create_candidate(
            'eg-0004', polygon=None, location=Point(5.5, 5.5),
            confidence=0.60, country_code='MX', source='other_source',
        )
        # Distinct creation times, oldest first in the order above.
        base = self.c_near_zero.created_at
        for days, candidate in enumerate(self.candidates()):
            Facility.including_candidates.filter(pk=candidate.pk).update(
                created_at=base + timedelta(days=days)
            )

    # --- fixture helpers ----------------------------------------------

    def candidates(self):
        return [
            self.c_near_zero, self.c_alone, self.c_near_three, self.c_mexico
        ]

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
        defaults = dict(
            name='',
            address='',
            is_candidate=True,
            confidence=0.87,
            external_id=external_id,
            source='earth_genome',
        )
        defaults.update(kwargs)
        return self._create_facility(self.candidate_source, **defaults)

    def _make_disputed(self, candidate):
        for voter, vote in zip(self.voters, (NO, NO, YES, YES)):
            cast_vote(candidate, voter, vote)
        return {'confirmed': 2, 'not_a_facility': 2}

    def _make_confirmed(self, candidate):
        for voter, vote in zip(self.voters, (YES, YES, YES)):
            cast_vote(candidate, voter, vote)

    def _make_retirement_pending(self, candidate):
        for voter, vote in zip(self.voters, (NO, NO, NO)):
            cast_vote(candidate, voter, vote)

    def _get(self, **params):
        return self.client.get(URL, params)

    def _ids(self, response):
        self.assertEqual(
            status.HTTP_200_OK, response.status_code, response.data
        )
        return [f['id'] for f in response.data['features']]

    def _props(self, response):
        return {
            f['id']: f['properties'] for f in response.data['features']
        }

    # --- envelope -----------------------------------------------------

    def test_default_page_lists_every_candidate_by_id(self):
        response = self._get()

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('noindex', response['X-Robots-Tag'])
        self.assertIn('private', response['Cache-Control'])
        body = response.data
        self.assertEqual(
            ['type', 'count', 'next', 'previous', 'features'],
            list(body.keys()),
        )
        self.assertEqual('FeatureCollection', body['type'])
        self.assertEqual(4, body['count'])
        self.assertIsNone(body['next'])
        self.assertIsNone(body['previous'])
        self.assertEqual(
            sorted(c.id for c in self.candidates()),
            [f['id'] for f in body['features']],
        )

    def test_feature_shape(self):
        props = self._props(self._get())[self.c_near_three.id]

        self.assertEqual(
            {
                'os_id', 'confidence', 'source', 'state', 'tally',
                'centroid', 'nearby_count', 'nearest_m', 'nearest',
                'created_at', 'country_code', 'external_id',
            },
            set(props.keys()),
        )
        self.assertEqual(0.95, props['confidence'])
        self.assertEqual('earth_genome', props['source'])
        self.assertEqual(UNVERIFIED, props['state'])
        self.assertEqual(ZERO_TALLY, props['tally'])
        self.assertEqual({'lat': 0.0, 'lng': 3.0}, props['centroid'])
        self.assertEqual('US', props['country_code'])
        self.assertEqual('eg-0003', props['external_id'])
        self.assertTrue(props['created_at'].startswith('20'))
        self.assertEqual(1, props['nearby_count'])
        self.assertAlmostEqual(388, props['nearest_m'], delta=3)
        self.assertEqual(self.facility_three.id, props['nearest']['os_id'])
        self.assertEqual('Confirmed near three', props['nearest']['name'])
        self.assertEqual(props['nearest_m'], props['nearest']['distance_m'])

    def test_paging_envelope_and_links(self):
        page_one = self._get(limit=3, sort='confidence')
        self.assertEqual(3, len(page_one.data['features']))
        self.assertEqual(4, page_one.data['count'])
        self.assertIn('page=2', page_one.data['next'])
        self.assertIn('limit=3', page_one.data['next'])
        self.assertIn('sort=confidence', page_one.data['next'])
        self.assertIsNone(page_one.data['previous'])

        page_two = self._get(limit=3, sort='confidence', page=2)
        self.assertEqual(1, len(page_two.data['features']))
        self.assertIsNone(page_two.data['next'])
        # Back to page one keeps ``page``: it is the mode discriminator.
        self.assertIn('page=1', page_two.data['previous'])
        self.assertIn('limit=3', page_two.data['previous'])

        page_three = self._get(limit=3, page=3)
        self.assertEqual(status.HTTP_404_NOT_FOUND, page_three.status_code)
        self.assertEqual(
            'The requested page is past the last page.',
            page_three.data['detail'],
        )

    def test_empty_result_is_an_empty_first_page(self):
        response = self._get(country='ZZ')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, response.data['count'])
        self.assertEqual([], response.data['features'])

    def test_limit_is_clamped_to_the_cap(self):
        response = self._get(limit=9999)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(4, len(response.data['features']))

    # --- sorting ------------------------------------------------------

    def test_sort_by_confidence(self):
        self.assertEqual(
            [
                self.c_near_zero.id, self.c_mexico.id,
                self.c_alone.id, self.c_near_three.id,
            ],
            self._ids(self._get(sort='confidence')),
        )
        self.assertEqual(
            [
                self.c_near_three.id, self.c_alone.id,
                self.c_mexico.id, self.c_near_zero.id,
            ],
            self._ids(self._get(sort='-confidence')),
        )

    def test_sort_by_created_at(self):
        expected = [c.id for c in self.candidates()]
        self.assertEqual(expected, self._ids(self._get(sort='created_at')))
        self.assertEqual(
            list(reversed(expected)),
            self._ids(self._get(sort='-created_at')),
        )

    def test_sort_by_id_descending(self):
        self.assertEqual(
            sorted((c.id for c in self.candidates()), reverse=True),
            self._ids(self._get(sort='-id')),
        )

    def test_sort_by_nearby_count_puts_candidates_with_neighbours_first(self):
        response = self._get(sort='-nearby_count')

        ids = self._ids(response)
        self.assertEqual(
            sorted([self.c_near_zero.id, self.c_near_three.id]), ids[:2]
        )
        self.assertEqual(
            sorted([self.c_alone.id, self.c_mexico.id]), ids[2:]
        )
        props = self._props(response)
        self.assertEqual(1, props[self.c_near_three.id]['nearby_count'])
        self.assertAlmostEqual(
            388, props[self.c_near_three.id]['nearest_m'], delta=3
        )
        self.assertEqual(0, props[self.c_alone.id]['nearby_count'])
        self.assertIsNone(props[self.c_alone.id]['nearest_m'])
        self.assertIsNone(props[self.c_alone.id]['nearest'])

    def test_sort_by_nearest_distance_keeps_nulls_last(self):
        ids = self._ids(self._get(sort='nearest_m'))
        self.assertEqual(self.c_near_zero.id, ids[0])  # 0 m
        self.assertEqual(self.c_near_three.id, ids[1])  # 388 m
        self.assertEqual(sorted([self.c_alone.id, self.c_mexico.id]), ids[2:])

        ids = self._ids(self._get(sort='-nearest_m'))
        self.assertEqual(self.c_near_three.id, ids[0])
        self.assertEqual(self.c_near_zero.id, ids[1])
        self.assertEqual(sorted([self.c_alone.id, self.c_mexico.id]), ids[2:])

    def test_nearby_never_counts_another_candidate(self):
        # Two candidates on the same spot: neither counts the other.
        twin = self._create_candidate(
            'eg-0005', polygon=None, location=Point(0.5, 0.5)
        )
        props = self._props(self._get())
        self.assertEqual(0, props[self.c_alone.id]['nearby_count'])
        self.assertEqual(0, props[twin.id]['nearby_count'])

    # --- cached ordering ----------------------------------------------

    def test_nearby_ordering_is_cached_per_filter_set(self):
        first = self._get(sort='-nearby_count', limit=2)
        self.assertEqual(4, first.data['count'])

        # A candidate added after the first request is not in the cached
        # order until the window passes, but the plain sorts see it now.
        newcomer = self._create_candidate(
            'eg-0006', polygon=None, location=Point(3, 0.001)
        )
        cached = self._get(sort='-nearby_count', limit=2, page=2)
        self.assertEqual(4, cached.data['count'])
        self.assertNotIn(newcomer.id, self._ids(cached))
        self.assertIn(newcomer.id, self._ids(self._get(sort='confidence')))

        # Different filters are a different entry.
        other = self._get(sort='-nearby_count', has_nearby='true')
        self.assertEqual(3, other.data['count'])
        self.assertIn(newcomer.id, self._ids(other))

        caches[ORDER_CACHE_ALIAS].clear()
        fresh = self._get(sort='-nearby_count', limit=2)
        self.assertEqual(5, fresh.data['count'])

    def test_cached_page_rows_are_served_live(self):
        self._get(sort='-nearby_count')
        expected_tally = self._make_disputed(self.c_near_three)
        retire_candidate(
            self.c_mexico, {'confirmed': 0, 'not_a_facility': 3}
        )

        response = self._get(sort='-nearby_count')

        props = self._props(response)
        self.assertEqual(DISPUTED, props[self.c_near_three.id]['state'])
        self.assertEqual(expected_tally, props[self.c_near_three.id]['tally'])
        # The retired id is still counted by the cached order but the row
        # is gone, so it is simply absent from the page.
        self.assertNotIn(self.c_mexico.id, props)
        self.assertEqual(4, response.data['count'])

    def test_cached_order_does_not_serve_a_row_that_left_the_set(self):
        self._get(sort='-nearby_count')
        self._get(sort='-nearby_count', country='MX')

        # Promoted out of candidacy, and moved out of a country filter.
        Facility.including_candidates.filter(id=self.c_near_three.id).update(
            is_candidate=False
        )
        Facility.including_candidates.filter(id=self.c_mexico.id).update(
            country_code='US'
        )

        response = self._get(sort='-nearby_count')
        self.assertNotIn(self.c_near_three.id, self._ids(response))
        by_country = self._get(sort='-nearby_count', country='MX')
        self.assertNotIn(self.c_mexico.id, self._ids(by_country))

    def test_order_cache_key_changes_with_the_settings_it_depends_on(self):
        params = {'sort': '-nearby_count', 'page': 1, 'limit': 50}
        with override_settings(CANDIDATE_SUGGESTION_RADIUS_M=500):
            before = _order_cache_key(params)
        with override_settings(CANDIDATE_SUGGESTION_RADIUS_M=1000):
            after = _order_cache_key(params)
        with override_settings(CANDIDATE_VOTE_THRESHOLD=9):
            threshold = _order_cache_key(params)

        self.assertNotEqual(before, after)
        self.assertNotEqual(before, threshold)
        self.assertNotEqual(after, threshold)

    @override_settings(CANDIDATE_LIST_ORDER_CACHE_SECONDS=0)
    def test_order_cache_can_be_disabled(self):
        self._get(sort='-nearby_count')
        newcomer = self._create_candidate(
            'eg-0006', polygon=None, location=Point(7, 7)
        )

        self.assertIn(newcomer.id, self._ids(self._get(sort='-nearby_count')))

    def test_nearby_sorted_page_past_the_end_is_404(self):
        response = self._get(sort='-nearby_count', limit=3, page=3)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    # --- filters ------------------------------------------------------

    def test_filter_by_confidence_range(self):
        self.assertEqual(
            sorted([self.c_mexico.id, self.c_alone.id]),
            self._ids(self._get(confidence_min=0.5, confidence_max=0.9)),
        )
        self.assertEqual(
            [self.c_near_zero.id],
            self._ids(self._get(confidence_max=0.4)),
        )

    def test_filter_by_country_and_source(self):
        self.assertEqual(
            [self.c_mexico.id], self._ids(self._get(country='mx'))
        )
        self.assertEqual(
            4, len(self._ids(self._get(country='US,MX')))
        )
        self.assertEqual(
            [self.c_mexico.id], self._ids(self._get(source='other_source'))
        )

    def test_filter_by_bbox_is_not_capped_in_list_mode(self):
        # 6 degrees wide would be refused by the map mode; ``page``
        # selects the list.
        response = self._get(bbox='-1,-1,5,1', sort='confidence', page=1)

        self.assertEqual(
            [self.c_near_zero.id, self.c_alone.id, self.c_near_three.id],
            self._ids(response),
        )
        self.assertEqual(3, response.data['count'])

    def test_filter_by_has_nearby(self):
        self.assertEqual(
            sorted([self.c_near_zero.id, self.c_near_three.id]),
            self._ids(self._get(has_nearby='true')),
        )
        self.assertEqual(
            sorted([self.c_alone.id, self.c_mexico.id]),
            self._ids(self._get(has_nearby='false')),
        )

    def test_filter_by_state_matches_the_detail_endpoint(self):
        self._make_disputed(self.c_alone)
        self._make_confirmed(self.c_mexico)
        self._make_retirement_pending(self.c_near_three)

        expectations = {
            UNVERIFIED: [self.c_near_zero.id],
            DISPUTED: [self.c_alone.id],
            CONFIRMED: [self.c_mexico.id],
            RETIREMENT_PENDING: [self.c_near_three.id],
        }
        for state, expected in expectations.items():
            with self.subTest(state):
                response = self._get(state=state)
                self.assertEqual(expected, self._ids(response))
                props = self._props(response)[expected[0]]
                self.assertEqual(state, props['state'])
                detail = self.client.get(
                    f'/api/v1/production-locations/{expected[0]}/'
                )
                self.assertEqual(
                    detail.data['validation']['state'], props['state']
                )
                self.assertEqual(
                    detail.data['validation']['tally'], props['tally']
                )

        self.assertEqual(
            sorted([self.c_alone.id, self.c_near_zero.id]),
            self._ids(self._get(state=f'{UNVERIFIED},{DISPUTED}')),
        )

    def test_unverified_filter_keeps_candidates_below_the_threshold(self):
        # One vote is not enough to leave "unverified".
        cast_vote(self.c_alone, self.voters[0], NO)

        self.assertEqual(
            4, len(self._ids(self._get(state=UNVERIFIED)))
        )

    # --- exclusions ---------------------------------------------------

    def test_confirmed_facilities_and_retired_candidates_never_appear(self):
        retire_candidate(
            self.c_mexico, {'confirmed': 0, 'not_a_facility': 3}
        )

        ids = set(self._ids(self._get(limit=500)))

        self.assertNotIn(self.facility_zero.id, ids)
        self.assertNotIn(self.facility_three.id, ids)
        self.assertNotIn(self.c_mexico.id, ids)
        self.assertEqual(3, len(ids))

    # --- validation ---------------------------------------------------

    def test_bad_parameters_are_400(self):
        cases = {
            'sort': {'sort': 'name'},
            'state': {'state': 'unverified,retired'},
            'confidence_min': {'confidence_min': '1.5'},
            'confidence_min order': {
                'confidence_min': '0.9', 'confidence_max': '0.1'
            },
            'page': {'page': '0'},
            'limit': {'limit': 'abc'},
            'country': {'country': 'USA'},
            'bbox': {'bbox': '1,1,0,0', 'page': '1'},
            'has_nearby': {'has_nearby': 'maybe'},
        }
        for label, params in cases.items():
            with self.subTest(label):
                response = self._get(**params)
                self.assertEqual(
                    status.HTTP_400_BAD_REQUEST, response.status_code
                )
                self.assertEqual(
                    'The request query is invalid.', response.data['detail']
                )
                self.assertEqual(
                    label.split()[0], response.data['errors'][0]['field']
                )
                self.assertTrue(response.data['errors'][0]['detail'])

    def test_previous_link_of_a_wide_bbox_list_stays_in_list_mode(self):
        # 6 degrees wide: the map mode would refuse it, so a ``previous``
        # that dropped ``page`` would turn page 1 into a 400.
        page_two = self._get(bbox='-1,-1,5,1', page=2, limit=2)
        self.assertEqual(status.HTTP_200_OK, page_two.status_code)

        previous = page_two.data['previous']
        self.assertIn('page=1', previous)
        page_one = self.client.get(previous)
        self.assertEqual(status.HTTP_200_OK, page_one.status_code)
        self.assertEqual(3, page_one.data['count'])
        self.assertEqual(2, len(page_one.data['features']))

    def test_page_selects_list_mode_for_a_bbox_request(self):
        # ``page`` is the discriminator: bbox with it is the list.
        response = self._get(bbox='-1,-1,1,1', page=1)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('count', response.data)
        self.assertEqual(2, response.data['count'])

    def test_bbox_without_page_is_map_mode_whatever_else_it_carries(self):
        # A map caller that adds an unrelated parameter keeps its
        # contract: no envelope, and the list's sort is not applied.
        response = self._get(bbox='-1,-1,1,1', sort='-confidence', _='1')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertNotIn('count', response.data)
        self.assertCountEqual(
            [self.c_near_zero.id, self.c_alone.id], self._ids(response)
        )

    def test_anonymous_and_authenticated_see_the_same_list(self):
        authenticated = self._get(sort='confidence', country='US')
        self.client.force_authenticate(user=None)
        anonymous = self._get(sort='confidence', country='US')

        self.assertEqual(authenticated.data, anonymous.data)

    def test_nearby_sorts_and_filters_need_a_login(self):
        self.client.force_authenticate(user=None)
        for params in (
            {'sort': '-nearby_count'},
            {'sort': 'nearest_m'},
            {'has_nearby': 'true'},
        ):
            with self.subTest(params=params):
                response = self._get(**params)
                self.assertEqual(
                    status.HTTP_401_UNAUTHORIZED, response.status_code
                )
                self.assertEqual(
                    'Log in to sort or filter candidates by nearby '
                    'facilities.',
                    response.data['detail'],
                )
        # The plain list, and the page-level nearby figures, stay open.
        plain = self._get(sort='confidence')
        self.assertEqual(status.HTTP_200_OK, plain.status_code)
        self.assertIn('nearby_count', plain.data['features'][0]['properties'])

    def test_logs_when_the_order_does_not_fit_in_the_cache(self):
        cache = caches[ORDER_CACHE_ALIAS]
        with unittest.mock.patch.object(cache, 'set'), self.assertLogs(
            'api.services.candidate_listing', level='WARNING'
        ) as logs:
            response = self._get(sort='-nearby_count')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(4, response.data['count'])
        self.assertIn('was not cached', logs.output[0])
