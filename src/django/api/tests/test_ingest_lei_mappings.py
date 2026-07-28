import csv
import os
import tempfile
from datetime import date
from io import StringIO

from django.contrib.gis.geos import Point
from django.core.management import call_command
from django.test import TestCase

from api.models import Contributor, User
from api.models.extended_field import ExtendedField
from api.models.facility.facility import Facility
from api.models.facility.facility_alias import FacilityAlias
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_match import FacilityMatch
from api.models.lei_mapping import LeiMapping
from api.models.source import Source

VALID_LEI = 'ABCDEFGHIJKLMNOPQR12'
OTHER_LEI = 'ZYXWVUTSRQPONMLKJI34'
DEFAULT_COLUMNS = ('os_id', 'lei', 'match_type')


class IngestLeiMappingsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='gleif@example.com')
        self.gleif = Contributor.objects.create(
            admin=self.user,
            name='GLEIF',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.facility_user = User.objects.create(email='owner@example.com')
        self.facility_contributor = Contributor.objects.create(
            admin=self.facility_user,
            name='facility owner',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.facility = self._make_facility('US2026001TESTF1')

    def _make_facility(self, os_id, name='Facility', address='Address'):
        source = Source.objects.create(
            contributor=self.facility_contributor,
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            create=True,
        )
        list_item = FacilityListItem.objects.create(
            name=name,
            address=address,
            country_code='US',
            sector=['Apparel'],
            row_index=0,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.MATCHED,
            source=source,
        )
        facility = Facility.objects.create(
            id=os_id,
            name=name,
            address=address,
            country_code='US',
            location=Point(0, 0),
            created_from=list_item,
        )
        list_item.facility = facility
        list_item.save()
        return facility

    def _write_csv(self, rows, columns=DEFAULT_COLUMNS):
        handle = tempfile.NamedTemporaryFile(
            mode='w', suffix='.csv', delete=False, newline=''
        )
        with handle as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=list(columns))
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        self.addCleanup(os.remove, handle.name)
        return handle.name

    def _call(self, path, *extra):
        call_command(
            'ingest_lei_mappings',
            '--file', path,
            '--contributor-id', str(self.gleif.id),
            '--file-date', '2026-07-01',
            *extra,
            stdout=StringIO(),
            stderr=StringIO(),
        )

    def _row(self, **overrides):
        row = {
            'os_id': self.facility.id,
            'lei': VALID_LEI,
            'match_type': LeiMapping.FACILITY_NAME,
        }
        row.update(overrides)
        return row

    def _gleif_extended_fields(self):
        return ExtendedField.objects.filter(
            contributor=self.gleif,
            field_name=ExtendedField.LEI_ID,
        )

    def test_first_run_creates_ledger_and_contribution_chain(self):
        self._call(self._write_csv([self._row()]))

        mapping = LeiMapping.objects.get(os_id=self.facility.id)
        self.assertEqual(mapping.lei, VALID_LEI)
        self.assertEqual(mapping.match_type, LeiMapping.FACILITY_NAME)
        self.assertEqual(mapping.status, LeiMapping.ACTIVE)
        self.assertEqual(mapping.mapping_file_date, date(2026, 7, 1))

        source = Source.objects.get(contributor=self.gleif)
        self.assertEqual(source.source_type, Source.LIST)
        self.assertTrue(source.is_public)
        self.assertTrue(source.is_active)
        self.assertFalse(source.create)
        self.assertIn('GLEIF LEI Mapping', source.facility_list.name)

        item = FacilityListItem.objects.get(source=source)
        self.assertEqual(item.status, FacilityListItem.CONFIRMED_MATCH)
        self.assertEqual(item.facility, self.facility)
        self.assertEqual(item.row_index, 0)
        self.assertEqual(item.raw_json['lei'], VALID_LEI)

        match = FacilityMatch.objects.get(facility_list_item=item)
        self.assertEqual(match.facility, self.facility)
        self.assertEqual(match.status, FacilityMatch.CONFIRMED)
        self.assertTrue(match.is_active)
        self.assertEqual(
            match.results, {'match_type': 'lei_mapping_ingest'}
        )

        extended_field = self._gleif_extended_fields().get()
        self.assertEqual(extended_field.facility, self.facility)
        self.assertEqual(extended_field.facility_list_item, item)
        self.assertEqual(
            extended_field.value,
            {
                'raw_value': VALID_LEI,
                'match_type': LeiMapping.FACILITY_NAME,
            },
        )

    def test_rerun_with_same_file_is_a_no_op(self):
        path = self._write_csv([self._row()])
        self._call(path)
        self._call(path)

        self.assertEqual(LeiMapping.objects.count(), 1)
        self.assertEqual(self._gleif_extended_fields().count(), 1)
        self.assertEqual(
            Source.objects.filter(contributor=self.gleif).count(), 1
        )
        self.assertEqual(
            FacilityListItem.objects.filter(
                source__contributor=self.gleif
            ).count(),
            1,
        )

    def test_changed_lei_updates_extended_field_in_place(self):
        self._call(self._write_csv([self._row()]))
        original_field = self._gleif_extended_fields().get()

        self._call(self._write_csv([self._row(lei=OTHER_LEI)]))

        mapping = LeiMapping.objects.get(os_id=self.facility.id)
        self.assertEqual(mapping.lei, OTHER_LEI)
        self.assertEqual(mapping.status, LeiMapping.ACTIVE)

        extended_field = self._gleif_extended_fields().get()
        self.assertEqual(extended_field.id, original_field.id)
        self.assertEqual(
            extended_field.facility_list_item,
            original_field.facility_list_item,
        )
        self.assertEqual(
            extended_field.value,
            {
                'raw_value': OTHER_LEI,
                'match_type': LeiMapping.FACILITY_NAME,
            },
        )
        self.assertEqual(
            Source.objects.filter(contributor=self.gleif).count(), 1
        )

    def test_metadata_only_change_refreshes_ledger_not_extended_field(self):
        self._call(self._write_csv([self._row()]))
        original_field = self._gleif_extended_fields().get()

        columns = DEFAULT_COLUMNS + ('mapping_file_date',)
        self._call(self._write_csv(
            [self._row(mapping_file_date='2026-08-01')],
            columns=columns,
        ))

        # The ledger records the newest file that confirmed the mapping.
        mapping = LeiMapping.objects.get(os_id=self.facility.id)
        self.assertEqual(mapping.mapping_file_date, date(2026, 8, 1))
        self.assertEqual(mapping.lei, VALID_LEI)
        self.assertEqual(mapping.status, LeiMapping.ACTIVE)

        # The extended field is untouched (no reindex-trigger writes).
        extended_field = self._gleif_extended_fields().get()
        self.assertEqual(extended_field.id, original_field.id)
        self.assertEqual(
            extended_field.updated_at, original_field.updated_at
        )
        self.assertEqual(
            FacilityListItem.objects.filter(
                source__contributor=self.gleif
            ).count(),
            1,
        )

    def test_os_id_absent_from_second_file_is_removed(self):
        self._call(self._write_csv([self._row()]))
        self._call(self._write_csv([]))

        mapping = LeiMapping.objects.get(os_id=self.facility.id)
        self.assertEqual(mapping.status, LeiMapping.REMOVED)
        self.assertEqual(self._gleif_extended_fields().count(), 0)
        # The historical contribution records are left in place.
        self.assertEqual(
            FacilityListItem.objects.filter(
                source__contributor=self.gleif
            ).count(),
            1,
        )
        self.assertEqual(
            FacilityMatch.objects.filter(
                facility_list_item__source__contributor=self.gleif
            ).count(),
            1,
        )

    def test_merged_os_id_resolves_via_facility_alias(self):
        canonical = self._make_facility('US2026002CANON1')
        FacilityAlias.objects.create(
            os_id='US2026003MERGED',
            facility=canonical,
            reason=FacilityAlias.MERGE,
        )

        self._call(
            self._write_csv([self._row(os_id='US2026003MERGED')])
        )

        mapping = LeiMapping.objects.get()
        self.assertEqual(mapping.os_id, canonical.id)
        extended_field = self._gleif_extended_fields().get()
        self.assertEqual(extended_field.facility, canonical)

    def test_unknown_os_id_is_skipped(self):
        self._call(self._write_csv([self._row(os_id='XX2026000NOPE01')]))

        self.assertEqual(LeiMapping.objects.count(), 0)
        self.assertEqual(self._gleif_extended_fields().count(), 0)
        self.assertEqual(
            Source.objects.filter(contributor=self.gleif).count(), 0
        )

    def test_invalid_lei_is_counted_and_nothing_written(self):
        self._call(self._write_csv([self._row(lei='not-a-valid-lei')]))

        self.assertEqual(LeiMapping.objects.count(), 0)
        self.assertEqual(self._gleif_extended_fields().count(), 0)
        self.assertEqual(
            Source.objects.filter(contributor=self.gleif).count(), 0
        )

    def test_dry_run_writes_nothing(self):
        self._call(self._write_csv([self._row()]), '--dry-run')

        self.assertEqual(LeiMapping.objects.count(), 0)
        self.assertEqual(self._gleif_extended_fields().count(), 0)
        self.assertEqual(
            Source.objects.filter(contributor=self.gleif).count(), 0
        )
        self.assertEqual(
            FacilityListItem.objects.filter(
                source__contributor=self.gleif
            ).count(),
            0,
        )

    def test_denylisted_ledger_row_is_not_recreated(self):
        LeiMapping.objects.create(
            os_id=self.facility.id,
            lei=VALID_LEI,
            match_type=LeiMapping.FACILITY_NAME,
            mapping_file_date=date(2026, 6, 1),
            status=LeiMapping.DENYLISTED,
        )

        self._call(self._write_csv([self._row()]))

        mapping = LeiMapping.objects.get(os_id=self.facility.id)
        self.assertEqual(mapping.status, LeiMapping.DENYLISTED)
        self.assertEqual(mapping.mapping_file_date, date(2026, 6, 1))
        self.assertEqual(self._gleif_extended_fields().count(), 0)
        self.assertEqual(
            Source.objects.filter(contributor=self.gleif).count(), 0
        )
