import json
from unittest.mock import Mock, patch

from api.models import ExtendedField
from api.models.facility.facility_index import FacilityIndex
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase
from api.tests.test_data import geocoding_data

from django.urls import reverse


class FacilityAndProcessingTypeAPITest(FacilityAPITestCaseBase):
    fixtures = ["sectors"]

    def setUp(self):
        super(FacilityAndProcessingTypeAPITest, self).setUp()
        self.url = reverse("facility-list")

    def _create_processing_type_extended_field(
        self, raw_value, matched_values
    ):
        # The ExtendedField insert trigger reindexes FacilityIndex, so the
        # facility must be linked directly for index_processing_type() to
        # pick the value up.
        return ExtendedField.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            facility_list_item=self.list_item,
            field_name=ExtendedField.PROCESSING_TYPE,
            value={
                "raw_values": raw_value,
                "matched_values": matched_values,
            },
        )

    def _create_facility_type_extended_field(
        self, raw_value, matched_values
    ):
        return ExtendedField.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            facility_list_item=self.list_item,
            field_name=ExtendedField.FACILITY_TYPE,
            value={
                "raw_values": raw_value,
                "matched_values": matched_values,
            },
        )

    def test_unmatched_raw_processing_type_indexed(self):
        self._create_processing_type_extended_field(
            ["cement mixing"],
            [[None, None, None, None]],
        )

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertIn("cement mixing", facility_index.processing_type)

    def test_unmatched_raw_facility_type_indexed(self):
        self._create_facility_type_extended_field(
            ["cement mixing"],
            [[None, None, None, None]],
        )

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertIn("cement mixing", facility_index.facility_type)

    def test_unmatched_raw_processing_type_not_indexed_from_inactive_source(
        self,
    ):
        self.source.is_active = False
        self.source.save()

        self._create_processing_type_extended_field(
            ["cement mixing"],
            [[None, None, None, None]],
        )

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertNotIn("cement mixing", facility_index.processing_type)

    def test_skipped_matching_raw_facility_type_indexed(self):
        # Non-apparel SKIPPED_MATCHING stores the raw value in slot 3 only;
        # facility_type slot 2 is null, so the raw value must be indexed from
        # raw_values.
        self._create_facility_type_extended_field(
            ["custom facility label"],
            [
                [
                    "PROCESSING_TYPE",
                    "SKIPPED_MATCHING",
                    None,
                    "custom facility label",
                ]
            ],
        )

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertIn("custom facility label", facility_index.facility_type)

    def test_processing_type_indexed_when_tagged_as_facility_type(self):
        # "Final Product Assembly" is both a facility type and a processing
        # type, so the taxonomy matcher tags it FACILITY_TYPE even when it is
        # contributed as a processing type. It must still be indexed in (and
        # searchable via) processing_type. Regression test for OSDEV-1034.
        self._create_processing_type_extended_field(
            ["Final Product Assembly"],
            [
                [
                    "FACILITY_TYPE",
                    "EXACT",
                    "Final Product Assembly",
                    "Final Product Assembly",
                ]
            ],
        )

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertIn(
            "Final Product Assembly", facility_index.processing_type
        )

        response = self.client.get(
            self.url + "?processing_type=Final%20Product%20Assembly"
        )
        data = json.loads(response.content)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["features"][0]["id"], self.facility.id)

    def test_processing_type_indexed_when_tagged_as_processing_type(self):
        # A value the matcher tags PROCESSING_TYPE (e.g. "Cutting") must keep
        # being indexed in processing_type after the OSDEV-1034 change.
        self._create_processing_type_extended_field(
            ["Cutting"],
            [
                [
                    "PROCESSING_TYPE",
                    "EXACT",
                    "Final Product Assembly",
                    "Cutting",
                ]
            ],
        )

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertIn("Cutting", facility_index.processing_type)

        response = self.client.get(self.url + "?processing_type=Cutting")
        data = json.loads(response.content)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["features"][0]["id"], self.facility.id)

    def test_search_unmatched_raw_processing_type_by_free_text(self):
        self._create_processing_type_extended_field(
            ["cement mixing"],
            [[None, None, None, None]],
        )

        response = self.client.get(
            self.url + "?processing_type=cement%20mixing"
        )
        data = json.loads(response.content)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["features"][0]["id"], self.facility.id)

    def test_search_unmatched_raw_processing_type_by_substring(self):
        self._create_processing_type_extended_field(
            ["cement mixing"],
            [[None, None, None, None]],
        )

        response = self.client.get(self.url + "?processing_type=cement")
        data = json.loads(response.content)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["features"][0]["id"], self.facility.id)

    def test_search_processing_type_fuzzy_typo_still_uses_taxonomy(self):
        self._create_processing_type_extended_field(
            ["Assembly"],
            [
                [
                    "PROCESSING_TYPE",
                    "EXACT",
                    "Final Product Assembly",
                    "Assembly",
                ]
            ],
        )

        response = self.client.get(
            self.url + "?processing_type=asembley"
        )
        data = json.loads(response.content)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["features"][0]["id"], self.facility.id)

    def test_search_mixed_taxonomy_and_free_text(self):
        self._create_processing_type_extended_field(
            ["Cutting"],
            [
                [
                    "PROCESSING_TYPE",
                    "EXACT",
                    "Final Product Assembly",
                    "Cutting",
                ],
            ],
        )

        response = self.client.get(
            self.url
            + "?processing_type=Cutting&processing_type=cement%20mixing"
        )
        data = json.loads(response.content)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["features"][0]["id"], self.facility.id)

    def test_search_facility_type_and_processing_type_params_are_anded(self):
        self._create_facility_type_extended_field(
            ["Office / HQ"],
            [
                [
                    "FACILITY_TYPE",
                    "EXACT",
                    "Office / HQ",
                    "Office / HQ",
                ]
            ],
        )
        self._create_processing_type_extended_field(
            ["cement mixing"],
            [[None, None, None, None]],
        )

        response = self.client.get(
            self.url
            + "?facility_type=Office%20/%20HQ&processing_type=cement%20mixing"
        )
        data = json.loads(response.content)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["features"][0]["id"], self.facility.id)

        response = self.client.get(
            self.url
            + "?facility_type=Final%20Product%20Assembly"
            + "&processing_type=cement%20mixing"
        )
        data = json.loads(response.content)
        self.assertEqual(data["count"], 0)

    def test_search_free_text_below_min_length_returns_no_results(self):
        self._create_processing_type_extended_field(
            ["cement mixing"],
            [[None, None, None, None]],
        )

        response = self.client.get(self.url + "?processing_type=ce")
        data = json.loads(response.content)
        self.assertEqual(data["count"], 0)

    def test_invalid_processing_type_does_not_broaden_facility_type_search(
        self,
    ):
        self._create_facility_type_extended_field(
            ["Office / HQ"],
            [
                [
                    "FACILITY_TYPE",
                    "EXACT",
                    "Office / HQ",
                    "Office / HQ",
                ]
            ],
        )

        response = self.client.get(
            self.url + "?facility_type=Office%20/%20HQ&processing_type=ce"
        )
        data = json.loads(response.content)
        self.assertEqual(data["count"], 0)

    def test_search_free_text_finds_value_in_either_column(self):
        self._create_facility_type_extended_field(
            ["cement mixing"],
            [[None, None, None, None]],
        )

        response = self.client.get(
            self.url + "?processing_type=cement%20mixing"
        )
        data = json.loads(response.content)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["features"][0]["id"], self.facility.id)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_single_processing_value(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector': 'Apparel',
    #         'processing_type': ['cutting']
    #     }), content_type='application/json')
    #     self.assertEqual(2, ExtendedField.objects.all().count())
    #     ef = ExtendedField.objects.first()
    #     self.assertEqual(ExtendedField.FACILITY_TYPE, ef.field_name)
    #     self.assertEqual(
    #         {'matched_values': [
    #             [
    #                 'PROCESSING_TYPE',
    #                 'EXACT',
    #                 'Final Product Assembly',
    #                 'Cutting'
    #             ]
    #         ], 'raw_values': ['cutting']}, ef.value)
    #     ef = ExtendedField.objects.last()
    #     self.assertEqual(ExtendedField.PROCESSING_TYPE, ef.field_name)
    #     self.assertEqual(
    #         {'matched_values': [
    #             [
    #                 'PROCESSING_TYPE',
    #                 'EXACT',
    #                 'Final Product Assembly',
    #                 'Cutting'
    #             ]
    #         ], 'raw_values': ['cutting']}, ef.value)
    #     facility_index = FacilityIndex.objects.get(id=ef.facility.id)
    #     self.assertNotIn('Cutting', facility_index.facility_type)
    #     self.assertIn('Final Product Assembly', facility_index.facility_type)
    #     self.assertIn('Cutting', facility_index.processing_type)
    #     self.assertNotIn('Final Product Assembly',
    #                      facility_index.processing_type)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_multiple_facility_values(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector': 'Apparel',
    #         'facility_type': ['office hq', 'final product assembly']
    #     }), content_type='application/json')
    #     self.assertEqual(2, ExtendedField.objects.all().count())
    #     ef = ExtendedField.objects.first()
    #     self.assertEqual(ExtendedField.FACILITY_TYPE, ef.field_name)
    #     self.assertEqual(
    #         {'matched_values': [
    #             [
    #                 'FACILITY_TYPE',
    #                 'EXACT',
    #                 'Office / HQ',
    #                 'Office / HQ'
    #             ],
    #             [
    #                 'FACILITY_TYPE',
    #                 'EXACT',
    #                 'Final Product Assembly',
    #                 'Final Product Assembly'
    #             ]
    #         ], 'raw_values': ['office hq', 'final product assembly']},
    #         ef.value)
    #     facility_index = FacilityIndex.objects.get(id=ef.facility.id)
    #     self.assertIn('Final Product Assembly', facility_index.facility_type)
    #     self.assertIn('Office / HQ', facility_index.facility_type)
    #     self.assertEqual(0, len(facility_index.processing_type))

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_non_taxonomy_value(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     response = self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         "sector": "Apparel",
    #         'facility_type_processing_type': 'sewing|not a taxonomy value'
    #     }), content_type='application/json')
    #     self.assertEqual(1, ExtendedField.objects.filter(
    #         field_name='facility_type').count())
    #     self.assertEqual(1, ExtendedField.objects.filter(
    #         field_name='processing_type').count())
    #     self.assertEqual(response.status_code, 201)

    #     data = json.loads(response.content)
    #     index_row = FacilityIndex.objects.filter(id=data['os_id']).first()
    #     self.assertEqual(['Final Product Assembly'], index_row.facility_type)
    #     self.assertEqual(['Sewing'], index_row.processing_type)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_search_by_processing_type(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     facility_response = self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector': 'Apparel',
    #         'processing_type': ['cutting']
    #     }), content_type='application/json')
    #     facility_data = json.loads(facility_response.content)
    #     facility_id = facility_data['os_id']

    #     response = self.client.get(self.url + '?processing_type=cutting')
    #     data = json.loads(response.content)
    #     self.assertEqual(data['count'], 1)
    #     self.assertEqual(data['features'][0]['id'], facility_id)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_search_by_facility_type(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     facility_response = self.client.post(self.url, json.dumps({
    #         'country': "US",
    #         'name': "Azavea",
    #         'address': "990 Spring Garden St., Philadelphia PA 19123",
    #         'sector': ['Health', 'Apparel'],
    #         'facility_type': ['office hq', 'final product assembly']
    #     }), content_type='application/json')
    #     facility_data = json.loads(facility_response.content)
    #     facility_id = facility_data['os_id']

    #     response = self.client.get(
    #         self.url + '?facility_type=final%20product%20assembly'
    #     )
    #     data = json.loads(response.content)
    #     self.assertEqual(data['count'], 1)
    #     self.assertEqual(data['features'][0]['id'], facility_id)

    @patch("api.geocoding.requests.get")
    def test_search_by_facility_type_omits_nonapparel(self, mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data
        self.join_group_and_login()
        self.client.post(
            self.url,
            json.dumps(
                {
                    "country": "US",
                    "name": "Azavea",
                    "address": "990 Spring Garden St., Philadelphia PA 19123",
                    "sector": "Health",
                    "facility_type": ["office hq", "final product assembly"],
                }
            ),
            content_type="application/json",
        )

        response = self.client.get(
            self.url + "?facility_type=final%20product%20assembly"
        )
        data = json.loads(response.content)
        self.assertEqual(data["count"], 0)

    def test_recruitment_agency_present_in_facility_processing_types(self):
        url = "/api/facility-processing-types/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        office_hq = next(
            (item for item in data
             if item["facilityType"].lower() == "office / hq".lower()),
            None
        )

        self.assertIsNotNone(office_hq)
        self.assertIn(
            "Recruitment Agency",
            office_hq["processingTypes"]
        )
        self.assertIn(
            "Union Headquarters/Office",
            office_hq["processingTypes"]
        )
