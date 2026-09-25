from unittest.mock import patch

from django.contrib.gis.geos import Point
from django.db.models.signals import post_save
from django.test import override_settings
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from api.constants import FacilityClaimStatuses
from api.moderation_event_actions.approval.event_approval_template import (
    ANONYMIZE_SLC_SOURCES_SWITCH,
)
from api.models import (
    Contributor,
    ExtendedField,
    Facility,
    FacilityClaim,
    FacilityClaimReviewNote,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    ModerationEvent,
    Sector,
    Source,
    User,
)
from api.services.claim_contribution_service import (
    CLAIM_ADDRESS_PIN_MOVE_SWITCH,
    CLAIM_NAME_ADDRESS_EDIT_SWITCH,
)
from api.signals import moderation_event_update_handler_for_opensearch

GEOCODE_PATH = 'api.services.claim_contribution_service.geocode_address'


def geocode_result(lat, lng, location_type='ROOFTOP'):
    return {
        'result_count': 1,
        'geocoded_point': {'lat': lat, 'lng': lng},
        'geocoded_address': 'Formatted Address',
        'full_response': {
            'results': [
                {
                    'geometry': {
                        'location': {'lat': lat, 'lng': lng},
                        'location_type': location_type,
                    }
                }
            ]
        },
    }


NO_GEOCODE_RESULTS = {
    'result_count': 0,
    'geocoded_point': None,
    'geocoded_address': None,
    'full_response': {'results': []},
}


@override_settings(DEBUG=True)
@override_switch('claim_a_facility', active=True)
@override_switch(CLAIM_NAME_ADDRESS_EDIT_SWITCH, active=True)
class ClaimContributionTestBase(APITestCase):
    '''
    A production location with one list contribution, a claimant with no
    prior contributions, and a superuser who decides claims.
    '''

    def setUp(self):
        # Moderation event propagation to OpenSearch is outside unit tests.
        post_save.disconnect(
            moderation_event_update_handler_for_opensearch, ModerationEvent
        )

        Sector.objects.get_or_create(name='Apparel')

        self.claimant_email = 'claimant@example.com'
        self.password = 'example123'
        self.claimant_user = User.objects.create(email=self.claimant_email)
        self.claimant_user.set_password(self.password)
        self.claimant_user.save()
        self.claimant = Contributor.objects.create(
            admin=self.claimant_user,
            name='Claimant Co',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.superuser_email = 'admin@example.com'
        self.superuser = User.objects.create_superuser(
            email=self.superuser_email, password=self.password
        )

        list_user = User.objects.create(email='lister@example.com')
        self.list_contributor = Contributor.objects.create(
            admin=list_user,
            name='List Contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='List'
        )
        source = Source.objects.create(
            facility_list=facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.list_contributor,
        )
        self.list_item = FacilityListItem.objects.create(
            name='Original Name',
            address='1 Original Street',
            country_code='US',
            sector=['Apparel'],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )
        self.facility = Facility.objects.create(
            name='Original Name',
            address='1 Original Street',
            country_code='US',
            location=Point(0, 0),
            created_from=self.list_item,
        )
        self.list_item.facility = self.facility
        self.list_item.save()
        FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=self.facility,
            results='',
            facility_list_item=self.list_item,
        )

    def make_claim(self, **overrides):
        values = {
            'contributor': self.claimant,
            'facility': self.facility,
            'contact_person': 'Claimant',
            'job_title': 'Owner',
            'sector': ['Apparel'],
        }
        values.update(overrides)
        return FacilityClaim.objects.create(**values)

    def approve(self, claim):
        self.client.logout()
        self.client.login(
            email=self.superuser_email, password=self.password
        )
        response = self.client.post(
            f'/api/facility-claims/{claim.id}/approve/',
            {'reason': 'documents verified'},
        )
        self.assertEqual(200, response.status_code, response.content)
        return response

    def claim_events(self, claim):
        return ModerationEvent.objects.filter(claim=claim).order_by(
            'created_at'
        )

    def assertPointEqual(self, point, lng, lat):
        self.assertIsNotNone(point)
        self.assertAlmostEqual(lng, point.x, places=6)
        self.assertAlmostEqual(lat, point.y, places=6)

    def pin_notes(self, claim):
        return FacilityClaimReviewNote.objects.filter(
            claim=claim, note__icontains='pin'
        )


