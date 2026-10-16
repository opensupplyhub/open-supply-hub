from unittest.mock import patch

from django.contrib.gis.geos import Point
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase, override_settings

from api.candidate_exclusion import exclude_candidate_rows
from api.constants import OriginSource
from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.reassert_rba_promotions import after_database_sync


class AfterDatabaseSyncTest(SimpleTestCase):
    '''
    After a successful sync on the RBA instance, promotions the overwrite
    reverted have to be restored. These tests cover that post-sync hook
    without importing sync_databases, whose synchronizer has no unit tests
    and must not enter the coverage report as a side effect.
    '''

    databases = []

    @override_settings(INSTANCE_SOURCE=OriginSource.RBA)
    @patch('api.reassert_rba_promotions.call_command')
    def test_reasserts_promotions_after_an_error_free_sync(
            self, nested_call_command):
        after_database_sync(error_count=0, dry_run=False)

        nested_call_command.assert_called_once_with(
            'reassert_rba_promotions',
            dry_run=False,
        )

    @override_settings(INSTANCE_SOURCE=OriginSource.RBA)
    @patch('api.reassert_rba_promotions.call_command')
    def test_passes_dry_run_through_to_the_reassert(
            self, nested_call_command):
        after_database_sync(error_count=0, dry_run=True)

        nested_call_command.assert_called_once_with(
            'reassert_rba_promotions',
            dry_run=True,
        )

    @override_settings(INSTANCE_SOURCE=OriginSource.OSHUB)
    @patch('api.reassert_rba_promotions.call_command')
    def test_skips_reassert_outside_the_rba_instance(
            self, nested_call_command):
        after_database_sync(error_count=0)

        nested_call_command.assert_not_called()

    @override_settings(INSTANCE_SOURCE=OriginSource.RBA)
    @patch('api.reassert_rba_promotions.call_command')
    def test_does_not_reassert_after_a_partial_sync(
            self, nested_call_command):
        with self.assertRaises(CommandError) as context:
            after_database_sync(error_count=2)

        self.assertIn('2 error(s)', str(context.exception))
        nested_call_command.assert_not_called()


class ExcludeCandidateRowsTest(TestCase):
    '''
    The RBA sync reads source rows through ``exclude_candidate_rows`` with
    each model's ``candidate_lookup`` (sync_databases.SYNC_MODELS). These
    tests pin the helper against real rows so a candidate production
    location, and everything hanging off it, is never read from the
    source instance.
    '''

    def setUp(self):
        user = User.objects.create(email='sync@example.com')
        contributor = Contributor.objects.create(
            admin=user,
            name='sync contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        guard_settings = override_settings(
            EARTH_GENOME_CONTRIBUTOR_ID=contributor.id
        )
        guard_settings.enable()
        self.addCleanup(guard_settings.disable)
        facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='Sync list'
        )
        source = Source.objects.create(
            facility_list=facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=contributor,
        )

        def make_item(row_index):
            return FacilityListItem.objects.create(
                name='Item',
                address='Address',
                country_code='US',
                sector=['Apparel'],
                row_index=row_index,
                geocoded_point=Point(0, 0),
                status=FacilityListItem.CONFIRMED_MATCH,
                source=source,
            )

        def make_match(item, facility):
            return FacilityMatch.objects.create(
                status=FacilityMatch.AUTOMATIC,
                facility=facility,
                facility_list_item=item,
                confidence=0.85,
                results='',
            )

        self.regular_item = make_item(1)
        self.regular = Facility.objects.create(
            name='Regular',
            address='Address',
            country_code='US',
            location=Point(0, 0),
            created_from=self.regular_item,
        )
        self.regular_item.facility = self.regular
        self.regular_item.save()
        self.regular_match = make_match(self.regular_item, self.regular)

        self.candidate_item = make_item(2)
        self.candidate = Facility.objects.create(
            name='Candidate',
            address='Address',
            country_code='US',
            location=Point(1, 1),
            created_from=self.candidate_item,
            is_candidate=True,
            source='earth_genome',
            external_id='eg-sync-0001',
        )
        self.candidate_item.facility = self.candidate
        self.candidate_item.save()
        self.candidate_match = make_match(self.candidate_item, self.candidate)

        self.unmatched_item = make_item(3)

    def test_facility_lookup_drops_candidates_even_when_opted_in(self):
        ids = set(
            exclude_candidate_rows(
                Facility.including_candidates.all(), 'is_candidate'
            ).values_list('id', flat=True)
        )

        self.assertEqual(ids, {self.regular.id})

    def test_child_rows_of_a_candidate_are_dropped(self):
        ids = set(
            exclude_candidate_rows(
                FacilityMatch.objects.all(), 'facility__is_candidate'
            ).values_list('id', flat=True)
        )

        self.assertIn(self.regular_match.id, ids)
        self.assertNotIn(self.candidate_match.id, ids)

    def test_rows_with_a_null_facility_are_kept(self):
        ids = set(
            exclude_candidate_rows(
                FacilityListItem.objects.all(), 'facility__is_candidate'
            ).values_list('id', flat=True)
        )

        self.assertEqual(ids, {self.regular_item.id, self.unmatched_item.id})

    def test_no_lookup_leaves_the_queryset_alone(self):
        queryset = Contributor.objects.all()

        self.assertIs(exclude_candidate_rows(queryset, None), queryset)

    def test_every_model_with_a_facility_path_declares_a_lookup(self):
        '''
        Reads SYNC_MODELS from the command's source text rather than
        importing it, keeping the synchronizer out of the coverage report.
        '''
        import ast
        import pathlib

        import api

        command_path = (
            pathlib.Path(api.__file__).parent
            / 'management' / 'commands' / 'sync_databases.py'
        )
        module = ast.parse(command_path.read_text())
        sync_models = next(
            node.value
            for node in ast.walk(module)
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == 'SYNC_MODELS'
                for target in node.targets
            )
        )
        declared = {}
        for key, value in zip(sync_models.keys, sync_models.values):
            config = {
                k.value: v for k, v in zip(value.keys, value.values)
            }
            lookup = config.get('candidate_lookup')
            declared[key.value] = (
                lookup.value if lookup is not None else None
            )

        self.assertEqual(declared['Facility'], 'is_candidate')
        for name in (
            'FacilityListItem',
            'FacilityMatch',
            'FacilityLocation',
            'FacilityClaim',
            'ExtendedField',
            'FacilityActivityReport',
            'FacilityAlias',
        ):
            self.assertEqual(
                declared[name], 'facility__is_candidate', name
            )
        for name in ('User', 'Contributor', 'FacilityList', 'Source'):
            self.assertIsNone(declared[name], name)
