"""
OSDEV-3376: proof that the candidate-excluding default manager
(``Facility.objects``, OSDEV-3380) covers every ORM-backed read surface.

Every test here creates one confirmed facility and one candidate and
asserts that the surface behaves exactly as it would in a database with
no candidate at all: the candidate is not counted, not listed, and its OS
ID is treated like an OS ID that does not exist.

Surfaces that read ``FacilityIndex`` (``/api/facilities/`` list and
detail, downloads, tiles, sectors, parent companies) are NOT tested here:
they are covered by OSDEV-3243 (index trigger) and OSDEV-3378 (index
surfaces). Note that with the trigger as it stands today a candidate does
get an index row, so those surfaces still show it until that work lands.
"""
import json
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import Mock, patch

from allauth.account.models import EmailAddress
from django.contrib.gis.geos import GEOSGeometry, Point
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.exceptions import NotFound
from rest_framework.test import APITestCase
from waffle.testutils import override_flag, override_switch

from api.constants import (
    APIV1CommonErrorMessages,
    FacilityClaimStatuses,
    FeatureGroups,
)
from api.models import (
    Contributor,
    Facility,
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    ModerationEvent,
    Source,
    User,
)
from api.os_id_lookup import OSIDLookup
from api.partner_data_file_upload.processing.event_creator import (
    PartnerPatchModerationEventCreator,
)
from api.partner_fields.wage_indicator_provider import WageIndicatorProvider
from api.serializers import FacilityMergeQueryParamsSerializer
from api.serializers.user.user_serializer import UserSerializer
from api.services.moderation_events_service import ModerationEventsService
from api.services.production_locations_lookup import fetch_required_fields
from api.tests.base_moderation_events_production_location_test import (
    BaseModerationEventsProductionLocationTest,
)
from api.views.v1.production_locations import ProductionLocations

CANDIDATE_POLYGON_WKT = 'POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))'
MISSING_OS_ID = 'US0000000000000'


class CandidateFixtureMixin:
    """One confirmed facility, one candidate, both from the same source.

    Mirrors the fixture in api/tests/test_facility_default_manager.py.
    """

    def create_fixture(self):
        self.user_email = 'test@example.com'
        self.user_password = 'example123'
        self.user = User.objects.create(email=self.user_email)
        self.user.set_password(self.user_password)
        self.user.save()
        EmailAddress.objects.create(
            user=self.user, email=self.user_email, verified=True, primary=True
        )

        self.superuser_email = 'super@example.com'
        self.superuser_password = 'example123'
        self.superuser = User.objects.create_superuser(
            email=self.superuser_email, password=self.superuser_password
        )

        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='test contributor 1',
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
        self.source = Source.objects.create(
            facility_list=self.list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        self.next_row_index = 0

        self.facility = self.create_facility(name='Confirmed')
        self.match = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility,
            facility_list_item=self.facility.created_from,
            confidence=0.85,
            results={},
        )
        self.candidate = self.create_candidate()

    def create_list_item(self):
        self.next_row_index += 1
        return FacilityListItem.objects.create(
            name='Item',
            address='Address',
            country_code='US',
            sector=['Apparel'],
            row_index=self.next_row_index,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )

    def create_facility(self, **kwargs):
        defaults = {
            'name': 'Name',
            'address': 'Address',
            'country_code': 'US',
            'location': Point(0, 0),
            'created_from': self.create_list_item(),
        }
        defaults.update(kwargs)
        return Facility.including_candidates.create(**defaults)

    def create_candidate(self, **kwargs):
        defaults = {
            'name': '',
            'address': '',
            'is_candidate': True,
            'polygon': GEOSGeometry(CANDIDATE_POLYGON_WKT, srid=4326),
            'confidence': 0.87,
            'external_id': 'eg-facility-0001',
            'source': 'earth_genome',
        }
        defaults.update(kwargs)
        return self.create_facility(**defaults)

    def login_as_user(self):
        self.client.login(
            email=self.user_email, password=self.user_password
        )

    def login_as_superuser(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )


