from unittest.mock import MagicMock, patch

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from api.models import (
    Contributor,
    FacilityList,
    FacilityListItem,
    ListCleaningRun,
    ListCleaningSuggestion,
    Source,
    User,
)
from api.services.list_cleaning import (
    SWITCH_NAME,
    apply_run,
    ingest_result,
    refresh_run,
    start_run,
)

SAMPLE_RESULT = {
    'file_pass': {
        'mode': 'file_pass', 'row_count': 3,
        'exact_duplicates': [{'keep': 2, 'remove': 4, 'match': 'exact'}],
        'repeated_names': [],
        'header_issues': [],
    },
    'records': [
        {
            'row': 2, 'status': 'auto_corrected',
            'changes': [
                {'field': 'country', 'value': 'VN',
                 'reason': 'country_code'},
                {'field': 'number_of_workers', 'value': '1200',
                 'reason': 'workers_format'},
                {'field': 'address',
                 'value': '36 Tay Thanh Street, Ho Chi Minh City',
                 'reason': 'country_in_address'},
            ],
            'issues': [
                {'code': 'address_too_few', 'severity': 'internal_note',
                 'field': 'address', 'note': 'For the moderator only.'},
            ],
        },
        {
            'row': 3, 'status': 'needs_your_action',
            'changes': [],
            'issues': [
                {'code': 'address_po_box', 'severity': 'must_fix',
                 'field': 'address',
                 'note': 'The address has no street.'},
            ],
        },
        {
            'row': 4, 'status': 'removed', 'changes': [], 'issues': [],
            'removed_reason': 'duplicate', 'duplicate_of': 2,
        },
    ],
    'usage': {'input_tokens': 10, 'output_tokens': 20, 'seconds': 1.5},
    'prompt_version': '01',
}


