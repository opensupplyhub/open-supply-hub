import json
from datetime import timedelta
from importlib import import_module
from smtplib import SMTPException
from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from django.apps import apps as django_apps
from django.contrib.gis.geos import Point
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from django.utils import timezone

from api.constants import (
    FacilityClaimAIDecisions,
    FacilityClaimDenialTypes,
    FacilityClaimReviewNoteTypes,
    FacilityClaimStatuses,
    FacilityClaimWaitingOn,
)
from api.admin import FacilityClaimAdmin
from api.models import (
    Contributor,
    Facility,
    FacilityClaim,
    FacilityClaimAttachments,
    FacilityClaimReviewNote,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.services import facility_claim_status_service
from api.services.facility_claim_status_service import (
    AUTOMATED_REVIEW_MARKER,
    get_status_label,
    is_claims_automation_account,
)

BOT_EMAIL = 'claims.bot@example.org'
PASSWORD = 'example123'
LIST_FIELDS = ('status_label', 'waiting_on', 'denial_type', 'ai_decision')
NEW_FIELDS = LIST_FIELDS + ('ai_decision_reason',)
PNG_BYTES = b'\x89PNG\r\n\x1a\n' + b'\x00' * 64


def make_png(name='document.png'):
    return SimpleUploadedFile(name, PNG_BYTES, content_type='image/png')


def automated_review_note(decision='NOT_VALIDATED', **overrides):
    '''A review note shaped like the one the claims pipeline posts.'''
    block = {
        'v': 1,
        'kind': 'automated_review',
        'decision': decision,
        'reasoning': {
            'address_match': 'The documents show a different street.',
        },
    }
    block.update(overrides)
    return 'Automated review.\n{}\n{}'.format(
        AUTOMATED_REVIEW_MARKER, json.dumps(block)
    )


class ClaimStatusFieldsTestBase(APITestCase):
    def setUp(self):
        self.claimant = User.objects.create(email='claimant@example.com')
        self.claimant.set_password(PASSWORD)
        self.claimant.save()
        self.contributor = Contributor.objects.create(
            name='Claimant Contributor', admin=self.claimant
        )

        self.moderator = User.objects.create_superuser(
            email='moderator@example.com', password=PASSWORD
        )
        self.bot = User.objects.create_superuser(
            email=BOT_EMAIL, password=PASSWORD
        )

        self.facility = self.create_facility('first')
        self.claim = self.create_claim(self.facility)

    def create_facility(self, name):
        facility_list = FacilityList.objects.create(
            header='header', file_name=name, name=name
        )
        source = Source.objects.create(
            facility_list=facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        list_item = FacilityListItem.objects.create(
            name=name,
            address='address',
            country_code='US',
            sector=['Apparel'],
            source=source,
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
        )
        facility = Facility.objects.create(
            name=name,
            address='address',
            country_code='US',
            location=Point(0, 0),
            created_from=list_item,
        )
        FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=facility,
            results='',
            facility_list_item=list_item,
        )
        return facility

    def create_claim(self, facility, **kwargs):
        return FacilityClaim.objects.create(
            facility=facility,
            contributor=self.contributor,
            contact_person='Name',
            job_title='Title',
            **kwargs,
        )

    def login(self, user):
        self.client.logout()
        self.client.login(email=user.email, password=PASSWORD)

    def post(self, action, data=None, claim=None):
        claim = claim or self.claim
        return self.client.post(
            f'/api/facility-claims/{claim.id}/{action}/',
            data or {},
            format='json',
        )

    def create_message_note(self, claim, created_at=None):
        note = FacilityClaimReviewNote.objects.create(
            claim=claim,
            author=self.moderator,
            note='Please send a document.',
            note_type=FacilityClaimReviewNoteTypes.CLAIMANT_MESSAGE,
        )
        if created_at:
            # created_at is auto_now_add, so set it after the insert.
            FacilityClaimReviewNote.objects.filter(pk=note.pk).update(
                created_at=created_at
            )
        return note


@override_settings(CLAIMS_AUTOMATION_ACCOUNT_EMAIL=BOT_EMAIL)
class ClaimWaitingOnTest(ClaimStatusFieldsTestBase):
    def test_new_claim_waits_on_os_hub(self):
        self.assertEqual(FacilityClaimStatuses.PENDING, self.claim.status)
        self.assertEqual(FacilityClaimWaitingOn.OS_HUB, self.claim.waiting_on)
        self.assertIsNone(self.claim.denial_type)
        self.assertIsNone(self.claim.ai_decision)
        self.assertIsNone(self.claim.ai_decision_reason)

    def test_moderator_message_makes_claim_wait_on_claimant(self):
        self.login(self.moderator)
        updated_at = self.claim.updated_at

        response = self.post('message-claimant', {'message': 'Hello'})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            FacilityClaimStatuses.PENDING, response.data['status']
        )
        self.assertEqual(
            FacilityClaimWaitingOn.CLAIMANT, response.data['waiting_on']
        )
        self.assertEqual('Waiting on claimant', response.data['status_label'])
        self.claim.refresh_from_db()
        self.assertEqual(
            FacilityClaimWaitingOn.CLAIMANT, self.claim.waiting_on
        )
        # Messaging a claimant has never bumped updated_at.
        self.assertEqual(updated_at, self.claim.updated_at)

    def test_automation_message_makes_claim_wait_on_claimant(self):
        self.login(self.bot)

        response = self.post('message-claimant', {'message': 'Reminder'})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.claim.refresh_from_db()
        self.assertEqual(
            FacilityClaimWaitingOn.CLAIMANT, self.claim.waiting_on
        )

    def test_waiting_on_change_is_recorded_in_claim_history(self):
        self.login(self.moderator)

        self.post('message-claimant', {'message': 'Hello'})

        self.assertEqual(
            FacilityClaimWaitingOn.CLAIMANT,
            self.claim.history.latest().waiting_on,
        )

    def test_message_on_decided_claim_does_not_set_waiting_on(self):
        self.claim.status = FacilityClaimStatuses.APPROVED
        self.claim.waiting_on = None
        self.claim.save()
        self.login(self.moderator)

        response = self.post('message-claimant', {'message': 'Hello'})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.claim.refresh_from_db()
        self.assertIsNone(self.claim.waiting_on)

    def test_failed_message_leaves_claim_waiting_on_os_hub(self):
        self.login(self.moderator)
        self.client.raise_request_exception = False

        with patch(
            'api.mail.send_mail',
            side_effect=SMTPException('simulated SMTP outage'),
        ):
            response = self.post('message-claimant', {'message': 'Hello'})

        self.assertEqual(
            status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code
        )
        self.claim.refresh_from_db()
        self.assertEqual(FacilityClaimWaitingOn.OS_HUB, self.claim.waiting_on)

    def test_non_superuser_cannot_message_claimant(self):
        self.login(self.claimant)

        response = self.post('message-claimant', {'message': 'Hello'})

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.claim.refresh_from_db()
        self.assertEqual(FacilityClaimWaitingOn.OS_HUB, self.claim.waiting_on)

    @override_switch('claim_a_facility', active=True)
    def test_claimant_edit_makes_claim_wait_on_os_hub(self):
        self.claim.waiting_on = FacilityClaimWaitingOn.CLAIMANT
        self.claim.save()
        self.login(self.claimant)

        response = self.client.patch(
            f'/api/facility-claims/{self.claim.id}/pending/',
            {'your_name': 'New Name'},
            format='json',
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.claim.refresh_from_db()
        self.assertEqual(FacilityClaimWaitingOn.OS_HUB, self.claim.waiting_on)

    @override_switch('claim_a_facility', active=True)
    def test_claimant_edit_that_changes_nothing_keeps_waiting_on(self):
        self.claim.waiting_on = FacilityClaimWaitingOn.CLAIMANT
        self.claim.save()
        self.login(self.claimant)

        response = self.client.patch(
            f'/api/facility-claims/{self.claim.id}/pending/',
            {'your_name': self.claim.contact_person},
            format='json',
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.claim.refresh_from_db()
        self.assertEqual(
            FacilityClaimWaitingOn.CLAIMANT, self.claim.waiting_on
        )

    @override_switch('claim_a_facility', active=True)
    def test_claimant_adding_document_makes_claim_wait_on_os_hub(self):
        self.claim.waiting_on = FacilityClaimWaitingOn.CLAIMANT
        self.claim.save()
        self.login(self.claimant)

        response = self.client.post(
            f'/api/facility-claims/{self.claim.id}/attachments/',
            {'files': [make_png()]},
            format='multipart',
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.claim.refresh_from_db()
        self.assertEqual(FacilityClaimWaitingOn.OS_HUB, self.claim.waiting_on)

    @override_switch('claim_a_facility', active=True)
    def test_claimant_removing_document_makes_claim_wait_on_os_hub(self):
        attachment = FacilityClaimAttachments.objects.create(
            claim=self.claim,
            file_name='existing.png',
            claim_attachment=make_png('existing.png'),
        )
        self.claim.waiting_on = FacilityClaimWaitingOn.CLAIMANT
        self.claim.save()
        self.login(self.claimant)

        response = self.client.delete(
            f'/api/facility-claims/{self.claim.id}/attachments/'
            f'{attachment.id}/'
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.claim.refresh_from_db()
        self.assertEqual(FacilityClaimWaitingOn.OS_HUB, self.claim.waiting_on)

    @override_switch('claim_a_facility', active=True)
    def test_approve_clears_waiting_on(self):
        self.login(self.moderator)

        response = self.post('approve', {'reason': 'Looks right'})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            FacilityClaimStatuses.APPROVED, response.data['status']
        )
        self.assertIsNone(response.data['waiting_on'])
        self.assertEqual('Approved', response.data['status_label'])
        self.claim.refresh_from_db()
        self.assertIsNone(self.claim.waiting_on)

    @override_switch('claim_a_facility', active=True)
    def test_revoke_keeps_waiting_on_empty(self):
        self.claim.status = FacilityClaimStatuses.APPROVED
        self.claim.save()
        self.login(self.moderator)

        response = self.post('revoke', {'reason': 'Left the company'})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            FacilityClaimStatuses.REVOKED, response.data['status']
        )
        self.assertIsNone(response.data['waiting_on'])
        self.assertEqual('Revoked', response.data['status_label'])
        self.claim.refresh_from_db()
        self.assertIsNone(self.claim.waiting_on)

    def test_saving_a_decided_claim_always_empties_waiting_on(self):
        # No caller clears waiting_on by hand: any save of a claim that
        # is not PENDING does it, whoever changed the status.
        for decided_status in (
            FacilityClaimStatuses.APPROVED,
            FacilityClaimStatuses.DENIED,
            FacilityClaimStatuses.REVOKED,
        ):
            with self.subTest(status=decided_status):
                claim = self.create_claim(
                    self.create_facility(decided_status)
                )
                self.assertEqual(
                    FacilityClaimWaitingOn.OS_HUB, claim.waiting_on
                )

                claim.status = decided_status
                claim.save()

                claim.refresh_from_db()
                self.assertEqual(decided_status, claim.status)
                self.assertIsNone(claim.waiting_on)

    def test_partial_save_of_a_decided_claim_writes_the_emptied_value(self):
        self.claim.status = FacilityClaimStatuses.DENIED

        self.claim.save(update_fields=['status'])

        self.claim.refresh_from_db()
        self.assertEqual(FacilityClaimStatuses.DENIED, self.claim.status)
        self.assertIsNone(self.claim.waiting_on)

    def test_partial_save_of_a_pending_claim_writes_only_its_fields(self):
        self.claim.contact_person = 'New Name'
        self.claim.waiting_on = FacilityClaimWaitingOn.CLAIMANT

        self.claim.save(update_fields=['contact_person'])

        self.claim.refresh_from_db()
        self.assertEqual('New Name', self.claim.contact_person)
        self.assertEqual(FacilityClaimWaitingOn.OS_HUB, self.claim.waiting_on)

    def test_claim_created_as_decided_has_no_waiting_on(self):
        claim = self.create_claim(
            self.create_facility('approved'),
            status=FacilityClaimStatuses.APPROVED,
        )

        claim.refresh_from_db()
        self.assertIsNone(claim.waiting_on)

    def test_status_cannot_be_edited_in_the_django_admin(self):
        # The admin cannot flip a status, so the save guard is the only
        # path it needs; this fails if that ever changes.
        self.assertIn('status', FacilityClaimAdmin.readonly_fields)


@override_settings(CLAIMS_AUTOMATION_ACCOUNT_EMAIL=BOT_EMAIL)
class ClaimDenialTypeTest(ClaimStatusFieldsTestBase):
    @override_switch('claim_a_facility', active=True)
    def test_moderator_denial_without_type_is_not_classified(self):
        self.login(self.moderator)

        response = self.post('deny', {'reason': 'No'})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(FacilityClaimStatuses.DENIED, response.data['status'])
        self.assertIsNone(response.data['denial_type'])
        self.assertIsNone(response.data['waiting_on'])
        self.assertEqual('Denied', response.data['status_label'])
        self.claim.refresh_from_db()
        self.assertEqual(FacilityClaimStatuses.DENIED, self.claim.status)
        self.assertIsNone(self.claim.denial_type)
        self.assertIsNone(self.claim.waiting_on)

    @override_switch('claim_a_facility', active=True)
    def test_moderator_can_deny_as_not_eligible(self):
        self.login(self.moderator)

        response = self.post('deny', {
            'reason': 'Not an employee',
            'denial_type': FacilityClaimDenialTypes.NOT_ELIGIBLE,
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(FacilityClaimStatuses.DENIED, response.data['status'])
        self.assertEqual(
            FacilityClaimDenialTypes.NOT_ELIGIBLE,
            response.data['denial_type'],
        )
        self.assertEqual(
            'Denied, not eligible', response.data['status_label']
        )
        self.claim.refresh_from_db()
        self.assertEqual(
            FacilityClaimDenialTypes.NOT_ELIGIBLE, self.claim.denial_type
        )

    @override_switch('claim_a_facility', active=True)
    def test_moderator_can_close_as_no_response(self):
        self.login(self.moderator)

        response = self.post('deny', {
            'reason': 'No reply',
            'denial_type': FacilityClaimDenialTypes.NO_RESPONSE,
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(FacilityClaimStatuses.DENIED, response.data['status'])
        self.assertEqual(
            'Closed, no response', response.data['status_label']
        )
        self.claim.refresh_from_db()
        self.assertEqual(
            FacilityClaimDenialTypes.NO_RESPONSE, self.claim.denial_type
        )

    @override_switch('claim_a_facility', active=True)
    def test_empty_denial_type_is_treated_as_not_sent(self):
        self.login(self.moderator)

        response = self.post('deny', {'reason': 'No', 'denial_type': ''})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(FacilityClaimStatuses.DENIED, response.data['status'])
        self.assertIsNone(response.data['denial_type'])
        self.assertEqual('Denied', response.data['status_label'])

    @override_switch('claim_a_facility', active=True)
    def test_empty_denial_type_from_automation_is_no_response(self):
        self.login(self.bot)

        response = self.post('deny', {'reason': 'No', 'denial_type': ''})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            FacilityClaimDenialTypes.NO_RESPONSE,
            response.data['denial_type'],
        )

    @override_switch('claim_a_facility', active=True)
    def test_unknown_denial_type_is_rejected_and_claim_stays_pending(self):
        self.login(self.moderator)

        response = self.post('deny', {
            'reason': 'No',
            'denial_type': 'SOMETHING_ELSE',
        })

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(
            'denial_type must be one of: NO_RESPONSE, NOT_ELIGIBLE.',
            response.data['detail'],
        )
        self.claim.refresh_from_db()
        self.assertEqual(FacilityClaimStatuses.PENDING, self.claim.status)
        self.assertEqual(FacilityClaimWaitingOn.OS_HUB, self.claim.waiting_on)
        self.assertIsNone(self.claim.denial_type)
        self.assertEqual(0, len(mail.outbox))

    @override_switch('claim_a_facility', active=True)
    def test_automation_denial_is_no_response(self):
        self.login(self.bot)

        response = self.post('deny', {'reason': 'No reply in 15 days'})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(FacilityClaimStatuses.DENIED, response.data['status'])
        self.assertEqual(
            FacilityClaimDenialTypes.NO_RESPONSE,
            response.data['denial_type'],
        )
        self.assertEqual(
            'Closed, no response', response.data['status_label']
        )
        self.claim.refresh_from_db()
        self.assertEqual(
            FacilityClaimDenialTypes.NO_RESPONSE, self.claim.denial_type
        )

    @override_switch('claim_a_facility', active=True)
    def test_denial_type_sent_by_automation_wins_over_the_default(self):
        self.login(self.bot)

        self.post('deny', {
            'reason': 'Ruled out',
            'denial_type': FacilityClaimDenialTypes.NOT_ELIGIBLE,
        })

        self.claim.refresh_from_db()
        self.assertEqual(
            FacilityClaimDenialTypes.NOT_ELIGIBLE, self.claim.denial_type
        )

    @override_switch('claim_a_facility', active=True)
    @override_settings(CLAIMS_AUTOMATION_ACCOUNT_EMAIL='')
    def test_no_automation_account_configured_classifies_nothing(self):
        self.login(self.bot)

        self.post('deny', {'reason': 'No'})

        self.claim.refresh_from_db()
        self.assertEqual(FacilityClaimStatuses.DENIED, self.claim.status)
        self.assertIsNone(self.claim.denial_type)

    @override_switch('claim_a_facility', active=True)
    def test_non_superuser_cannot_deny(self):
        self.login(self.claimant)

        response = self.post('deny', {
            'denial_type': FacilityClaimDenialTypes.NOT_ELIGIBLE,
        })

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.claim.refresh_from_db()
        self.assertEqual(FacilityClaimStatuses.PENDING, self.claim.status)
        self.assertIsNone(self.claim.denial_type)

    @override_switch('claim_a_facility', active=True)
    def test_anonymous_cannot_deny(self):
        response = self.post('deny', {
            'denial_type': FacilityClaimDenialTypes.NOT_ELIGIBLE,
        })

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.claim.refresh_from_db()
        self.assertEqual(FacilityClaimStatuses.PENDING, self.claim.status)

    @override_switch('claim_a_facility', active=False)
    def test_deny_with_claims_switch_off_changes_nothing(self):
        self.login(self.moderator)

        response = self.post('deny', {
            'denial_type': FacilityClaimDenialTypes.NOT_ELIGIBLE,
        })

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.claim.refresh_from_db()
        self.assertEqual(FacilityClaimStatuses.PENDING, self.claim.status)
        self.assertEqual(FacilityClaimWaitingOn.OS_HUB, self.claim.waiting_on)
        self.assertIsNone(self.claim.denial_type)


@override_settings(CLAIMS_AUTOMATION_ACCOUNT_EMAIL=BOT_EMAIL)
class ClaimAIDecisionTest(ClaimStatusFieldsTestBase):
    def assert_no_ai_decision(self):
        self.claim.refresh_from_db()
        self.assertIsNone(self.claim.ai_decision)
        self.assertIsNone(self.claim.ai_decision_reason)

    @override_switch('claim_a_facility', active=True)
    def test_automation_review_note_records_held_with_reason(self):
        self.login(self.bot)
        updated_at = self.claim.updated_at

        response = self.post('note', {'note': automated_review_note()})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            FacilityClaimStatuses.PENDING, response.data['status']
        )
        self.assertEqual(
            FacilityClaimAIDecisions.HELD, response.data['ai_decision']
        )
        self.assertEqual(
            'Automated review result: NOT_VALIDATED.\n'
            'address_match: The documents show a different street.',
            response.data['ai_decision_reason'],
        )
        # A held claim is still OS Hub's to review.
        self.assertEqual('Waiting on OS Hub', response.data['status_label'])
        self.claim.refresh_from_db()
        self.assertEqual(FacilityClaimAIDecisions.HELD, self.claim.ai_decision)
        self.assertEqual(updated_at, self.claim.updated_at)

    @override_switch('claim_a_facility', active=True)
    def test_review_without_reasoning_records_the_result_alone(self):
        self.login(self.bot)

        self.post('note', {
            'note': automated_review_note('HUMAN_REVIEW', reasoning=None),
        })

        self.claim.refresh_from_db()
        self.assertEqual(FacilityClaimAIDecisions.HELD, self.claim.ai_decision)
        self.assertEqual(
            'Automated review result: HUMAN_REVIEW.',
            self.claim.ai_decision_reason,
        )

    @override_switch('claim_a_facility', active=True)
    def test_text_after_the_review_block_is_ignored(self):
        self.login(self.bot)

        response = self.post('note', {
            'note': automated_review_note() + '\n\nEnd of review. {draft}',
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            FacilityClaimAIDecisions.HELD, response.data['ai_decision']
        )
        self.assertEqual(
            'Automated review result: NOT_VALIDATED.\n'
            'address_match: The documents show a different street.',
            response.data['ai_decision_reason'],
        )

    @override_switch('claim_a_facility', active=True)
    def test_automation_note_without_review_block_records_nothing(self):
        self.login(self.bot)

        with self.assertNoLogs(
            facility_claim_status_service.log, level='WARNING'
        ):
            response = self.post('note', {'note': 'Extracted document text.'})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assert_no_ai_decision()

    @override_switch('claim_a_facility', active=True)
    def test_unreadable_review_block_saves_the_note_and_records_nothing(self):
        self.login(self.bot)
        notes = (
            f'{AUTOMATED_REVIEW_MARKER}\n{{not json',
            f'{AUTOMATED_REVIEW_MARKER}\nno block here',
            f'{AUTOMATED_REVIEW_MARKER}\n{{"v": 1, "kind": "other"}}',
            automated_review_note(v=2),
        )

        for note in notes:
            with self.subTest(note=note):
                with self.assertLogs(
                    facility_claim_status_service.log, level='WARNING'
                ) as logs:
                    response = self.post('note', {'note': note})
                self.assertEqual(status.HTTP_200_OK, response.status_code)
                self.assert_no_ai_decision()
                self.assertEqual(1, len(logs.output))
                self.assertIn(f'Claim {self.claim.id}:', logs.output[0])
                # The log line names the claim and never quotes the note.
                self.assertNotIn(AUTOMATED_REVIEW_MARKER, logs.output[0])

        self.assertEqual(
            len(notes),
            FacilityClaimReviewNote.objects.filter(claim=self.claim).count(),
        )

    @override_switch('claim_a_facility', active=True)
    def test_review_block_posted_by_moderator_records_nothing(self):
        self.login(self.moderator)

        response = self.post('note', {'note': automated_review_note()})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assert_no_ai_decision()

    @override_switch('claim_a_facility', active=True)
    def test_review_note_on_decided_claim_records_nothing(self):
        self.claim.status = FacilityClaimStatuses.DENIED
        self.claim.save()
        self.login(self.bot)

        response = self.post('note', {'note': automated_review_note()})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assert_no_ai_decision()

    @override_switch('claim_a_facility', active=True)
    def test_non_superuser_cannot_post_a_review_note(self):
        self.login(self.claimant)

        response = self.post('note', {'note': automated_review_note()})

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assert_no_ai_decision()

    @override_switch('claim_a_facility', active=True)
    def test_automation_approval_records_approved_and_keeps_reason(self):
        self.login(self.bot)
        self.post('note', {'note': automated_review_note('VALIDATED')})

        response = self.post('approve')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            FacilityClaimStatuses.APPROVED, response.data['status']
        )
        self.assertEqual(
            FacilityClaimAIDecisions.APPROVED, response.data['ai_decision']
        )
        self.assertEqual(
            'Automated review result: VALIDATED.\n'
            'address_match: The documents show a different street.',
            response.data['ai_decision_reason'],
        )
        self.claim.refresh_from_db()
        self.assertEqual(
            FacilityClaimAIDecisions.APPROVED, self.claim.ai_decision
        )

    @override_switch('claim_a_facility', active=True)
    def test_automation_approval_reason_replaces_the_review_reason(self):
        self.login(self.bot)
        self.post('note', {'note': automated_review_note('VALIDATED')})

        self.post('approve', {'reason': 'All four checks passed'})

        self.claim.refresh_from_db()
        self.assertEqual(
            FacilityClaimAIDecisions.APPROVED, self.claim.ai_decision
        )
        self.assertEqual(
            'All four checks passed', self.claim.ai_decision_reason
        )

    @override_switch('claim_a_facility', active=True)
    def test_moderator_approval_records_no_ai_decision(self):
        self.login(self.moderator)

        response = self.post('approve', {'reason': 'Looks right'})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assert_no_ai_decision()

    @override_switch('claim_a_facility', active=True)
    def test_moderator_approval_of_held_claim_keeps_it_held(self):
        self.login(self.bot)
        self.post('note', {'note': automated_review_note()})
        self.login(self.moderator)

        response = self.post('approve', {'reason': 'Checked by phone'})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.claim.refresh_from_db()
        self.assertEqual(FacilityClaimStatuses.APPROVED, self.claim.status)
        self.assertEqual(FacilityClaimAIDecisions.HELD, self.claim.ai_decision)


@override_settings(CLAIMS_AUTOMATION_ACCOUNT_EMAIL=BOT_EMAIL)
class ClaimStatusFieldsPayloadTest(ClaimStatusFieldsTestBase):
    def test_moderator_list_carries_the_fields_and_the_same_statuses(self):
        denied = self.create_claim(
            self.create_facility('second'),
            status=FacilityClaimStatuses.DENIED,
            waiting_on=None,
            denial_type=FacilityClaimDenialTypes.NO_RESPONSE,
            ai_decision=FacilityClaimAIDecisions.HELD,
            ai_decision_reason='Automated review result: NOT_VALIDATED.',
        )
        self.login(self.moderator)

        response = self.client.get('/api/facility-claims/')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        by_id = {claim['id']: claim for claim in response.data}
        self.assertEqual(
            {
                'status': FacilityClaimStatuses.PENDING,
                'status_label': 'Waiting on OS Hub',
                'waiting_on': FacilityClaimWaitingOn.OS_HUB,
                'denial_type': None,
                'ai_decision': None,
            },
            {
                key: by_id[self.claim.id][key]
                for key in ('status', *LIST_FIELDS)
            },
        )
        self.assertEqual(
            {
                'status': FacilityClaimStatuses.DENIED,
                'status_label': 'Closed, no response',
                'waiting_on': None,
                'denial_type': FacilityClaimDenialTypes.NO_RESPONSE,
                'ai_decision': FacilityClaimAIDecisions.HELD,
            },
            {key: by_id[denied.id][key] for key in ('status', *LIST_FIELDS)},
        )
        # The reason can be long, so only the detail payload carries it.
        self.assertNotIn('ai_decision_reason', by_id[denied.id])

    def test_status_filter_still_uses_the_four_statuses(self):
        self.create_claim(
            self.create_facility('second'),
            status=FacilityClaimStatuses.DENIED,
            waiting_on=None,
            denial_type=FacilityClaimDenialTypes.NO_RESPONSE,
        )
        self.login(self.moderator)

        response = self.client.get('/api/facility-claims/?statuses=DENIED')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            [FacilityClaimStatuses.DENIED],
            [claim['status'] for claim in response.data],
        )

    def test_stored_status_values_are_unchanged(self):
        self.assertEqual(
            ['PENDING', 'APPROVED', 'DENIED', 'REVOKED'],
            [value for value, _ in FacilityClaim.STATUS_CHOICES],
        )

    @override_switch('claim_a_facility', active=True)
    def test_moderator_detail_carries_all_the_fields(self):
        self.login(self.moderator)

        response = self.client.get(f'/api/facility-claims/{self.claim.id}/')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            {
                'status_label': 'Waiting on OS Hub',
                'waiting_on': FacilityClaimWaitingOn.OS_HUB,
                'denial_type': None,
                'ai_decision': None,
                'ai_decision_reason': None,
            },
            {key: response.data[key] for key in NEW_FIELDS},
        )

    @override_switch('claim_a_facility', active=True)
    def test_claimant_cannot_read_the_moderator_payloads(self):
        self.login(self.claimant)

        list_response = self.client.get('/api/facility-claims/')
        detail_response = self.client.get(
            f'/api/facility-claims/{self.claim.id}/'
        )

        self.assertEqual(status.HTTP_403_FORBIDDEN, list_response.status_code)
        self.assertEqual(
            status.HTTP_403_FORBIDDEN, detail_response.status_code
        )

    @override_switch('claim_a_facility', active=True)
    def test_claimant_payloads_do_not_carry_the_fields(self):
        self.claim.ai_decision = FacilityClaimAIDecisions.HELD
        self.claim.ai_decision_reason = 'Automated review result: HELD.'
        self.claim.save()
        self.login(self.claimant)

        pending = self.client.get(
            f'/api/facility-claims/{self.claim.id}/pending/'
        )
        claimed = self.client.get('/api/facilities/claimed/?statuses=PENDING')

        self.assertEqual(status.HTTP_200_OK, pending.status_code)
        self.assertEqual(status.HTTP_200_OK, claimed.status_code)
        self.assertEqual(1, len(claimed.data))
        for field in NEW_FIELDS:
            with self.subTest(field=field):
                self.assertNotIn(field, pending.data)
                self.assertNotIn(field, claimed.data[0])


class ClaimStatusLabelTest(SimpleTestCase):
    def test_label_for_every_status(self):
        cases = (
            (FacilityClaimStatuses.PENDING, FacilityClaimWaitingOn.OS_HUB,
             None, 'Waiting on OS Hub'),
            (FacilityClaimStatuses.PENDING, FacilityClaimWaitingOn.CLAIMANT,
             None, 'Waiting on claimant'),
            # A pending claim with no value reads as ours, never as lost.
            (FacilityClaimStatuses.PENDING, None, None, 'Waiting on OS Hub'),
            (FacilityClaimStatuses.APPROVED, None, None, 'Approved'),
            (FacilityClaimStatuses.DENIED, None,
             FacilityClaimDenialTypes.NO_RESPONSE, 'Closed, no response'),
            (FacilityClaimStatuses.DENIED, None,
             FacilityClaimDenialTypes.NOT_ELIGIBLE, 'Denied, not eligible'),
            (FacilityClaimStatuses.DENIED, None, None, 'Denied'),
            (FacilityClaimStatuses.REVOKED, None, None, 'Revoked'),
            # Stale values on a decided claim do not leak into the label.
            (FacilityClaimStatuses.APPROVED, FacilityClaimWaitingOn.CLAIMANT,
             FacilityClaimDenialTypes.NO_RESPONSE, 'Approved'),
        )

        for claim_status, waiting_on, denial_type, label in cases:
            with self.subTest(label=label):
                claim = FacilityClaim(
                    status=claim_status,
                    waiting_on=waiting_on,
                    denial_type=denial_type,
                )
                self.assertEqual(label, get_status_label(claim))


class ClaimsAutomationAccountTest(SimpleTestCase):
    def test_matches_the_configured_account_in_any_case(self):
        with self.settings(
            CLAIMS_AUTOMATION_ACCOUNT_EMAIL=' Claims.Bot@Example.org '
        ):
            self.assertTrue(
                is_claims_automation_account(User(email=BOT_EMAIL))
            )
            self.assertFalse(
                is_claims_automation_account(User(email='other@example.org'))
            )

    def test_empty_setting_matches_nobody(self):
        with self.settings(CLAIMS_AUTOMATION_ACCOUNT_EMAIL=''):
            self.assertFalse(
                is_claims_automation_account(User(email=BOT_EMAIL))
            )
            self.assertFalse(is_claims_automation_account(User(email='')))


class ClaimWaitingOnBackfillTest(ClaimStatusFieldsTestBase):
    '''
    The data step of migration 0271. The schema steps run when the test
    database is built; this runs the backfill against rows in the state
    the migration finds them in: waiting_on empty on every claim.
    '''

    def setUp(self):
        super().setUp()
        self.now = timezone.now()
        self.new = self.claim
        self.messaged = self.create_claim(self.create_facility('messaged'))
        self.create_message_note(self.messaged)
        self.replied = self.create_claim(
            self.create_facility('replied'),
            claimant_updated_at=self.now,
        )
        self.create_message_note(
            self.replied, created_at=self.now - timedelta(days=2)
        )
        self.messaged_again = self.create_claim(
            self.create_facility('messaged again'),
            claimant_updated_at=self.now - timedelta(days=2),
        )
        self.create_message_note(
            self.messaged_again, created_at=self.now - timedelta(days=3)
        )
        self.create_message_note(
            self.messaged_again, created_at=self.now - timedelta(days=1)
        )
        self.internal_note_only = self.create_claim(
            self.create_facility('internal')
        )
        FacilityClaimReviewNote.objects.create(
            claim=self.internal_note_only,
            author=self.moderator,
            note='Checked the website.',
        )
        self.decided = {
            decided_status: self.create_claim(
                self.create_facility(decided_status),
                status=decided_status,
            )
            for decided_status in (
                FacilityClaimStatuses.APPROVED,
                FacilityClaimStatuses.DENIED,
                FacilityClaimStatuses.REVOKED,
            )
        }
        self.create_message_note(
            self.decided[FacilityClaimStatuses.DENIED]
        )
        FacilityClaim.objects.update(waiting_on=None)

    def run_backfill(self):
        migration = import_module(
            'api.migrations.0271_add_claim_status_detail_fields'
        )
        migration.backfill_waiting_on(django_apps, None)

    def waiting_on(self, claim):
        claim.refresh_from_db()
        return claim.waiting_on

    def test_pending_claims_get_who_they_wait_on(self):
        self.run_backfill()

        self.assertEqual(
            FacilityClaimWaitingOn.OS_HUB, self.waiting_on(self.new)
        )
        self.assertEqual(
            FacilityClaimWaitingOn.CLAIMANT, self.waiting_on(self.messaged)
        )
        self.assertEqual(
            FacilityClaimWaitingOn.OS_HUB, self.waiting_on(self.replied)
        )
        self.assertEqual(
            FacilityClaimWaitingOn.CLAIMANT,
            self.waiting_on(self.messaged_again),
        )
        self.assertEqual(
            FacilityClaimWaitingOn.OS_HUB,
            self.waiting_on(self.internal_note_only),
        )

    def test_decided_claims_stay_empty_and_keep_their_status(self):
        self.run_backfill()

        for decided_status, claim in self.decided.items():
            with self.subTest(status=decided_status):
                self.assertIsNone(self.waiting_on(claim))
                self.assertEqual(decided_status, claim.status)
                self.assertIsNone(claim.denial_type)
                self.assertIsNone(claim.ai_decision)

    def test_backfill_runs_two_queries_whatever_the_claim_count(self):
        with self.assertNumQueries(2):
            self.run_backfill()