class FacilityEndpointsCandidateAuditTest(CandidateFixtureMixin, APITestCase):
    """/api/facilities/ actions that read Facility.objects directly."""

    def setUp(self):
        self.create_fixture()

    def test_count_excludes_candidate(self):
        response = self.client.get('/api/facilities/count/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def assert_candidate_behaves_like_missing_os_id(self, request):
        """`request(os_id)` must answer the same for a candidate as for an
        OS ID that was never issued."""
        candidate_response = request(self.candidate.id)
        missing_response = request(MISSING_OS_ID)

        self.assertEqual(candidate_response.status_code, 404)
        self.assertEqual(
            candidate_response.status_code, missing_response.status_code
        )
        # Some messages echo the OS ID; normalise it before comparing.
        self.assertEqual(
            str(candidate_response.data).replace(self.candidate.id, '{id}'),
            str(missing_response.data).replace(MISSING_OS_ID, '{id}'),
        )

    def test_superuser_actions_404_on_candidate(self):
        self.login_as_superuser()
        requests = {
            'destroy': lambda os_id: self.client.delete(
                f'/api/facilities/{os_id}/'
            ),
            'split (GET)': lambda os_id: self.client.get(
                f'/api/facilities/{os_id}/split/'
            ),
            'update-location': lambda os_id: self.client.post(
                f'/api/facilities/{os_id}/update-location/',
                {'lat': 1, 'lng': 1},
            ),
            'promote': lambda os_id: self.client.post(
                f'/api/facilities/{os_id}/promote/',
                {'match_id': self.match.id},
            ),
            'move': lambda os_id: self.client.post(
                f'/api/facilities/{os_id}/move/',
                {'match_id': self.match.id},
            ),
            'link': lambda os_id: self.client.post(
                f'/api/facilities/{os_id}/link/',
                {'new_os_id': self.facility.id},
            ),
        }

        for name, request in requests.items():
            with self.subTest(action=name):
                self.assert_candidate_behaves_like_missing_os_id(request)

    def test_link_rejects_candidate_as_new_os_id(self):
        self.login_as_superuser()

        response = self.client.post(
            f'/api/facilities/{self.facility.id}/link/',
            {'new_os_id': self.candidate.id},
        )

        self.assertEqual(response.status_code, 400)
        self.facility.refresh_from_db()
        self.assertIsNone(self.facility.new_os_id)

    def test_registered_user_actions_404_on_candidate(self):
        self.login_as_user()
        requests = {
            'report': lambda os_id: self.client.post(
                f'/api/facilities/{os_id}/report/',
                {'closure_state': 'CLOSED', 'reason_for_report': 'closed'},
            ),
            'dissociate': lambda os_id: self.client.post(
                f'/api/facilities/{os_id}/dissociate/'
            ),
        }

        for name, request in requests.items():
            with self.subTest(action=name):
                self.assert_candidate_behaves_like_missing_os_id(request)

    def test_merge_params_reject_candidate(self):
        for params in (
            {'target': self.facility.id, 'merge': self.candidate.id},
            {'target': self.candidate.id, 'merge': self.facility.id},
        ):
            with self.subTest(params=params):
                serializer = FacilityMergeQueryParamsSerializer(data=params)

                self.assertFalse(serializer.is_valid())

        serializer = FacilityMergeQueryParamsSerializer(
            data={'target': self.facility.id, 'merge': self.facility.id}
        )
        self.assertTrue(serializer.is_valid())

    @override_flag(FeatureGroups.CAN_GET_FACILITY_HISTORY, active=True)
    def test_history_404s_on_candidate(self):
        """Facility.history is not Facility.objects; the view hides
        candidates itself."""
        self.login_as_superuser()
        self.assertEqual(
            Facility.history.filter(id=self.candidate.id).count(), 1
        )

        self.assert_candidate_behaves_like_missing_os_id(
            lambda os_id: self.client.get(
                f'/api/facilities/{os_id}/history/'
            )
        )
        self.assertEqual(
            self.client.get(
                f'/api/facilities/{self.facility.id}/history/'
            ).status_code,
            200,
        )

    def test_tile_cache_key_ignores_candidate_updates(self):
        Facility.including_candidates.filter(pk=self.candidate.id).update(
            updated_at=timezone.now() + timedelta(days=1)
        )
        self.facility.refresh_from_db()
        expected = str(int(self.facility.updated_at.timestamp()))

        key = Facility.current_tile_cache_key()

        self.assertEqual(key.split('-')[0], expected)


class ClaimsCandidateAuditTest(CandidateFixtureMixin, APITestCase):
    """Claim creation reads Facility.objects, so a candidate can never
    acquire a claim; every claim listing that joins through
    FacilityClaim.facility is therefore candidate-free by construction."""

    def setUp(self):
        self.create_fixture()
        self.login_as_user()

    @override_switch('claim_a_facility', active=True)
    def test_claim_on_candidate_404s_and_creates_nothing(self):
        for os_id in (self.candidate.id, MISSING_OS_ID):
            with self.subTest(os_id=os_id):
                response = self.client.post(
                    f'/api/facilities/{os_id}/claim/',
                    {'your_name': 'Name', 'your_title': 'Title'},
                )

                self.assertEqual(response.status_code, 404)
                self.assertEqual(
                    response.data['detail'], 'Facility not found.'
                )

        self.assertFalse(
            FacilityClaim.objects.filter(facility=self.candidate).exists()
        )

    @override_switch('claim_a_facility', active=True)
    def test_claimed_listings_only_see_confirmed_claims(self):
        FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            status=FacilityClaimStatuses.APPROVED,
        )

        response = self.client.get('/api/facilities/claimed/')
        claimed_ids = UserSerializer().get_claimed_facility_ids(self.user)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [claim['os_id'] for claim in response.data], [self.facility.id]
        )
        self.assertEqual(list(claimed_ids['approved']), [self.facility.id])
        self.assertEqual(list(claimed_ids['pending']), [])


