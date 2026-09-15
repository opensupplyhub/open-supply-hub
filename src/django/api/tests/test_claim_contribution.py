from django.contrib.gis.geos import Point
from django.db.models.signals import post_save
from django.test import override_settings
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from api.constants import FacilityClaimStatuses
from api.models import (
    Contributor,
    ExtendedField,
    Facility,
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    ModerationEvent,
    Sector,
    Source,
    User,
)
from api.serializers.facility.facility_create_claim_serializer import (
    FacilityCreateClaimSerializer,
)
from api.services.claim_contribution_service import (
    CLAIM_NAME_ADDRESS_EDIT_SWITCH,
)
from api.signals import moderation_event_update_handler_for_opensearch


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


class ApprovalRecordsContributionTest(ClaimContributionTestBase):

    def test_approval_records_contribution_and_promotes(self):
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

        # The item sits at the current pin; the pin itself is untouched.
        self.facility.refresh_from_db()
        self.assertPointEqual(self.facility.location, 0, 0)

    def test_approval_without_name_or_address_records_nothing(self):
        claim = self.make_claim()

        self.approve(claim)

        self.assertEqual(0, self.claim_events(claim).count())
        self.assertEqual(
            0,
            FacilityListItem.objects.filter(
                source__contributor=self.claimant
            ).count(),
        )

    @override_switch(CLAIM_NAME_ADDRESS_EDIT_SWITCH, active=False)
    def test_nothing_is_recorded_while_the_switch_is_off(self):
        claim = self.make_claim(
            facility_name_english='Claimed Name',
            facility_address='2 New Street',
        )

        self.approve(claim)

        claim.refresh_from_db()
        self.assertEqual(FacilityClaimStatuses.APPROVED, claim.status)
        self.assertEqual(0, self.claim_events(claim).count())
        # The claim fields still promote on their own, as before.
        self.assertTrue(
            ExtendedField.objects.filter(
                facility_claim=claim, field_name=ExtendedField.NAME
            ).exists()
        )

    def test_approval_backfills_the_missing_value(self):
        claim = self.make_claim(facility_name_english='Claimed Name')

        self.approve(claim)

        event = self.claim_events(claim).get()
        self.assertEqual(['address'], event.backfilled_fields)
        item = FacilityListItem.objects.get(moderation_event=event)
        self.assertEqual('Claimed Name', item.name)
        self.assertEqual('1 Original Street', item.address)

    def test_unknown_claim_sectors_are_not_passed_as_product_types(self):
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

    def test_changed_address_places_item_at_current_pin(self):
        claim = self.make_claim(
            facility_name_english='Claimed Name',
            facility_address='2 New Street',
        )

        self.approve(claim)

        item = FacilityListItem.objects.get(moderation_event__claim=claim)
        self.assertEqual('2 New Street', item.address)
        self.assertPointEqual(item.geocoded_point, 0, 0)
        geocode_steps = [
            step for step in item.processing_results
            if step['action'] == 'geocode'
        ]
        self.assertEqual(1, len(geocode_steps))
        self.assertTrue(geocode_steps[0]['skipped_geocoder'])
        self.facility.refresh_from_db()
        self.assertPointEqual(self.facility.location, 0, 0)

    def test_claimant_pin_is_used_when_set(self):
        claim = self.make_claim(
            facility_name_english='Claimed Name',
            facility_address='2 New Street',
            facility_location=Point(0.02, 0.01),
        )

        self.approve(claim)

        item = FacilityListItem.objects.get(moderation_event__claim=claim)
        self.assertPointEqual(item.geocoded_point, 0.02, 0.01)


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

    def test_name_change_records_a_second_event(self):
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

        properties = self.client.get(
            f'/api/facilities/{self.facility.id}/'
        ).json()['properties']
        self.assertEqual('Renamed', properties['name'])

    def test_unrelated_edit_records_nothing(self):
        claim = self.make_claim(
            facility_name_english='Claimed Name',
            facility_address='1 Original Street',
        )
        self.approve(claim)

        self.put_claimed(claim, facility_description='new description')

        self.assertEqual(1, self.claim_events(claim).count())


