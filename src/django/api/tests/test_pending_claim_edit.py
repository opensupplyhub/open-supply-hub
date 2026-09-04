import json
from datetime import date

from api.constants import FacilityClaimStatuses
from api.models import (
    Contributor,
    Facility,
    FacilityClaim,
    FacilityClaimAttachments,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile

# Minimal valid file contents for each allowed attachment type.
PNG_BYTES = (
    b'\x89PNG\r\n\x1a\n' + b'\x00' * 64
)
PDF_BYTES = b'%PDF-1.4\n%fake minimal pdf\n' + b'\x00' * 32
JPEG_BYTES = b'\xff\xd8\xff\xe0' + b'\x00' * 64
HTML_BYTES = b'<html><script>alert(1)</script></html>'


def make_png(name='document.png'):
    return SimpleUploadedFile(name, PNG_BYTES, content_type='image/png')


def make_pdf(name='document.pdf'):
    return SimpleUploadedFile(name, PDF_BYTES, content_type='application/pdf')


class PendingClaimEditTest(APITestCase):
    def setUp(self):
        self.email = 'claimant@example.com'
        self.password = 'example123'
        self.user = User.objects.create(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

        self.contributor = Contributor.objects.create(
            name='Claimant Contributor', admin=self.user
        )

        self.other_email = 'other@example.com'
        self.other_user = User.objects.create(email=self.other_email)
        self.other_user.set_password(self.password)
        self.other_user.save()

        self.other_contributor = Contributor.objects.create(
            name='Other Contributor', admin=self.other_user
        )

        self.superuser_email = 'admin@example.com'
        self.superuser = User.objects.create_superuser(
            email=self.superuser_email, password=self.password
        )

        self.facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='list'
        )
        self.source = Source.objects.create(
            facility_list=self.facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        self.list_item = FacilityListItem.objects.create(
            name='name',
            address='address',
            country_code='US',
            sector=['Apparel'],
            source=self.source,
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
        )
        self.facility = Facility.objects.create(
            name='name',
            address='address',
            country_code='US',
            location=Point(0, 0),
            created_from=self.list_item,
        )
        FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=self.facility,
            results='',
            facility_list_item=self.list_item,
        )

        self.claim = FacilityClaim.objects.create(
            facility=self.facility,
            contributor=self.contributor,
            contact_person='Original Name',
            job_title='Original Title',
            status=FacilityClaimStatuses.PENDING,
        )

        self.pending_url = f'/api/facility-claims/{self.claim.id}/pending/'
        self.attachments_url = (
            f'/api/facility-claims/{self.claim.id}/attachments/'
        )

    def login(self, email=None):
        self.client.post(
            '/user-login/',
            {'email': email or self.email, 'password': self.password},
            format='json',
        )

    def add_attachment(self, name='existing.png'):
        return FacilityClaimAttachments.objects.create(
            claim=self.claim,
            file_name=name,
            claim_attachment=make_png(name),
        )

    # ------------------------------------------------------------------
    # Guard matrix: PATCH /pending/
    # ------------------------------------------------------------------

    @override_switch('claim_a_facility', active=True)
    def test_patch_requires_login(self):
        response = self.client.patch(
            self.pending_url, {'your_name': 'New'}, format='json'
        )
        self.assertEqual(401, response.status_code)

    @override_switch('claim_a_facility', active=True)
    def test_owner_can_patch_pending_claim(self):
        self.login()
        response = self.client.patch(
            self.pending_url,
            {'your_name': 'Updated Name', 'your_title': 'Updated Title'},
            format='json',
        )
        self.assertEqual(200, response.status_code)

        self.claim.refresh_from_db()
        self.assertEqual('Updated Name', self.claim.contact_person)
        self.assertEqual('Updated Title', self.claim.job_title)

    @override_switch('claim_a_facility', active=True)
    def test_partial_update_leaves_other_fields_untouched(self):
        self.login()
        response = self.client.patch(
            self.pending_url, {'your_name': 'Only Name'}, format='json'
        )
        self.assertEqual(200, response.status_code)

        self.claim.refresh_from_db()
        self.assertEqual('Only Name', self.claim.contact_person)
        self.assertEqual('Original Title', self.claim.job_title)

    @override_switch('claim_a_facility', active=True)
    def test_null_clears_optional_numeric_and_date_fields(self):
        # In a partial PATCH omitted means "unchanged", so null is the
        # only way a claimant can clear these values (e.g. unchecking
        # an emissions section in the edit UI).
        self.claim.energy_coal = 1000
        self.claim.opening_date = date(2020, 1, 1)
        self.claim.estimated_annual_throughput = 5000
        self.claim.facility_workers_count = '50'
        self.claim.save()

        self.login()
        response = self.client.patch(
            self.pending_url,
            {
                'energy_coal': None,
                'opening_date': None,
                'estimated_annual_throughput': None,
                'number_of_workers': None,
            },
            format='json',
        )
        self.assertEqual(200, response.status_code)

        self.claim.refresh_from_db()
        self.assertIsNone(self.claim.energy_coal)
        self.assertIsNone(self.claim.opening_date)
        self.assertIsNone(self.claim.estimated_annual_throughput)
        self.assertIsNone(self.claim.facility_workers_count)

        self.assertIsNone(response.data['energy_coal'])
        self.assertIsNone(response.data['opening_date'])
        self.assertIsNone(response.data['estimated_annual_throughput'])
        self.assertIsNone(response.data['number_of_workers'])

    @override_switch('claim_a_facility', active=True)
    def test_null_is_rejected_for_non_clearable_fields(self):
        self.login()
        response = self.client.patch(
            self.pending_url, {'your_name': None}, format='json'
        )
        self.assertEqual(400, response.status_code)

        self.claim.refresh_from_db()
        self.assertEqual('Original Name', self.claim.contact_person)

    @override_switch('claim_a_facility', active=True)
    def test_stranger_gets_404_not_403(self):
        self.login(self.other_email)
        response = self.client.patch(
            self.pending_url, {'your_name': 'Hacked'}, format='json'
        )
        self.assertEqual(404, response.status_code)

        self.claim.refresh_from_db()
        self.assertEqual('Original Name', self.claim.contact_person)

    @override_switch('claim_a_facility', active=True)
    def test_decided_claims_are_not_editable(self):
        self.login()
        for status in (
            FacilityClaimStatuses.APPROVED,
            FacilityClaimStatuses.DENIED,
            FacilityClaimStatuses.REVOKED,
        ):
            self.claim.status = status
            self.claim.save()
            response = self.client.patch(
                self.pending_url, {'your_name': 'Too Late'}, format='json'
            )
            self.assertEqual(404, response.status_code)

    @override_switch('claim_a_facility', active=True)
    def test_patch_rejects_invalid_url(self):
        self.login()
        response = self.client.patch(
            self.pending_url,
            {'your_business_website': 'not a url'},
            format='json',
        )
        self.assertEqual(400, response.status_code)

    @override_switch('claim_a_facility', active=True)
    def test_patch_cannot_change_status(self):
        self.login()
        response = self.client.patch(
            self.pending_url,
            {'your_name': 'Fine', 'status': FacilityClaimStatuses.APPROVED},
            format='json',
        )
        self.assertEqual(200, response.status_code)
        self.claim.refresh_from_db()
        self.assertEqual(FacilityClaimStatuses.PENDING, self.claim.status)

    # ------------------------------------------------------------------
    # GET /pending/
    # ------------------------------------------------------------------

    @override_switch('claim_a_facility', active=True)
    def test_get_pending_claim_uses_form_field_names(self):
        self.login()
        self.add_attachment()

        response = self.client.get(self.pending_url)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)

        self.assertEqual('Original Name', data['your_name'])
        self.assertEqual('Original Title', data['your_title'])
        self.assertEqual(FacilityClaimStatuses.PENDING, data['status'])
        self.assertEqual(1, len(data['attachments']))
        attachment = data['attachments'][0]
        self.assertIn('id', attachment)
        self.assertIn('file_name', attachment)
        # No storage URL anywhere in the payload.
        self.assertNotIn('claim_attachment', attachment)

    # ------------------------------------------------------------------
    # POST /attachments/
    # ------------------------------------------------------------------

    @override_switch('claim_a_facility', active=True)
    def test_owner_can_add_attachments(self):
        self.login()
        response = self.client.post(
            self.attachments_url,
            {'files': [make_png(), make_pdf()]},
            format='multipart',
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            2,
            FacilityClaimAttachments.objects.filter(
                claim=self.claim
            ).count(),
        )

    @override_switch('claim_a_facility', active=True)
    def test_attachment_keys_are_opaque(self):
        self.login()
        self.client.post(
            self.attachments_url,
            {'files': [make_png('my-passport-jane-doe.png')]},
            format='multipart',
        )
        attachment = FacilityClaimAttachments.objects.get(claim=self.claim)
        # Original name preserved for display...
        self.assertEqual('my-passport-jane-doe.png', attachment.file_name)
        # ...but never in the storage key.
        self.assertNotIn('passport', attachment.claim_attachment.name)
        self.assertNotIn('jane', attachment.claim_attachment.name)
        self.assertTrue(
            attachment.claim_attachment.name.endswith('.png')
        )

    @override_switch('claim_a_facility', active=True)
    def test_attachment_cap_applies_to_claim_lifetime(self):
        self.login()
        for i in range(19):
            self.add_attachment(name=f'file-{i}.png')

        # 19 existing + 2 new exceeds the cap of 20.
        response = self.client.post(
            self.attachments_url,
            {'files': [make_png('a.png'), make_png('b.png')]},
            format='multipart',
        )
        self.assertEqual(400, response.status_code)

        # 19 existing + 1 new is allowed.
        response = self.client.post(
            self.attachments_url,
            {'files': [make_png('a.png')]},
            format='multipart',
        )
        self.assertEqual(200, response.status_code)

    @override_switch('claim_a_facility', active=True)
    def test_attachment_content_must_match_extension(self):
        self.login()
        fake_pdf = SimpleUploadedFile(
            'report.pdf', HTML_BYTES, content_type='application/pdf'
        )
        response = self.client.post(
            self.attachments_url,
            {'files': [fake_pdf]},
            format='multipart',
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            0,
            FacilityClaimAttachments.objects.filter(
                claim=self.claim
            ).count(),
        )

    @override_switch('claim_a_facility', active=True)
    def test_attachment_extension_allowlist(self):
        self.login()
        executable = SimpleUploadedFile(
            'malware.exe', b'MZ' + b'\x00' * 32,
            content_type='application/octet-stream',
        )
        response = self.client.post(
            self.attachments_url,
            {'files': [executable]},
            format='multipart',
        )
        self.assertEqual(400, response.status_code)

    @override_switch('claim_a_facility', active=True)
    def test_stranger_cannot_add_attachments(self):
        self.login(self.other_email)
        response = self.client.post(
            self.attachments_url,
            {'files': [make_png()]},
            format='multipart',
        )
        self.assertEqual(404, response.status_code)

    # ------------------------------------------------------------------
    # DELETE /attachments/{id}/
    # ------------------------------------------------------------------

    @override_switch('claim_a_facility', active=True)
    def test_owner_can_delete_own_attachment(self):
        self.login()
        attachment = self.add_attachment()
        response = self.client.delete(
            f'{self.attachments_url}{attachment.id}/'
        )
        self.assertEqual(200, response.status_code)
        self.assertFalse(
            FacilityClaimAttachments.objects.filter(
                pk=attachment.id
            ).exists()
        )

    @override_switch('claim_a_facility', active=True)
    def test_stranger_cannot_delete_attachment(self):
        attachment = self.add_attachment()
        self.login(self.other_email)
        response = self.client.delete(
            f'{self.attachments_url}{attachment.id}/'
        )
        self.assertEqual(404, response.status_code)
        self.assertTrue(
            FacilityClaimAttachments.objects.filter(
                pk=attachment.id
            ).exists()
        )

    # ------------------------------------------------------------------
    # GET /attachments/{id}/download/
    # ------------------------------------------------------------------

    @override_switch('claim_a_facility', active=True)
    def test_owner_can_download_attachment(self):
        self.login()
        attachment = self.add_attachment()
        response = self.client.get(
            f'{self.attachments_url}{attachment.id}/download/'
        )
        self.assertEqual(302, response.status_code)

    @override_switch('claim_a_facility', active=True)
    def test_superuser_can_download_attachment(self):
        attachment = self.add_attachment()
        self.login(self.superuser_email)
        response = self.client.get(
            f'{self.attachments_url}{attachment.id}/download/'
        )
        self.assertEqual(302, response.status_code)

    @override_switch('claim_a_facility', active=True)
    def test_stranger_cannot_download_attachment(self):
        attachment = self.add_attachment()
        self.login(self.other_email)
        response = self.client.get(
            f'{self.attachments_url}{attachment.id}/download/'
        )
        self.assertEqual(404, response.status_code)

    @override_switch('claim_a_facility', active=True)
    def test_anonymous_cannot_download_attachment(self):
        attachment = self.add_attachment()
        response = self.client.get(
            f'{self.attachments_url}{attachment.id}/download/'
        )
        self.assertEqual(401, response.status_code)

    # ------------------------------------------------------------------
    # Moderator claim details payload
    # ------------------------------------------------------------------

    @override_switch('claim_a_facility', active=True)
    def test_claim_details_payload_has_no_storage_urls(self):
        self.add_attachment()
        self.login(self.superuser_email)
        response = self.client.get(
            f'/api/facility-claims/{self.claim.id}/'
        )
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        self.assertEqual(1, len(data['attachments']))
        self.assertNotIn('claim_attachment', data['attachments'][0])
        self.assertIn('id', data['attachments'][0])

    # ------------------------------------------------------------------
    # Cascade fix (previously on_delete=PROTECT)
    # ------------------------------------------------------------------

    @override_switch('claim_a_facility', active=True)
    def test_deleting_claim_with_attachments_succeeds(self):
        attachment = self.add_attachment()
        # Under PROTECT this raised ProtectedError and aborted facility
        # deletion whenever a claim carried attachments.
        self.claim.delete()
        self.assertFalse(
            FacilityClaimAttachments.objects.filter(
                pk=attachment.id
            ).exists()
        )


