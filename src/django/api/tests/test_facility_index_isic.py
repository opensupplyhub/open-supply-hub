from django.contrib.gis.geos import Point
from django.db import connection
from django.test import override_settings

from api.constants import FacilityClaimStatuses
from api.models.extended_field import ExtendedField
from api.models.facility.facility_claim import FacilityClaim
from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_index import FacilityIndex
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase


class FacilityIndexIsicTest(FacilityAPITestCaseBase):
    def setUp(self):
        super().setUp()
        self.isic_field = ExtendedField.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            facility_list_item=self.list_item,
            field_name=ExtendedField.ISIC_4,
            value={
                'raw_value': [
                    {
                        'section': 'J - Information and communication',
                        'division': (
                            '62 - Computer programming, consultancy and '
                            'related activities'
                        ),
                        'group': '620 - Computer programming activities',
                        'class': '6201 - Computer programming activities',
                    },
                    {
                        'section': 'C - Manufacturing',
                        'class': (
                            '1410 - Manufacture of wearing apparel, '
                            'except fur apparel'
                        ),
                    },
                    {
                        'class': (
                            '0111 - Growing of cereals (except rice), '
                            'leguminous crops and oil seeds'
                        ),
                    },
                ],
            },
        )

    def _replace_entries(self, entries):
        self.isic_field.value = {'raw_value': entries}
        self.isic_field.save(update_fields=['value'])

    def _fetch_index_array(self, function_name, column_name):
        with connection.cursor() as cursor:
            cursor.execute(
                f'SELECT array_agg({column_name}) FROM {function_name}(%s)',
                [self.facility.id],
            )
            row = cursor.fetchone()
        return sorted(row[0] or [])

    def test_index_isic_sql_functions_extract_normalized_codes(self):
        self.assertEqual(
            self._fetch_index_array('index_isic_section', 'isic_section'),
            ['A', 'C', 'J'],
        )
        self.assertEqual(
            self._fetch_index_array('index_isic_division', 'isic_division'),
            ['01', '14', '62'],
        )
        self.assertEqual(
            self._fetch_index_array('index_isic_group', 'isic_group'),
            ['011', '141', '620'],
        )
        self.assertEqual(
            self._fetch_index_array('index_isic_class', 'isic_class'),
            ['0111', '1410', '6201'],
        )

    def test_index_facilities_by_populates_isic_columns(self):
        with connection.cursor() as cursor:
            cursor.execute(
                'CALL index_facilities_by(%s)',
                [[self.facility.id]],
            )

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertEqual(
            sorted(facility_index.isic_section),
            ['A', 'C', 'J'],
        )
        self.assertEqual(
            sorted(facility_index.isic_division),
            ['01', '14', '62'],
        )
        self.assertEqual(
            sorted(facility_index.isic_group),
            ['011', '141', '620'],
        )
        self.assertEqual(
            sorted(facility_index.isic_class),
            ['0111', '1410', '6201'],
        )

    def test_derives_ancestors_from_group_only(self):
        self._replace_entries([
            {'group': '011 - Growing of non-perennial crops'},
        ])

        self.assertEqual(
            self._fetch_index_array('index_isic_section', 'isic_section'),
            ['A'],
        )
        self.assertEqual(
            self._fetch_index_array('index_isic_division', 'isic_division'),
            ['01'],
        )
        self.assertEqual(
            self._fetch_index_array('index_isic_group', 'isic_group'),
            ['011'],
        )

    def test_derives_section_from_division_only(self):
        self._replace_entries([
            {'division': '62 - Computer programming activities'},
        ])

        self.assertEqual(
            self._fetch_index_array('index_isic_section', 'isic_section'),
            ['J'],
        )
        self.assertEqual(
            self._fetch_index_array('index_isic_division', 'isic_division'),
            ['62'],
        )
        self.assertEqual(
            self._fetch_index_array('index_isic_group', 'isic_group'),
            [],
        )

    def test_malformed_partial_codes_do_not_add_null_ancestors(self):
        self._replace_entries([
            {'group': '62 - Wrong length for an ISIC group'},
        ])

        self.assertEqual(
            self._fetch_index_array('index_isic_section', 'isic_section'),
            [],
        )
        self.assertEqual(
            self._fetch_index_array('index_isic_division', 'isic_division'),
            [],
        )
        self.assertEqual(
            self._fetch_index_array('index_isic_group', 'isic_group'),
            [],
        )

    def test_rev4_division_to_section_mapping_boundaries(self):
        expected_sections = {
            '01': 'A', '03': 'A',
            '05': 'B', '09': 'B',
            '10': 'C', '33': 'C',
            '35': 'D',
            '36': 'E', '39': 'E',
            '41': 'F', '43': 'F',
            '45': 'G', '47': 'G',
            '49': 'H', '53': 'H',
            '55': 'I', '56': 'I',
            '58': 'J', '63': 'J',
            '64': 'K', '66': 'K',
            '68': 'L',
            '69': 'M', '75': 'M',
            '77': 'N', '82': 'N',
            '84': 'O',
            '85': 'P',
            '86': 'Q', '88': 'Q',
            '90': 'R', '93': 'R',
            '94': 'S', '96': 'S',
            '97': 'T', '98': 'T',
            '99': 'U',
        }
        unmapped_codes = [
            '00', '04', '34', '40', '44', '48', '54', '57', '67',
            '76', '83', '89', '100', 'invalid', '',
        ]

        with connection.cursor() as cursor:
            for division_code, expected_section in expected_sections.items():
                with self.subTest(division_code=division_code):
                    cursor.execute(
                        'SELECT isic_rev4_section_for_division(%s)',
                        [division_code],
                    )
                    self.assertEqual(cursor.fetchone()[0], expected_section)

            for division_code in unmapped_codes:
                with self.subTest(division_code=division_code):
                    cursor.execute(
                        'SELECT isic_rev4_section_for_division(%s)',
                        [division_code],
                    )
                    self.assertIsNone(cursor.fetchone()[0])

    def test_extended_field_trigger_populates_isic_columns(self):
        # setUp inserts the isic_4 ExtendedField after the facility is
        # already indexed, which is the order list processing uses. The
        # api_extendedfield trigger alone must bring the columns up to date.
        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertEqual(sorted(facility_index.isic_section), ['A', 'C', 'J'])
        self.assertEqual(
            sorted(facility_index.isic_class),
            ['0111', '1410', '6201'],
        )

    def test_extended_field_trigger_refreshes_isic_columns_on_update(self):
        self._replace_entries([
            {'class': '1311 - Preparation and spinning of textile fibres'},
        ])

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertEqual(facility_index.isic_section, ['C'])
        self.assertEqual(facility_index.isic_division, ['13'])
        self.assertEqual(facility_index.isic_group, ['131'])
        self.assertEqual(facility_index.isic_class, ['1311'])

    def test_extended_field_trigger_clears_isic_columns_on_delete(self):
        self.isic_field.delete()

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertEqual(facility_index.isic_section, [])
        self.assertEqual(facility_index.isic_class, [])

    def test_index_facilities_by_still_excludes_candidates(self):
        # 0254 re-creates the procedures 0250 changed; candidates must
        # still never get an index row.
        candidate_item = FacilityListItem.objects.create(
            name='Candidate',
            address='Address',
            country_code='US',
            sector=['Apparel'],
            row_index=2,
            geocoded_point=Point(1, 1),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )
        with override_settings(
            EARTH_GENOME_CONTRIBUTOR_ID=self.contributor.id,
        ):
            candidate = Facility.objects.create(
                name='Candidate',
                address='Address',
                country_code='US',
                location=Point(1, 1),
                created_from=candidate_item,
                is_candidate=True,
            )
        with connection.cursor() as cursor:
            cursor.execute(
                'CALL index_facilities_by(%s)',
                [[candidate.id, self.facility.id]],
            )

        self.assertFalse(
            FacilityIndex.objects.filter(id=candidate.id).exists()
        )
        self.assertTrue(
            FacilityIndex.objects.filter(id=self.facility.id).exists()
        )

    def test_isic_columns_have_a_valid_gin_index(self):
        # 0255 builds it CONCURRENTLY; an interrupted build would leave it
        # invalid and unused by the planner.
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT idx.indisvalid, am.amname "
                "FROM pg_index idx "
                "JOIN pg_class cls ON cls.oid = idx.indexrelid "
                "JOIN pg_am am ON am.oid = cls.relam "
                "WHERE cls.relname = 'api_facilityindex_isic_gin'"
            )
            self.assertEqual(cursor.fetchall(), [(True, 'gin')])

    def _index(self):
        return FacilityIndex.objects.get(id=self.facility.id)

    def test_deactivating_the_source_hides_its_isic_values(self):
        # perform_source_indexing must recompute the ISIC columns, as it
        # does facility_type / processing_type (OSDEV-3428).
        self.assertEqual(sorted(self._index().isic_section), ['A', 'C', 'J'])

        self.source.is_active = False
        self.source.save()
        self.assertEqual(self._index().isic_section, [])

        self.source.is_active = True
        self.source.save()
        self.assertEqual(sorted(self._index().isic_section), ['A', 'C', 'J'])

    def test_deactivating_the_match_hides_its_isic_values(self):
        self.match.is_active = False
        self.match.save()

        self.assertEqual(self._index().isic_class, [])

    def test_claim_isic_values_show_only_while_the_claim_is_approved(self):
        # perform_facility_claim_indexing must recompute the ISIC columns.
        self.isic_field.delete()
        claim = FacilityClaim.objects.create(
            facility=self.facility,
            contributor=self.contributor,
            contact_person='Person',
            job_title='Title',
            status=FacilityClaimStatuses.PENDING,
        )
        ExtendedField.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            facility_claim=claim,
            field_name=ExtendedField.ISIC_4,
            value={'raw_value': [{'class': '1410 - Apparel'}]},
        )
        self.assertEqual(self._index().isic_class, [])

        claim.status = FacilityClaimStatuses.APPROVED
        claim.save()
        self.assertEqual(self._index().isic_class, ['1410'])

        claim.status = FacilityClaimStatuses.REVOKED
        claim.save()
        self.assertEqual(self._index().isic_class, [])
