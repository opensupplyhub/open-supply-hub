import csv
import os
import tempfile
from io import StringIO
from unittest.mock import patch

from django.core.cache import caches
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from waffle.testutils import override_switch

from api.constants import FacilityClaimStatuses
from api.facility_index_backfill.specs import (
    build_update_sql,
    get_field_spec,
)
from api.facility_type_processing_type import (
    ALL_FACILITY_TYPES,
    FACILITY_PROCESSING_TYPES,
)
from api.isic_taxonomy.crosswalk import (
    CROSSWALK_CSV_PATH,
    CrosswalkError,
    load_crosswalk_rows,
)
from api.models import ExtendedField, FacilityClaim, IsicCrosswalkEntry
from api.models.facility.facility_index import FacilityIndex
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase


def mapped_codes(facility_types, processing_types):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT isic_level, isic_code '
            'FROM isic_mapped_codes(%s::varchar[], %s::varchar[])',
            [facility_types, processing_types],
        )
        rows = cursor.fetchall()
    codes = {'section': [], 'division': [], 'group': [], 'class': []}
    for level, code in rows:
        codes[level].append(code)
    return {level: sorted(values) for level, values in codes.items()}


NO_CODES = {'section': [], 'division': [], 'group': [], 'class': []}


class CrosswalkFileTest(SimpleTestCase):
    '''The shipped CSV is valid and only names real taxonomy values.'''

    def test_shipped_crosswalk_loads(self):
        rows = load_crosswalk_rows()
        self.assertGreater(len(rows), 100)
        self.assertTrue(any(row['isic_class'] for row in rows))

    def test_every_row_names_a_real_facility_and_processing_type(self):
        # A misspelled value would never match a location, silently.
        pairs = set()
        facility_types = set()
        for key, facility_type in ALL_FACILITY_TYPES.items():
            facility_types.add(facility_type.lower())
            for processing_type in FACILITY_PROCESSING_TYPES.get(
                key, {}
            ).values():
                pairs.add((facility_type.lower(), processing_type.lower()))

        for row in load_crosswalk_rows():
            facility_type = row['facility_type'].lower()
            processing_type = row['processing_type'].lower()
            with self.subTest(row=row):
                self.assertIn(facility_type, facility_types)
                if processing_type:
                    self.assertIn((facility_type, processing_type), pairs)

    def test_every_code_has_one_title_across_rows(self):
        titles = {}
        for row in load_crosswalk_rows():
            for level in ('section', 'division', 'group', 'class'):
                code = row[f'isic_{level}']
                if code:
                    with self.subTest(code=code):
                        title = row[f'isic_{level}_title']
                        self.assertEqual(titles.setdefault(code, title), title)

    def test_unmapped_rows_carry_no_codes(self):
        with open(CROSSWALK_CSV_PATH, newline='') as csv_file:
            rows = list(csv.DictReader(csv_file))
        for row in rows:
            if row['match_type'] == 'Does not map':
                with self.subTest(row=row):
                    self.assertEqual(row['isic_section'], '')

    def _write_csv(self, content):
        handle = tempfile.NamedTemporaryFile(
            'w', suffix='.csv', delete=False
        )
        handle.write(content)
        handle.close()
        self.addCleanup(os.unlink, handle.name)
        return handle.name

    HEADER = (
        'facility_type,processing_type,isic_section,isic_section_title,'
        'isic_division,isic_division_title,isic_group,isic_group_title,'
        'isic_class,isic_class_title,match_type\n'
    )

    def test_accepts_a_valid_row(self):
        path = self._write_csv(
            self.HEADER
            + 'Final Product Assembly,Sewing,C,Manufacturing,14,Apparel,'
            '141,Apparel,1410,Apparel,Exact\n'
        )
        self.assertEqual(len(load_crosswalk_rows(path)), 1)

    def test_rejects_class_outside_its_group(self):
        path = self._write_csv(
            self.HEADER
            + 'Final Product Assembly,Sewing,C,Manufacturing,14,Apparel,'
            '141,Apparel,1311,Spinning,Exact\n'
        )
        with self.assertRaisesRegex(CrosswalkError, 'not under 141'):
            load_crosswalk_rows(path)

    def test_rejects_code_without_title(self):
        path = self._write_csv(
            self.HEADER + 'Final Product Assembly,Sewing,C,,,,,,,,Partial\n'
        )
        with self.assertRaisesRegex(CrosswalkError, 'title'):
            load_crosswalk_rows(path)

    def test_rejects_duplicate_rows_ignoring_case(self):
        path = self._write_csv(
            self.HEADER
            + 'Final Product Assembly,Sewing,C,Manufacturing,,,,,,,Partial\n'
            'final product assembly,SEWING,C,Manufacturing,,,,,,,Partial\n'
        )
        with self.assertRaisesRegex(CrosswalkError, 'duplicate'):
            load_crosswalk_rows(path)

    def test_rejects_level_without_parent(self):
        path = self._write_csv(
            self.HEADER
            + 'Final Product Assembly,Sewing,,,14,Apparel,,,,,Exact\n'
        )
        with self.assertRaisesRegex(CrosswalkError, 'without gaps'):
            load_crosswalk_rows(path)

    def test_rejects_missing_columns(self):
        path = self._write_csv('facility_type,processing_type\nA,B\n')
        with self.assertRaisesRegex(CrosswalkError, 'Missing columns'):
            load_crosswalk_rows(path)


