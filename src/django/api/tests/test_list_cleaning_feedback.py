import json
import os
import tempfile
from datetime import timedelta
from io import StringIO
from unittest.mock import MagicMock, patch

from django.contrib.gis.geos import Point
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from api.extended_fields import create_extendedfields_for_single_item
from api.models import (
    Contributor,
    ExtendedField,
    Facility,
    FacilityList,
    FacilityListItem,
    ListCleaningEvent,
    ListCleaningRun,
    ListCleaningSuggestion,
    Source,
    User,
)
from api.services.list_cleaning import (
    SWITCH_NAME,
    apply_run,
    ingest_result,
    record_decisions,
    refresh_run,
    start_run,
)
from api.services.list_cleaning.runners import RunFailed
from api.services.list_cleaning.service import build_fixed_csv
from api.services.list_cleaning.stub import run_rules

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
@override_switch(SWITCH_NAME, active=True)
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
        # A failed run has nothing to review, so it must not hold the
        # list for the review window: moderation and a restart go ahead.
        self.assertEqual(run.closed_reason, ListCleaningRun.FAILED_RUN)
        self.assertIsNotNone(run.closed_at)
        self.client.force_login(self.superuser)
        response = self.client.get(self.url())
        self.assertFalse(response.data['window_open'])
        response = self.client.post(
            f'/api/facility-lists/{self.list.id}/approve/',
            {'reason': 'x'}, format='json')
        self.assertNotEqual(response.status_code,
                            status.HTTP_400_BAD_REQUEST, response.data)
        self.list.refresh_from_db()
        self.list.status = FacilityList.PENDING
        self.list.save()
        with override_settings(LIST_CLEANING_RUNNER='stub'):
            response = self.client.post(
                self.url('start/'), {'runner': 'stub'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         response.data)
        self.assertEqual(response.data['run']['status'],
                         ListCleaningRun.COMPLETE)

    # -- API ----------------------------------------------------------

    def _ingested_run(self, minutes_left=60):
        run = ListCleaningRun.objects.create(
            facility_list=self.list, runner=ListCleaningRun.IMPORT,
            review_until=timezone.now() + timedelta(minutes=minutes_left))
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
        # the readiness tracker: two silent fixes done, the address fix
        # and the PO Box flag still waiting
        self.assertEqual(response.data['summary']['auto_fixes'], 3)
        self.assertEqual(
            response.data['summary']['fixes_to_review_total'], 1)
        self.assertEqual(
            response.data['summary']['fixes_to_review_decided'], 0)
        self.assertEqual(response.data['summary']['must_fix_total'], 1)

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
        # nothing touches the list until the one submission, the
        # automatic fixes included: the typed value, the accepted address
        # fix and the kept-original country all wait for it
        first = FacilityListItem.objects.get(pk=self.items[0].id)
        self.assertEqual(first.raw_json['number_of_workers'], '1,200')
        self.assertEqual(first.raw_json['country'], 'Viet Nam')
        self.assertEqual(response.data['summary']['corrections_unapplied'],
                         2)
        self.assertEqual(response.data['summary']['changes_unapplied'], 3)
        self.assertTrue(response.data['window_open'])

        response = self.client.post(self.url('submit/'), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         response.data)
        self.assertEqual(response.data['applied'],
                         {'applied': 3, 'reverted': 0})
        self.assertFalse(response.data['window_open'])
        self.assertEqual(response.data['run']['closed_reason'], 'submitted')

        first.refresh_from_db()
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

        # submitted means submitted: no decision, submission or change
        # of mind is accepted afterwards
        for body in ({'decisions': [{'id': corrections['address'].id,
                                     'decision': 'REJECTED'}]},
                     {'groups': [{'key': 'CORRECTION:country_code:country',
                                  'decision': 'REJECTED'}]}):
            response = self.client.post(
                self.url('decisions/'), body, format='json')
            self.assertEqual(response.status_code,
                             status.HTTP_400_BAD_REQUEST)
            self.assertIn('already been submitted', str(response.data))
        self.assertEqual(
            self.client.post(self.url('submit/'), {}).status_code,
            status.HTTP_400_BAD_REQUEST)
        first.refresh_from_db()
        self.assertEqual(first.address,
                         '36 Tay Thanh Street, Ho Chi Minh City')
        # ...and the submission is on the record
        submitted = run.events.get(kind=ListCleaningEvent.SUBMITTED)
        self.assertFalse(submitted.meta['as_uploaded'])
        self.assertEqual(submitted.meta['applied'], 3)
        self.assertEqual(submitted.meta['rows_removed'], 1)
        self.assertEqual(submitted.meta['row_decisions'], 4)
        # automatic versus through review: the country fix (auto) was
        # turned off, the workers fix (auto) was retyped, the address fix
        # accepted; the duplicate removal is automatic
        self.assertEqual(submitted.meta['auto_offered'], 3)
        self.assertEqual(submitted.meta['auto_applied'], 1)
        self.assertEqual(submitted.meta['auto_turned_off'], 1)
        self.assertEqual(submitted.meta['fixes_offered'], 1)
        self.assertEqual(submitted.meta['fixes_accepted'], 1)
        self.assertEqual(submitted.meta['values_typed'], 1)
        self.assertEqual(submitted.meta['flags_offered'], 1)
        self.assertEqual(submitted.meta['flags_left_as_uploaded'], 1)
        self.assertEqual(submitted.meta['reviewed_changes'], 2)

    def test_flagged_row_cannot_be_accepted_but_can_be_fixed_or_removed(
            self):
        run = self._ingested_run()
        issue = run.suggestions.get(kind=ListCleaningSuggestion.ISSUE,
                                    severity='must_fix')
        self.client.force_login(self.user)
        response = self.client.post(self.url('decisions/'), {
            'decisions': [{'id': issue.id, 'decision': 'ACCEPTED'}]},
            format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # fix the flagged address in place, without re-uploading
        response = self.client.post(self.url('decisions/'), {
            'decisions': [{'id': issue.id, 'decision': 'EDITED',
                           'value': '41 Mirpur Road, Dhaka'}]},
            format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         response.data)
        self.assertEqual(response.data['summary']['must_fix_resolved'], 1)
        self.assertEqual(response.data['summary']['must_fix_pending'], 0)
        apply_run(run)
        second = FacilityListItem.objects.get(pk=self.items[1].id)
        self.assertEqual(second.address, '41 Mirpur Road, Dhaka')
        self.assertEqual(second.raw_json['address'], '41 Mirpur Road, Dhaka')

        # change of mind: drop the row instead
        self.client.post(self.url('decisions/'), {
            'decisions': [{'id': issue.id, 'decision': 'REMOVED'}]},
            format='json')
        counts = apply_run(run)
        second.refresh_from_db()
        self.assertEqual(second.status, FacilityListItem.ITEM_REMOVED)
        # the edit was undone and the row dropped
        self.assertEqual(second.address, 'PO Box 41, Dhaka')
        self.assertEqual(counts, {'applied': 1, 'reverted': 1})

        # and back again: leave the row as it was uploaded
        self.client.post(self.url('decisions/'), {
            'decisions': [{'id': issue.id, 'decision': 'REJECTED'}]},
            format='json')
        counts = apply_run(run)
        second.refresh_from_db()
        self.assertEqual(second.status, FacilityListItem.PARSED)
        self.assertEqual(counts, {'applied': 0, 'reverted': 1})

    def test_group_decisions_cover_every_row_of_that_error_type(self):
        run = self._ingested_run()
        self.client.force_login(self.user)
        response = self.client.get(self.url())
        groups = {g['key']: g for g in response.data['groups']}
        key = 'CORRECTION:country_code:country'
        self.assertIn(key, groups)
        self.assertEqual(groups[key]['count'], 1)
        self.assertEqual(groups[key]['accepted'], 1)  # silent code
        self.assertEqual(groups[key]['examples'][0]['corrected_value'],
                         'VN')
        # must-fix flags sort first so the contributor sees them first
        self.assertEqual(response.data['groups'][0]['kind'],
                         ListCleaningSuggestion.ISSUE)

        response = self.client.post(self.url('decisions/'), {
            'groups': [{'key': key, 'decision': 'REJECTED'}]},
            format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         response.data)
        country = run.suggestions.get(field='country')
        self.assertEqual(country.decision, ListCleaningSuggestion.REJECTED)
        self.assertEqual(country.decided_by, self.user)

        # A row the contributor decided on its own keeps that decision
        # when the rest of its error type is decided as a group.
        name_key = 'CORRECTION:country_in_address:address'
        self.assertIn(name_key, groups)
        name = run.suggestions.get(code='country_in_address')
        response = self.client.post(self.url('decisions/'), {
            'decisions': [{'id': name.id, 'decision': 'EDITED',
                           'value': 'Hand-typed name'}]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         response.data)
        response = self.client.post(self.url('decisions/'), {
            'groups': [{'key': name_key, 'decision': 'REJECTED'}]},
            format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         response.data)
        name.refresh_from_db()
        self.assertEqual(name.decision, ListCleaningSuggestion.EDITED)
        self.assertEqual(name.decided_value, 'Hand-typed name')
        groups = {g['key']: g for g in response.data['groups']}
        self.assertEqual(groups[name_key]['by_row'], 1)
        self.assertEqual(groups[name_key]['edited'], 1)
        # ...but a group decision can be overridden by a later one.
        country.refresh_from_db()
        self.assertFalse(country.extra.get('by_row'))
        # A reset puts the row-by-row rows back to undecided, after which
        # the group buttons cover them again.
        response = self.client.post(self.url('decisions/'), {
            'groups': [{'key': name_key, 'reset': True},
                       {'key': name_key, 'decision': 'REJECTED'}]},
            format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         response.data)
        name.refresh_from_db()
        self.assertEqual(name.decision, ListCleaningSuggestion.REJECTED)
        self.assertEqual(name.decided_value, '')
        self.assertFalse(name.extra.get('by_row'))
        groups = {g['key']: g for g in response.data['groups']}
        self.assertEqual(groups[name_key]['by_row'], 0)

        for bad in ({'key': 'nope', 'decision': 'ACCEPTED'},
                    {'key': key, 'decision': 'EDITED'}):
            response = self.client.post(self.url('decisions/'), {
                'groups': [bad]}, format='json')
            self.assertEqual(response.status_code,
                             status.HTTP_400_BAD_REQUEST, bad)

    def test_fixed_list_download_puts_removed_rows_last_with_a_tag(self):
        run = self._ingested_run()
        self.client.force_login(self.user)
        removal = run.suggestions.get(kind=ListCleaningSuggestion.REMOVAL)
        self.client.post(self.url('decisions/'), {'decisions': [
            {'id': removal.id, 'decision': 'ACCEPTED'}]}, format='json')
        self.client.post(self.url('submit/'), {}, format='json')

        response = self.client.get(self.url('download/'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('-fixed.csv', response['Content-Disposition'])
        lines = response.content.decode('utf-8').splitlines()
        # every column is followed by the value as it was uploaded
        self.assertEqual(
            lines[0],
            'country,country (as uploaded),name,name (as uploaded),'
            'address,address (as uploaded),number_of_workers,'
            'number_of_workers (as uploaded),os_hub_cleaning')
        self.assertEqual(len(lines), 4)
        # the accepted worker-count fix is in the file beside the
        # uploaded value, the row order kept
        self.assertTrue(lines[1].startswith(
            'VN,Viet Nam,Thanh Cong Textile,Thanh Cong Textile,'))
        self.assertIn(',1200,"1,200",', lines[1])
        self.assertTrue(lines[2].startswith('Bangladesh,Bangladesh,'))
        self.assertTrue(lines[3].endswith(',removed: duplicate of row 2'))

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
            self.client.post(self.url('submit/'), {}).status_code,
            status.HTTP_400_BAD_REQUEST)

    def test_lapsed_window_sends_the_list_as_uploaded(self):
        run = self._ingested_run(minutes_left=-1)
        self.client.force_login(self.user)
        # noticed lazily on the next read, no scheduler needed
        response = self.client.get(self.url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['window_open'])
        self.assertEqual(response.data['seconds_left'], 0)
        self.assertEqual(response.data['run']['closed_reason'], 'lapsed')
        run.refresh_from_db()
        self.assertTrue(run.events.filter(
            kind=ListCleaningEvent.LAPSED).exists())
        # nothing was applied, not even the silent fixes
        first = FacilityListItem.objects.get(pk=self.items[0].id)
        self.assertEqual(first.raw_json['number_of_workers'], '1,200')
        third = FacilityListItem.objects.get(pk=self.items[2].id)
        self.assertEqual(third.status, FacilityListItem.PARSED)
        # and nothing can be changed any more
        suggestion = run.suggestions.filter(
            kind=ListCleaningSuggestion.CORRECTION).first()
        response = self.client.post(self.url('decisions/'), {
            'decisions': [{'id': suggestion.id, 'decision': 'ACCEPTED'}]},
            format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('has closed', str(response.data))
        self.assertEqual(
            self.client.post(self.url('submit/'), {}).status_code,
            status.HTTP_400_BAD_REQUEST)

    def test_submit_as_uploaded_applies_nothing_but_closes(self):
        run = self._ingested_run()
        self.client.force_login(self.user)
        response = self.client.post(
            self.url('submit/'), {'as_uploaded': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         response.data)
        self.assertEqual(response.data['applied'],
                         {'applied': 0, 'reverted': 0})
        run.refresh_from_db()
        self.assertEqual(run.closed_reason, ListCleaningRun.SUBMITTED)
        self.assertIsNotNone(run.submitted_at)
        first = FacilityListItem.objects.get(pk=self.items[0].id)
        self.assertEqual(first.raw_json['number_of_workers'], '1,200')
        self.assertTrue(
            run.events.get(kind=ListCleaningEvent.SUBMITTED)
            .meta['as_uploaded'])

    # -- extended fields follow the corrected row ----------------------

    def _workers_field(self, item):
        return ExtendedField.objects.get(
            facility_list_item=item,
            field_name=ExtendedField.NUMBER_OF_WORKERS)

    def _parse_like_upload(self):
        """Give the fixture items what parse would have derived."""
        for item in self.items:
            create_extendedfields_for_single_item(item, item.raw_json)

    def test_submit_rederives_extended_fields_from_corrected_values(self):
        self._parse_like_upload()
        first = self.items[0]
        # already matched before the contributor finished reviewing
        facility = Facility.objects.create(
            name=first.name, address=first.address, country_code='VN',
            location=Point(0, 0), created_from=first)
        first.facility = facility
        first.status = FacilityListItem.MATCHED
        first.save()
        for field in ExtendedField.objects.filter(facility_list_item=first):
            field.facility = facility
            field.save()
        self.assertEqual(self._workers_field(first).value,
                         {'min': 1200, 'max': 1200})
        before = facility.updated_at

        run = self._ingested_run()
        workers = run.suggestions.get(
            field='number_of_workers', kind=ListCleaningSuggestion.CORRECTION)
        record_decisions(
            run,
            [{'id': workers.id, 'decision': ListCleaningSuggestion.EDITED,
              'value': '1250'}],
            self.user)
        self.client.force_login(self.user)
        response = self.client.post(self.url('submit/'), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         response.data)

        field = self._workers_field(first)
        self.assertEqual(field.value, {'min': 1250, 'max': 1250})
        self.assertEqual(field.facility_id, facility.id)
        facility.refresh_from_db()
        self.assertGreater(facility.updated_at, before)
        first.refresh_from_db()
        self.assertEqual(first.sector, ['Unspecified'])

    def test_removed_row_loses_its_extended_fields(self):
        self._parse_like_upload()
        duplicate = self.items[2]
        self.assertTrue(ExtendedField.objects.filter(
            facility_list_item=duplicate).exists())
        self._ingested_run()
        self.client.force_login(self.user)
        response = self.client.post(self.url('submit/'), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         response.data)
        duplicate.refresh_from_db()
        self.assertEqual(duplicate.status, FacilityListItem.DUPLICATE)
        self.assertFalse(ExtendedField.objects.filter(
            facility_list_item=duplicate).exists())

    def test_submit_as_uploaded_leaves_extended_fields_alone(self):
        self._parse_like_upload()
        ids = set(ExtendedField.objects.values_list('id', flat=True))
        self._ingested_run()
        self.client.force_login(self.user)
        response = self.client.post(
            self.url('submit/'), {'as_uploaded': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(ExtendedField.objects.values_list('id', flat=True)), ids)

    # -- review follow-ups ---------------------------------------------

    def test_clean_result_closes_the_window_at_once(self):
        run = ListCleaningRun.objects.create(
            facility_list=self.list, runner=ListCleaningRun.IMPORT,
            review_until=timezone.now() + timedelta(minutes=60))
        ingest_result(run, {'records': [], 'file_pass': {}})
        run.refresh_from_db()
        self.assertEqual(run.status, ListCleaningRun.COMPLETE)
        self.assertEqual(run.closed_reason, ListCleaningRun.CLEAN)
        self.client.force_login(self.user)
        response = self.client.get(self.url())
        self.assertFalse(response.data['window_open'])
        # moderation is not held up by a review with nothing in it
        self.client.force_login(self.superuser)
        response = self.client.post(
            f'/api/facility-lists/{self.list.id}/approve/',
            {'reason': 'x'}, format='json')
        self.assertNotEqual(response.status_code,
                            status.HTTP_400_BAD_REQUEST, response.data)

    def test_internal_notes_alone_close_the_window_at_once(self):
        run = ListCleaningRun.objects.create(
            facility_list=self.list, runner=ListCleaningRun.IMPORT,
            review_until=timezone.now() + timedelta(minutes=60))
        ingest_result(run, {'records': [{
            'row': 2, 'status': 'needs_your_action', 'changes': [],
            'issues': [{'code': 'address_too_few',
                        'severity': 'internal_note', 'field': 'address',
                        'note': 'For the moderator only.'}],
        }], 'file_pass': {}})
        run.refresh_from_db()
        self.assertEqual(run.suggestions.count(), 1)
        # the contributor is shown nothing, so there is nothing to wait for
        self.assertEqual(run.closed_reason, ListCleaningRun.CLEAN)
        self.client.force_login(self.user)
        response = self.client.get(self.url())
        self.assertFalse(response.data['window_open'])
        self.assertEqual(response.data['rows'], [])

    def test_parser_duplicate_is_shown_but_cannot_be_put_back(self):
        # The parser dropped the exact repeat at upload, before the
        # pipeline ran; restoring it would only give two identical rows.
        self.items[2].status = FacilityListItem.DUPLICATE
        self.items[2].save()
        run = self._ingested_run()
        removal = run.suggestions.get(kind=ListCleaningSuggestion.REMOVAL)
        self.assertTrue(removal.extra['parser_removed'])
        self.assertIn('cannot be put back', removal.note)
        self.client.force_login(self.user)
        response = self.client.post(self.url('decisions/'), {
            'decisions': [{'id': removal.id, 'decision': 'REJECTED'}]},
            format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertIn('cannot be put back', str(response.data))
        # a group decision on the duplicate type leaves it alone
        response = self.client.post(self.url('decisions/'), {
            'groups': [{'key': 'REMOVAL:duplicate:row',
                        'decision': 'REJECTED'}]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         response.data)
        removal.refresh_from_db()
        self.assertEqual(removal.decision, ListCleaningSuggestion.ACCEPTED)
        groups = {g['key']: g for g in response.data['groups']}
        self.assertEqual(groups['REMOVAL:duplicate:row']['fixed'], 1)
        response = self.client.post(self.url('submit/'), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         response.data)
        self.items[2].refresh_from_db()
        self.assertEqual(self.items[2].status, FacilityListItem.DUPLICATE)
        self.assertIn('removed: duplicate of row 2', build_fixed_csv(run))

    def test_typed_country_updates_the_country_code(self):
        run = self._ingested_run()
        country = run.suggestions.get(field='country')
        self.client.force_login(self.user)
        response = self.client.post(self.url('decisions/'), {
            'decisions': [{'id': country.id, 'decision': 'EDITED',
                           'value': 'Narnia'}]}, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertIn('not a country', str(response.data))
        response = self.client.post(self.url('decisions/'), {
            'decisions': [{'id': country.id, 'decision': 'EDITED',
                           'value': 'Cambodia'}]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         response.data)
        response = self.client.post(self.url('submit/'), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         response.data)
        first = FacilityListItem.objects.get(pk=self.items[0].id)
        self.assertEqual(first.raw_json['country'], 'Cambodia')
        self.assertEqual(first.country_code, 'KH')

    def test_malformed_decision_bodies_are_rejected(self):
        self._ingested_run()
        self.client.force_login(self.user)
        for body in ({'decisions': ['12']}, {'groups': ['x']},
                     {'decisions': [None]}):
            response = self.client.post(
                self.url('decisions/'), body, format='json')
            self.assertEqual(response.status_code,
                             status.HTTP_400_BAD_REQUEST, body)

    def test_undo_hands_the_row_back_and_replies_with_that_row_only(self):
        run = self._ingested_run()
        flag = run.suggestions.get(code='address_po_box')
        self.client.force_login(self.user)
        response = self.client.post(self.url('decisions/'), {
            'decisions': [{'id': flag.id, 'decision': 'REJECTED'}]},
            format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         response.data)
        flag.refresh_from_db()
        self.assertTrue(flag.extra['by_row'])
        # only the changed row comes back, with the summary in full
        self.assertTrue(response.data['rows_partial'])
        self.assertEqual([r['row_number'] for r in response.data['rows']],
                         [3])
        self.assertEqual(response.data['summary']['rows_pending_review'],
                         1)
        response = self.client.post(self.url('decisions/'), {
            'decisions': [{'id': flag.id, 'decision': 'PENDING'}]},
            format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         response.data)
        flag.refresh_from_db()
        self.assertEqual(flag.decision, ListCleaningSuggestion.PENDING)
        # undone, so the group buttons cover it again
        self.assertFalse(flag.extra['by_row'])
        self.assertEqual(response.data['summary']['rows_pending_review'],
                         2)
        # the full read is never partial
        response = self.client.get(self.url())
        self.assertFalse(response.data['rows_partial'])
        self.assertEqual(len(response.data['rows']), 3)

    def test_refresh_marks_a_broken_result_failed(self):
        run = ListCleaningRun.objects.create(
            facility_list=self.list, runner=ListCleaningRun.STEP_FUNCTIONS,
            status=ListCleaningRun.RUNNING,
            review_until=timezone.now() + timedelta(minutes=60))
        broken = {'records': [{'row': 'two', 'status': 'auto_corrected',
                               'changes': [{'field': 'country',
                                            'value': 'VN',
                                            'reason': 'country_code'}]}]}
        with patch('api.services.list_cleaning.service.get_runner') as g:
            g.return_value.fetch_result.return_value = broken
            refresh_run(run)
        run.refresh_from_db()
        self.assertEqual(run.status, ListCleaningRun.FAILED)
        self.assertIn('Could not store', run.error)
        self.assertEqual(run.suggestions.count(), 0)

    def test_failure_does_not_undo_a_completed_run(self):
        run = self._ingested_run()
        from api.services.list_cleaning.service import _fail
        _fail(run, 'late failure from an overlapping refresh')
        run.refresh_from_db()
        self.assertEqual(run.status, ListCleaningRun.COMPLETE)
        self.assertEqual(run.error, '')

    def test_row_removal_waits_for_the_review_window(self):
        self._ingested_run()
        self.client.force_login(self.user)
        response = self.client.post(
            f'/api/facility-lists/{self.list.id}/remove/',
            {'list_item_id': self.items[1].id}, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.items[1].refresh_from_db()
        self.assertEqual(self.items[1].status, FacilityListItem.PARSED)

    def test_restart_refused_while_the_window_is_open(self):
        run = self._ingested_run()
        self.client.force_login(self.superuser)
        response = self.client.post(self.url('start/'), {}, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertIn('still reviewing', str(response.data))
        self.assertEqual(self.list.cleaning_runs.first().id, run.id)

    @override_switch(SWITCH_NAME, active=False)
    def test_switch_off_blocks_review_writes(self):
        run = self._ingested_run()
        fix = run.suggestions.filter(
            kind=ListCleaningSuggestion.CORRECTION).first()
        self.client.force_login(self.user)
        response = self.client.post(self.url('decisions/'), {
            'decisions': [{'id': fix.id, 'decision': 'REJECTED'}]},
            format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        response = self.client.post(self.url('submit/'), {}, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        run.refresh_from_db()
        self.assertIsNone(run.closed_at)

    def test_decisions_request_is_all_or_nothing(self):
        run = self._ingested_run()
        fix = run.suggestions.get(code='country_in_address')
        self.client.force_login(self.user)
        response = self.client.post(self.url('decisions/'), {
            'decisions': [{'id': fix.id, 'decision': 'REJECTED'}],
            'groups': [{'key': 'no:such:group', 'decision': 'ACCEPTED'}],
        }, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        fix.refresh_from_db()
        self.assertEqual(fix.decision, ListCleaningSuggestion.PENDING)

    def test_fixed_csv_neutralises_formulas(self):
        self.items[1].raw_json['name'] = '=HYPERLINK("http://x")'
        self.items[1].raw_data = '"Bangladesh","=HYPERLINK(""http://x"")",' \
                                 '"PO Box 41, Dhaka","500"'
        self.items[1].save()
        run = self._ingested_run()
        body = build_fixed_csv(run)
        self.assertNotIn(',=HYPERLINK', body)
        self.assertIn("'=HYPERLINK", body)

    def test_download_filename_is_encoded(self):
        self.list.file_name = 'my "list"; rm.csv'
        self.list.save()
        self._ingested_run()
        self.client.force_login(self.user)
        response = self.client.get(self.url('download/'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        disposition = response['Content-Disposition']
        # one filename parameter, with the quotes escaped inside it
        self.assertEqual(disposition.count('filename'), 1)
        self.assertIn('\\"list\\"', disposition)

    def test_stub_duplicate_key_includes_country(self):
        result = run_rules({'rows': [
            {'row': 2, 'country': 'Viet Nam', 'name': 'Same Name',
             'address': 'Industrial Zone 1'},
            {'row': 3, 'country': 'Cambodia', 'name': 'Same Name',
             'address': 'Industrial Zone 1'},
        ]})
        self.assertEqual(result['file_pass']['exact_duplicates'], [])
        self.assertEqual(
            [r['status'] for r in result['records']].count('removed'), 0)

    def test_warning_counts_flags_left_as_uploaded(self):
        run = self._ingested_run()
        flag = run.suggestions.get(code='address_po_box')
        record_decisions(
            run, [{'id': flag.id, 'decision': 'REJECTED'}], self.user)
        self.client.force_login(self.user)
        summary = self.client.get(self.url()).data['summary']
        self.assertEqual(summary['rows_blocking_pending'], 0)
        self.assertEqual(summary['rows_flagged_unresolved'], 1)

    def test_submit_rejects_a_non_boolean_as_uploaded(self):
        run = self._ingested_run()
        self.client.force_login(self.user)
        response = self.client.post(
            self.url('submit/'), {'as_uploaded': 'false'}, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        run.refresh_from_db()
        self.assertIsNone(run.closed_at)

    def test_repeated_result_does_not_wipe_decisions(self):
        run = self._ingested_run()
        fix = run.suggestions.get(code='country_in_address')
        before = run.suggestions.count()
        record_decisions(
            run,
            [{'id': fix.id, 'decision': ListCleaningSuggestion.REJECTED}],
            self.user)
        # a second poll that fetched the same result
        ingest_result(run, SAMPLE_RESULT)
        fix.refresh_from_db()
        self.assertEqual(fix.decision, ListCleaningSuggestion.REJECTED)
        self.assertEqual(run.suggestions.count(), before)

    def test_imported_run_opens_a_review_window(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, 'records.json')
            with open(path, 'w') as f:
                json.dump(SAMPLE_RESULT, f)
            call_command('list_cleaning', '-l', str(self.list.id),
                         '--records', path, stdout=StringIO())
        run = self.list.cleaning_runs.first()
        self.assertEqual(run.status, ListCleaningRun.COMPLETE)
        self.assertIsNotNone(run.review_until)
        self.client.force_login(self.user)
        response = self.client.post(
            self.url('submit/'), {'as_uploaded': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         response.data)

    def test_moderation_waits_for_the_review_window(self):
        self._ingested_run()
        self.client.force_login(self.superuser)
        for action in ('approve', 'reject'):
            response = self.client.post(
                f'/api/facility-lists/{self.list.id}/{action}/',
                {'reason': 'x'}, format='json')
            self.assertEqual(response.status_code,
                             status.HTTP_400_BAD_REQUEST, action)
            self.assertIn('review window', str(response.data))
        self.list.refresh_from_db()
        self.assertEqual(self.list.status, FacilityList.PENDING)

    def test_moderation_notices_a_run_that_failed_in_the_pipeline(self):
        # The execution failed out in Step Functions while nobody had the
        # review page open: the run is still RUNNING here. Moderation
        # must poll it rather than wait out the window.
        run = ListCleaningRun.objects.create(
            facility_list=self.list, runner=ListCleaningRun.STEP_FUNCTIONS,
            status=ListCleaningRun.RUNNING, execution_arn='arn:exec',
            review_until=timezone.now() + timedelta(minutes=60))
        self.client.force_login(self.superuser)
        with patch('api.services.list_cleaning.service.get_runner') as g:
            g.return_value.fetch_result.side_effect = RunFailed(
                'Execution ended with FAILED: States.Timeout')
            response = self.client.post(
                f'/api/facility-lists/{self.list.id}/approve/',
                {'reason': 'x'}, format='json')
        self.assertNotEqual(response.status_code,
                            status.HTTP_400_BAD_REQUEST, response.data)
        run.refresh_from_db()
        self.assertEqual(run.status, ListCleaningRun.FAILED)
        self.assertEqual(run.closed_reason, ListCleaningRun.FAILED_RUN)
        self.assertIn('States.Timeout', run.error)

    def test_moderation_waits_while_the_pipeline_is_still_running(self):
        ListCleaningRun.objects.create(
            facility_list=self.list, runner=ListCleaningRun.STEP_FUNCTIONS,
            status=ListCleaningRun.RUNNING, execution_arn='arn:exec',
            review_until=timezone.now() + timedelta(minutes=60))
        self.client.force_login(self.superuser)
        with patch('api.services.list_cleaning.service.get_runner') as g:
            g.return_value.fetch_result.return_value = None
            response = self.client.post(
                f'/api/facility-lists/{self.list.id}/approve/',
                {'reason': 'x'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('review window', str(response.data))

    def test_release_command_polls_running_runs(self):
        run = ListCleaningRun.objects.create(
            facility_list=self.list, runner=ListCleaningRun.STEP_FUNCTIONS,
            status=ListCleaningRun.RUNNING, execution_arn='arn:exec',
            review_until=timezone.now() + timedelta(minutes=60))
        with patch('api.services.list_cleaning.service.get_runner') as g:
            g.return_value.fetch_result.side_effect = RunFailed('boom')
            call_command('list_cleaning_release', stdout=StringIO())
        run.refresh_from_db()
        self.assertEqual(run.status, ListCleaningRun.FAILED)
        self.assertIsNotNone(run.closed_at)

    def test_closing_the_walkthrough_is_remembered_per_user(self):
        self._ingested_run()
        self.client.force_login(self.user)
        self.assertFalse(self.client.get(self.url()).data['tour_seen'])
        response = self.client.post(self.url('events/'), {
            'kind': 'tour_dismissed', 'meta': {'how': 'skipped'}},
            format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.client.get(self.url()).data['tour_seen'])
        # on every list of theirs, not just this one
        other_list = FacilityList.objects.create(
            header='country,name,address', file_name='b.csv', name='B')
        Source.objects.create(
            source_type=Source.LIST, facility_list=other_list,
            contributor=self.contributor)
        response = self.client.get(
            f'/api/facility-lists/{other_list.id}/cleaning/')
        self.assertIsNone(response.data['run'])
        self.assertTrue(response.data['tour_seen'])
        # but only for them
        self.client.force_login(self.superuser)
        self.assertFalse(self.client.get(self.url()).data['tour_seen'])

    def test_review_events_and_metrics(self):
        run = self._ingested_run()
        self.client.force_login(self.user)
        for kind, meta in (('opened', {}), ('left', {'seconds_open': 40}),
                           ('resumed', {})):
            response = self.client.post(self.url('events/'), {
                'kind': kind, 'meta': meta}, format='json')
            self.assertEqual(response.status_code,
                             status.HTTP_201_CREATED, kind)
        self.assertEqual(
            self.client.post(self.url('events/'), {'kind': 'submitted'},
                             format='json').status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            [e.kind for e in run.events.all()],
            ['opened', 'left', 'resumed'])
        self.client.post(self.url('submit/'), {}, format='json')

        # a second list whose window lapsed before anyone looked
        other = FacilityList.objects.create(
            header='country,name,address,number_of_workers',
            file_name='other.csv', name='Other')
        Source.objects.create(
            source_type=Source.LIST, facility_list=other,
            contributor=self.contributor)
        lapsed = ListCleaningRun.objects.create(
            facility_list=other, runner=ListCleaningRun.IMPORT,
            review_until=timezone.now() - timedelta(minutes=1))
        ingest_result(lapsed, SAMPLE_RESULT)

        self.assertEqual(
            self.client.get('/api/facility-lists/cleaning-metrics/')
            .status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_login(self.superuser)
        response = self.client.get('/api/facility-lists/cleaning-metrics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # the lapsed run is only closed once something reads it
        self.assertEqual(response.data['runs_open'], 1)
        from api.services.list_cleaning import sweep_lapsed
        self.assertEqual(sweep_lapsed(), 1)
        response = self.client.get('/api/facility-lists/cleaning-metrics/')
        self.assertEqual(response.data['runs_complete'], 2)
        self.assertEqual(response.data['submitted_with_changes'], 1)
        self.assertEqual(response.data['lapsed_never_opened'], 1)
        self.assertEqual(response.data['left_at_least_once'], 1)
        self.assertEqual(response.data['resumed_at_least_once'], 1)
        self.assertEqual(response.data['submit_rate'], 0.5)
        # nothing was decided in that submission: the automatic fixes
        # went on, the one suggested fix and the flag were left
        self.assertEqual(response.data['median_auto_applied'], 3)
        self.assertEqual(response.data['median_reviewed_changes'], 0)
        self.assertEqual(response.data['totals']['auto_applied'], 3)
        self.assertEqual(response.data['totals']['fixes_offered'], 1)
        self.assertEqual(response.data['totals']['flags_left_as_uploaded'],
                         1)

    def test_start_is_superuser_only(self):
        self.client.force_login(self.user)
        self.assertEqual(
            self.client.post(self.url('start/'), {}).status_code,
            status.HTTP_403_FORBIDDEN)
        self.client.force_login(self.superuser)
        response = self.client.post(self.url('start/'), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['run']['status'], 'COMPLETE')
