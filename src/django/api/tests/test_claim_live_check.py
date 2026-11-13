import json
from datetime import timedelta
from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from django.contrib.gis.geos import Point
from django.core import mail
from django.test import SimpleTestCase, override_settings
from django.utils import timezone

from api.constants import (
    FacilityClaimLiveCheckStatuses,
    FacilityClaimReviewNoteTypes,
    FacilityClaimStatuses,
)
from api.models import (
    Contributor,
    Facility,
    FacilityClaim,
    FacilityClaimAttachments,
    FacilityClaimLiveCheck,
    FacilityClaimReviewNote,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.services import claim_live_check_service, claim_live_review_trigger
from api.services.claim_live_check_fixes import (
    CHECK_ADDRESS,
    CHECK_AFFILIATION,
    CHECK_DOCUMENTS,
    CHECK_MANAGER,
    CHECK_NAME,
    FIX_COMPANY_ADDRESS_DOCUMENT,
    FIX_COMPANY_NAME_DOCUMENT,
    FIX_NAME_AND_COMPANY_DOCUMENT,
    FIX_UNREADABLE_DOCUMENT,
    FIX_UPLOAD_DOCUMENT,
    FIX_TEXTS,
    FIX_WORK_EMAIL,
    FIXES,
    failed_checks,
    fixes_for_review,
    is_free_mail,
)
from api.services.claim_live_check_service import (
    CLAIM_LIVE_CHECK_SWITCH,
    LIVE_CHECK_TIMEOUT_SECONDS,
    MAX_LIVE_CHECKS_PER_CLAIM,
    PAGE_LEFT_AFTER_SECONDS,
    STUB_DELAY_SECONDS,
    get_dev_stub,
)
from api.services.claim_live_review_trigger import trigger_live_review
from api.services.facility_claim_status_service import (
    AUTOMATED_REVIEW_MARKER,
)

BOT_EMAIL = 'claims.pipeline@example.org'
PASSWORD = 'example123'
FUNCTION = 'claims-review-function'
WORK_EMAIL = 'claimant@factory.example.com'

CHECKING = FacilityClaimLiveCheckStatuses.CHECKING
PASSED = FacilityClaimLiveCheckStatuses.PASSED
NOT_PASSED = FacilityClaimLiveCheckStatuses.NOT_PASSED
UNAVAILABLE = FacilityClaimLiveCheckStatuses.UNAVAILABLE

# Test values only. The real thresholds live with the pipeline and
# reach this app inside each review block.
THRESHOLD = 0.5
PASS_SCORE = 0.9
FAIL_SCORE = 0.1


def review_block(failed=(), **overrides):
    '''A review block shaped like the pipeline's, failing `failed`.'''
    checks = (
        CHECK_ADDRESS,
        CHECK_NAME,
        CHECK_DOCUMENTS,
        CHECK_AFFILIATION,
        CHECK_MANAGER,
    )
    block = {
        'v': 1,
        'kind': 'automated_review',
        'decision': 'NOT_VALIDATED' if failed else 'VALIDATED',
        'confidence_scores': {
            check: FAIL_SCORE if check in failed else PASS_SCORE
            for check in checks
        },
        'threshold_config_snapshot': {
            'score_thresholds': {check: THRESHOLD for check in checks},
        },
        'skipped_dimensions': {},
        'reasoning': {
            check: 'Model reasoning that must not reach a claimant.'
            for check in failed
        },
    }
    block.update(overrides)
    return block


def review_note(block):
    return 'Automated Claim Review\n\n{}\n{}'.format(
        AUTOMATED_REVIEW_MARKER, json.dumps(block)
    )


class ClaimLiveCheckFixesTest(SimpleTestCase):
    '''The mapping from the pipeline's review to the preset fixes.'''

    def fixes(self, failed, email=WORK_EMAIL, has_attachments=True):
        return fixes_for_review(
            review_block(failed), email, has_attachments
        )

    def test_free_mail_addresses_are_recognised(self):
        self.assertTrue(is_free_mail('someone@gmail.com'))
        self.assertTrue(is_free_mail(' Someone@163.COM '))
        self.assertFalse(is_free_mail(WORK_EMAIL))
        self.assertFalse(is_free_mail(''))
        self.assertFalse(is_free_mail(None))
        self.assertFalse(is_free_mail('gmail.com@factory.example.com'))

    def test_affiliation_failed_with_free_mail_asks_for_work_email(self):
        self.assertEqual(
            self.fixes([CHECK_AFFILIATION], email='someone@gmail.com'),
            [FIX_WORK_EMAIL],
        )

    def test_affiliation_failed_with_work_email_asks_for_who_document(self):
        self.assertEqual(
            self.fixes([CHECK_AFFILIATION]),
            [FIX_NAME_AND_COMPANY_DOCUMENT],
        )

    def test_manager_failed_asks_for_who_document(self):
        self.assertEqual(
            self.fixes([CHECK_MANAGER]),
            [FIX_NAME_AND_COMPANY_DOCUMENT],
        )

    def test_name_failed_asks_for_company_name_document(self):
        self.assertEqual(
            self.fixes([CHECK_NAME]), [FIX_COMPANY_NAME_DOCUMENT]
        )

    def test_address_failed_asks_for_company_address_document(self):
        self.assertEqual(
            self.fixes([CHECK_ADDRESS]), [FIX_COMPANY_ADDRESS_DOCUMENT]
        )

    def test_documents_failed_with_attachments_says_unreadable(self):
        self.assertEqual(
            self.fixes([CHECK_DOCUMENTS]), [FIX_UNREADABLE_DOCUMENT]
        )

    def test_documents_failed_without_attachments_asks_for_upload(self):
        self.assertEqual(
            self.fixes([CHECK_DOCUMENTS], has_attachments=False),
            [FIX_UPLOAD_DOCUMENT],
        )

    def test_held_claim_without_attachments_is_asked_for_upload(self):
        self.assertEqual(
            self.fixes([CHECK_ADDRESS], has_attachments=False),
            [FIX_UPLOAD_DOCUMENT, FIX_COMPANY_ADDRESS_DOCUMENT],
        )

    def test_several_failures_come_in_display_order_and_capped(self):
        fixes = self.fixes(
            [
                CHECK_ADDRESS,
                CHECK_NAME,
                CHECK_DOCUMENTS,
                CHECK_AFFILIATION,
                CHECK_MANAGER,
            ],
            email='someone@gmail.com',
        )
        self.assertEqual(fixes, [
            FIX_WORK_EMAIL,
            FIX_UNREADABLE_DOCUMENT,
            FIX_NAME_AND_COMPANY_DOCUMENT,
            FIX_COMPANY_NAME_DOCUMENT,
            FIX_COMPANY_ADDRESS_DOCUMENT,
        ])
        self.assertLessEqual(len(fixes), 5)

    def test_every_fix_is_one_of_the_six_presets(self):
        self.assertEqual(len(FIXES), 6)
        self.assertEqual(len(set(FIXES)), 6)

    def test_every_fix_has_its_preset_line(self):
        self.assertEqual(set(FIX_TEXTS), set(FIXES))
        self.assertEqual(
            FIX_TEXTS[FIX_WORK_EMAIL],
            'Use a work email, not a personal email.',
        )

    def test_no_failed_check_gives_no_fixes(self):
        self.assertEqual(self.fixes([]), [])
        self.assertEqual(self.fixes([], has_attachments=False), [])

    def test_skipped_check_does_not_fail(self):
        block = review_block(
            [CHECK_ADDRESS],
            skipped_dimensions={CHECK_ADDRESS: 'skip rule'},
        )
        self.assertEqual(failed_checks(block), set())

    def test_reason_alone_marks_a_check_failed(self):
        block = review_block()
        block['threshold_config_snapshot'] = {}
        block['reasoning'] = {CHECK_NAME: 'Different legal entity.'}
        self.assertEqual(failed_checks(block), {CHECK_NAME})

    def test_score_under_threshold_alone_marks_a_check_failed(self):
        block = review_block([CHECK_NAME], reasoning={})
        self.assertEqual(failed_checks(block), {CHECK_NAME})

    def test_malformed_block_fails_nothing(self):
        for block in (
            {},
            {'confidence_scores': 'high', 'reasoning': ['x']},
            {
                'confidence_scores': {CHECK_NAME: 'low'},
                'threshold_config_snapshot': {
                    'score_thresholds': {CHECK_NAME: None},
                },
                'skipped_dimensions': 'none',
            },
        ):
            self.assertEqual(failed_checks(block), set())
            self.assertEqual(fixes_for_review(block, WORK_EMAIL, True), [])


class ClaimLiveReviewTriggerTest(SimpleTestCase):
    '''The one call the app makes to the pipeline.'''

    @override_settings(CLAIMS_LIVE_REVIEW_FUNCTION='')
    @patch.object(claim_live_review_trigger, 'boto3')
    def test_not_configured_calls_nothing(self, boto3):
        self.assertFalse(trigger_live_review(1))
        boto3.client.assert_not_called()

    @override_settings(CLAIMS_LIVE_REVIEW_FUNCTION=FUNCTION)
    @patch.object(claim_live_review_trigger, 'boto3')
    def test_accepted_invocation_is_asynchronous_and_carries_claim_id(
        self, boto3
    ):
        invoke = boto3.client.return_value.invoke
        invoke.return_value = {'StatusCode': 202}

        self.assertTrue(trigger_live_review(42))

        self.assertEqual(boto3.client.call_args.args, ('lambda',))
        kwargs = invoke.call_args.kwargs
        self.assertEqual(kwargs['FunctionName'], FUNCTION)
        self.assertEqual(kwargs['InvocationType'], 'Event')
        self.assertEqual(json.loads(kwargs['Payload']), {'claim_id': 42})

    @override_settings(CLAIMS_LIVE_REVIEW_FUNCTION=FUNCTION)
    @patch.object(claim_live_review_trigger, 'boto3')
    def test_unaccepted_invocation_is_not_triggered(self, boto3):
        boto3.client.return_value.invoke.return_value = {'StatusCode': 500}
        self.assertFalse(trigger_live_review(42))

    @override_settings(CLAIMS_LIVE_REVIEW_FUNCTION=FUNCTION)
    @patch.object(claim_live_review_trigger, 'boto3')
    def test_failed_invocation_never_raises(self, boto3):
        boto3.client.return_value.invoke.side_effect = RuntimeError('down')
        self.assertFalse(trigger_live_review(42))

    @override_settings(CLAIMS_LIVE_REVIEW_FUNCTION=FUNCTION)
    @patch.object(claim_live_review_trigger, 'boto3')
    def test_failing_client_never_raises(self, boto3):
        boto3.client.side_effect = RuntimeError('no credentials')
        self.assertFalse(trigger_live_review(42))


class ClaimLiveCheckDevStubSettingTest(SimpleTestCase):
    @override_settings(DEBUG=True, CLAIMS_LIVE_REVIEW_DEV_STUB=' pass ')
    def test_stub_is_read_with_debug_on(self):
        self.assertEqual(get_dev_stub(), 'pass')

    @override_settings(DEBUG=False, CLAIMS_LIVE_REVIEW_DEV_STUB='pass')
    def test_stub_is_ignored_with_debug_off(self):
        self.assertEqual(get_dev_stub(), '')


@override_settings(
    CLAIMS_AUTOMATION_ACCOUNT_EMAIL=BOT_EMAIL,
    CLAIMS_LIVE_REVIEW_FUNCTION=FUNCTION,
    CLAIMS_LIVE_REVIEW_DEV_STUB='',
)
@override_switch('claim_a_facility', active=True)
@override_switch(CLAIM_LIVE_CHECK_SWITCH, active=True)
class ClaimLiveCheckTestBase(APITestCase):
    def setUp(self):
        self.claimant = self.create_user(WORK_EMAIL)
        self.contributor = Contributor.objects.create(
            name='Claimant Contributor', admin=self.claimant
        )
        self.other_user = self.create_user('other@example.com')
        Contributor.objects.create(
            name='Other Contributor', admin=self.other_user
        )
        self.moderator = User.objects.create_superuser(
            email='moderator@example.com', password=PASSWORD
        )
        self.bot = User.objects.create_superuser(
            email=BOT_EMAIL, password=PASSWORD
        )

        self.facility = self.create_facility()
        self.claim = FacilityClaim.objects.create(
            facility=self.facility,
            contributor=self.contributor,
            contact_person='Name',
            job_title='Title',
        )
        self.url = f'/api/facility-claims/{self.claim.id}/live-check/'

        trigger_patch = patch.object(
            claim_live_check_service,
            'trigger_live_review',
            return_value=True,
        )
        self.trigger = trigger_patch.start()
        self.addCleanup(trigger_patch.stop)

        self.login(self.claimant)

    def create_user(self, email):
        user = User.objects.create(email=email)
        user.set_password(PASSWORD)
        user.save()
        return user

    def create_facility(self):
        facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='one'
        )
        source = Source.objects.create(
            facility_list=facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        list_item = FacilityListItem.objects.create(
            name='Name',
            address='Address',
            country_code='US',
            sector=['Apparel'],
            source=source,
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
        )
        facility = Facility.objects.create(
            name='Name',
            address='Address',
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

    def login(self, user):
        self.client.logout()
        self.client.login(email=user.email, password=PASSWORD)

    def start(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.json()

    def poll(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.json()

    def checks(self):
        return FacilityClaimLiveCheck.objects.filter(claim=self.claim)

    def age_checks(self, seconds):
        '''Make every check of the claim `seconds` older.'''
        for check in self.checks():
            FacilityClaimLiveCheck.objects.filter(pk=check.pk).update(
                created_at=check.created_at - timedelta(seconds=seconds)
            )

    def post_review(self, block, author=None):
        return FacilityClaimReviewNote.objects.create(
            claim=self.claim,
            author=author or self.bot,
            note=review_note(block),
            note_type=FacilityClaimReviewNoteTypes.INTERNAL,
        )

    def approve(self):
        self.claim.status = FacilityClaimStatuses.APPROVED
        self.claim.save()

    def claimant_edits(self):
        self.claim.claimant_updated_at = timezone.now()
        self.claim.save()


class ClaimLiveCheckAccessTest(ClaimLiveCheckTestBase):
    def test_switch_off_returns_404_and_starts_nothing(self):
        with override_switch(CLAIM_LIVE_CHECK_SWITCH, active=False):
            self.assertEqual(
                self.client.post(self.url).status_code,
                status.HTTP_404_NOT_FOUND,
            )
            self.assertEqual(
                self.client.get(self.url).status_code,
                status.HTTP_404_NOT_FOUND,
            )
        self.assertFalse(self.checks().exists())
        self.trigger.assert_not_called()

    def test_claim_a_facility_switch_off_returns_404(self):
        with override_switch('claim_a_facility', active=False):
            self.assertEqual(
                self.client.post(self.url).status_code,
                status.HTTP_404_NOT_FOUND,
            )

    def test_anonymous_user_cannot_start_or_read_a_check(self):
        self.client.logout()
        for response in (self.client.post(self.url),
                         self.client.get(self.url)):
            self.assertIn(response.status_code, (
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ))
        self.assertFalse(self.checks().exists())

    def test_another_claimant_cannot_start_or_read_a_check(self):
        self.start()
        self.trigger.reset_mock()
        self.login(self.other_user)
        self.assertEqual(
            self.client.post(self.url).status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            self.client.get(self.url).status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.trigger.assert_not_called()

    def test_moderator_who_does_not_own_the_claim_gets_404(self):
        self.login(self.moderator)
        self.assertEqual(
            self.client.get(self.url).status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_unknown_claim_returns_404(self):
        response = self.client.post('/api/facility-claims/0/live-check/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_response_carries_only_status_fixes_and_checks_left(self):
        self.start()
        self.post_review(review_block([CHECK_ADDRESS]))
        self.claim.ai_decision_reason = 'Moderator-only reason.'
        self.claim.save()

        state = self.poll()

        self.assertEqual(
            set(state), {'status', 'fixes', 'checks_left'}
        )
        body = json.dumps(state)
        self.assertNotIn('reasoning', body)
        self.assertNotIn('Moderator-only', body)
        self.assertNotIn(str(FAIL_SCORE), body)


class ClaimLiveCheckOutcomeTest(ClaimLiveCheckTestBase):
    def test_start_asks_the_pipeline_and_returns_checking(self):
        state = self.start()

        self.assertEqual(state, {
            'status': CHECKING,
            'fixes': [],
            'checks_left': MAX_LIVE_CHECKS_PER_CLAIM - 1,
        })
        self.trigger.assert_called_once_with(self.claim.id)
        self.assertEqual(self.checks().count(), 1)
        self.assertEqual(self.poll()['status'], CHECKING)

    def test_start_leaves_the_claim_untouched(self):
        before = FacilityClaim.objects.values().get(pk=self.claim.pk)
        self.start()
        self.poll()
        after = FacilityClaim.objects.values().get(pk=self.claim.pk)
        self.assertEqual(before, after)

    def test_approved_claim_passes(self):
        self.start()
        self.approve()

        state = self.poll()

        self.assertEqual(state['status'], PASSED)
        self.assertEqual(state['fixes'], [])
        self.assertEqual(state['checks_left'], 0)
        self.assertEqual(self.checks().get().status, PASSED)

    def test_held_claim_does_not_pass_and_lists_fixes(self):
        self.start()
        self.post_review(review_block([CHECK_ADDRESS, CHECK_AFFILIATION]))

        state = self.poll()

        self.assertEqual(state['status'], NOT_PASSED)
        self.assertEqual(state['fixes'], [
            FIX_UPLOAD_DOCUMENT,
            FIX_NAME_AND_COMPANY_DOCUMENT,
            FIX_COMPANY_ADDRESS_DOCUMENT,
        ])
        self.claim.refresh_from_db()
        self.assertEqual(self.claim.status, FacilityClaimStatuses.PENDING)

    def test_fixes_use_the_claimants_email_and_attachments(self):
        self.claimant.email = 'claimant@gmail.com'
        self.claimant.save()
        self.login(self.claimant)
        FacilityClaimAttachments.objects.create(
            claim=self.claim,
            file_name='badge.png',
            claim_attachment='badge.png',
        )
        self.start()
        self.post_review(review_block([CHECK_DOCUMENTS, CHECK_AFFILIATION]))

        self.assertEqual(
            self.poll()['fixes'],
            [FIX_WORK_EMAIL, FIX_UNREADABLE_DOCUMENT],
        )

    def test_settled_check_is_not_settled_again(self):
        self.start()
        self.post_review(review_block([CHECK_ADDRESS]))
        first = self.poll()
        self.post_review(review_block([CHECK_NAME]))

        self.assertEqual(self.poll(), first)

    def test_validated_review_keeps_checking_until_the_approval(self):
        self.start()
        self.post_review(review_block())

        self.assertEqual(self.poll()['status'], CHECKING)

        self.approve()
        self.assertEqual(self.poll()['status'], PASSED)

    def test_validated_review_without_approval_times_out(self):
        self.start()
        self.post_review(review_block())
        self.age_checks(LIVE_CHECK_TIMEOUT_SECONDS)

        self.assertEqual(self.poll()['status'], UNAVAILABLE)

    def test_review_by_anyone_but_the_pipeline_is_ignored(self):
        self.start()
        self.post_review(
            review_block([CHECK_ADDRESS]), author=self.moderator
        )

        self.assertEqual(self.poll()['status'], CHECKING)

    def test_review_posted_before_the_check_is_ignored(self):
        note = self.post_review(review_block([CHECK_ADDRESS]))
        FacilityClaimReviewNote.objects.filter(pk=note.pk).update(
            created_at=timezone.now() - timedelta(hours=1)
        )
        self.start()

        self.assertEqual(self.poll()['status'], CHECKING)

    def test_note_without_a_readable_block_is_ignored(self):
        self.start()
        FacilityClaimReviewNote.objects.create(
            claim=self.claim,
            author=self.bot,
            note='{}\nnot json'.format(AUTOMATED_REVIEW_MARKER),
        )

        self.assertEqual(self.poll()['status'], CHECKING)

    def test_held_for_an_unknown_reason_is_unavailable(self):
        self.start()
        self.post_review(
            review_block(decision='NOT_VALIDATED', reasoning={})
        )

        state = self.poll()

        self.assertEqual(state['status'], UNAVAILABLE)
        self.assertEqual(state['fixes'], [])

    def test_denied_claim_is_unavailable(self):
        self.start()
        self.claim.status = FacilityClaimStatuses.DENIED
        self.claim.save()

        self.assertEqual(self.poll()['status'], UNAVAILABLE)

    def test_check_with_no_answer_times_out(self):
        self.start()
        self.age_checks(LIVE_CHECK_TIMEOUT_SECONDS - 5)
        self.assertEqual(self.poll()['status'], CHECKING)

        self.age_checks(5)
        self.assertEqual(self.poll()['status'], UNAVAILABLE)
        self.assertEqual(self.checks().get().status, UNAVAILABLE)

    def test_read_before_any_check_is_unavailable(self):
        self.assertEqual(self.poll(), {
            'status': UNAVAILABLE,
            'fixes': [],
            'checks_left': MAX_LIVE_CHECKS_PER_CLAIM,
        })


class ClaimLiveCheckFailOpenTest(ClaimLiveCheckTestBase):
    @override_settings(CLAIMS_LIVE_REVIEW_FUNCTION='')
    def test_not_configured_is_unavailable_and_records_nothing(self):
        state = self.start()

        self.assertEqual(state, {
            'status': UNAVAILABLE,
            'fixes': [],
            'checks_left': MAX_LIVE_CHECKS_PER_CLAIM,
        })
        self.assertFalse(self.checks().exists())
        self.trigger.assert_not_called()

    def test_failed_trigger_is_unavailable(self):
        self.trigger.return_value = False

        state = self.start()

        self.assertEqual(state['status'], UNAVAILABLE)
        self.assertEqual(self.checks().get().status, UNAVAILABLE)
        self.assertEqual(self.poll()['status'], UNAVAILABLE)

    def test_unavailable_check_can_be_tried_again(self):
        self.trigger.return_value = False
        self.start()
        self.trigger.return_value = True

        self.assertEqual(self.start()['status'], CHECKING)
        self.assertEqual(self.checks().count(), 2)

    def test_unexpected_error_is_answered_as_unavailable(self):
        self.trigger.side_effect = RuntimeError('boom')

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {
            'status': UNAVAILABLE,
            'fixes': [],
            'checks_left': 0,
        })
        self.assertFalse(self.checks().exists())
        self.claim.refresh_from_db()
        self.assertEqual(self.claim.status, FacilityClaimStatuses.PENDING)

    def test_unexpected_error_on_read_is_answered_as_unavailable(self):
        self.start()
        with patch(
            'api.views.facility.facility_claim_view_set'
            '.get_live_check_state',
            side_effect=RuntimeError('boom'),
        ):
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], UNAVAILABLE)


class ClaimLiveCheckLimitTest(ClaimLiveCheckTestBase):
    def answer_not_passed(self):
        self.post_review(review_block([CHECK_ADDRESS]))
        self.assertEqual(self.poll()['status'], NOT_PASSED)

    def test_second_start_while_checking_does_not_start_another(self):
        self.start()
        state = self.start()

        self.assertEqual(state['status'], CHECKING)
        self.assertEqual(self.checks().count(), 1)
        self.trigger.assert_called_once()

    def test_unchanged_claim_is_not_checked_again(self):
        self.start()
        self.answer_not_passed()

        state = self.start()

        self.assertEqual(state['status'], NOT_PASSED)
        self.assertEqual(self.checks().count(), 1)
        self.trigger.assert_called_once()

    def test_edited_claim_can_be_checked_again(self):
        self.start()
        self.answer_not_passed()
        self.claimant_edits()

        state = self.start()

        self.assertEqual(state['status'], CHECKING)
        self.assertEqual(state['fixes'], [])
        self.assertEqual(
            state['checks_left'], MAX_LIVE_CHECKS_PER_CLAIM - 2
        )
        self.assertEqual(self.trigger.call_count, 2)

    def test_claim_gets_at_most_three_checks(self):
        for _ in range(MAX_LIVE_CHECKS_PER_CLAIM):
            self.assertEqual(self.start()['status'], CHECKING)
            self.answer_not_passed()
            self.claimant_edits()
        self.trigger.reset_mock()

        state = self.start()

        self.assertEqual(state['status'], NOT_PASSED)
        self.assertEqual(state['checks_left'], 0)
        self.assertEqual(self.checks().count(), MAX_LIVE_CHECKS_PER_CLAIM)
        self.trigger.assert_not_called()

    def test_decided_claim_is_not_checked(self):
        self.approve()

        state = self.start()

        self.assertEqual(state['status'], UNAVAILABLE)
        self.assertFalse(self.checks().exists())
        self.trigger.assert_not_called()


@override_settings(DEBUG=True, CLAIMS_LIVE_REVIEW_FUNCTION='')
class ClaimLiveCheckDevStubTest(ClaimLiveCheckTestBase):
    def start_and_wait(self):
        self.assertEqual(self.start()['status'], CHECKING)
        self.assertEqual(self.poll()['status'], CHECKING)
        self.age_checks(STUB_DELAY_SECONDS)

    @override_settings(CLAIMS_LIVE_REVIEW_DEV_STUB='pass')
    def test_stubbed_pass_answers_without_calling_or_approving(self):
        self.start_and_wait()

        self.assertEqual(self.poll()['status'], PASSED)
        self.trigger.assert_not_called()
        self.claim.refresh_from_db()
        self.assertEqual(self.claim.status, FacilityClaimStatuses.PENDING)

    @override_settings(
        CLAIMS_LIVE_REVIEW_DEV_STUB=(
            'not_pass:company_address_document, work_email,made_up'
        )
    )
    def test_stubbed_not_pass_shows_the_chosen_fixes(self):
        self.start_and_wait()

        state = self.poll()

        self.assertEqual(state['status'], NOT_PASSED)
        self.assertEqual(
            state['fixes'],
            [FIX_WORK_EMAIL, FIX_COMPANY_ADDRESS_DOCUMENT],
        )

    @override_settings(CLAIMS_LIVE_REVIEW_DEV_STUB='not_pass')
    def test_stubbed_not_pass_without_fixes_shows_one(self):
        self.start_and_wait()
        self.assertEqual(self.poll()['fixes'], [FIX_UPLOAD_DOCUMENT])

    @override_settings(CLAIMS_LIVE_REVIEW_DEV_STUB='timeout')
    def test_stubbed_timeout_never_answers(self):
        self.start_and_wait()
        self.assertEqual(self.poll()['status'], CHECKING)

        self.age_checks(LIVE_CHECK_TIMEOUT_SECONDS)
        self.assertEqual(self.poll()['status'], UNAVAILABLE)

    @override_settings(DEBUG=False, CLAIMS_LIVE_REVIEW_DEV_STUB='pass')
    def test_stub_does_nothing_with_debug_off(self):
        self.assertEqual(self.start()['status'], UNAVAILABLE)
        self.assertFalse(self.checks().exists())


class ClaimLiveCheckCreateClaimResponseTest(ClaimLiveCheckTestBase):
    '''The claim form learns the new claim's id only with the switch on.'''

    def setUp(self):
        super().setUp()
        self.claim.delete()
        self.create_url = f'/api/facilities/{self.facility.id}/claim/'
        self.data = {
            'your_name': 'Name',
            'your_title': 'Title',
            'your_business_website': '',
            'business_website': '',
            'business_linkedin_profile':
                'https://www.linkedin.com/company/example',
            'sectors': 'Apparel',
        }

    def create_claim(self):
        response = self.client.post(self.create_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.json()

    def test_switch_on_returns_the_claim_id(self):
        body = self.create_claim()

        claim = FacilityClaim.objects.get(facility=self.facility)
        self.assertEqual(body['claim_id'], claim.id)
        self.assertEqual(body['pending'], [self.facility.id])
        self.trigger.assert_not_called()

    def test_switch_off_response_is_unchanged(self):
        with override_switch(CLAIM_LIVE_CHECK_SWITCH, active=False):
            body = self.create_claim()

        self.assertEqual(set(body), {'approved', 'pending'})


NOT_PASSED_SUBJECT = 'Your claim on Open Supply Hub needs one more step'
APPROVED_SUBJECT = (
    'Your request to claim a profile on Open Supply Hub has been approved!'
)


class ClaimLiveCheckEmailTest(ClaimLiveCheckTestBase):
    '''A claimant who left the page gets the result by email.'''

    def setUp(self):
        super().setUp()
        self.note_url = f'/api/facility-claims/{self.claim.id}/note/'
        mail.outbox = []

    def leave_page(self):
        '''The claimant's page stopped asking some time ago.'''
        self.checks().update(
            last_polled_at=timezone.now() - timedelta(
                seconds=PAGE_LEFT_AFTER_SECONDS
            )
        )

    def pipeline_posts(self, block, user=None):
        '''The review note arrives through the API, as it really does.'''
        self.login(user or self.bot)
        response = self.client.post(
            self.note_url, {'note': review_note(block)}
        )
        self.login(self.claimant)
        return response

    def pipeline_approves(self):
        self.login(self.bot)
        response = self.client.post(
            f'/api/facility-claims/{self.claim.id}/approve/'
        )
        self.login(self.claimant)
        return response

    def test_claimant_who_left_is_emailed_the_fixes_and_a_way_back(self):
        self.start()
        self.leave_page()

        response = self.pipeline_posts(
            review_block([CHECK_ADDRESS, CHECK_AFFILIATION])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, [WORK_EMAIL])
        self.assertEqual(email.subject, NOT_PASSED_SUBJECT)
        link = '/claimed/pending/{}?fix={}&check=1'.format(
            self.claim.id, FIX_UPLOAD_DOCUMENT
        )
        html = email.alternatives[0][0]
        for fix in (
            FIX_UPLOAD_DOCUMENT,
            FIX_NAME_AND_COMPANY_DOCUMENT,
            FIX_COMPANY_ADDRESS_DOCUMENT,
        ):
            self.assertIn(FIX_TEXTS[fix], email.body)
            self.assertIn(FIX_TEXTS[fix], html)
        self.assertNotIn(FIX_TEXTS[FIX_WORK_EMAIL], email.body)
        self.assertIn(link, email.body)
        self.assertIn(link.replace('&', '&amp;'), html)
        self.assertIn('The claim did not pass the automatic check.',
                      email.body)
        self.assertIn(self.facility.name, email.body)
        self.assertIn('The OS Hub Claims Team', email.body)

        check = self.checks().get()
        self.assertEqual(check.status, NOT_PASSED)
        self.assertIsNotNone(check.emailed_at)
        self.assertEqual(self.poll()['status'], NOT_PASSED)

    def test_email_carries_no_score_or_model_text(self):
        self.start()
        self.leave_page()

        self.pipeline_posts(review_block([CHECK_ADDRESS]))

        email = mail.outbox[0]
        for content in (email.body, email.alternatives[0][0]):
            self.assertNotIn('Model reasoning', content)
            self.assertNotIn(str(FAIL_SCORE), content)
            self.assertNotIn(str(THRESHOLD), content)

    def test_claimant_still_on_the_page_is_not_emailed(self):
        self.start()
        self.poll()

        self.pipeline_posts(review_block([CHECK_ADDRESS]))

        self.assertEqual(mail.outbox, [])
        check = self.checks().get()
        self.assertEqual(check.status, NOT_PASSED)
        self.assertIsNone(check.emailed_at)
        self.assertEqual(self.poll()['status'], NOT_PASSED)

    def test_one_check_is_emailed_at_most_once(self):
        self.start()
        self.leave_page()

        self.pipeline_posts(review_block([CHECK_ADDRESS]))
        self.pipeline_posts(review_block([CHECK_NAME]))
        self.poll()

        self.assertEqual(len(mail.outbox), 1)

    def test_last_allowed_check_links_back_without_another_check(self):
        for _ in range(MAX_LIVE_CHECKS_PER_CLAIM - 1):
            self.start()
            self.post_review(review_block([CHECK_ADDRESS]))
            self.poll()
            self.claimant_edits()
        self.start()
        self.leave_page()

        self.pipeline_posts(review_block([CHECK_ADDRESS]))

        self.assertEqual(len(mail.outbox), 1)
        body = mail.outbox[0].body
        self.assertIn('?fix={}'.format(FIX_UPLOAD_DOCUMENT), body)
        self.assertNotIn('check=1', body)

    def test_switch_off_sends_nothing(self):
        self.start()
        self.leave_page()

        with override_switch(CLAIM_LIVE_CHECK_SWITCH, active=False):
            response = self.pipeline_posts(review_block([CHECK_ADDRESS]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(mail.outbox, [])
        self.assertEqual(self.checks().get().status, CHECKING)

    def test_claim_without_a_live_check_sends_nothing(self):
        self.pipeline_posts(review_block([CHECK_ADDRESS]))

        self.assertEqual(mail.outbox, [])
        self.assertFalse(self.checks().exists())

    def time_out_on_the_page(self):
        '''The page waited its minute and was told "not available".'''
        self.start()
        self.age_checks(LIVE_CHECK_TIMEOUT_SECONDS)
        self.assertEqual(self.poll()['status'], UNAVAILABLE)

    def test_timed_out_check_with_no_result_sends_nothing(self):
        self.time_out_on_the_page()

        self.assertEqual(mail.outbox, [])
        self.assertIsNone(self.checks().get().emailed_at)

    def test_late_not_pass_after_timeout_sends_exactly_one_email(self):
        self.time_out_on_the_page()

        self.pipeline_posts(review_block([CHECK_ADDRESS]))
        self.pipeline_posts(review_block([CHECK_NAME]))

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, [WORK_EMAIL])
        self.assertEqual(email.subject, NOT_PASSED_SUBJECT)
        self.assertIn(FIX_TEXTS[FIX_COMPANY_ADDRESS_DOCUMENT], email.body)
        self.assertNotIn(FIX_TEXTS[FIX_COMPANY_NAME_DOCUMENT], email.body)
        self.assertIn(
            '/claimed/pending/{}?fix='.format(self.claim.id), email.body
        )
        check = self.checks().get()
        self.assertEqual(check.status, NOT_PASSED)
        self.assertIsNotNone(check.emailed_at)
        # Coming back from the email shows the result, and an edit
        # earns a fresh check.
        self.assertEqual(self.poll()['status'], NOT_PASSED)
        self.claimant_edits()
        self.assertEqual(self.start()['status'], CHECKING)

    def test_late_not_pass_after_a_failed_trigger_is_emailed_too(self):
        self.trigger.return_value = False
        self.assertEqual(self.start()['status'], UNAVAILABLE)

        self.pipeline_posts(review_block([CHECK_ADDRESS]))

        self.assertEqual(len(mail.outbox), 1)

    def test_late_pass_sends_only_the_existing_approval_email(self):
        self.time_out_on_the_page()

        self.pipeline_posts(review_block())
        self.assertEqual(mail.outbox, [])
        response = self.pipeline_approves()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        subjects = [
            email.subject for email in mail.outbox
            if email.to == [WORK_EMAIL]
        ]
        self.assertEqual(subjects.count(APPROVED_SUBJECT), 1)
        self.assertNotIn(NOT_PASSED_SUBJECT, subjects)
        self.assertIsNone(self.checks().get().emailed_at)

    def test_late_result_with_the_switch_off_sends_nothing(self):
        self.time_out_on_the_page()

        with override_switch(CLAIM_LIVE_CHECK_SWITCH, active=False):
            self.pipeline_posts(review_block([CHECK_ADDRESS]))

        self.assertEqual(mail.outbox, [])
        self.assertEqual(self.checks().get().status, UNAVAILABLE)

    def test_result_after_an_answered_check_sends_nothing(self):
        self.start()
        self.post_review(review_block([CHECK_ADDRESS]))
        self.assertEqual(self.poll()['status'], NOT_PASSED)
        self.leave_page()

        self.pipeline_posts(review_block([CHECK_NAME]))

        self.assertEqual(mail.outbox, [])

    @override_settings(
        DEBUG=True,
        CLAIMS_LIVE_REVIEW_FUNCTION='',
        CLAIMS_LIVE_REVIEW_DEV_STUB='late_not_pass:work_email',
    )
    def test_dev_stub_can_show_not_available_and_send_the_email(self):
        self.assertEqual(self.start()['status'], CHECKING)
        self.age_checks(STUB_DELAY_SECONDS)

        state = self.poll()
        self.poll()

        self.assertEqual(state['status'], UNAVAILABLE)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, NOT_PASSED_SUBJECT)
        self.assertIn(FIX_TEXTS[FIX_WORK_EMAIL], mail.outbox[0].body)
        self.assertIn('localhost:6543/claimed/pending/', mail.outbox[0].body)
        self.trigger.assert_not_called()

    def test_held_for_an_unknown_reason_sends_nothing(self):
        self.start()
        self.leave_page()

        self.pipeline_posts(
            review_block(decision='NOT_VALIDATED', reasoning={})
        )

        self.assertEqual(mail.outbox, [])
        self.assertEqual(self.checks().get().status, UNAVAILABLE)

    def test_lookalike_note_from_a_moderator_sends_nothing(self):
        self.start()
        self.leave_page()

        self.pipeline_posts(
            review_block([CHECK_ADDRESS]), user=self.moderator
        )

        self.assertEqual(mail.outbox, [])
        self.assertEqual(self.checks().get().status, CHECKING)

    def test_claimant_still_cannot_post_a_note(self):
        self.start()
        self.leave_page()

        response = self.pipeline_posts(
            review_block([CHECK_ADDRESS]), user=self.claimant
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(mail.outbox, [])

    @override_settings(DEBUG=True, CLAIMS_LIVE_REVIEW_DEV_STUB='pass')
    def test_dev_stub_sends_nothing(self):
        self.start()
        self.leave_page()

        self.pipeline_posts(review_block([CHECK_ADDRESS]))

        self.assertEqual(mail.outbox, [])

    def test_failed_email_does_not_fail_the_note(self):
        self.start()
        self.leave_page()

        with patch('api.mail.send_mail', side_effect=RuntimeError('smtp')):
            response = self.pipeline_posts(review_block([CHECK_ADDRESS]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            FacilityClaimReviewNote.objects.filter(claim=self.claim).count(),
            1,
        )
        check = self.checks().get()
        self.assertEqual(check.status, CHECKING)
        self.assertIsNone(check.emailed_at)

    def test_pass_sends_only_the_existing_approval_email(self):
        self.start()
        self.leave_page()

        self.pipeline_posts(review_block())
        self.assertEqual(mail.outbox, [])

        response = self.pipeline_approves()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # The claimant in this fixture also contributed the location,
        # so the usual notice to contributors reaches them too.
        subjects = [
            email.subject for email in mail.outbox
            if email.to == [WORK_EMAIL]
        ]
        self.assertEqual(subjects.count(APPROVED_SUBJECT), 1)
        self.assertNotIn(NOT_PASSED_SUBJECT, subjects)
        self.assertEqual(self.poll()['status'], PASSED)
        self.assertIsNone(self.checks().get().emailed_at)
