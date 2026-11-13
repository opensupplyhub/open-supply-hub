import csv
import os
import tempfile
from datetime import date
from io import StringIO

from django.contrib.auth.models import Group
from django.contrib.gis.geos import Point
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse
from rest_framework.test import APITestCase
from waffle.testutils import override_flag

from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityProfileCompleteness,
    Source,
    User,
)
from api.profile_completeness import (
    COMPONENT_KEYS,
    PROFILE_COMPLETENESS_FLAG,
    level_for_score,
)


COMPONENT_VALUES = {
    'claimed_status': 1,
    'recency_score': 0.84,
    'contribution_count_score': 0.68,
    'contribution_mix_score': 0.67,
    'completeness_score': 0.667,
    'claimed_only_score': 0.15,
    'assessments_audits_score': 1,
    'certifications_score': 0,
}


class ProfileCompletenessTestBase(APITestCase):
    def setUp(self):
        self.password = 'example123'
        self.superuser = self._make_user('admin@example.com')
        self.superuser.is_superuser = True
        self.superuser.is_staff = True
        self.superuser.save()
        self.user = self._make_user('user@example.com')
        self.contributor = Contributor.objects.create(
            name='Contributor', admin=self.user
        )
        self.facility = self._make_facility('US2026001AAAAAA')

    def _make_user(self, email):
        user = User.objects.create(email=email)
        user.set_password(self.password)
        user.save()
        return user

    def _make_facility(self, os_id):
        facility_list = FacilityList.objects.create(
            header='header', file_name=os_id, name=os_id
        )
        source = Source.objects.create(
            facility_list=facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        list_item = FacilityListItem.objects.create(
            name='name',
            address='address',
            country_code='US',
            sector=['Apparel'],
            source=source,
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
        )
        return Facility.objects.create(
            id=os_id,
            name='name',
            address='address',
            country_code='US',
            location=Point(0, 0),
            created_from=list_item,
        )

    def _url(self, os_id=None):
        return reverse(
            'profile_completeness',
            kwargs={'os_id': os_id or self.facility.id},
        )


class LevelForScoreTest(APITestCase):
    def test_levels_follow_the_cutoffs(self):
        self.assertEqual(level_for_score(0), 1)
        self.assertEqual(level_for_score(0.449), 1)
        self.assertEqual(level_for_score(0.45), 2)
        self.assertEqual(level_for_score(0.699), 2)
        self.assertEqual(level_for_score(0.70), 3)
        self.assertEqual(level_for_score(1), 3)
        self.assertIsNone(level_for_score(None))


class ProfileCompletenessEndpointTest(ProfileCompletenessTestBase):
    def setUp(self):
        super().setUp()
        FacilityProfileCompleteness.objects.create(
            facility=self.facility,
            run_date=date(2026, 11, 11),
            score=0.627,
            components=COMPONENT_VALUES,
            scorer_version='v111126',
        )
        FacilityProfileCompleteness.objects.create(
            facility=self.facility,
            run_date=date(2026, 11, 12),
            classifier_tier='high',
            classifier_agreement_tier='best',
            classifier_field_tier='high',
            classifier_model='model-1.0',
        )

    def test_anonymous_visitor_gets_404(self):
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 404)

    def test_regular_user_gets_404(self):
        self.client.login(email=self.user.email, password=self.password)
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 404)

    def test_superuser_gets_score_and_classifier(self):
        self.client.login(
            email=self.superuser.email, password=self.password
        )
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Cache-Control'], 'private, no-store')

        data = response.json()
        self.assertEqual(data['os_id'], self.facility.id)
        self.assertEqual(data['score']['value'], 0.627)
        self.assertEqual(data['score']['level'], 2)
        self.assertEqual(data['score']['max_level'], 3)
        self.assertEqual(data['score']['scorer_version'], 'v111126')
        self.assertEqual(data['score']['run_date'], '2026-11-11')
        self.assertEqual(
            [c['key'] for c in data['score']['components']],
            list(COMPONENT_KEYS),
        )
        self.assertEqual(
            data['score']['components'][0],
            {'key': 'claimed_status', 'label': 'Claimed status', 'value': 1},
        )
        self.assertEqual(data['classifier'], {
            'tier': 'high',
            'level': 3,
            'agreement_tier': 'best',
            'field_tier': 'high',
            'model': 'model-1.0',
            'run_date': '2026-11-12',
        })

    def test_group_member_gets_data(self):
        Group.objects.get(name=PROFILE_COMPLETENESS_FLAG).user_set.add(
            self.user
        )
        self.client.login(email=self.user.email, password=self.password)
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)

    @override_flag(PROFILE_COMPLETENESS_FLAG, active=False)
    def test_flag_off_hides_it_from_superusers(self):
        self.client.login(
            email=self.superuser.email, password=self.password
        )
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 404)

    def test_latest_run_of_each_kind_is_returned(self):
        FacilityProfileCompleteness.objects.create(
            facility=self.facility,
            run_date=date(2026, 12, 1),
            score=0.71,
            components=COMPONENT_VALUES,
            scorer_version='v120126',
        )
        self.client.login(
            email=self.superuser.email, password=self.password
        )
        data = self.client.get(self._url()).json()
        self.assertEqual(data['score']['value'], 0.71)
        self.assertEqual(data['score']['level'], 3)
        self.assertEqual(data['classifier']['run_date'], '2026-11-12')

    def test_location_without_data_gets_404(self):
        other = self._make_facility('US2026001BBBBBB')
        self.client.login(
            email=self.superuser.email, password=self.password
        )
        response = self.client.get(self._url(other.id))
        self.assertEqual(response.status_code, 404)

    def test_score_only_location_has_null_classifier(self):
        FacilityProfileCompleteness.objects.exclude(
            classifier_tier=''
        ).delete()
        self.client.login(
            email=self.superuser.email, password=self.password
        )
        data = self.client.get(self._url()).json()
        self.assertIsNone(data['classifier'])
        self.assertEqual(data['score']['level'], 2)


