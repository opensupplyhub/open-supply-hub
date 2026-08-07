import json
from unittest.mock import Mock, patch

from django.test import SimpleTestCase
from django.urls import reverse

from api.helpers.data_center import (
    PROVENANCE_FIELDS,
    extract_provenance,
)
from api.models.extended_field import ExtendedField
from api.models.facility.facility_list_item import FacilityListItem
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase
from api.tests.test_data import geocoding_data


RAW_ROW = {
    'name': 'Acme DC1',
    'source_name': 'US EPA FRS',
    'source_link': 'https://example.com/dc?id=1,2',
    'information_source_type': 'air quality permit',
    'date_of_source': '2024-06-15',
    'notes': 'inferred operator from website',
    'data_collection_methodology': 'downloaded from source',
    'ai_usage_notes': 'Claude used to extract the fields',
}


class ExtractProvenanceTest(SimpleTestCase):
    def test_extracts_all_provenance_fields(self):
        result = extract_provenance(RAW_ROW)
        for field in PROVENANCE_FIELDS:
            self.assertEqual(result[field], RAW_ROW[field])

    def test_partial_dates_of_source_are_kept(self):
        # ISO reduced precision: whatever the source provides.
        for partial in ['2024', '2024-06', '2024-06-15']:
            with self.subTest(partial=partial):
                result = extract_provenance({'date_of_source': partial})
                self.assertEqual(result, {'date_of_source': partial})

    def test_invalid_date_of_source_is_omitted(self):
        for invalid in ['June 2024', '2024-13', '2024-02-30', '15/06/2024']:
            with self.subTest(invalid=invalid):
                result = extract_provenance(
                    {'source_name': 'X', 'date_of_source': invalid}
                )
                self.assertEqual(result, {'source_name': 'X'})

    def test_excludes_non_provenance_fields(self):
        self.assertNotIn('name', extract_provenance(RAW_ROW))

    def test_preserves_source_link_unmodified(self):
        # A URL containing a comma must survive unmangled (read from raw row).
        result = extract_provenance(RAW_ROW)
        self.assertEqual(
            result['source_link'], 'https://example.com/dc?id=1,2'
        )

    def test_omits_missing_and_empty_values(self):
        result = extract_provenance(
            {'source_name': 'X', 'source_link': '', 'notes': None}
        )
        self.assertEqual(result, {'source_name': 'X'})

    def test_empty_input_returns_empty_dict(self):
        self.assertEqual(extract_provenance({}), {})
        self.assertEqual(extract_provenance(None), {})


class FacilityListItemProvenanceTest(FacilityAPITestCaseBase):
    def test_provenance_persists_on_facility_list_item(self):
        item = FacilityListItem.objects.create(
            name='Acme DC1',
            address='123 Main St',
            country_code='US',
            sector=['Apparel'],
            row_index=2,
            source=self.source,
            **extract_provenance(RAW_ROW),
        )
        item.refresh_from_db()

        self.assertEqual(item.source_name, 'US EPA FRS')
        self.assertEqual(item.source_link, 'https://example.com/dc?id=1,2')
        self.assertEqual(item.information_source_type, 'air quality permit')
        self.assertEqual(item.date_of_source, '2024-06-15')
        self.assertEqual(item.notes, 'inferred operator from website')
        self.assertEqual(
            item.data_collection_methodology, 'downloaded from source'
        )
        self.assertEqual(
            item.ai_usage_notes, 'Claude used to extract the fields'
        )

    def test_no_provenance_leaves_columns_null(self):
        item = FacilityListItem.objects.create(
            name='Factory',
            address='123 Main St',
            country_code='US',
            sector=['Apparel'],
            row_index=3,
            source=self.source,
            **extract_provenance({'name': 'Factory'}),
        )
        item.refresh_from_db()

        self.assertIsNone(item.source_name)
        self.assertIsNone(item.source_link)
        self.assertIsNone(item.ai_usage_notes)


class LegacyApiDataCenterContributionTest(FacilityAPITestCaseBase):
    """
    OSDEV-3068: the legacy API (POST /api/facilities/) accepts a data-center
    contribution carrying attribute fields and per-row provenance. Uses
    create=false so no facility/match is created, and patches the Kafka /
    match handling so the test is isolated from the dedupe hub.
    """

    fixtures = ["sectors"]

    @patch(
        'api.facility_actions.processing_facility_api'
        '.handle_external_match_process_result'
    )
    @patch(
        'api.facility_actions.processing_facility_api'
        '.produce_message_match_process'
    )
    @patch('api.geocoding.requests.get')
    def test_data_center_with_provenance_is_ingested(
        self, mock_get, mock_produce, mock_match_result
    ):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data

        async def noop(*args, **kwargs):
            return None

        mock_produce.side_effect = noop
        mock_match_result.return_value = {}

        self.join_group_and_login()
        response = self.client.post(
            reverse('facility-list') + '?create=false',
            json.dumps({
                'country': 'US',
                'name': 'Blue Horizon Data Center',
                'address': '990 Spring Garden St., Philadelphia PA 19123',
                'facility_type': 'Data Center',
                'name_operator': 'Blue Horizon Ops',
                'capacity': '20',
                'capacity_units': 'MW',
                'source_name': 'US EPA FRS',
                'source_link': 'https://example.com/dc?id=1',
                'information_source_type': 'air quality permit',
                'date_of_source': '2024-06-15',
                'ai_usage_notes': 'AI-extracted; human reviewed',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)

        item = FacilityListItem.objects.exclude(
            id=self.list_item.id
        ).get(name='Blue Horizon Data Center')

        # Per-row provenance persisted (OSDEV-3070 / 3071 / 3075).
        self.assertEqual(item.source_name, 'US EPA FRS')
        self.assertEqual(item.source_link, 'https://example.com/dc?id=1')
        self.assertEqual(item.information_source_type, 'air quality permit')
        self.assertEqual(item.date_of_source, '2024-06-15')
        self.assertEqual(item.ai_usage_notes, 'AI-extracted; human reviewed')

        # Data-center attribute ExtendedFields created (OSDEV-3066).
        ef_names = set(
            ExtendedField.objects.filter(
                facility_list_item=item
            ).values_list('field_name', flat=True)
        )
        self.assertIn(ExtendedField.NAME_OPERATOR, ef_names)
        self.assertIn(ExtendedField.CAPACITY, ef_names)
        self.assertIn(ExtendedField.CAPACITY_UNITS, ef_names)
        self.assertIn(ExtendedField.FACILITY_TYPE, ef_names)

        # facility_type resolves to Data Center (OSDEV-2587).
        facility_type_ef = ExtendedField.objects.get(
            facility_list_item=item,
            field_name=ExtendedField.FACILITY_TYPE,
        )
        matched_types = [
            mv[2] for mv in facility_type_ef.value.get('matched_values', [])
        ]
        self.assertIn('Data Center', matched_types)
