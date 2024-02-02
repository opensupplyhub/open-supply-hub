from api.models import Contributor, EmbedConfig, EmbedField
from api.models.facility.facility_index import FacilityIndex
from api.serializers.facility.facility_download_serializer_embed_mode import (
    FacilityDownloadSerializerEmbedMode,
)

from django.test import TestCase


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
