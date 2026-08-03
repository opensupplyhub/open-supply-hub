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
            "parent_company",
            "is_closed",
        ]
        self.assertEqual(headers, expected_headers)

    def test_visible_empty_header_is_retained(self):
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

    def test_hidden_header_is_omitted_despite_data(self):
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
            "Parent Company Service Provider A",
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

    def test_get_row_keeps_only_top_ranked_contribution_per_field(self):
        EmbedField.objects.create(
            embed_config=self.embed_config,
            order=4,
            column_name="number_of_workers",
            display_name="Number of Workers",
            visible=True,
            searchable=True,
        )
        serializer = FacilityDownloadSerializerEmbedMode(contributor_id="1")
        own_number_of_workers = next(
            field
            for field in self.facility_one.extended_fields
            if field["field_name"] == "number_of_workers"
            and field["contributor"]["id"] == 1
        )
        verified_duplicate = {
            **own_number_of_workers,
            "value": {"min": 900, "max": 900},
            "is_verified": True,
        }
        self.facility_one.extended_fields.append(verified_duplicate)

        row_by_header = dict(
            zip(
                serializer.get_headers(),
                serializer.get_row(self.facility_one),
            )
        )

        self.assertEqual(row_by_header["number_of_workers"], "900")

    def test_get_row_uses_display_ranking_for_single_value(self):
        EmbedField.objects.create(
            embed_config=self.embed_config,
            order=4,
            column_name="number_of_workers",
            display_name="Number of Workers",
            visible=True,
            searchable=True,
        )
        serializer = FacilityDownloadSerializerEmbedMode(contributor_id="1")
        original = next(
            field
            for field in self.facility_one.extended_fields
            if field["field_name"] == "number_of_workers"
            and field["contributor"]["id"] == 1
        )
        original.update({
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-06-01T00:00:00Z",
        })
        self.facility_one.extended_fields.append({
            **original,
            "id": 999,
            "value": {"min": 200, "max": 200},
            "created_at": "2026-02-01T00:00:00Z",
            "updated_at": "2026-03-01T00:00:00Z",
        })

        row_by_header = dict(zip(
            serializer.get_headers(),
            serializer.get_row(self.facility_one),
        ))

        self.assertEqual(row_by_header["number_of_workers"], "200")

    def test_get_row_skips_unmatched_facility_type_before_ranking(self):
        EmbedField.objects.create(
            embed_config=self.embed_config,
            order=4,
            column_name="facility_type",
            display_name="Facility Type",
            visible=True,
            searchable=True,
        )
        serializer = FacilityDownloadSerializerEmbedMode(contributor_id="1")
        matched = next(
            field
            for field in self.facility_one.extended_fields
            if field["field_name"] == "facility_type"
            and field["contributor"]["id"] == 1
        )
        matched["is_verified"] = False
        self.facility_one.extended_fields.append({
            **matched,
            "id": 999,
            "value": {
                "raw_values": ["Unmatched"],
                "matched_values": [[None, None, None, None]],
            },
            "is_verified": True,
        })

        row_by_header = dict(zip(
            serializer.get_headers(),
            serializer.get_row(self.facility_one),
        ))

        self.assertEqual(
            row_by_header["facility_type"],
            "Matched facility type value one Service Provider A|"
            "Matched facility type value two Service Provider A",
        )

    def test_get_row_falls_back_to_custom_standard_field_value(self):
        EmbedField.objects.create(
            embed_config=self.embed_config,
            order=4,
            column_name="facility_type",
            display_name="Facility Type",
            visible=True,
            searchable=True,
        )
        self.facility_one.extended_fields = [
            field
            for field in self.facility_one.extended_fields
            if not (
                field["field_name"] == "facility_type"
                and field["contributor"]["id"] == 1
            )
        ]
        info = next(
            info
            for info in self.facility_one.custom_field_info
            if info["contributor_id"] == 1
        )
        info["list_header"] += "facility_type"
        info["raw_data"] += ',"Custom facility type"'

        serializer = FacilityDownloadSerializerEmbedMode(contributor_id="1")
        row_by_header = dict(zip(
            serializer.get_headers(),
            serializer.get_row(self.facility_one),
        ))

        self.assertEqual(
            row_by_header["facility_type"],
            "Custom facility type",
        )

    def test_get_row_formats_extended_fields_like_embed_profile(self):
        for order, field_name in enumerate(
            ("parent_company", "processing_type"),
            start=4,
        ):
            EmbedField.objects.create(
                embed_config=self.embed_config,
                order=order,
                column_name=field_name,
                display_name=field_name,
                visible=True,
                searchable=True,
            )
        serializer = FacilityDownloadSerializerEmbedMode(contributor_id="1")
        parent = next(
            field
            for field in self.facility_one.extended_fields
            if field["field_name"] == "parent_company"
            and field["contributor"]["id"] == 1
        )
        parent["value"] = {"raw_value": "Raw Parent"}
        processing = next(
            field
            for field in self.facility_one.extended_fields
            if field["field_name"] == "processing_type"
            and field["contributor"]["id"] == 1
        )
        processing["value"] = {
            "raw_values": ["Raw fallback", "Other raw", "Duplicate raw"],
            "matched_values": [
                [None, None, None, None],
                [None, None, None, "Matched processing"],
                [None, None, None, "Matched processing"],
            ],
        }

        row_by_header = dict(zip(
            serializer.get_headers(),
            serializer.get_row(self.facility_one),
        ))

        self.assertEqual(row_by_header["parent_company"], "Raw Parent")
        self.assertEqual(
            row_by_header["processing_type"],
            "Raw fallback|Matched processing",
        )

    def test_get_row_omits_invisible_extended_fields(self):
        serializer = FacilityDownloadSerializerEmbedMode(contributor_id="1")
        headers = serializer.get_headers()

        self.assertNotIn("number_of_workers", headers)
        self.assertNotIn("processing_type_facility_type_raw", headers)
        self.assertNotIn("facility_type", headers)
        self.assertNotIn("processing_type", headers)
        self.assertNotIn("product_type", headers)

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

    def test_employee_headers_do_not_alias_or_fall_back(self):
        EmbedField.objects.create(
            embed_config=self.embed_config,
            order=4,
            column_name="total_number_of_employees",
            display_name="Total Number of Employees",
            visible=True,
            searchable=True,
        )
        EmbedField.objects.create(
            embed_config=self.embed_config,
            order=5,
            column_name="number_of_workers",
            display_name="Number of Workers",
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

    def test_get_row_includes_visible_raw_type_custom_field(self):
        EmbedField.objects.create(
            embed_config=self.embed_config,
            order=4,
            column_name="processing_type_facility_type_raw",
            display_name="Raw Type",
            visible=True,
            searchable=True,
        )
        info = self.facility_one.custom_field_info[0]
        info["list_header"] = (
            "extra_1,extra_2,parent_company,"
            "processing_type_facility_type_raw"
        )
        info["raw_data"] = (
            '"Extra 1","Extra 2","Parent","Raw configured type"'
        )
        serializer = FacilityDownloadSerializerEmbedMode(contributor_id="1")

        row_by_header = dict(zip(
            serializer.get_headers(),
            serializer.get_row(self.facility_one),
        ))

        self.assertEqual(
            row_by_header["processing_type_facility_type_raw"],
            "Raw configured type",
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