class IsicMappedCodesTest(TestCase):
    '''
    isic_mapped_codes() against the seeded crosswalk. Expected codes come
    from the OSDEV-3414 crosswalk rows named in each test.
    '''

    def test_mapped_columns_have_a_valid_gin_index(self):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT idx.indisvalid FROM pg_index idx "
                "JOIN pg_class cls ON cls.oid = idx.indexrelid "
                "WHERE cls.relname = 'api_facilityindex_isic_mapped_gin'"
            )
            self.assertEqual(cursor.fetchall(), [(True,)])

    def test_migration_seeds_every_csv_row(self):
        self.assertEqual(
            IsicCrosswalkEntry.objects.count(),
            len(load_crosswalk_rows()),
        )

    def test_processing_type_maps_to_class(self):
        # AC1: Final Product Assembly > Cut & Sew -> 1410.
        self.assertEqual(
            mapped_codes(['Final Product Assembly'], ['Cut & Sew']),
            {
                'section': ['C'],
                'division': ['14'],
                'group': ['141'],
                'class': ['1410'],
            },
        )

    def test_facility_type_alone_maps_to_broader_level(self):
        # AC2: Textile or Material Production -> section C only.
        self.assertEqual(
            mapped_codes(['Textile or Material Production'], []),
            {'section': ['C'], 'division': [], 'group': [], 'class': []},
        )

    def test_data_center_maps_from_facility_type(self):
        self.assertEqual(
            mapped_codes(['Data Center'], []),
            {
                'section': ['J'],
                'division': ['63'],
                'group': ['631'],
                'class': ['6311'],
            },
        )

    def test_unmappable_processing_type_does_not_fall_back(self):
        # AC3: Final Product Assembly > Tailoring "does not map", and the
        # processing type takes precedence over the facility type row (C).
        self.assertEqual(
            mapped_codes(['Final Product Assembly'], ['Tailoring']),
            NO_CODES,
        )

    def test_unmappable_facility_type_maps_to_nothing(self):
        self.assertEqual(
            mapped_codes(['Raw Material Processing or Production'], []),
            NO_CODES,
        )

    def test_no_taxonomy_values_maps_to_nothing(self):
        # AC4.
        self.assertEqual(mapped_codes([], []), NO_CODES)
        self.assertEqual(mapped_codes(None, None), NO_CODES)

    def test_matching_ignores_case_and_whitespace(self):
        self.assertEqual(
            mapped_codes([' final product assembly'], ['CUT & SEW ']),
            mapped_codes(['Final Product Assembly'], ['Cut & Sew']),
        )

    def test_raw_values_that_are_not_taxonomy_values_are_ignored(self):
        self.assertEqual(mapped_codes(['Factory'], ['denim']), NO_CODES)

    def test_each_facility_type_falls_back_independently(self):
        # Cut & Sew covers Final Product Assembly; Warehousing has no
        # processing type, so its own row (5210) applies too.
        self.assertEqual(
            mapped_codes(
                ['Final Product Assembly', 'Warehousing / Distribution'],
                ['Cut & Sew'],
            ),
            {
                'section': ['C', 'H'],
                'division': ['14', '52'],
                'group': ['141', '521'],
                'class': ['1410', '5210'],
            },
        )

    def test_processing_type_needs_its_facility_type(self):
        # Pairs only apply when the processing type's own facility type is
        # on the location.
        self.assertEqual(
            mapped_codes(['Office / HQ'], ['Cut & Sew']),
            mapped_codes(['Office / HQ'], []),
        )