class ApprovalRecordsContributionTest(ClaimContributionTestBase):

    @override_switch(ANONYMIZE_SLC_SOURCES_SWITCH, active=True)
    @patch(GEOCODE_PATH)
    def test_approval_records_contribution_and_promotes(self, geocode):
        claim = self.make_claim(
            facility_name_english='Claimed Name',
            facility_address='1 Original Street',
        )

        self.approve(claim)

        events = self.claim_events(claim)
        self.assertEqual(1, events.count())
        event = events.first()
        self.assertEqual(ModerationEvent.RequestType.CLAIM, event.request_type)
        self.assertEqual(ModerationEvent.Status.APPROVED, event.status)
        self.assertEqual(ModerationEvent.ActionType.MATCHED, event.action_type)
        self.assertEqual(self.superuser, event.action_perform_by)
        self.assertEqual(self.facility, event.os)
        self.assertEqual(self.facility.id, event.os_id_snapshot)
        self.assertEqual('', event.source)
        self.assertEqual([], event.backfilled_fields)

        item = FacilityListItem.objects.get(moderation_event=event)
        self.assertEqual('Claimed Name', item.name)
        self.assertEqual('1 Original Street', item.address)
        self.assertEqual('US', item.country_code)
        self.assertEqual(['Apparel'], item.sector)
        self.assertEqual(FacilityListItem.CONFIRMED_MATCH, item.status)
        self.assertEqual(self.facility, item.facility)
        self.assertEqual(Source.SINGLE, item.source.source_type)
        self.assertEqual(self.claimant, item.source.contributor)
        # Not anonymized even with the SLC anonymization switch on: a
        # CLAIM event has no source type, so the SLC rule never applies.
        self.assertFalse(item.source.is_anonymized)

        match = FacilityMatch.objects.get(facility_list_item=item)
        self.assertEqual(FacilityMatch.CONFIRMED, match.status)
        self.assertTrue(match.is_active)

        # The claim fields keep driving promotion, as before.
        name_field = ExtendedField.objects.get(
            facility_claim=claim, field_name=ExtendedField.NAME
        )
        self.assertEqual('Claimed Name', name_field.value)
        properties = self.client.get(
            f'/api/facilities/{self.facility.id}/'
        ).json()['properties']
        self.assertEqual('Claimed Name', properties['name'])
        contributor_names = [
            c['name'] for c in properties['contributors']
        ]
        self.assertIn('Claimant Co', contributor_names)

        # Same address as the location: nothing geocoded, pin unchanged.
        geocode.assert_not_called()
        self.facility.refresh_from_db()
        self.assertPointEqual(self.facility.location, 0, 0)
        self.assertEqual(0, self.pin_notes(claim).count())

    @patch(GEOCODE_PATH)
    def test_approval_without_name_or_address_records_nothing(
        self, geocode
    ):
        claim = self.make_claim()

        self.approve(claim)

        self.assertEqual(0, self.claim_events(claim).count())
        self.assertEqual(
            0,
            FacilityListItem.objects.filter(
                source__contributor=self.claimant
            ).count(),
        )
        geocode.assert_not_called()

    @override_switch(CLAIM_NAME_ADDRESS_EDIT_SWITCH, active=False)
    @patch(GEOCODE_PATH)
    def test_nothing_is_recorded_while_the_switch_is_off(self, geocode):
        claim = self.make_claim(
            facility_name_english='Claimed Name',
            facility_address='2 New Street',
        )

        self.approve(claim)

        claim.refresh_from_db()
        self.assertEqual(FacilityClaimStatuses.APPROVED, claim.status)
        self.assertEqual(0, self.claim_events(claim).count())
        geocode.assert_not_called()
        # The claim fields still promote on their own, as before.
        self.assertTrue(
            ExtendedField.objects.filter(
                facility_claim=claim, field_name=ExtendedField.NAME
            ).exists()
        )

    @patch(GEOCODE_PATH)
    def test_approval_backfills_the_missing_value(self, geocode):
        claim = self.make_claim(facility_name_english='Claimed Name')

        self.approve(claim)

        event = self.claim_events(claim).get()
        self.assertEqual(['address'], event.backfilled_fields)
        item = FacilityListItem.objects.get(moderation_event=event)
        self.assertEqual('Claimed Name', item.name)
        self.assertEqual('1 Original Street', item.address)
        geocode.assert_not_called()

    @patch(GEOCODE_PATH)
    def test_unknown_claim_sectors_are_not_passed_as_product_types(
        self, geocode
    ):
        claim = self.make_claim(
            facility_name_english='Claimed Name',
            sector=['Not A Real Sector'],
        )

        self.approve(claim)

        item = FacilityListItem.objects.get(
            moderation_event__claim=claim
        )
        self.assertEqual(['Unspecified'], item.sector)
        self.assertFalse(
            ExtendedField.objects.filter(
                facility_list_item=item,
                field_name=ExtendedField.PRODUCT_TYPE,
            ).exists()
        )


