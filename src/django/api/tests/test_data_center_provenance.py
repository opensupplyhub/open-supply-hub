from django.test import SimpleTestCase

from api.helpers.data_center import (
    PROVENANCE_FIELDS,
    extract_provenance,
)
from api.models.facility.facility_list_item import FacilityListItem
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase


RAW_ROW = {
    'name': 'Acme DC1',
    'source_name': 'US EPA FRS',
    'source_link': 'https://example.com/dc?id=1,2',
    'information_source_type': 'air quality permit',
    'date_of_source': 'June 2024',
    'notes': 'inferred operator from website',
    'data_collection_methodology': 'downloaded from source',
    'ai_usage_notes': 'Claude used to extract the fields',
}


class ExtractProvenanceTest(SimpleTestCase):
    def test_extracts_all_provenance_fields(self):
        result = extract_provenance(RAW_ROW)
        for field in PROVENANCE_FIELDS:
            self.assertEqual(result[field], RAW_ROW[field])

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
        self.assertEqual(item.date_of_source, 'June 2024')
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
