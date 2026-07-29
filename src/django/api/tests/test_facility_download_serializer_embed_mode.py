from unittest.mock import patch

from django.test import TestCase

from api.helpers.helpers import get_csv_values
from api.models.contributor.contributor import Contributor
from api.models.embed_config import EmbedConfig
from api.models.embed_field import EmbedField
from api.models.facility.facility_index import FacilityIndex
from api.serializers.facility.facility_download_serializer_embed_mode import (
    FacilityDownloadSerializerEmbedMode,
)


class FacilityDownloadSerializerEmbedModeTest(TestCase):
    fixtures = ["facilities_index", "contributors", "users"]

    def setUp(self):
        self.facility_one = FacilityIndex.objects.get(id="1")

        self.embed_config = EmbedConfig.objects.create()
        self.contributor = Contributor.objects.get(id=1)
        self.contributor.embed_config = self.embed_config
        self.contributor.save()
        self.embed_one = EmbedField.objects.create(
            embed_config=self.embed_config,
            order=0,
            column_name="extra_1",
            display_name="ExtraOne",
            visible=True,
            searchable=True,
        )
        self.embed_two = EmbedField.objects.create(
            embed_config=self.embed_config,
            order=1,
            column_name="extra_2",
            display_name="ExtraTwo",
            visible=True,
            searchable=True,
        )
        self.embed_three = EmbedField.objects.create(
            embed_config=self.embed_config,
            order=2,
            column_name="parent_company",
            display_name="Parent Company",
            visible=True,
            searchable=True,
        )
        self.embed_four = EmbedField.objects.create(
            embed_config=self.embed_config,
            order=3,
            column_name="extra_3",
            display_name="ExtraThree",
            visible=False,
            searchable=False,
        )

    def test_get_headers(self):
        contributor_id = "1"
        serializer = FacilityDownloadSerializerEmbedMode(
            contributor_id=contributor_id
        )
        headers = serializer.get_headers()
        expected_headers = [
            "os_id",
            "contribution_date",
            "name",
            "address",
            "country_code",
            "country_name",
            "lat",
            "lng",
            "sector",
            "extra_1",
            "extra_2",
            "number_of_workers",
            "parent_company",
            "processing_type_facility_type_raw",
            "facility_type",
            "processing_type",
            "product_type",
            "is_closed",
        ]
        self.assertEqual(headers, expected_headers)

    def test_get_row(self):
        contributor_id = "1"
        serializer = FacilityDownloadSerializerEmbedMode(
            contributor_id=contributor_id
        )
        row = serializer.get_row(self.facility_one)
        headers = serializer.get_headers()
        row_by_header = dict(zip(headers, row))

        expected_common_and_custom_values = [
            "1",
            "2022-05-18",
            "First Facility",
            "First Facility Address",
            "US",
            "United States",
            0.0,
            0.0,
            "Test Sector",
            "Extra 1 custom field data",
            "Extra 2 custom field data",
        ]
        self.assertEqual(row[:11], expected_common_and_custom_values)
        self.assertEqual(
            row_by_header["processing_type_facility_type_raw"], "Raw Data"
        )
        self.assertEqual(row_by_header["is_closed"], "False")
        self.assertEqual(
            set(row_by_header["number_of_workers"].split("|")),
            {"1", "101-500"},
        )
        self.assertEqual(
            set(row_by_header["parent_company"].split("|")),
            {
                "Parent Company Service Provider A",
                "Parent Company Factory A",
            },
        )
        self.assertEqual(
            set(row_by_header["facility_type"].split("|")),
            {
                "Matched facility type value one Service Provider A",
                "Matched facility type value two Service Provider A",
                "Matched facility type value one Factory A",
            },
        )
        self.assertEqual(
            set(row_by_header["processing_type"].split("|")),
            {
                "Matched processing type value one Service Provider A",
                "Matched processing type value two Service Provider A",
                "Matched processing type value one Factory A",
            },
        )
        self.assertEqual(
            set(row_by_header["product_type"].split("|")),
            {
                "Product Type Service Provider A",
                "Product Type Factory A",
            },
        )

    def test_get_list_custom_fields_preserves_configured_header_case(self):
        EmbedField.objects.create(
            embed_config=self.embed_config,
            order=4,
            column_name="program_1_Name",
            display_name="Program Name",
            visible=True,
            searchable=True,
        )
        EmbedField.objects.create(
            embed_config=self.embed_config,
            order=5,
            column_name="total_number_of_employees",
            display_name="Total Number of Employees",
            visible=True,
            searchable=True,
        )
        info = self.facility_one.custom_field_info[0]
        info["list_header"] = (
            "extra_1,extra_2,parent_company,program_1_Name,"
            "total_number_of_employees"
        )
        info["raw_data"] = (
            '"Extra 1 custom field data","Extra 2 custom field data",'
            '"Parent Company","Program One","250"'
        )

        serializer = FacilityDownloadSerializerEmbedMode(contributor_id="1")

        self.assertEqual(
            serializer.get_contributor_custom_fields(self.facility_one),
            [
                "Extra 1 custom field data",
                "Extra 2 custom field data",
                "Program One",
                "250",
            ],
        )

    def test_get_list_custom_fields_matches_headers_case_insensitively(self):
        info = self.facility_one.custom_field_info[0]
        info["list_header"] = "Extra_1,EXTRA_2,parent_company"

        serializer = FacilityDownloadSerializerEmbedMode(contributor_id="1")

        self.assertEqual(
            serializer.get_contributor_custom_fields(self.facility_one),
            [
                "Extra 1 custom field data",
                "Extra 2 custom field data",
            ],
        )

    def test_get_list_custom_fields_prefers_exact_case_match(self):
        EmbedField.objects.create(
            embed_config=self.embed_config,
            order=4,
            column_name="Extra_1",
            display_name="Uppercase Extra One",
            visible=True,
            searchable=True,
        )
        info = self.facility_one.custom_field_info[0]
        info["list_header"] = "extra_1,Extra_1,parent_company"
        info["raw_data"] = '"lowercase value","uppercase value","Parent"'

        serializer = FacilityDownloadSerializerEmbedMode(contributor_id="1")

        self.assertEqual(
            serializer.get_contributor_custom_fields(self.facility_one),
            [
                "lowercase value",
                "",
                "uppercase value",
            ],
        )

    def test_get_list_custom_fields_caches_header_indexes(self):
        serializer = FacilityDownloadSerializerEmbedMode(contributor_id="1")
        list_header = self.facility_one.custom_field_info[0]["list_header"]
        get_csv_values_path = (
            "api.serializers.facility."
            "facility_download_serializer_embed_mode.get_csv_values"
        )

        with patch(get_csv_values_path, wraps=get_csv_values) as get_values:
            serializer.get_contributor_custom_fields(self.facility_one)
            serializer.get_contributor_custom_fields(self.facility_one)

        header_calls = [
            call for call in get_values.call_args_list
            if call.args == (list_header,)
        ]
        self.assertEqual(len(header_calls), 1)

    def test_get_api_custom_fields_uses_configured_names(self):
        self.facility_one.custom_field_info = [
            {
                "raw_data": (
                    "{'extra_1': 'API extra one', "
                    "'extra_2': 'API extra two'}"
                ),
                "list_header": "",
                "source_type": "SINGLE",
                "contributor_id": 1,
            }
        ]
        serializer = FacilityDownloadSerializerEmbedMode(contributor_id="1")

        self.assertEqual(
            serializer.get_contributor_custom_fields(self.facility_one),
            ["API extra one", "API extra two"],
        )