class PendingClaimNotificationAndListTest(APITestCase):
    def setUp(self):
        self.email = 'claimant2@example.com'
        self.password = 'example123'
        self.user = User.objects.create(email=self.email)
        self.user.set_password(self.password)
        self.user.save()
        self.contributor = Contributor.objects.create(
            name='Claimant Two', admin=self.user
        )

        self.facility_list = FacilityList.objects.create(
            header='header', file_name='two', name='list-two'
        )
        self.source = Source.objects.create(
            facility_list=self.facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        self.list_item = FacilityListItem.objects.create(
            name='name two',
            address='address two',
            country_code='US',
            sector=['Apparel'],
            source=self.source,
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
        )
        self.facility = Facility.objects.create(
            name='name two',
            address='address two',
            country_code='US',
            location=Point(0, 0),
            created_from=self.list_item,
        )
        FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=self.facility,
            results='',
            facility_list_item=self.list_item,
        )
        self.claim = FacilityClaim.objects.create(
            facility=self.facility,
            contributor=self.contributor,
            contact_person='Someone',
            job_title='Something',
            status=FacilityClaimStatuses.PENDING,
        )
        self.pending_url = f'/api/facility-claims/{self.claim.id}/pending/'
        self.attachments_url = (
            f'/api/facility-claims/{self.claim.id}/attachments/'
        )
        self.claimed_url = '/api/facilities/claimed/'

    def login(self):
        self.client.post(
            '/user-login/',
            {'email': self.email, 'password': self.password},
            format='json',
        )

    @override_switch('claim_a_facility', active=True)
    def test_patch_stamps_claimant_updated_at_and_sends_email(self):
        from django.core import mail as django_mail

        self.login()
        self.assertIsNone(self.claim.claimant_updated_at)

        # The notification is deferred with transaction.on_commit;
        # TestCase never commits, so capture and execute the callbacks.
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.patch(
                self.pending_url, {'your_name': 'Someone Else'}, format='json'
            )
        self.assertEqual(200, response.status_code)

        self.claim.refresh_from_db()
        self.assertIsNotNone(self.claim.claimant_updated_at)

        self.assertEqual(1, len(django_mail.outbox))
        message = django_mail.outbox[0]
        self.assertIn(str(self.claim.id), message.subject)
        self.assertIn('contact_person', message.body)
        self.assertIn(
            f'/dashboard/claims/{self.claim.id}', message.body
        )
        # The notification carries names and a link, never documents.
        self.assertEqual([], message.attachments)

    @override_switch('claim_a_facility', active=True)
    def test_noop_patch_sends_no_email_and_no_stamp(self):
        from django.core import mail as django_mail

        self.login()
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.patch(
                self.pending_url, {'your_name': 'Someone'}, format='json'
            )
        self.assertEqual(200, response.status_code)
        self.claim.refresh_from_db()
        self.assertIsNone(self.claim.claimant_updated_at)
        self.assertEqual(0, len(django_mail.outbox))

    @override_switch('claim_a_facility', active=True)
    def test_attachment_add_stamps_and_notifies(self):
        from django.core import mail as django_mail

        self.login()
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                self.attachments_url,
                {'files': [make_png('proof.png')]},
                format='multipart',
            )
        self.assertEqual(200, response.status_code)
        self.claim.refresh_from_db()
        self.assertIsNotNone(self.claim.claimant_updated_at)
        self.assertEqual(1, len(django_mail.outbox))
        self.assertIn('proof.png', django_mail.outbox[0].body)

    @override_switch('claim_a_facility', active=True)
    def test_claimed_list_defaults_to_approved_only(self):
        self.login()
        response = self.client.get(self.claimed_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(json.loads(response.content)))

    @override_switch('claim_a_facility', active=True)
    def test_claimed_list_statuses_param_includes_pending(self):
        self.login()
        response = self.client.get(
            f'{self.claimed_url}?statuses=PENDING,APPROVED'
        )
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        self.assertEqual(1, len(data))
        self.assertEqual(FacilityClaimStatuses.PENDING, data[0]['status'])
        self.assertIn('claimant_updated_at', data[0])

    @override_switch('claim_a_facility', active=True)
    def test_claimed_list_rejects_invalid_status(self):
        self.login()
        response = self.client.get(f'{self.claimed_url}?statuses=BOGUS')
        self.assertEqual(400, response.status_code)