class LoadProfileCompletenessCommandTest(ProfileCompletenessTestBase):
    def setUp(self):
        super().setUp()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def _write_csv(self, name, header, rows):
        path = os.path.join(self.tmp.name, name)
        with open(path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(header)
            writer.writerows(rows)
        return path

    def _scores_file(self, rows=None):
        header = ['facility_id', 'final_data_quality_score'] + list(
            COMPONENT_KEYS
        )
        values = [COMPONENT_VALUES[key] for key in COMPONENT_KEYS]
        if rows is None:
            rows = [
                [self.facility.id, 0.627] + values,
                ['XX0000000UNKNOWN', 0.2] + values,
            ]
        return self._write_csv('scores.csv', header, rows)

    def _classifier_file(self, rows=None):
        header = ['os_id', 'A_tier', 'B_tier', 'final_tier', 'model']
        if rows is None:
            rows = [[self.facility.id, 'best', 'high', 'high', 'model-1.0']]
        return self._write_csv('classifier.csv', header, rows)

    def _run(self, **options):
        out = StringIO()
        call_command('load_profile_completeness', stdout=out, **options)
        return out.getvalue()

    def test_loads_both_files_into_one_row_and_skips_unknown_ids(self):
        output = self._run(
            scores_file=self._scores_file(),
            scorer_version='v111126',
            classifier_file=self._classifier_file(),
            run_date=date(2026, 11, 12),
        )

        run = FacilityProfileCompleteness.objects.get()
        self.assertEqual(run.facility_id, self.facility.id)
        self.assertEqual(run.run_date, date(2026, 11, 12))
        self.assertEqual(run.score, 0.627)
        self.assertEqual(run.level, 2)
        self.assertEqual(run.components['recency_score'], 0.84)
        self.assertEqual(run.scorer_version, 'v111126')
        self.assertEqual(run.classifier_tier, 'high')
        self.assertEqual(run.classifier_agreement_tier, 'best')
        self.assertEqual(run.classifier_field_tier, 'high')
        self.assertEqual(run.classifier_model, 'model-1.0')
        self.assertIn('Loaded 1 rows', output)
        self.assertIn('XX0000000UNKNOWN', output)

    def test_same_run_date_updates_and_new_run_date_adds(self):
        self._run(
            scores_file=self._scores_file(), run_date=date(2026, 11, 11)
        )
        self._run(
            classifier_file=self._classifier_file(),
            run_date=date(2026, 11, 11),
        )
        run = FacilityProfileCompleteness.objects.get()
        self.assertEqual(run.score, 0.627)
        self.assertEqual(run.classifier_tier, 'high')

        self._run(
            scores_file=self._scores_file(), run_date=date(2026, 12, 1)
        )
        self.assertEqual(FacilityProfileCompleteness.objects.count(), 2)

    def test_dry_run_changes_nothing(self):
        output = self._run(scores_file=self._scores_file(), dry_run=True)
        self.assertEqual(FacilityProfileCompleteness.objects.count(), 0)
        self.assertIn('Nothing was changed', output)

    def test_requires_a_file(self):
        with self.assertRaises(CommandError):
            self._run()

    def test_rejects_missing_columns(self):
        path = self._write_csv(
            'bad.csv', ['facility_id', 'final_data_quality_score'], []
        )
        with self.assertRaisesMessage(CommandError, 'missing the column'):
            self._run(scores_file=path)

    def test_rejects_out_of_range_score(self):
        values = [COMPONENT_VALUES[key] for key in COMPONENT_KEYS]
        path = self._scores_file([[self.facility.id, 1.4] + values])
        with self.assertRaisesMessage(CommandError, 'outside 0 to 1'):
            self._run(scores_file=path)
        self.assertEqual(FacilityProfileCompleteness.objects.count(), 0)

    def test_rejects_unknown_tier(self):
        path = self._classifier_file(
            [[self.facility.id, 'high', 'high', 'excellent', 'model-1.0']]
        )
        with self.assertRaisesMessage(CommandError, 'expected one of'):
            self._run(classifier_file=path)
