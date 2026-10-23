from datetime import timedelta
from unittest.mock import patch

from django.contrib.gis.geos import Point
from django.core import mail
from django.core.cache import caches
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from api.constants import FacilityClaimStatuses
from api.models import (
    Contributor,
    Facility,
    FacilityClaim,
    FacilityClaimInvite,
    FacilityList,
    FacilityListItem,
    Sector,
    Source,
    User,
)
from api.throttles import ClaimInviteThrottle
from api.services.facility_claim_invite_service import (
    CLAIM_INVITE_SWITCH,
    PER_FACILITY_MAX_INVITES,
    SAME_RECIPIENT_WINDOW,
)


@override_settings(DEBUG=True)
@override_switch('claim_a_facility', active=True)
@override_switch('enable_v1_claims_flow', active=True)
@override_switch(CLAIM_INVITE_SWITCH, active=True)
class FacilityClaimInviteTest(APITestCase):
    def setUp(self):
        # ClaimInviteThrottle keys on user id in the shared
        # 'api_throttling' cache, which outlives a test run; the test DB
        # reuses ids, so a stale entry could turn a request into a 429.
        caches['api_throttling'].clear()
        Sector.objects.get_or_create(name='Apparel')

        self.password = 'example123'
        self.sender_email = 'sender@example.com'
        self.sender_user = User.objects.create(email=self.sender_email)
        self.sender_user.set_password(self.password)
        self.sender_user.save()
        self.sender = Contributor.objects.create(
            admin=self.sender_user,
            name='Example Brand',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.claimant_email = 'claimant@example.com'
        self.claimant_user = User.objects.create(email=self.claimant_email)
        self.claimant_user.set_password(self.password)
        self.claimant_user.save()
        self.claimant = Contributor.objects.create(
            admin=self.claimant_user,
            name='Example Factory',
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
            contributor=self.sender,
        )
        self.source = source
        list_item = FacilityListItem.objects.create(
            name='Example Factory',
            address='1 Example Street',
            country_code='US',
            sector=['Apparel'],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )
        self.facility = Facility.objects.create(
            name='Example Factory',
            address='1 Example Street',
            country_code='US',
            location=Point(0, 0),
            created_from=list_item,
        )

    def invite_url(self, facility=None):
        facility = facility or self.facility
        return f'/api/facilities/{facility.id}/claim-invite/'

    def send_invite(self, **fields):
        data = {'recipient_email': 'manager@factory.example'}
        data.update(fields)
        return self.client.post(self.invite_url(), data)

    def login_sender(self):
        self.client.login(email=self.sender_email, password=self.password)

    def test_sends_invite_email_and_records_it(self):
        self.login_sender()
        response = self.send_invite(
            recipient_email=' Manager@Factory.example ',
            note='We work with you & would like to see your profile claimed.',
        )

        self.assertEqual(201, response.status_code, response.content)
        invite = FacilityClaimInvite.objects.get()
        self.assertEqual('manager@factory.example', invite.recipient_email)
        self.assertEqual(self.sender, invite.sent_by_contributor)
        self.assertEqual(self.sender_user, invite.sent_by_user)

        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(['manager@factory.example'], email.to)
        self.assertEqual(
            "Example Brand invited you to claim your profile on "
            "OS Hub",
            email.subject,
        )
        self.assertIn('Example Brand found your listing', email.body)
        self.assertIn(
            f'/claim/{self.facility.id}?invite={invite.uuid}', email.body
        )
        self.assertIn('claim-a-facility', email.body)
        # The plain-text body isn't HTML-escaped; the HTML body is.
        self.assertIn('We work with you & would like', email.body)
        html = email.alternatives[0][0]
        self.assertIn('We work with you &amp; would like', html)

    def test_requires_login(self):
        response = self.send_invite()
        self.assertIn(response.status_code, (401, 403))
        self.assertFalse(FacilityClaimInvite.objects.exists())
        self.assertEqual(0, len(mail.outbox))

    @override_switch(CLAIM_INVITE_SWITCH, active=False)
    def test_not_found_when_switch_is_off(self):
        self.login_sender()
        self.assertEqual(404, self.send_invite().status_code)

    def test_rejects_invalid_email_and_long_note(self):
        self.login_sender()
        self.assertEqual(
            400, self.send_invite(recipient_email='not-an-email').status_code
        )
        self.assertEqual(400, self.send_invite(note='a' * 501).status_code)
        self.assertFalse(FacilityClaimInvite.objects.exists())

    def test_rejects_links_in_the_note(self):
        self.login_sender()
        for note in (
            'Verify your account at https://evil.example/login',
            'Go to http://203.0.113.5 now',
            'See www.example.org',
            'Log in at evil.com/verify',
            'Visit SECURE-LOGIN.CO',
            'Details at bit.ly',
            'Visit login.attacker.ai/verify',
            'See example.museum',
            'Open 203.0.113.5/login',
            'Write to jane@factory.example',
        ):
            response = self.send_invite(note=note)
            self.assertEqual(400, response.status_code, note)
            self.assertIn('links', str(response.json()), note)
        self.assertFalse(FacilityClaimInvite.objects.exists())

    def test_allows_notes_without_links(self):
        self.login_sender()
        for i, note in enumerate((
            'We work with them. Please claim by Nov. 30.',
            'Ask for the plant manager at Example Co. Ltd.',
            'Our v2.0 audit is due soon.',
            'Ask for the manager, e.g. the plant manager.',
        )):
            response = self.send_invite(
                recipient_email=f'manager{i}@factory.example', note=note
            )
            self.assertEqual(201, response.status_code, note)

    def test_rejects_claimed_or_pending_location(self):
        for claim_status in (FacilityClaimStatuses.APPROVED,
                             FacilityClaimStatuses.PENDING):
            claim = FacilityClaim.objects.create(
                contributor=self.claimant,
                facility=self.facility,
                contact_person='Claimant',
                job_title='Owner',
                status=claim_status,
            )
            self.login_sender()
            response = self.send_invite()
            self.assertEqual(400, response.status_code, claim_status)
            claim.delete()

        self.assertFalse(FacilityClaimInvite.objects.exists())

    def test_allows_location_whose_claim_was_denied(self):
        FacilityClaim.objects.create(
            contributor=self.claimant,
            facility=self.facility,
            contact_person='Claimant',
            job_title='Owner',
            status=FacilityClaimStatuses.DENIED,
        )
        self.login_sender()
        self.assertEqual(201, self.send_invite().status_code)

    def test_rejects_closed_location(self):
        self.facility.is_closed = True
        self.facility.save()
        self.login_sender()
        self.assertEqual(400, self.send_invite().status_code)

    def test_rejects_repeat_invite_to_same_address(self):
        self.login_sender()
        self.assertEqual(201, self.send_invite().status_code)
        self.assertEqual(400, self.send_invite().status_code)

        # Allowed again once the window has passed.
        FacilityClaimInvite.objects.update(
            created_at=timezone.now() - SAME_RECIPIENT_WINDOW
            - timedelta(days=1)
        )
        self.assertEqual(201, self.send_invite().status_code)

    def test_limits_invites_per_location(self):
        self.login_sender()
        for i in range(PER_FACILITY_MAX_INVITES):
            response = self.send_invite(
                recipient_email=f'person{i}@factory.example'
            )
            self.assertEqual(201, response.status_code)

        response = self.send_invite(recipient_email='another@factory.example')
        self.assertEqual(400, response.status_code)

    @patch.object(ClaimInviteThrottle, 'rate', '2/day', create=True)
    def test_daily_limit_counts_only_sent_invites(self):
        self.login_sender()
        self.assertEqual(201, self.send_invite().status_code)
        # Refused repeats to the same address don't use up the limit.
        for _ in range(3):
            self.assertEqual(400, self.send_invite().status_code)

        self.assertEqual(
            201,
            self.send_invite(
                recipient_email='second@factory.example'
            ).status_code,
        )
        self.assertEqual(
            429,
            self.send_invite(
                recipient_email='third@factory.example'
            ).status_code,
        )

    def claim_form_data(self, **overrides):
        data = {
            'your_name': 'Claimant',
            'your_title': 'Owner',
            'your_business_website': '',
            'business_website': '',
            'business_linkedin_profile':
                'https://www.linkedin.com/company/example',
            'sectors': 'Apparel',
        }
        data.update(overrides)
        return data

    def submit_claim(self, **overrides):
        self.client.logout()
        self.client.login(email=self.claimant_email, password=self.password)
        return self.client.post(
            f'/api/facilities/{self.facility.id}/claim/',
            self.claim_form_data(**overrides),
        )

    def test_claim_from_invite_link_is_linked_to_the_invite(self):
        self.login_sender()
        self.send_invite()
        invite = FacilityClaimInvite.objects.get()

        response = self.submit_claim(claim_invite=str(invite.uuid))

        self.assertEqual(200, response.status_code, response.content)
        claim = FacilityClaim.objects.get()
        self.assertEqual(invite, claim.claim_invite)

    def claim_details(self, claim):
        superuser = User.objects.create_superuser(
            email='moderator@example.com', password=self.password
        )
        self.client.login(email=superuser.email, password=self.password)
        response = self.client.get(f'/api/facility-claims/{claim.id}/')
        self.assertEqual(200, response.status_code, response.content)
        return response.json()

    def test_claim_details_show_the_invite_to_moderators(self):
        self.login_sender()
        self.send_invite(note='We work with them.')
        invite = FacilityClaimInvite.objects.get()
        self.submit_claim(claim_invite=str(invite.uuid))

        details = self.claim_details(FacilityClaim.objects.get())

        claim_invite = details['claim_invite']
        self.assertEqual(
            {'id': self.sender.id, 'name': 'Example Brand'},
            claim_invite['sent_by_contributor'],
        )
        self.assertEqual(self.sender_user.id, claim_invite['sent_by_user_id'])
        self.assertEqual(self.sender_email, claim_invite['sent_by_email'])
        self.assertEqual(
            'manager@factory.example', claim_invite['recipient_email']
        )
        self.assertEqual('We work with them.', claim_invite['note'])
        self.assertIsNotNone(claim_invite['created_at'])

    def test_claim_details_without_an_invite_have_no_invite(self):
        self.submit_claim()

        details = self.claim_details(FacilityClaim.objects.get())

        self.assertIsNone(details['claim_invite'])

    def test_claim_with_unknown_or_malformed_invite_code_still_succeeds(self):
        for code in ('not-a-uuid', '00000000-0000-0000-0000-000000000000'):
            response = self.submit_claim(claim_invite=code)
            self.assertEqual(200, response.status_code, response.content)
            claim = FacilityClaim.objects.get()
            self.assertIsNone(claim.claim_invite)
            claim.delete()

    def test_invite_code_for_another_location_is_ignored(self):
        other_list_item = FacilityListItem.objects.create(
            name='Other Factory',
            address='2 Example Street',
            country_code='US',
            sector=['Apparel'],
            row_index=2,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )
        other_facility = Facility.objects.create(
            name='Other Factory',
            address='2 Example Street',
            country_code='US',
            location=Point(0, 0),
            created_from=other_list_item,
        )
        other_invite = FacilityClaimInvite.objects.create(
            facility=other_facility,
            sent_by_user=self.sender_user,
            sent_by_contributor=self.sender,
            recipient_email='manager@factory.example',
        )

        response = self.submit_claim(claim_invite=str(other_invite.uuid))

        self.assertEqual(200, response.status_code, response.content)
        self.assertIsNone(FacilityClaim.objects.get().claim_invite)
