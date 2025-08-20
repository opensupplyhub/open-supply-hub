import json
from unittest.mock import Mock, patch

from api.helpers.helpers import parse_raw_data
from api.models import (
    Contributor,
    EmbedConfig,
    EmbedField,
    ExtendedField,
    Facility,
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from django.core.files.uploadedfile import SimpleUploadedFile
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase
from api.tests.test_data import geocoding_data
from rest_framework import status
from waffle.testutils import override_flag, override_switch

from django.contrib.gis.geos import Point
from django.urls import reverse
from django.utils import timezone


class FacilityDownloadTest(FacilityAPITestCaseBase):
    fixtures = ["sectors"]

    def setUp(self):
        super(FacilityDownloadTest, self).setUp()
        self.download_url = "/api/facilities-downloads/"
        self.contributor_column_index = 9
        self.date = timezone.now().strftime("%Y-%m-%d")
        self.embed_config = EmbedConfig.objects.create()

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

        self.contrib_list = FacilityList.objects.create(
            header="country,name,address,sector,extra_1",
            file_name="one",
            name="First List",
        )

        self.contrib_list_source = Source.objects.create(
            facility_list=self.contrib_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        raw_data = (
            '"US","Towel Factory 42",' + '"42 Dolphin St","Apparel","data one"'
        )
        self.contrib_list_item = FacilityListItem.objects.create(
            name="Towel Factory 42",
            address="42 Dolphin St",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.contrib_list_source,
            raw_data=raw_data,
        )

        self.contrib_facility = Facility.objects.create(
            name="Towel Factory 42",
            address="42 Dolphin St",
            country_code="US",
            created_from=self.contrib_list_item,
            location=Point(0, 0),
        )

        self.contrib_match_one = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.contrib_facility,
            facility_list_item=self.contrib_list_item,
            confidence=0.85,
            results="",
            is_active=True,
        )

        self.contrib_list_item.facility = self.contrib_facility
        self.contrib_list_item.save()

        self.contrib_api_source = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        self.contrib_api_list_item = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            raw_data=(
                "{'country': 'US', 'name': 'Item',"
                + "'address': 'Address', 'extra_2': 'data two',"
                + "'sector': 'Apparel'}"
            ),
            raw_json=parse_raw_data(
                (
                    "{'country': 'US', 'name': 'Item',"
                    "'address': 'Address', 'extra_2': 'data two',"
                    "'sector': 'Apparel'}"
                )
            ),
            raw_header="",
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.contrib_api_source,
        )
        self.contrib_facility_two = Facility.objects.create(
            name="Item",
            address="Address",
            country_code=self.contrib_api_list_item.country_code,
            created_from=self.contrib_api_list_item,
            location=Point(0, 0),
        )
        self.contrib_match_one = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility_list_item=self.contrib_api_list_item,
            facility=self.contrib_facility_two,
            confidence=0.85,
            results="",
            is_active=True,
        )

        self.contrib_api_list_item.facility = self.contrib_facility_two
        self.contrib_api_list_item.save()

        self.default_headers = [
            "os_id",
            "contribution_date",
            "name",
            "address",
            "country_code",
            "country_name",
            "lat",
            "lng",
            "sector",
            "contributor (list)",
            "number_of_workers",
            "parent_company",
            "processing_type_facility_type_raw",
            "facility_type",
            "processing_type",
            "product_type",
            "is_closed",
        ]
        self.contrib_facility_base_row = [
            self.contrib_facility.id,
            self.date,
            "Towel Factory 42",
            "42 Dolphin St",
            "US",
            "United States",
            0.0,
            0.0,
            "Apparel",
            "test contributor 1 (First List)",
            "",
            "",
            "",
            "",
            "",
            "",
            "False",
        ]

        self.user_two = User.objects.create(email="test2@example.com")
        self.contributor_two = Contributor.objects.create(
            admin=self.user_two,
            name="test contributor 2",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

    @override_flag("can_get_facility_history", active=True)
    @override_switch("claim_a_facility", active=True)
    def create_claim(self):
        self.client.logout()
        self.client.login(email=self.user_email, password=self.user_password)

        claim_facility_url = "/api/facilities/{}/claim/".format(
            self.facility.id,
        )

        claim_facility_data = {
            "your_name": "your_name",
            "your_title": "your_title",
            "your_business_website": "https://example.com",
            "business_website": "https://example.com",
            "business_linkedin_profile": "https://example.com",
        }

        file_data = {
            'test_attachment_1.jpg': (
                b'claimant_attachment_content_jpg', 'image/jpg'
            ),
            'test_attachment_2.jpeg': (
                b'claimant_attachment_content_jpeg', 'image/jpeg'
            ),
            'test_attachment_3.png': (
                b'claimant_attachment_content_png', 'image/png'
            ),
            'test_attachment_4.pdf': (
                b'claimant_attachment_content_pdf', 'application/pdf'
            )
        }

        upload_files = []
        for name, (content, content_type) in file_data.items():
            upload_files.append(
                SimpleUploadedFile(
                    name=name,
                    content=content,
                    content_type=content_type
                )
            )

        claim_facility_data["files"] = upload_files

        self.client.post(claim_facility_url, claim_facility_data)

        self.client.logout()
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        claim = FacilityClaim.objects.first()

        approve_claim_url = "/api/facility-claims/{}/approve/".format(
            claim.id,
        )

        self.client.post(approve_claim_url, {"reason": "reason"})

        self.client.logout()
        self.client.login(email=self.user_email, password=self.user_password)

        update_claim_url = "/api/facility-claims/{}/claimed/".format(
            claim.id,
        )

        update_claim_data = {
            "id": claim.id,
            "facility_name_english": "Claim Name",
            "facility_name_native_language": "native_language",
            "facility_address": "facility_address",
            "facility_description": "facility_description",
            "facility_phone_number": 1234567,
            "facility_phone_number_publicly_visible": True,
            "facility_website": "https://opensupplyhub.org",
            "facility_website_publicly_visible": True,
            "facility_minimum_order_quantity": 10,
            "facility_average_lead_time": "2 months",
            "point_of_contact_person_name": "point_of_contact_person_name",
            "point_of_contact_email": "point_of_contact_email",
            "facility_workers_count": 20,
            "facility_female_workers_percentage": 50,
            "point_of_contact_publicly_visible": True,
            "office_official_name": "office_official_name",
            "office_address": "office_address",
            "office_country_code": "US",
            "office_phone_number": 2345678,
            "office_info_publicly_visible": True,
            "facility_type": "Cut and Sew / RMG",
        }
        self.client.put(update_claim_url, update_claim_data)
        self.create_extended_fields({"claim_id": claim.id})

    def create_extended_fields(self, source):
        claim_id = source.get("claim_id", None)
        list_item_id = source.get("list_item_id", None)
        if claim_id is None:
            ExtendedField.objects.create(
                field_name="number_of_workers",
                value={"max": 5000, "min": 100},
                contributor=self.contributor,
                facility=self.facility,
                facility_claim_id=claim_id,
                facility_list_item_id=list_item_id,
            )

        ExtendedField.objects.create(
            field_name="parent_company",
            value={"name": "Contributor", "raw_value": "Contributor"},
            contributor=self.contributor,
            facility=self.facility,
            facility_claim_id=claim_id,
            facility_list_item_id=list_item_id,
        )

        ExtendedField.objects.create(
            field_name="facility_type",
            value={
                "raw_values": ["biological recycling"],
                "matched_values": [
                    [
                        "PROCESSING_TYPE",
                        "EXACT",
                        "Raw Material Processing or Production",
                        "Biological Recycling",
                    ]
                ],
            },
            contributor=self.contributor,
            facility=self.facility,
            facility_claim_id=claim_id,
            facility_list_item_id=list_item_id,
        )

        ExtendedField.objects.create(
            field_name="processing_type",
            value={
                "raw_values": ["biological recycling"],
                "matched_values": [
                    [
                        "PROCESSING_TYPE",
                        "EXACT",
                        "Raw Material Processing or Production",
                        "Biological Recycling",
                    ]
                ],
            },
            contributor=self.contributor,
            facility=self.facility,
            facility_claim_id=claim_id,
            facility_list_item_id=list_item_id,
        )

        ExtendedField.objects.create(
            field_name="product_type",
            value={"raw_values": ["Shirts"]},
            contributor=self.contributor,
            facility=self.facility,
            facility_claim_id=claim_id,
            facility_list_item_id=list_item_id,
        )

    @patch("api.geocoding.requests.get")
    def create_additional_list_item(self, mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data
        self.join_group_and_login()
        url = reverse("facility-list")
        response = self.client.post(
            url,
            json.dumps(
                {
                    "country": "US",
                    "name": "Towel Factory 42",
                    "address": "42 Dolphin St",
                    "sector": "Apparel",
                    "product_type": ["a"],
                    "parent_company": "Contributor A",
                    "processing_type": ["biological recycling"],
                    "number_of_workers": "0-100",
                }
            ),
            content_type="application/json",
        )
        item_id = response.data["item_id"]
        return FacilityListItem.objects.get(id=item_id)

    def get_facility_download(self, params=None):
        url = self.download_url
        if params is not None:
            url = "{}?{}".format(self.download_url, params)

        return self.client.get(url)

    def get_rows(self, response):
        return response.data["results"]["rows"]

    def get_headers(self, response):
        return response.data["results"]["headers"]

    def get_is_same_contributor(self, response):
        return response.data["results"].get("is_same_contributor")

    def test_download_is_fetched(self):
        response = self.get_facility_download()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data["count"], 3)

    def test_default_headers_are_created(self):
        response = self.get_facility_download()
        headers = self.get_headers(response)
        expected_headers = self.default_headers
        self.assertEqual(headers, expected_headers)
        # Ensure flag is present at top-level results for UI logic
        self.assertIn("is_same_contributor", response.data["results"])

    def test_embed_headers_exclude_contributor(self):
        params = "embed=1&contributors={}".format(self.contributor.id)
        response = self.get_facility_download(params)
        headers = self.get_headers(response)
        self.assertNotIn("contributor (list)", headers)

    def test_embed_headers_include_contributor_fields(self):
        params = "embed=1&contributors={}".format(self.contributor.id)
        response = self.get_facility_download(params)
        headers = self.get_headers(response)
        self.assertEquals(headers[9], "extra_1")
        self.assertEquals(headers[10], "extra_2")

    def test_embed_headers_dedupe_extended_fields(self):
        params = "embed=1&contributors={}".format(self.contributor.id)
        response = self.get_facility_download(params)
        headers = self.get_headers(response)
        self.assertEqual(headers.count("parent_company"), 1)

    def test_embed_headers_exclude_invisible_contributor_fields(self):
        params = "embed=1&contributors={}".format(self.contributor.id)
        response = self.get_facility_download(params)
        headers = self.get_headers(response)
        self.assertNotIn("extra_3", headers)

    def test_base_row_is_created(self):
        params = "q={}".format(self.facility.id)
        response = self.get_facility_download(params)
        base_row = self.get_rows(response)[0]
        expected_base_row = [
            self.facility.id,
            self.date,
            "Name",
            "Address",
            "US",
            "United States",
            0.0,
            0.0,
            "Apparel",
            "test contributor 1 (First List)",
            "",
            "",
            "",
            "",
            "",
            "",
            "False",
        ]
        self.assertEqual(len(base_row), len(expected_base_row))
        self.assertEqual(base_row, expected_base_row)
        # Assert the flag exists and is boolean
        self.assertIsInstance(self.get_is_same_contributor(response), bool)

    def test_contrib_rows_are_created_for_no_contrib_values(self):
        params = "embed=1&contributors={}&q={}".format(
            self.contributor.id, self.facility.id
        )
        response = self.get_facility_download(params)
        base_row = self.get_rows(response)[0]
        expected_base_row = [
            self.facility.id,
            self.date,
            "Name",
            "Address",
            "US",
            "United States",
            0.0,
            0.0,
            "Apparel",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "False",
        ]
        self.assertEqual(len(base_row), len(expected_base_row))
        self.assertEqual(base_row, expected_base_row)

    def test_contrib_rows_are_created_for_list_contrib_values(self):
        params = "embed=1&contributors={}&q={}".format(
            self.contributor.id, self.contrib_facility.id
        )
        response = self.get_facility_download(params)
        base_row = self.get_rows(response)[0]
        expected_base_row = [
            self.contrib_facility.id,
            self.date,
            "Towel Factory 42",
            "42 Dolphin St",
            "US",
            "United States",
            0.0,
            0.0,
            "Apparel",
            "data one",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "False",
        ]
        self.assertEqual(len(base_row), len(expected_base_row))
        self.assertEqual(base_row, expected_base_row)

    def test_contrib_rows_are_created_for_API_contrib_values(self):
        params = "embed=1&contributors={}&q={}".format(
            self.contributor.id, self.contrib_facility_two.id
        )
        response = self.get_facility_download(params)
        base_row = self.get_rows(response)[0]
        expected_base_row = [
            self.contrib_facility_two.id,
            self.date,
            "Item",
            "Address",
            "US",
            "United States",
            0.0,
            0.0,
            "Apparel",
            "",
            "data two",
            "",
            "",
            "",
            "",
            "",
            "",
            "False",
        ]
        self.assertEqual(len(base_row), len(expected_base_row))
        self.assertEqual(base_row, expected_base_row)

    def test_extended_fields(self):
        self.create_extended_fields({"list_item_id": self.list_item.id})
        params = "q={}".format(self.facility.id)
        response = self.get_facility_download(params)
        base_row = self.get_rows(response)[0]
        row = [
            self.facility.id,
            self.date,
            "Name",
            "Address",
            "US",
            "United States",
            0.0,
            0.0,
            "Apparel",
            "test contributor 1 (First List)",
            "100-5000",
            "Contributor",
            "biological recycling",
            "Raw Material Processing or Production",
            "Biological Recycling",
            "Shirts",
            "False",
        ]
        self.assertEqual(len(base_row), len(row))
        self.assertEqual(base_row, row)

    def test_claim_base_row(self):
        self.create_claim()
        params = "q={}".format(self.facility.id)
        response = self.get_facility_download(params)
        rows = self.get_rows(response)
        row = [
            self.facility.id,
            self.date,
            "Claim Name",
            "Address",
            "US",
            "United States",
            0.0,
            0.0,
            "Apparel",
            "test contributor 1 (Claimed)|test contributor 1 (First List)",
            "20",
            "Contributor",
            "biological recycling",
            "Raw Material Processing or Production",
            "Biological Recycling",
            "Shirts",
            "False",
        ]
        self.assertEquals(rows[0], row)

    def test_handles_additional_list_items(self):
        self.create_additional_list_item()

        params = "q={}".format(self.contrib_facility.id)
        response = self.get_facility_download(params)

        headers = self.get_headers(response)
        self.assertEqual(headers, self.default_headers)
        # Flag should exist regardless of headers
        self.assertIn("is_same_contributor", response.data["results"])

        rows = self.get_rows(response)

        row = [
            self.contrib_facility.id,
            self.date,
            "Towel Factory 42",
            "42 Dolphin St",
            "US",
            "United States",
            0.0,
            0.0,
            "Apparel",
            "test contributor 1 (First List)",
            "",
            "",
            "",
            "",
            "",
            "",
            "False",
        ]
        self.assertEqual(row, rows[0])

    def test_embed_excludes_alt_contributors(self):
        list_item = self.create_additional_list_item()
        list_item.source.contributor_id = self.contributor_two.id
        list_item.source.save()

        params = "embed=1&contributors={}&q={}".format(
            self.contributor.id, self.contrib_facility.id
        )
        response = self.get_facility_download(params)
        rows = self.get_rows(response)

        self.assertEquals(len(rows), 1)

        expected_base_row = [
            self.contrib_facility.id,
            self.date,
            "Towel Factory 42",
            "42 Dolphin St",
            "US",
            "United States",
            0.0,
            0.0,
            "Apparel",
            "data one",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "False",
        ]
        self.assertEquals(rows[0], expected_base_row)

    def test_inactive_source_is_anonymized(self):
        list_item = self.create_additional_list_item()
        list_item.source.is_active = False
        list_item.source.save()

        params = "q={}".format(self.contrib_facility.id)
        response = self.get_facility_download(params)
        rows = self.get_rows(response)

        row = [
            self.contrib_facility.id,
            self.date,
            "Towel Factory 42",
            "42 Dolphin St",
            "US",
            "United States",
            0.0,
            0.0,
            "Apparel",
            "test contributor 1 (First List)",
            "",
            "",
            "",
            "",
            "",
            "",
            "False",
        ]
        self.assertEquals(rows[0], row)

    def test_private_source_is_anonymized(self):
        list_item = self.create_additional_list_item()
        list_item.source.is_public = False
        list_item.source.save()

        params = "q={}".format(self.contrib_facility.id)
        response = self.get_facility_download(params)
        rows = self.get_rows(response)

        row = [
            self.contrib_facility.id,
            self.date,
            "Towel Factory 42",
            "42 Dolphin St",
            "US",
            "United States",
            0.0,
            0.0,
            "Apparel",
            "test contributor 1 (First List)",
            "",
            "",
            "",
            "",
            "",
            "",
            "False",
        ]
        self.assertEquals(rows[0], row)

    def test_inactive_match_is_anonymized(self):
        self.match.is_active = False
        self.match.save()

        params = "q={}".format(self.facility.id)
        response = self.get_facility_download(params)
        rows = self.get_rows(response)
        self.assertEquals(len(rows), 1)

        contributor = rows[0][self.contributor_column_index]
        self.assertEquals(contributor, "An Other")

    def test_invalid_status_match_is_excluded(self):
        list_item = self.create_additional_list_item()
        for match in FacilityMatch.objects.filter(
            facility_list_item=list_item
        ):
            match.status = FacilityListItem.GEOCODED
            match.save()

        params = "q={}".format(self.contrib_facility.id)
        response = self.get_facility_download(params)
        rows = self.get_rows(response)
        self.assertEquals(len(rows), 1)

        expected_base_row = self.contrib_facility_base_row
        self.assertEquals(rows[0], expected_base_row)

    # TODO: Replace to Dedupe Hub if possible (issue between test database
    #       & Dedupe Hub live database)
    # @patch('api.geocoding.requests.get')
    # def test_anonymize_inactive_primary_source(self, mock_get):
    #     mock_get.return_value = Mock(ok=True, status_code=200)
    #     mock_get.return_value.json.return_value = geocoding_data
    #     self.join_group_and_login()
    #     url = reverse('facility-list')
    #     response = self.client.post(url, json.dumps({
    #         "country": "US",
    #         "name": "Azavea",
    #         "address": "990 Spring Garden St., Philadelphia PA 19123",
    #         "facility_type_processing_type": "stiching",
    #         "parent_company": "foo",
    #         "product_type": "shoes",
    #         "sector": "Apparel"
    #     }), content_type='application/json')
    #     os_id = response.data["os_id"]

    #     source = Source.objects.latest('created_at')
    #     source.is_active = False
    #     source.save()

    #     params = 'q={}'.format(os_id)
    #     response = self.get_facility_download(params)
    #     contributor = self.get_rows(
    #         response)[0][self.contributor_column_index]
    #     expected_contributor = 'An Other'
    #     self.assertEqual(contributor, expected_contributor)

    def test_handle_incomplete_raw_data(self):
        incomplete_raw_data = '"US","Towel Factory 42","42 Dolphin St"'
        self.contrib_list_item.raw_data = incomplete_raw_data
        self.contrib_list_item.save()

        params = "embed=1&contributors={}&q={}".format(
            self.contributor.id, self.contrib_facility.id
        )
        response = self.get_facility_download(params)
        rows = self.get_rows(response)

        self.assertEquals(len(rows), 1)

        expected_base_row = [
            self.contrib_facility.id,
            self.date,
            "Towel Factory 42",
            "42 Dolphin St",
            "US",
            "United States",
            0.0,
            0.0,
            "Apparel",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "False",
        ]
        self.assertEquals(rows[0], expected_base_row)
