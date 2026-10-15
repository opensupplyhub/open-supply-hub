from django.contrib.gis.geos import GEOSGeometry, Point
from django.db.models.signals import post_delete
from django.test import SimpleTestCase, override_settings
from rest_framework import status
from rest_framework.test import APITestCase

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
from api.services.candidate_retirement import RETIRED_DETAIL
from api.services.candidate_validation import (
    CONFIRMED,
    DISPUTED,
    RETIRED,
    RETIREMENT_PENDING,
    UNVERIFIED,
    derive_state,
    public_state,
)
from api.signals import location_post_delete_handler_for_opensearch

CANDIDATE_POLYGON_WKT = 'POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))'
YES = FacilityCandidateVote.Vote.CONFIRMED.value
NO = FacilityCandidateVote.Vote.NOT_A_FACILITY.value

# The pilot defaults from oar/settings.py, pinned so the tests below do
# not drift with a local .env.
PILOT_THRESHOLDS = dict(
    CANDIDATE_VOTE_THRESHOLD=3,
    CANDIDATE_CONFIRM_MARGIN=0.6,
    CANDIDATE_RETIRE_MARGIN=0.75,
    CANDIDATE_AUTO_RETIRE=False,
)


class DeriveStateTest(SimpleTestCase):
    """
    OSDEV-3245 / D6: the pure tally -> state function, no database.
    """

    def test_table(self):
        knobs = dict(threshold=3, confirm_margin=0.6, retire_margin=0.75)
        cases = [
            # (confirmed, not_a_facility, expected)
            (0, 0, UNVERIFIED),
            (1, 0, UNVERIFIED),
            (2, 0, UNVERIFIED),
            (1, 1, UNVERIFIED),
            (3, 0, CONFIRMED),
            (2, 1, CONFIRMED),       # 0.667 >= 0.6
            (1, 2, DISPUTED),        # 0.667 < 0.75: no consensus either way
            (2, 2, DISPUTED),
            (0, 3, RETIRED),
            (1, 3, RETIRED),         # 0.75 >= 0.75
            (2, 3, DISPUTED),        # 0.6 < 0.75 and 0.4 < 0.6
            (3, 2, CONFIRMED),       # 0.6 >= 0.6
            (10, 40, RETIRED),
            (40, 10, CONFIRMED),
        ]
        for confirmed, not_a_facility, expected in cases:
            with self.subTest(yes=confirmed, no=not_a_facility):
                self.assertEqual(
                    expected,
                    derive_state(
                        {'confirmed': confirmed,
                         'not_a_facility': not_a_facility},
                        **knobs,
                    ),
                )

    def test_threshold_and_margins_are_knobs(self):
        self.assertEqual(
            CONFIRMED,
            derive_state({'confirmed': 1, 'not_a_facility': 0},
                         threshold=1, confirm_margin=0.6, retire_margin=0.75),
        )
        self.assertEqual(
            RETIRED,
            derive_state({'confirmed': 1, 'not_a_facility': 1},
                         threshold=2, confirm_margin=0.9, retire_margin=0.5),
        )
        # Both margins reachable at once is a misconfiguration: no consensus.
        self.assertEqual(
            DISPUTED,
            derive_state({'confirmed': 1, 'not_a_facility': 1},
                         threshold=2, confirm_margin=0.5, retire_margin=0.5),
        )

    def test_missing_keys_count_as_zero(self):
        self.assertEqual(
            UNVERIFIED,
            derive_state({}, threshold=3, confirm_margin=0.6,
                         retire_margin=0.75),
        )

    @override_settings(**PILOT_THRESHOLDS)
    def test_defaults_come_from_settings(self):
        self.assertEqual(
            RETIRED, derive_state({'confirmed': 0, 'not_a_facility': 3})
        )
        self.assertEqual(
            CONFIRMED, derive_state({'confirmed': 3, 'not_a_facility': 0})
        )

    def test_public_state_labels_the_gated_edge(self):
        self.assertEqual(RETIREMENT_PENDING, public_state(RETIRED))
        self.assertEqual(RETIRED, public_state(RETIRED, retired=True))
        for state in (UNVERIFIED, DISPUTED, CONFIRMED):
            self.assertEqual(state, public_state(state))


