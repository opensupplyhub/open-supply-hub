from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import Group
from unittest.mock import patch

from api.models.user import User
from api.constants import FeatureGroups
from api.models.facility_download_limit import FacilityDownloadLimit
from django.utils import timezone
from django.utils.timezone import make_aware, datetime

# Override constants different from production value for easier testing.
FREE_FACILITIES_DOWNLOAD_LIMIT = 3


class FacilitiesDownloadViewSetTest(APITestCase):
    fixtures = ["facilities_index"]

    def setUp(self):
        self.download_url = reverse("facilities-downloads-list")
        self.email = "test@example.com"
        self.test_pass = "example123"

    def create_user(self, is_api_user=False):
        user = User.objects.create(email=self.email)
        user.set_password(self.test_pass)
        user.save()

        if is_api_user:
            group = Group.objects.get(name=FeatureGroups.CAN_SUBMIT_FACILITY)
            user.groups.add(group)

        return user

    def login_user(self, user):
        self.client.login(email=user.email, password=self.test_pass)

    def get_facility_downloads(self, params=None):
        return self.client.get(self.download_url, params or {})

    def test_queryset_ordering(self):
        user = self.create_user()
        self.login_user(user)

        response = self.get_facility_downloads()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
        actual_data = response.data.get("results", {}).get("rows", [])

        for expected, actual in zip(expected_data, actual_data):
            self.assertListEqual(expected, actual)

    def test_pagination(self):
        user = self.create_user()
        self.login_user(user)

        response = self.get_facility_downloads({"pageSize": 5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), 18)
        self.assertIsNone(response.data.get("previous"))
        self.assertEqual(
            response.data.get("next"),
            "http://testserver/api/facilities-downloads/?page=2&pageSize=5"
        )

    def test_query_parameters(self):
        user = self.create_user()
        self.login_user(user)

        response = self.get_facility_downloads({"countries": "IN"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
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

        self.assertEqual(
            response.data.get("results", {}).get("rows", []),
            expected_data
        )

    @patch(
        'api.constants.FacilitiesDownloadSettings.'
        'FREE_FACILITIES_DOWNLOAD_LIMIT',
        FREE_FACILITIES_DOWNLOAD_LIMIT,
    )
    def test_user_cannot_download_over_records_limit(self):
        user = self.create_user()
        self.login_user(user)
        FacilityDownloadLimit.objects.create(
            user=user,
            free_download_records=FREE_FACILITIES_DOWNLOAD_LIMIT,
            paid_download_records=1
        )
        response = self.get_facility_downloads()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            [('Downloads are supported only for searches '
              'resulting in 4 facilities or less.')]
        )

    def test_new_user_has_current_date_in_updated_at(self):
        user = self.create_user()
        self.login_user(user)

        limit = FacilityDownloadLimit.objects.create(
            user=user
        )
        current_date = timezone.now()

        self.assertEqual(limit.updated_at.date(), current_date.date())

    def test_old_user_has_release_date_in_updated_at(self):
        # The record has been added to FacilityDownloadLimit.
        user = self.create_user()
        # Simulation old user.
        FacilityDownloadLimit.objects.filter(user=user).delete()
        self.login_user(user)
        release_date = make_aware(datetime(2025, 7, 12))

        limit = FacilityDownloadLimit \
            .get_or_create_user_download_limit(
                user,
                release_date
            )

        self.assertEqual(limit.updated_at.date(), release_date.date())

    @patch(
        'api.constants.FacilitiesDownloadSettings.'
        'FREE_FACILITIES_DOWNLOAD_LIMIT',
        FREE_FACILITIES_DOWNLOAD_LIMIT,
    )
    def test_api_user_can_download_over_limit(self):
        user = self.create_user(is_api_user=True)
        self.login_user(user)

        response = self.get_facility_downloads()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(
            len(response.data.get("results", {}).get("rows", [])),
            FREE_FACILITIES_DOWNLOAD_LIMIT
        )

    def test_api_user_not_limited_by_download_count(self):
        user = self.create_user(is_api_user=True)
        self.login_user(user)

        # Make multiple downloads that would exceed the limit for regular
        # users.
        for _ in range(5):
            response = self.get_facility_downloads()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