class V1ProductionLocationsCandidateAuditTest(
    CandidateFixtureMixin, APITestCase
):
    """v1 production-locations paths that go through Facility.objects."""

    def setUp(self):
        self.create_fixture()
        self.login_as_user()

    def test_patch_on_candidate_404s_before_creating_an_event(self):
        for os_id in (self.candidate.id, MISSING_OS_ID):
            with self.subTest(os_id=os_id):
                response = self.client.patch(
                    f'/api/v1/production-locations/{os_id}/',
                    json.dumps({'name': 'New name'}),
                    content_type='application/json',
                )

                self.assertEqual(response.status_code, 404)
                self.assertEqual(
                    response.data,
                    {'detail': APIV1CommonErrorMessages.LOCATION_NOT_FOUND},
                )

        self.assertFalse(ModerationEvent.objects.exists())

    def test_fetch_required_fields_does_not_see_candidate(self):
        """SLC backfill helper; only reachable after the PATCH 404 above,
        and on its own it cannot resolve a candidate either."""
        self.assertEqual(
            fetch_required_fields(self.facility.id)['name'], 'Confirmed'
        )

        with self.assertRaises(Facility.DoesNotExist):
            fetch_required_fields(self.candidate.id)

    def test_partner_field_providers_are_not_run_for_candidate(self):
        partner_field = SimpleNamespace(
            name=WageIndicatorProvider()._get_field_name(),
            active=True,
            available_in_api=True,
            json_schema=None,
            type='object',
        )
        get_partner_fields = (
            ProductionLocations()._ProductionLocations__get_partner_fields
        )

        with patch(
            'api.views.v1.production_locations.get_cached_all_partner_fields',
            return_value=[partner_field],
        ), patch.object(
            WageIndicatorProvider, 'fetch_data', return_value=None
        ) as fetch_data:
            self.assertEqual(get_partner_fields(self.candidate.id), {})
            fetch_data.assert_not_called()

            get_partner_fields(self.facility.id)
            fetch_data.assert_called_once()
            self.assertEqual(
                fetch_data.call_args.args[0].id, self.facility.id
            )