@override_switch(CLAIM_ADDRESS_PIN_MOVE_SWITCH, active=True)
class ApprovalMovesPinTest(ClaimContributionTestBase):

    @patch(GEOCODE_PATH)
    def test_changed_address_moves_pin(self, geocode):
        geocode.return_value = geocode_result(0.01, 0.02)
        claim = self.make_claim(
            facility_name_english='Claimed Name',
            facility_address='2 New Street',
        )

        self.approve(claim)

        geocode.assert_called_once_with('2 New Street', 'US')
        self.facility.refresh_from_db()
        claim.refresh_from_db()
        self.assertPointEqual(self.facility.location, 0.02, 0.01)
        self.assertPointEqual(claim.facility_location, 0.02, 0.01)
        self.assertEqual(0, self.pin_notes(claim).count())

        item = FacilityListItem.objects.get(moderation_event__claim=claim)
        self.assertPointEqual(item.geocoded_point, 0.02, 0.01)
        self.assertEqual('Formatted Address', item.geocoded_address)

        # The approval template saves the facility again afterwards (to
        # bump updated_at), so look for the reason rather than at the
        # latest history row.
        self.assertTrue(
            self.facility.history.filter(
                history_change_reason__contains=f'FacilityClaim ({claim.id})'
            ).exists()
        )

    @override_switch(CLAIM_ADDRESS_PIN_MOVE_SWITCH, active=False)
    @patch(GEOCODE_PATH)
    def test_pin_switch_off_places_item_at_current_pin(self, geocode):
        claim = self.make_claim(
            facility_name_english='Claimed Name',
            facility_address='2 New Street',
        )

        self.approve(claim)

        geocode.assert_not_called()
        self.assertEqual(1, self.claim_events(claim).count())
        item = FacilityListItem.objects.get(moderation_event__claim=claim)
        self.assertPointEqual(item.geocoded_point, 0, 0)
        self.facility.refresh_from_db()
        self.assertPointEqual(self.facility.location, 0, 0)
        self.assertEqual(0, self.pin_notes(claim).count())

    @patch(GEOCODE_PATH)
    def test_approximate_geocode_keeps_pin(self, geocode):
        geocode.return_value = geocode_result(
            0.01, 0.02, location_type='APPROXIMATE'
        )
        claim = self.make_claim(
            facility_name_english='Claimed Name',
            facility_address='2 New Street',
        )

        self.approve(claim)

        self.facility.refresh_from_db()
        self.assertPointEqual(self.facility.location, 0, 0)
        self.assertIn('APPROXIMATE', self.pin_notes(claim).get().note)

    @patch(GEOCODE_PATH)
    def test_no_geocode_results_keeps_pin(self, geocode):
        geocode.return_value = NO_GEOCODE_RESULTS
        claim = self.make_claim(
            facility_name_english='Claimed Name',
            facility_address='2 New Street',
        )

        self.approve(claim)

        self.facility.refresh_from_db()
        self.assertPointEqual(self.facility.location, 0, 0)
        self.assertIn('no geocoding results', self.pin_notes(claim).get().note)
        item = FacilityListItem.objects.get(moderation_event__claim=claim)
        self.assertPointEqual(item.geocoded_point, 0, 0)

    @patch(GEOCODE_PATH)
    def test_geocoder_error_does_not_fail_approval(self, geocode):
        geocode.side_effect = ValueError('Geocoding request failed')
        claim = self.make_claim(
            facility_name_english='Claimed Name',
            facility_address='2 New Street',
        )

        self.approve(claim)

        claim.refresh_from_db()
        self.assertEqual(FacilityClaimStatuses.APPROVED, claim.status)
        self.assertEqual(1, self.claim_events(claim).count())
        self.facility.refresh_from_db()
        self.assertPointEqual(self.facility.location, 0, 0)
        self.assertIn('geocoder error', self.pin_notes(claim).get().note)

    @patch(GEOCODE_PATH)
    def test_unchanged_address_is_not_geocoded_even_if_formatted_differently(
        self, geocode
    ):
        claim = self.make_claim(
            facility_name_english='Claimed Name',
            facility_address='1, ORIGINAL STREET',
        )

        self.approve(claim)

        geocode.assert_not_called()