@override_settings(LIST_CLEANING_RUNNER='stub')
class ListCleaningFeedbackTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='owner@example.com')
        self.user.set_password('pw')
        self.user.save()
        self.contributor = Contributor.objects.create(
            admin=self.user, name='Owner',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE)

        self.other_user = User.objects.create(email='other@example.com')
        Contributor.objects.create(
            admin=self.other_user, name='Other',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE)

        self.superuser = User.objects.create(
            email='admin@example.com', is_superuser=True, is_staff=True)
        Contributor.objects.create(
            admin=self.superuser, name='Admin',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE)

        self.list = FacilityList.objects.create(
            header='country,name,address,number_of_workers',
            file_name='list.csv', name='List')
        self.source = Source.objects.create(
            source_type=Source.LIST, facility_list=self.list,
            contributor=self.contributor)
        rows = [
            ('Viet Nam', 'Thanh Cong Textile',
             '36 Tay Thanh Street, Ho Chi Minh City, Vietnam', '1,200'),
            ('Bangladesh', 'ABC Garments', 'PO Box 41, Dhaka', '500'),
            ('Viet Nam', 'Thanh Cong Textile',
             '36 Tay Thanh Street, Ho Chi Minh City, Vietnam', '1,200'),
        ]
        self.items = []
        for idx, (country, name, address, workers) in enumerate(rows):
            self.items.append(FacilityListItem.objects.create(
                source=self.source, row_index=idx,
                raw_data=f'"{country}","{name}","{address}","{workers}"',
                raw_json={'country': country, 'name': name,
                          'address': address,
                          'number_of_workers': workers},
                name=name, address=address, country_code='VN',
                sector=['Apparel'], status=FacilityListItem.PARSED))

    def url(self, suffix=''):
        return f'/api/facility-lists/{self.list.id}/cleaning/{suffix}'

    # -- trigger and storage ------------------------------------------

    @override_switch(SWITCH_NAME, active=False)
    def test_switch_off_starts_nothing(self):
        self.assertIsNone(start_run(self.list))
        self.assertEqual(ListCleaningRun.objects.count(), 0)

    @override_switch(SWITCH_NAME, active=True)
    def test_stub_run_completes_with_suggestions(self):
        run = start_run(self.list)
        self.assertEqual(run.status, ListCleaningRun.COMPLETE)
        self.assertEqual(run.runner, ListCleaningRun.STUB)
        codes = set(run.suggestions.values_list('code', flat=True))
        self.assertIn('country_code', codes)
        self.assertIn('address_po_box', codes)
        self.assertIn('duplicate', codes)

    def test_ingest_pre_accepts_silent_codes_but_never_protected_fields(
            self):
        run = ListCleaningRun.objects.create(
            facility_list=self.list, runner=ListCleaningRun.IMPORT)
        ingest_result(run, SAMPLE_RESULT)
        by_field = {
            s.field: s for s in run.suggestions.filter(
                kind=ListCleaningSuggestion.CORRECTION)}
        self.assertEqual(by_field['country'].decision,
                         ListCleaningSuggestion.ACCEPTED)
        self.assertEqual(by_field['country'].original_value, 'Viet Nam')
        self.assertEqual(by_field['number_of_workers'].decision,
                         ListCleaningSuggestion.ACCEPTED)
        self.assertEqual(by_field['address'].decision,
                         ListCleaningSuggestion.PENDING)
        self.assertEqual(run.prompt_version, '01')
        self.assertEqual(run.file_pass['exact_duplicates'][0]['remove'], 4)

    @override_switch(SWITCH_NAME, active=True)
    @override_settings(LIST_CLEANING_RUNNER='stepfunctions',
                       LIST_CLEANING_STATE_MACHINE_ARN='arn:aws:states:x')
    @patch('api.services.list_cleaning.runners.boto3')
    def test_step_functions_runner_starts_and_ingests(self, boto3):
        client = MagicMock()
        boto3.client.return_value = client
        client.start_execution.return_value = {'executionArn': 'arn:exec'}
        run = start_run(self.list)
        self.assertEqual(run.status, ListCleaningRun.RUNNING)
        self.assertEqual(run.execution_arn, 'arn:exec')
        sent = client.start_execution.call_args.kwargs
        self.assertEqual(sent['stateMachineArn'], 'arn:aws:states:x')
        self.assertIn('"list_id"', sent['input'])

        client.describe_execution.return_value = {'status': 'RUNNING'}
        self.assertEqual(refresh_run(run).status, ListCleaningRun.RUNNING)

        import json
        client.describe_execution.return_value = {
            'status': 'SUCCEEDED', 'output': json.dumps(SAMPLE_RESULT)}
        self.assertEqual(refresh_run(run).status, ListCleaningRun.COMPLETE)
        self.assertEqual(run.suggestions.count(), 6)

    @override_switch(SWITCH_NAME, active=True)
    @override_settings(LIST_CLEANING_RUNNER='stepfunctions',
                       LIST_CLEANING_STATE_MACHINE_ARN='')
    def test_runner_failure_is_recorded_not_raised(self):
        run = start_run(self.list)
        self.assertEqual(run.status, ListCleaningRun.FAILED)
        self.assertIn('LIST_CLEANING_STATE_MACHINE_ARN', run.error)

    # -- API ----------------------------------------------------------

    def _ingested_run(self):
        run = ListCleaningRun.objects.create(
            facility_list=self.list, runner=ListCleaningRun.IMPORT)
        ingest_result(run, SAMPLE_RESULT)
        return run

    def test_get_without_run(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['run'])

    def test_contributor_sees_must_fix_but_not_internal_notes(self):
        self._ingested_run()
        self.client.force_login(self.user)
        response = self.client.get(self.url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        severities = [s['severity'] for row in response.data['rows']
                      for s in row['suggestions'] if s['kind'] == 'ISSUE']
        self.assertEqual(severities, ['must_fix'])
        self.assertEqual(response.data['summary']['rows_must_fix'], 1)
        self.assertEqual(response.data['summary']['corrections_total'], 3)
        self.assertEqual(response.data['summary']['removals'], 1)
        self.assertEqual(response.data['summary']['internal_notes'], 0)

    def test_superuser_sees_internal_notes(self):
        self._ingested_run()
        self.client.force_login(self.superuser)
        response = self.client.get(self.url())
        severities = sorted(s['severity'] for row in response.data['rows']
                            for s in row['suggestions']
                            if s['kind'] == 'ISSUE')
        self.assertEqual(severities, ['internal_note', 'must_fix'])

    def test_other_contributor_gets_404(self):
        self._ingested_run()
        self.client.force_login(self.other_user)
        self.assertEqual(self.client.get(self.url()).status_code,
                         status.HTTP_404_NOT_FOUND)

    def test_decisions_are_recorded_per_suggestion_and_applied(self):
        run = self._ingested_run()
        corrections = {
            s.field: s for s in run.suggestions.filter(
                kind=ListCleaningSuggestion.CORRECTION)}
        removal = run.suggestions.get(kind=ListCleaningSuggestion.REMOVAL)
        self.client.force_login(self.user)

        response = self.client.post(self.url('decisions/'), {
            'decisions': [
                {'id': corrections['country'].id, 'decision': 'REJECTED'},
                {'id': corrections['number_of_workers'].id,
                 'decision': 'EDITED', 'value': '1250'},
                {'id': corrections['address'].id, 'decision': 'ACCEPTED'},
                {'id': removal.id, 'decision': 'ACCEPTED'},
            ]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         response.data)
        country = ListCleaningSuggestion.objects.get(
            pk=corrections['country'].id)
        self.assertEqual(country.decision, ListCleaningSuggestion.REJECTED)
        self.assertEqual(country.decided_by, self.user)
        self.assertEqual(response.data['summary']['corrections_unapplied'],
                         2)

        response = self.client.post(self.url('apply/'), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         response.data)
        self.assertEqual(response.data['applied'],
                         {'applied': 3, 'reverted': 0})

        first = FacilityListItem.objects.get(pk=self.items[0].id)
        self.assertEqual(first.raw_json['country'], 'Viet Nam')
        self.assertEqual(first.raw_json['number_of_workers'], '1250')
        self.assertEqual(first.address,
                         '36 Tay Thanh Street, Ho Chi Minh City')
        # the original upload is still recoverable
        self.assertIn('Vietnam', first.raw_data)
        third = FacilityListItem.objects.get(pk=self.items[2].id)
        self.assertEqual(third.status, FacilityListItem.DUPLICATE)
        self.assertEqual(self.list.status, FacilityList.PENDING)
        # the list items page must still load after changes were applied
        response = self.client.get(
            f'/api/facility-lists/{self.list.id}/items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

        # reversing a decision after apply restores the original
        self.client.post(self.url('decisions/'), {'decisions': [
            {'id': corrections['address'].id, 'decision': 'REJECTED'},
        ]}, format='json')
        counts = apply_run(run)
        self.assertEqual(counts['reverted'], 1)
        first.refresh_from_db()
        self.assertEqual(first.address,
                         '36 Tay Thanh Street, Ho Chi Minh City, Vietnam')

    def test_issue_cannot_be_decided(self):
        run = self._ingested_run()
        issue = run.suggestions.filter(kind=ListCleaningSuggestion.ISSUE,
                                       severity='must_fix').first()
        self.client.force_login(self.user)
        response = self.client.post(self.url('decisions/'), {
            'decisions': [{'id': issue.id, 'decision': 'ACCEPTED'}]},
            format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_decisions_blocked_once_list_is_not_pending(self):
        run = self._ingested_run()
        self.list.status = FacilityList.APPROVED
        self.list.save()
        suggestion = run.suggestions.filter(
            kind=ListCleaningSuggestion.CORRECTION).first()
        self.client.force_login(self.user)
        response = self.client.post(self.url('decisions/'), {
            'decisions': [{'id': suggestion.id, 'decision': 'ACCEPTED'}]},
            format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            self.client.post(self.url('apply/'), {}).status_code,
            status.HTTP_400_BAD_REQUEST)

    def test_start_is_superuser_only(self):
        self.client.force_login(self.user)
        self.assertEqual(
            self.client.post(self.url('start/'), {}).status_code,
            status.HTTP_403_FORBIDDEN)
        self.client.force_login(self.superuser)
        response = self.client.post(self.url('start/'), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['run']['status'], 'COMPLETE')