class IsicMappedIndexingTest(FacilityAPITestCaseBase):
    '''The index triggers keep the isic_mapped_* columns current.'''

    def _add_processing_type(self, facility_type, processing_type, **kwargs):
        value = {
            'raw_values': processing_type,
            'matched_values': [
                ['PROCESSING_TYPE', 'EXACT', facility_type, processing_type],
            ],
        }
        for field_name in (
            ExtendedField.FACILITY_TYPE,
            ExtendedField.PROCESSING_TYPE,
        ):
            ExtendedField.objects.create(
                contributor=self.contributor,
                facility=self.facility,
                field_name=field_name,
                value=value,
                **kwargs,
            )

    def _index(self):
        return FacilityIndex.objects.get(id=self.facility.id)

    def test_new_processing_type_populates_mapped_columns(self):
        self._add_processing_type(
            'Final Product Assembly',
            'Cut & Sew',
            facility_list_item=self.list_item,
        )

        index = self._index()
        self.assertEqual(index.processing_type, ['Cut & Sew'])
        self.assertEqual(index.isic_mapped_section, ['C'])
        self.assertEqual(index.isic_mapped_class, ['1410'])

    def test_mapped_values_never_touch_submitted_isic_columns(self):
        self._add_processing_type(
            'Final Product Assembly',
            'Cut & Sew',
            facility_list_item=self.list_item,
        )

        index = self._index()
        self.assertEqual(index.isic_section, [])
        self.assertEqual(index.isic_class, [])
        self.assertFalse(
            ExtendedField.objects.filter(
                facility=self.facility,
                field_name=ExtendedField.ISIC_4,
            ).exists()
        )

    def test_removing_processing_type_clears_mapped_columns(self):
        self._add_processing_type(
            'Final Product Assembly',
            'Cut & Sew',
            facility_list_item=self.list_item,
        )
        ExtendedField.objects.filter(facility=self.facility).delete()

        index = self._index()
        self.assertEqual(index.isic_mapped_section, [])
        self.assertEqual(index.isic_mapped_class, [])

    def test_claim_approval_and_revocation_update_mapped_columns(self):
        # Goes through perform_facility_claim_indexing (0236), not the
        # extended field trigger, so it proves the index trigger covers
        # every procedure that rewrites the taxonomy columns.
        claim = FacilityClaim.objects.create(
            facility=self.facility,
            contributor=self.contributor,
            contact_person='Person',
            job_title='Title',
            status=FacilityClaimStatuses.PENDING,
        )
        self._add_processing_type(
            'Warehousing / Distribution',
            'Warehousing / Distribution',
            facility_claim=claim,
        )
        self.assertEqual(self._index().isic_mapped_class, [])

        claim.status = FacilityClaimStatuses.APPROVED
        claim.save()
        self.assertEqual(self._index().isic_mapped_class, ['5210'])

        claim.status = FacilityClaimStatuses.REVOKED
        claim.save()
        self.assertEqual(self._index().isic_mapped_class, [])

    def test_deactivating_the_source_clears_mapped_columns(self):
        # perform_source_indexing (0235) drops the source's taxonomy values
        # from the index; the mapped values must go with them.
        self._add_processing_type(
            'Final Product Assembly',
            'Cut & Sew',
            facility_list_item=self.list_item,
        )
        self.assertEqual(self._index().isic_mapped_class, ['1410'])

        self.source.is_active = False
        self.source.save()

        index = self._index()
        self.assertEqual(index.processing_type, [])
        self.assertEqual(index.isic_mapped_class, [])

    def test_backfill_spec_recomputes_mapped_columns(self):
        self._add_processing_type(
            'Final Product Assembly',
            'Cut & Sew',
            facility_list_item=self.list_item,
        )
        # Simulate a row indexed before 0256 existed. A plain UPDATE of the
        # mapped columns does not fire the taxonomy-column trigger.
        FacilityIndex.objects.filter(id=self.facility.id).update(
            isic_mapped_section=[],
            isic_mapped_class=[],
        )

        with connection.cursor() as cursor:
            cursor.execute(
                build_update_sql(get_field_spec('isic_4_mapped')),
                {
                    'workers': 1,
                    'worker_id': 0,
                    'last_id': '',
                    'batch_size': 100,
                },
            )
            updated_ids = [row[0] for row in cursor.fetchall()]

        self.assertEqual(updated_ids, [self.facility.id])
        self.assertEqual(self._index().isic_mapped_class, ['1410'])

    def test_backfill_filter_respects_batch_cursor(self):
        # The filter is appended after AND; an unparenthesized OR would let
        # rows before last_id back in and the batches would never end.
        self._add_processing_type(
            'Final Product Assembly',
            'Cut & Sew',
            facility_list_item=self.list_item,
        )
        with connection.cursor() as cursor:
            cursor.execute(
                build_update_sql(get_field_spec('isic_4_mapped')),
                {
                    'workers': 1,
                    'worker_id': 0,
                    'last_id': self.facility.id,
                    'batch_size': 100,
                },
            )
            self.assertEqual(cursor.fetchall(), [])