@override_settings(**PILOT_THRESHOLDS)
class CandidateVotesApiTest(APITestCase):
    """
    OSDEV-3245: ``/api/v1/production-locations/{os_id}/candidate-votes/``
    and the moderator gate at ``/api/v1/candidate-retirement-requests/``.

    Fixture mirrors test_candidate_retirement: one confirmed facility and
    one candidate with the synthetic Source -> item -> match graph.
    """

    def setUp(self):
        post_delete.disconnect(
            location_post_delete_handler_for_opensearch, Facility
        )

        self.user = User.objects.create(email='one@example.com')
        self.user.set_password('example123')
        self.user.save()
        self.voters = [
            User.objects.create(email=f'voter{i}@example.com')
            for i in range(5)
        ]
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
        self._create_match(self.facility)

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
        self._create_match(self.candidate)
        self.url = self._votes_url(self.candidate.id)

    def tearDown(self):
        post_delete.connect(
            location_post_delete_handler_for_opensearch, Facility
        )

    # --- fixture helpers ----------------------------------------------

    @staticmethod
    def _votes_url(os_id):
        return f'/api/v1/production-locations/{os_id}/candidate-votes/'

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

    def _vote(self, user, vote, os_id=None):
        self.client.force_authenticate(user=user)
        response = self.client.post(
            self._votes_url(os_id or self.candidate.id),
            {'vote': vote},
            format='json',
        )
        self.client.force_authenticate(user=None)
        return response

    def _votes(self):
        return FacilityCandidateVote.objects.filter(facility=self.candidate)

    # --- AC 1: one row per user per candidate, change in place ---------

    def test_first_vote_creates_then_changes_in_place(self):
        response = self._vote(self.user, YES)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(
            {
                'os_id': self.candidate.id,
                'your_vote': YES,
                'tally': {'confirmed': 1, 'not_a_facility': 0},
                'state': UNVERIFIED,
            },
            response.data,
        )
        self.assertEqual(1, self._votes().count())

        response = self._vote(self.user, NO)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(NO, response.data['your_vote'])
        self.assertEqual(
            {'confirmed': 0, 'not_a_facility': 1}, response.data['tally']
        )
        self.assertEqual(1, self._votes().count())
        self.assertEqual(NO, self._votes().get().vote)

        # A repeat of the same vote is a harmless 200.
        response = self._vote(self.user, NO)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, self._votes().count())

    def test_each_user_has_their_own_row(self):
        self._vote(self.voters[0], YES)
        self._vote(self.voters[1], NO)

        self.assertEqual(2, self._votes().count())
        self.assertEqual(
            {'confirmed': 1, 'not_a_facility': 1},
            self.client.get(self.url).data['tally'],
        )

    def test_invalid_vote_is_400_and_writes_nothing(self):
        response = self._vote(self.user, 'maybe')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual('vote', response.data['errors'][0]['field'])
        self.assertEqual(0, self._votes().count())

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(0, self._votes().count())

    # --- AC 2: unauthenticated POST is 401, no row ----------------------

    def test_unauthenticated_post_is_401_and_writes_nothing(self):
        response = self.client.post(self.url, {'vote': YES}, format='json')

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual(0, FacilityCandidateVote.objects.count())

    # --- GET is open ----------------------------------------------------

    def test_get_is_open_and_shows_callers_vote_when_authenticated(self):
        self._vote(self.user, YES)

        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            {
                'os_id': self.candidate.id,
                'your_vote': None,
                'tally': {'confirmed': 1, 'not_a_facility': 0},
                'state': UNVERIFIED,
            },
            response.data,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(YES, response.data['your_vote'])

        self.client.force_authenticate(user=self.voters[0])
        response = self.client.get(self.url)
        self.assertIsNone(response.data['your_vote'])

    # --- 404 / 410 ------------------------------------------------------

    def test_non_candidate_is_404(self):
        for method in (self.client.get, self.client.post):
            self.client.force_authenticate(user=self.user)
            response = method(
                self._votes_url(self.facility.id), {'vote': YES},
                format='json',
            )
            self.assertEqual(
                status.HTTP_404_NOT_FOUND, response.status_code, method
            )
        self.assertEqual(0, FacilityCandidateVote.objects.count())

    def test_unknown_os_id_is_404(self):
        response = self.client.get(self._votes_url('US1234567ABCDEF'))
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_retired_os_id_is_410(self):
        os_id = self.candidate.id
        with override_settings(CANDIDATE_AUTO_RETIRE=True):
            for voter in self.voters[:3]:
                self._vote(voter, NO)
        self.assertFalse(
            Facility.including_candidates.filter(id=os_id).exists()
        )

        response = self.client.get(self._votes_url(os_id))
        self.assertEqual(status.HTTP_410_GONE, response.status_code)
        self.assertEqual(RETIRED_DETAIL, response.data['detail'])

        response = self._vote(self.user, YES, os_id=os_id)
        self.assertEqual(status.HTTP_410_GONE, response.status_code)

    # --- AC 4: split at threshold is disputed, visible, still voting ---

    def test_split_at_threshold_is_disputed_and_still_accepts_votes(self):
        self._vote(self.voters[0], YES)
        self._vote(self.voters[1], NO)
        response = self._vote(self.voters[2], NO)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(DISPUTED, response.data['state'])
        self.assertEqual(
            {'confirmed': 1, 'not_a_facility': 2}, response.data['tally']
        )
        self.assertTrue(
            Facility.including_candidates.filter(
                id=self.candidate.id
            ).exists()
        )
        self.assertFalse(FacilityCandidateRetirementRequest.objects.exists())

        # Still open: a fourth vote lands and can move the state.
        response = self._vote(self.voters[3], YES)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(DISPUTED, response.data['state'])
        response = self._vote(self.voters[4], YES)
        self.assertEqual(CONFIRMED, response.data['state'])

    # --- 409: confirmed closes voting -----------------------------------

    def test_confirmed_closes_voting_with_409(self):
        for voter in self.voters[:3]:
            response = self._vote(voter, YES)
        self.assertEqual(CONFIRMED, response.data['state'])

        response = self._vote(self.user, NO)

        self.assertEqual(status.HTTP_409_CONFLICT, response.status_code)
        self.assertEqual(3, self._votes().count())
        # Changing an existing vote is closed too.
        response = self._vote(self.voters[0], NO)
        self.assertEqual(status.HTTP_409_CONFLICT, response.status_code)
        self.assertEqual(YES, self._votes().get(user=self.voters[0]).vote)
        # GET still answers.
        self.assertEqual(CONFIRMED, self.client.get(self.url).data['state'])

    # --- AC 3: consensus-no, gated (default) ----------------------------

    def test_consensus_no_with_gate_opens_request_and_keeps_facility(self):
        self._vote(self.voters[0], NO)
        self._vote(self.voters[1], NO)
        response = self._vote(self.voters[2], NO)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(RETIREMENT_PENDING, response.data['state'])
        self.assertTrue(
            Facility.including_candidates.filter(
                id=self.candidate.id
            ).exists()
        )
        self.assertFalse(
            FacilityAlias.objects.filter(os_id=self.candidate.id).exists()
        )
        request = FacilityCandidateRetirementRequest.objects.get()
        self.assertEqual(self.candidate.id, request.facility_id)
        self.assertEqual(
            {'confirmed': 0, 'not_a_facility': 3}, request.tally
        )
        self.assertEqual(
            RETIREMENT_PENDING, self.client.get(self.url).data['state']
        )

    def test_gated_request_is_one_per_candidate_and_refreshes_tally(self):
        for voter in self.voters[:3]:
            self._vote(voter, NO)
        first = FacilityCandidateRetirementRequest.objects.get()

        self._vote(self.voters[3], NO)

        self.assertEqual(1, FacilityCandidateRetirementRequest.objects.count())
        refreshed = FacilityCandidateRetirementRequest.objects.get()
        self.assertEqual(first.id, refreshed.id)
        self.assertEqual(
            {'confirmed': 0, 'not_a_facility': 4}, refreshed.tally
        )

    def test_gated_request_dissolves_when_consensus_breaks(self):
        for voter in self.voters[:3]:
            self._vote(voter, NO)
        self.assertTrue(FacilityCandidateRetirementRequest.objects.exists())

        # 3 no / 1 yes is exactly the 0.75 margin: still pending.
        response = self._vote(self.voters[3], YES)
        self.assertEqual(RETIREMENT_PENDING, response.data['state'])
        self.assertTrue(FacilityCandidateRetirementRequest.objects.exists())

        # 3 no / 2 yes: disputed, nothing left to retire.
        response = self._vote(self.voters[4], YES)
        self.assertEqual(DISPUTED, response.data['state'])
        self.assertFalse(FacilityCandidateRetirementRequest.objects.exists())

    # --- AC 3: consensus-no, auto-retire --------------------------------

    @override_settings(CANDIDATE_AUTO_RETIRE=True)
    def test_consensus_no_with_auto_retire_retires_and_tombstones(self):
        os_id = self.candidate.id
        self._vote(self.voters[0], YES)
        self._vote(self.voters[1], NO)
        response = self._vote(self.voters[2], NO)
        # 1 yes / 2 no is disputed (0.667 < 0.75): nothing retired yet.
        self.assertEqual(DISPUTED, response.data['state'])
        self.assertTrue(
            Facility.including_candidates.filter(id=os_id).exists()
        )

        # 1 yes / 3 no is exactly the 0.75 margin: consensus-no.
        response = self._vote(self.voters[3], NO)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(
            {
                'os_id': os_id,
                'your_vote': NO,
                'tally': {'confirmed': 1, 'not_a_facility': 3},
                'state': RETIRED,
            },
            response.data,
        )
        self.assertFalse(
            Facility.including_candidates.filter(id=os_id).exists()
        )
        # Votes cascade away with the row; the tombstone keeps the tally.
        self.assertFalse(
            FacilityCandidateVote.objects.filter(facility_id=os_id).exists()
        )
        self.assertFalse(FacilityCandidateRetirementRequest.objects.exists())
        tombstone = FacilityAlias.objects.get(os_id=os_id)
        self.assertEqual(FacilityAlias.NOT_A_FACILITY, tombstone.reason)
        self.assertIsNone(tombstone.facility)
        self.assertEqual(1, tombstone.retirement_tally['confirmed'])
        self.assertEqual(3, tombstone.retirement_tally['not_a_facility'])
        self.assertEqual(
            self.voters[3].id, tombstone.retirement_tally['retired_by']
        )
        # The confirmed facility is untouched.
        self.assertTrue(Facility.objects.filter(id=self.facility.id).exists())

    # --- Moderator path -------------------------------------------------

    def test_retirement_requests_are_moderator_only(self):
        for voter in self.voters[:3]:
            self._vote(voter, NO)
        request = FacilityCandidateRetirementRequest.objects.get()
        list_url = '/api/v1/candidate-retirement-requests/'
        approve_url = f'{list_url}{request.id}/approve/'

        response = self.client.get(list_url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

        self.client.force_authenticate(user=self.user)
        self.assertEqual(
            status.HTTP_403_FORBIDDEN, self.client.get(list_url).status_code
        )
        self.assertEqual(
            status.HTTP_403_FORBIDDEN,
            self.client.post(approve_url).status_code,
        )
        self.assertTrue(
            Facility.including_candidates.filter(
                id=self.candidate.id
            ).exists()
        )

    def test_moderator_lists_and_approves_a_request(self):
        os_id = self.candidate.id
        for voter in self.voters[:3]:
            self._vote(voter, NO)
        request = FacilityCandidateRetirementRequest.objects.get()
        list_url = '/api/v1/candidate-retirement-requests/'
        approve_url = f'{list_url}{request.id}/approve/'
        self.client.force_authenticate(user=self.superuser)

        response = self.client.get(list_url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))
        self.assertEqual(request.id, response.data[0]['id'])
        self.assertEqual(os_id, response.data[0]['os_id'])
        self.assertEqual(
            {'confirmed': 0, 'not_a_facility': 3}, response.data[0]['tally']
        )

        response = self.client.post(approve_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(os_id, response.data['os_id'])
        self.assertEqual(RETIRED, response.data['state'])
        self.assertEqual(3, response.data['tally']['not_a_facility'])
        self.assertFalse(
            Facility.including_candidates.filter(id=os_id).exists()
        )
        self.assertFalse(FacilityCandidateRetirementRequest.objects.exists())
        self.assertFalse(
            FacilityCandidateVote.objects.filter(facility_id=os_id).exists()
        )
        tombstone = FacilityAlias.objects.get(os_id=os_id)
        self.assertEqual(FacilityAlias.NOT_A_FACILITY, tombstone.reason)
        self.assertEqual(
            self.superuser.id, tombstone.retirement_tally['retired_by']
        )
        self.assertEqual([], self.client.get(list_url).data)

        # Approving twice is a 404, and the OS ID is now 410 for voters.
        self.assertEqual(
            status.HTTP_404_NOT_FOUND,
            self.client.post(approve_url).status_code,
        )
        self.assertEqual(
            status.HTTP_410_GONE,
            self.client.get(self._votes_url(os_id)).status_code,
        )
