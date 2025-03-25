from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import Group
from unittest.mock import patch

from api.models.user import User
from api.constants import FeatureGroups


DEFAULT_LIMIT = 3


class FacilitiesDownloadViewSetTest(APITestCase):
    fixtures = ["facilities_index"]

    def test_download_is_not_allowed_for_anonymous(self):
        download_url = reverse("facilities-downloads-list")
        response = self.client.get(download_url)
        expected_error_message = 'Authentication credentials were not provided.'

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(expected_error_message,response.data['detail'])

    def test_queryset_ordering(self):
        email = "test@example.com"
        password = "example123"
        user = User.objects.create(email=email)
        user.set_password(password)
        user.save()
        self.client.login(email=email, password=password)
        download_url = reverse("facilities-downloads-list")
        expected_data = [
            [
                "1",
                "2022-05-18",
                "First Facility",
                "First Facility Address",
                "US",
                "United States",
                0.0,
                0.0,
                "Test Sector",
                "A Service Provider|A Factory / Facility|Brand A",
                "1|101-500",
                "Parent Company Service Provider A|Parent Company Factory A",
                "Raw Data",
                "Matched facility type value one Service Provider A|Matched"
                " facility type value two Service Provider A|Matched facility"
                " type value one Factory A",
                "Matched processing type value one Service Provider A|Matched"
                " processing type value two Service Provider A|Matched"
                " processing type value one Factory A",
                "Product Type Service Provider A|Product Type Factory A",
                "False",
            ],
            [
                "2",
                "2020-02-22",
                "Second Facility Name English",
                "Second Facility Address",
                "IN",
                "India",
                0.0,
                0.0,
                "Test Sector",
                "Factory A (Claimed)|A Service Provider|A Factory / Facility|"
                "Brand A",
                "101-500",
                "Parent Company Factory A",
                "Raw Data",
                "Matched facility type value one Factory A",
                "Matched processing type value one Factory A",
                "Product Type Factory A",
                "False",
            ],
            [
                "4",
                "2020-02-22",
                "Test Same Facility Name A",
                "Address A",
                "US",
                "United States",
                0.0,
                0.0,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "False",
            ],
            [
                "5",
                "2020-02-22",
                "Test Same Facility Name A",
                "Address B",
                "US",
                "United States",
                0.0,
                0.0,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "False",
            ],
            [
                "6",
                "2020-02-22",
                "Test Same Facility Name A",
                "Address C",
                "US",
                "United States",
                0.0,
                0.0,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "False",
            ],
            [
                "7",
                "2020-02-22",
                "Test Same Facility Name A",
                "Address D",
                "US",
                "United States",
                0.0,
                0.0,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "False",
            ],
            [
                "8",
                "2020-02-22",
                "Test Same Facility Name A",
                "Address D",
                "US",
                "United States",
                0.0,
                0.0,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "False",
            ],
            [
                "9",
                "2020-02-22",
                "Test Same Facility Name B",
                "Address A",
                "US",
                "United States",
                0.0,
                0.0,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "False",
            ],
            [
                "10",
                "2020-02-22",
                "Test Same Facility Name B",
                "Address B",
                "US",
                "United States",
                0.0,
                0.0,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "False",
            ],
            [
                "11",
                "2020-02-22",
                "Test Same Facility Name B",
                "Address C",
                "US",
                "United States",
                0.0,
                0.0,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "False",
            ],
            [
                "12",
                "2020-02-22",
                "Test Same Facility Name B",
                "Address D",
                "US",
                "United States",
                0.0,
                0.0,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "False",
            ],
            [
                "13",
                "2020-02-22",
                "Test Same Facility Name B",
                "Address D",
                "US",
                "United States",
                0.0,
                0.0,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "False",
            ],
            [
                "14",
                "2020-02-22",
                "Test Same Facility Name C",
                "Address A",
                "US",
                "United States",
                0.0,
                0.0,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "False",
            ],
            [
                "15",
                "2020-02-22",
                "Test Same Facility Name C",
                "Address B",
                "US",
                "United States",
                0.0,
                0.0,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "False",
            ],
            [
                "16",
                "2020-02-22",
                "Test Same Facility Name C",
                "Address C",
                "US",
                "United States",
                0.0,
                0.0,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "False",
            ],
            [
                "17",
                "2020-02-22",
                "Test Same Facility Name C",
                "Address D",
                "US",
                "United States",
                0.0,
                0.0,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "False",
            ],
            [
                "18",
                "2020-02-22",
                "Test Same Facility Name C",
                "Address D",
                "US",
                "United States",
                0.0,
                0.0,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "False",
            ],
            [
                "3",
                "2020-02-22",
                "Third Facility",
                "Third Facility Address",
                "CN",
                "China",
                0.0,
                0.0,
                "Test Sector",
                "Factory A (Claimed)|A Service Provider|A Factory / Facility",
                "",
                "",
                "",
                "",
                "",
                "",
                "False",
            ],
        ]
        response = self.client.get(download_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rows = response.data.get("results", {}).get("rows", [])

        for expected_facility, actual_facility in zip(expected_data, rows):
            self.assertListEqual(expected_facility, actual_facility)

    def test_pagination(self):
        email = "test@example.com"
        password = "example123"
        user = User.objects.create(email=email)
        user.set_password(password)
        user.save()
        self.client.login(email=email, password=password)
        download_url = reverse("facilities-downloads-list")
        page_size = {"pageSize": 5}

        response = self.client.get(download_url, page_size)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

        expected_count = 18
        self.assertEqual(response.data.get("count"), expected_count)

        self.assertIsNone(response.data.get("previous"))

        expected_next = (
            "http://testserver/api/facilities-downloads/?page=2&pageSize=5"
        )
        self.assertEqual(response.data.get("next"), expected_next)

    def test_query_parameters(self):
        email = "test@example.com"
        password = "example123"
        user = User.objects.create(email=email)
        user.set_password(password)
        user.save()
        self.client.login(email=email, password=password)
        download_url = reverse("facilities-downloads-list")
        query_params = {"countries": "IN"}
        expected_data = [
            [
                "2",
                "2020-02-22",
                "Second Facility Name English",
                "Second Facility Address",
                "IN",
                "India",
                0.0,
                0.0,
                "Test Sector",
                "Factory A (Claimed)|A Service Provider|A Factory / Facility|"
                "Brand A",
                "101-500",
                "Parent Company Factory A",
                "Raw Data",
                "Matched facility type value one Factory A",
                "Matched processing type value one Factory A",
                "Product Type Factory A",
                "False",
            ],
        ]

        response = self.client.get(download_url, query_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rows = response.data.get("results", {}).get("rows", [])
        self.assertEqual(rows, expected_data)

    @patch('api.constants.FacilitiesDownloadSettings.DEFAULT_LIMIT',
           DEFAULT_LIMIT)
    def test_user_cannot_download_over_limit(self):
        email = "test@example.com"
        password = "example123"
        user = User.objects.create(email=email)
        user.set_password(password)
        user.save()
        self.client.login(email=email, password=password)
        download_url = reverse("facilities-downloads-list")
        expected_error = ['Downloads are supported only for searches resulting in 3 facilities or less.']

        response = self.client.get(download_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(expected_error, response.json())

    def test_api_user_can_download_over_limit(self):
        email = "test@example.com"
        password = "example123"
        user = User.objects.create(email=email)
        user.set_password(password)
        group = Group.objects.get(
            name=FeatureGroups.CAN_SUBMIT_FACILITY,
        )
        user.groups.set([group.id])
        user.save()
        self.client.login(email=email, password=password)

        download_url = reverse("facilities-downloads-list")

        response = self.client.get(download_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rows = response.data.get("results", {}).get("rows", [])
        self.assertGreater(len(rows), DEFAULT_LIMIT)