@override_switch('enable_isic_taxonomy', active=True)
class IsicMappedSearchTest(FacilityAPITestCaseBase):
    '''Mapped values are opt-in in search and in the counts.'''

    def setUp(self):
        super().setUp()
        caches['view_cache'].clear()
        FacilityIndex.objects.filter(id=self.facility.id).update(
            isic_mapped_section=['C'],
            isic_mapped_division=['14'],
            isic_mapped_group=['141'],
            isic_mapped_class=['1410'],
        )

    def _search_ids(self, params):
        response = self.client.get('/api/facilities/', params)
        self.assertEqual(response.status_code, 200)
        return [
            feature['id'] for feature in response.json()['features']
        ]

    def test_mapped_values_are_excluded_by_default(self):
        self.assertEqual(self._search_ids({'isic_4': 'class:1410'}), [])

    def test_opt_in_includes_mapped_values(self):
        self.assertEqual(
            self._search_ids({
                'isic_4': 'section:C',
                'isic_4_include_mapped': 'true',
            }),
            [self.facility.id],
        )

    def test_opt_in_combines_with_other_filters(self):
        self.assertEqual(
            self._search_ids({
                'isic_4': 'class:1410',
                'isic_4_include_mapped': 'true',
                'countries': 'US',
            }),
            [self.facility.id],
        )
        self.assertEqual(
            self._search_ids({
                'isic_4': 'class:1410',
                'isic_4_include_mapped': 'true',
                'countries': 'CN',
            }),
            [],
        )

    def test_opt_in_false_behaves_like_default(self):
        self.assertEqual(
            self._search_ids({
                'isic_4': 'class:1410',
                'isic_4_include_mapped': 'false',
            }),
            [],
        )

    def test_counts_exclude_mapped_values_by_default(self):
        response = self.client.get(
            reverse('taxonomy_counts'), {'kind': 'isic4'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('class:1410', response.data)

    def test_counts_with_include_mapped(self):
        response = self.client.get(
            reverse('taxonomy_counts'),
            {'kind': 'isic4', 'include_mapped': 'true'},
        )
        self.assertEqual(response.data['section:C'], 1)
        self.assertEqual(response.data['class:1410'], 1)

    def test_counts_count_a_location_once_when_submitted_and_mapped(self):
        FacilityIndex.objects.filter(id=self.facility.id).update(
            isic_section=['C'],
        )
        response = self.client.get(
            reverse('taxonomy_counts'),
            {'kind': 'isic4', 'include_mapped': 'true'},
        )
        self.assertEqual(response.data['section:C'], 1)

    def test_mapped_extra_count(self):
        response = self.client.get(
            reverse('taxonomy_counts'),
            {'kind': 'isic4_mapped_extra', 'isic_4': 'division:14'},
        )
        self.assertEqual(response.data, {'count': 1})

        FacilityIndex.objects.filter(id=self.facility.id).update(
            isic_division=['14'],
        )
        caches['view_cache'].clear()
        response = self.client.get(
            reverse('taxonomy_counts'),
            {'kind': 'isic4_mapped_extra', 'isic_4': 'division:14'},
        )
        self.assertEqual(response.data, {'count': 0})

    def test_mapped_extra_count_rejects_malformed_codes(self):
        response = self.client.get(
            reverse('taxonomy_counts'),
            {'kind': 'isic4_mapped_extra', 'isic_4': 'class:abc'},
        )
        self.assertEqual(response.status_code, 400)

    def test_mapped_extra_count_rejects_oversized_selection(self):
        response = self.client.get(
            reverse('taxonomy_counts'),
            {
                'kind': 'isic4_mapped_extra',
                'isic_4': [f'class:{n:04d}' for n in range(51)],
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_mapped_extra_count_without_selection_is_zero(self):
        response = self.client.get(
            reverse('taxonomy_counts'), {'kind': 'isic4_mapped_extra'}
        )
        self.assertEqual(response.data, {'count': 0})


# The loader's backfill spawns worker processes on their own connections;
# stub it so tests never write outside the test transaction.
@patch('api.management.commands.load_isic_crosswalk.call_command')
class LoadIsicCrosswalkCommandTest(TestCase):
    def test_dry_run_changes_nothing(self, backfill):
        IsicCrosswalkEntry.objects.all().delete()
        out = StringIO()
        call_command('load_isic_crosswalk', dry_run=True, stdout=out)
        self.assertEqual(IsicCrosswalkEntry.objects.count(), 0)
        self.assertIn('Nothing was changed', out.getvalue())
        backfill.assert_not_called()

    def test_reload_replaces_rows(self, backfill):
        IsicCrosswalkEntry.objects.all().delete()
        call_command('load_isic_crosswalk', stdout=StringIO())
        self.assertEqual(
            IsicCrosswalkEntry.objects.count(),
            len(load_crosswalk_rows()),
        )

    def test_reload_refreshes_existing_locations(self, backfill):
        # The triggers fire only when a location's types change, so a
        # crosswalk edit reaches existing locations through the backfill.
        call_command('load_isic_crosswalk', stdout=StringIO())

        backfill.assert_called_once_with(
            'backfill_facility_index', fields='isic_4_mapped',
        )

    def test_invalid_file_is_rejected_without_changes(self, backfill):
        before = IsicCrosswalkEntry.objects.count()
        with self.assertRaises(CommandError):
            call_command(
                'load_isic_crosswalk',
                file='/nonexistent/crosswalk.csv',
                stdout=StringIO(),
            )
        self.assertEqual(IsicCrosswalkEntry.objects.count(), before)