@override_switch(CLAIM_ADDRESS_PIN_MOVE_SWITCH, active=True)
class ClaimedDetailsEditRecordsContributionTest(ClaimContributionTestBase):

    def put_claimed(self, claim, **fields):
        self.client.logout()
        self.client.login(
            email=self.claimant_email, password=self.password
        )
        payload = {
            'facility_name_english': claim.facility_name_english,
            'facility_address': claim.facility_address,
            'facility_description': claim.facility_description or '',
            'facility_phone_number_publicly_visible': False,
            'point_of_contact_publicly_visible': False,
            'office_info_publicly_visible': False,
            'facility_website_publicly_visible': False,
        }
        payload.update(fields)
        response = self.client.put(
            f'/api/facility-claims/{claim.id}/claimed/', payload
        )
        self.assertEqual(200, response.status_code, response.content)
        return response

    @patch(GEOCODE_PATH)
    def test_name_change_records_a_second_event(self, geocode):
        claim = self.make_claim(
            facility_name_english='Claimed Name',
            facility_address='1 Original Street',
        )
        self.approve(claim)

        self.put_claimed(claim, facility_name_english='Renamed')

        events = self.claim_events(claim)
        self.assertEqual(2, events.count())
        second = events.last()
        self.assertEqual(self.claimant_user, second.action_perform_by)
        items = FacilityListItem.objects.filter(
            moderation_event__claim=claim
        ).order_by('id')
        self.assertEqual(['Claimed Name', 'Renamed'],
                         [item.name for item in items])
        # Append-only: the earlier contribution stays active history.
        self.assertTrue(
            FacilityMatch.objects.get(facility_list_item=items[0]).is_active
        )
        geocode.assert_not_called()

        properties = self.client.get(
            f'/api/facilities/{self.facility.id}/'
        ).json()['properties']
        self.assertEqual('Renamed', properties['name'])

    @patch(GEOCODE_PATH)
    def test_address_change_geocodes_and_moves_pin(self, geocode):
        geocode.return_value = geocode_result(0.01, 0.02)
        claim = self.make_claim(
            facility_name_english='Claimed Name',
            facility_address='1 Original Street',
        )
        self.approve(claim)

        self.put_claimed(claim, facility_address='2 New Street')

        geocode.assert_called_once_with('2 New Street', 'US')
        self.facility.refresh_from_db()
        self.assertPointEqual(self.facility.location, 0.02, 0.01)
        self.assertEqual(2, self.claim_events(claim).count())

    @patch(GEOCODE_PATH)
    def test_unrelated_edit_records_nothing(self, geocode):
        claim = self.make_claim(
            facility_name_english='Claimed Name',
            facility_address='1 Original Street',
        )
        self.approve(claim)

        self.put_claimed(claim, facility_description='new description')

        self.assertEqual(1, self.claim_events(claim).count())
        geocode.assert_not_called()