class ModerationApprovalCandidateAuditTest(
    CandidateFixtureMixin, BaseModerationEventsProductionLocationTest
):
    """Moderation-event approval paths (api/moderation_event_actions)."""

    def setUp(self):
        super().setUp()
        # The base class already made the regular user and superuser;
        # reuse its credentials and only add the facilities.
        self.user_email = self.email
        self.user_password = self.password
        self.list = FacilityList.objects.create(
            header='header', file_name='one', name='First List'
        )
        self.source = Source.objects.create(
            facility_list=self.list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        self.next_row_index = 0
        self.facility = self.create_facility(name='Confirmed')
        self.candidate = self.create_candidate()

    def approval_url(self, os_id):
        return (
            f'/api/v1/moderation-events/{self.moderation_event_id}'
            f'/production-locations/{os_id}/'
        )

    def test_update_approval_targeting_candidate_fails_cleanly(self):
        self.login_as_superuser()

        response = self.client.patch(
            self.approval_url(self.candidate.id),
            data=json.dumps({}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['errors'][0]['field'], 'os_id')
        self.assertEqual(
            response.data['errors'][0]['detail'],
            APIV1CommonErrorMessages.LOCATION_NOT_FOUND,
        )
        self.moderation_event.refresh_from_db()
        self.assertEqual(
            self.moderation_event.status, ModerationEvent.Status.PENDING
        )
        self.assertIsNone(self.moderation_event.os_id)
        self.assertFalse(
            FacilityListItem.objects.filter(facility=self.candidate).exists()
        )
        self.assertFalse(
            FacilityMatch.objects.filter(facility=self.candidate).exists()
        )

    def test_validate_location_os_id_rejects_candidate(self):
        ModerationEventsService.validate_location_os_id(self.facility.id)

        with self.assertRaises(NotFound):
            ModerationEventsService.validate_location_os_id(self.candidate.id)

    def test_update_approval_on_confirmed_facility_still_works(self):
        self.login_as_superuser()

        response = self.client.patch(
            self.approval_url(self.facility.id),
            data=json.dumps({}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['os_id'], self.facility.id)

    def test_add_approval_creates_a_confirmed_facility(self):
        self.login_as_superuser()

        response = self.client.post(
            f'/api/v1/moderation-events/{self.moderation_event_id}'
            '/production-locations/',
            data=json.dumps({}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        created = Facility.objects.get(id=response.data['os_id'])
        self.assertFalse(created.is_candidate)
        self.assertEqual(Facility.objects.count(), 2)


class LookupHelpersCandidateAuditTest(CandidateFixtureMixin, TestCase):
    """OS ID resolution helpers used by list upload and partner uploads."""

    def setUp(self):
        self.create_fixture()

    def test_contricleaner_os_id_lookup_does_not_resolve_candidate(self):
        lookup = OSIDLookup()

        self.assertEqual(
            lookup.get(self.facility.id), {self.facility.id: self.facility.id}
        )
        self.assertEqual(
            lookup.get(self.candidate.id), {self.candidate.id: None}
        )
        self.assertEqual(
            lookup.bulk_get([self.facility.id, self.candidate.id]),
            {self.facility.id: self.facility.id, self.candidate.id: None},
        )

    def test_partner_patch_event_creator_rejects_candidate(self):
        me_creator = Mock()
        creator = PartnerPatchModerationEventCreator(me_creator)

        with self.assertRaisesMessage(ValueError, 'was not found'):
            creator.create(
                self.contributor, {'os_id': self.candidate.id}, {}
            )

        me_creator.perform_event_creation.assert_not_called()