class ClaimSubmissionAcceptsNameAndAddressTest(ClaimContributionTestBase):

    def valid_form_data(self, **overrides):
        data = {
            'your_name': 'Claimant',
            'your_title': 'Owner',
            'your_business_website': '',
            'business_website': '',
            'business_linkedin_profile':
                'https://www.linkedin.com/company/example',
        }
        data.update(overrides)
        return data

    def serializer(self, **overrides):
        return FacilityCreateClaimSerializer(
            data=self.valid_form_data(**overrides),
            context={'facility': self.facility},
        )

    def test_serializer_accepts_and_strips_values(self):
        serializer = self.serializer(
            facility_name_english='  Claimed Name ',
            facility_address=' 2 New Street ',
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            'Claimed Name', serializer.validated_data['facility_name_english']
        )
        self.assertEqual(
            '2 New Street', serializer.validated_data['facility_address']
        )

    def test_serializer_normalizes_blank_to_none(self):
        serializer = self.serializer(
            facility_name_english='', facility_address='   '
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIsNone(serializer.validated_data['facility_name_english'])
        self.assertIsNone(serializer.validated_data['facility_address'])

    def test_serializer_rejects_punctuation_only_values(self):
        serializer = self.serializer(
            facility_name_english='Fine', facility_address='-- , / :'
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('facility_address', serializer.errors)
        self.assertIn(
            'punctuation or whitespace',
            str(serializer.errors['facility_address'][0]),
        )

    def test_serializer_rejects_values_over_200_characters(self):
        serializer = self.serializer(facility_name_english='a' * 201)
        self.assertFalse(serializer.is_valid())
        self.assertIn('facility_name_english', serializer.errors)

    def test_claim_post_stores_the_values(self):
        self.client.login(
            email=self.claimant_email, password=self.password
        )
        response = self.client.post(
            f'/api/facilities/{self.facility.id}/claim/',
            self.valid_form_data(
                facility_name_english='Claimed Name',
                facility_address='2 New Street',
                sectors='Apparel',
            ),
        )
        self.assertEqual(200, response.status_code, response.content)

        claim = FacilityClaim.objects.get(facility=self.facility)
        self.assertEqual('Claimed Name', claim.facility_name_english)
        self.assertEqual('2 New Street', claim.facility_address)
        self.assertEqual(FacilityClaimStatuses.PENDING, claim.status)
        # Nothing is recorded until the claim is approved.
        self.assertEqual(0, self.claim_events(claim).count())

    def test_claim_post_without_the_values_stores_null(self):
        self.client.login(
            email=self.claimant_email, password=self.password
        )
        response = self.client.post(
            f'/api/facilities/{self.facility.id}/claim/',
            self.valid_form_data(sectors='Apparel'),
        )
        self.assertEqual(200, response.status_code, response.content)
        claim = FacilityClaim.objects.get(facility=self.facility)
        self.assertIsNone(claim.facility_name_english)
        self.assertIsNone(claim.facility_address)

    def test_pending_claim_patch_edits_and_clears_the_values(self):
        claim = self.make_claim(
            facility_name_english='Claimed Name',
            facility_address='1 Original Street',
        )
        self.client.login(
            email=self.claimant_email, password=self.password
        )
        url = f'/api/facility-claims/{claim.id}/pending/'

        response = self.client.patch(
            url, {'facility_address': '2 New Street'}, format='json'
        )
        self.assertEqual(200, response.status_code, response.content)
        self.assertEqual('2 New Street', response.json()['facility_address'])
        self.assertEqual(
            'Claimed Name', response.json()['facility_name_english']
        )
        claim.refresh_from_db()
        self.assertEqual('2 New Street', claim.facility_address)

        response = self.client.patch(
            url, {'facility_address': None}, format='json'
        )
        self.assertEqual(200, response.status_code, response.content)
        claim.refresh_from_db()
        self.assertIsNone(claim.facility_address)

        response = self.client.patch(
            url, {'facility_name_english': '-- , /'}, format='json'
        )
        self.assertEqual(400, response.status_code, response.content)
