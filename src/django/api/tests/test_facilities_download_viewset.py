from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import Group
from unittest.mock import patch, MagicMock

from api.models.user import User
from api.models.contributor.contributor import Contributor
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
            "http://testserver/api/facilities-downloads/?pageSize=5&page=2"
        )

    def test_query_parameters(self):
        user = self.create_user()
        self.login_user(user)

        response = self.get_facility_downloads({"countries": ["IN"]})

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

    def test_query_multi_param_next_page(self):
        user = self.create_user()
        self.login_user(user)

        response = self.get_facility_downloads({"countries": ["IN", "US"], "pageSize": 2})

        expected_root = "http://testserver/api/facilities-downloads/"
        expected_query = "?countries=IN&countries=US&pageSize=2&page=2"

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("next", ""),
            expected_root + expected_query
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
        user = self.create_user()
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

        for _ in range(5):
            response = self.get_facility_downloads()
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_is_same_contributor_true_when_all_facilities_belong_to_user(self):
        user = self.create_user()
        self.login_user(user)

        contributor = Contributor.objects.create(
            admin=user,
            name="Test Contributor",
            contrib_type="Brand / Retailer"
        )

        response = self.get_facility_downloads(
                {'contributors': [str(contributor.id)]}
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            response.data['results']['is_same_contributor']
        )

    def test_is_same_contributor_false_when_mixed_contributors(self):
        user = self.create_user()
        self.login_user(user)

        contributor = Contributor.objects.create(
            admin=user,
            name="Test Contributor",
            contrib_type="Brand / Retailer"
        )

        response = self.get_facility_downloads(
                {'contributors': [str(contributor.id), '123']}
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            response.data['results']['is_same_contributor']
        )

    def test_is_same_contributor_false_when_user_has_no_contributor(self):
        user = self.create_user()
        self.login_user(user)

        response = self.get_facility_downloads({'contributors': ['123']})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            response.data['results']['is_same_contributor']
        )

    def test_is_same_contributor_with_combine_contributors_and_logic(self):
        user = self.create_user()
        self.login_user(user)

        contributor = Contributor.objects.create(
            admin=user,
            name="Test Contributor",
            contrib_type="Brand / Retailer"
        )

        response = self.get_facility_downloads({
            'contributors': [str(contributor.id), '456'],
            'combine_contributors': 'AND'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            response.data['results']['is_same_contributor']
        )

    def test_multi_page_download_decrements_free_by_total_count(self):
        user = self.create_user()
        self.login_user(user)

        limit = FacilityDownloadLimit.objects.create(
            user=user,
            free_download_records=20,
            paid_download_records=0,
        )

        # Request first page to get the total count from the payload
        resp_page1 = self.get_facility_downloads({"pageSize": 10, "page": 1})
        self.assertEqual(resp_page1.status_code, status.HTTP_200_OK)
        total_count = resp_page1.data.get("count")
        self.assertIsNotNone(total_count)

        # Quotas should remain unchanged after first page
        limit.refresh_from_db()
        self.assertEqual(limit.free_download_records, 20)
        self.assertEqual(limit.paid_download_records, 0)

        # Request last page to trigger quota registration using total_count
        # Patch email/checkout to avoid external calls during tests
        with patch(
            'api.services.facilities_download_service.'
            'FacilitiesDownloadService.send_email_if_needed',
            return_value=None
        ):
            resp_page2 = self.get_facility_downloads({
                "pageSize": 10,
                "page": 2
            })
        self.assertEqual(resp_page2.status_code, status.HTTP_200_OK)

        limit.refresh_from_db()
        expected_free = max(20 - total_count, 0)
        self.assertEqual(limit.free_download_records, expected_free)
        self.assertEqual(limit.paid_download_records, 0)

    def test_multi_page_download_consumes_paid_when_free_insufficient(self):
        user = self.create_user()
        self.login_user(user)

        limit = FacilityDownloadLimit.objects.create(
            user=user,
            free_download_records=5,
            paid_download_records=20,
        )

        resp_page1 = self.get_facility_downloads({"pageSize": 10, "page": 1})
        self.assertEqual(resp_page1.status_code, status.HTTP_200_OK)
        total_count = resp_page1.data.get("count")
        self.assertIsNotNone(total_count)

        # Trigger decrement on last page
        with patch(
            'api.services.facilities_download_service.'
            'FacilitiesDownloadService.send_email_if_needed',
            return_value=None
        ):
            resp_page2 = self.get_facility_downloads({
                "pageSize": 10,
                "page": 2
            })
        self.assertEqual(resp_page2.status_code, status.HTTP_200_OK)

        limit.refresh_from_db()
        self.assertEqual(limit.free_download_records, 0)
        expected_paid = max(20 - max(total_count - 5, 0), 0)
        self.assertEqual(limit.paid_download_records, expected_paid)

    def test_exhausted_quota_all_mine_still_allowed(self):
        user = self.create_user()
        self.login_user(user)

        contributor = Contributor.objects.create(
            admin=user,
            name="Test Contributor",
            contrib_type="Brand / Retailer"
        )

        limit = FacilityDownloadLimit.objects.create(
            user=user,
            free_download_records=0,
            paid_download_records=0,
        )

        with patch(
            'api.services.facilities_download_service.'
            'FacilitiesDownloadService.get_filtered_queryset'
        ) as mock_get_queryset:
            mock_queryset = MagicMock()
            mock_facility = MagicMock()
            mock_facility.contributors = [{'id': contributor.id}]
            mock_queryset.__iter__.return_value = [mock_facility]
            mock_queryset.count.return_value = 1
            mock_get_queryset.return_value = mock_queryset

            resp = self.get_facility_downloads({
                'contributors': [str(contributor.id)]
            })
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            # Quotas must remain unchanged since it's an own-data download
            limit.refresh_from_db()
            self.assertEqual(limit.free_download_records, 0)
            self.assertEqual(limit.paid_download_records, 0)
