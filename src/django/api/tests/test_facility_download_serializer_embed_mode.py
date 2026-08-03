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

    def test_visible_empty_custom_header_is_retained(self):
        EmbedField.objects.create(
            embed_config=self.embed_config,
            order=4,
            column_name="configured_without_data",
            display_name="Configured Without Data",
            visible=True,
            searchable=True,
        )
        serializer = FacilityDownloadSerializerEmbedMode(contributor_id="1")
        headers = serializer.get_headers()
        row_by_header = dict(
            zip(headers, serializer.get_row(self.facility_one))
        )

        self.assertIn("configured_without_data", headers)
        self.assertEqual(row_by_header["configured_without_data"], "")

    def test_hidden_custom_header_is_omitted_despite_data(self):
        info = self.facility_one.custom_field_info[0]
        info["list_header"] += ",extra_3"
        info["raw_data"] += ',"Hidden field data"'

        serializer = FacilityDownloadSerializerEmbedMode(contributor_id="1")

        self.assertNotIn("extra_3", serializer.get_headers())

    def test_get_row(self):
        contributor_id = "1"
        serializer = FacilityDownloadSerializerEmbedMode(
            contributor_id=contributor_id
        )
        row = serializer.get_row(self.facility_one)

        # Contributor 2 also contributed every standard field to this facility,
        # but the embedded map only shows contributor 1's data.
        expected_row = [
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
            "1",
            "Parent Company Service Provider A",
            "Raw Data",
            "Matched facility type value one Service Provider A|"
            "Matched facility type value two Service Provider A",
            "Matched processing type value one Service Provider A|"
            "Matched processing type value two Service Provider A",
            "Product Type Service Provider A",
            "False",
        ]
        self.assertEqual(row, expected_row)

    def test_get_row_preserves_baseline_sector_aggregation(self):
        self.facility_one.sector = ["apparel", "TEXTILES"]
        serializer = FacilityDownloadSerializerEmbedMode(contributor_id="1")
        row_by_header = dict(
            zip(
                serializer.get_headers(),
                serializer.get_row(self.facility_one),
            )
        )

        self.assertEqual(row_by_header["sector"], "Apparel|Textiles")

    def test_get_row_joins_all_owner_extended_field_values(self):
        serializer = FacilityDownloadSerializerEmbedMode(contributor_id="1")
        own_number_of_workers = next(
            field
            for field in self.facility_one.extended_fields
            if field["field_name"] == "number_of_workers"
            and field["contributor"]["id"] == 1
        )
        self.facility_one.extended_fields.append({
            **own_number_of_workers,
            "id": 999,
            "value": {"min": 900, "max": 900},
            "is_verified": True,
        })

        row_by_header = dict(
            zip(
                serializer.get_headers(),
                serializer.get_row(self.facility_one),
            )
        )

        self.assertEqual(row_by_header["number_of_workers"], "1|900")

    def test_get_contributor_custom_fields_preserve_list_header_case(self):
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

    def test_employee_headers_do_not_alias_or_fall_back(self):
        EmbedField.objects.create(
            embed_config=self.embed_config,
            order=4,
            column_name="total_number_of_employees",
            display_name="Total Number of Employees",
            visible=True,
            searchable=True,
        )
        info = self.facility_one.custom_field_info[0]
        info["list_header"] = (
            "extra_1,extra_2,parent_company,total_number_of_employees"
        )
        info["raw_data"] = '"Extra 1","Extra 2","Parent","250"'
        self.facility_one.extended_fields = [
            field
            for field in self.facility_one.extended_fields
            if field["field_name"] != "number_of_workers"
            or field["contributor"]["id"] != 1
        ]

        serializer = FacilityDownloadSerializerEmbedMode(contributor_id="1")
        row_by_header = dict(
            zip(
                serializer.get_headers(),
                serializer.get_row(self.facility_one),
            )
        )

        self.assertEqual(row_by_header["total_number_of_employees"], "250")
        self.assertEqual(row_by_header["number_of_workers"], "")

    def test_get_contributor_custom_fields_match_case_insensitively(self):
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

    def test_get_contributor_custom_fields_prefer_exact_case(self):
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

    def test_get_contributor_custom_fields_use_single_field_names(self):
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
            [
                "API extra one",
                "API extra two",
            ],
        )
