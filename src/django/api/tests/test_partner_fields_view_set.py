"""
Tests for the PartnerFieldsViewSet.
"""

from rest_framework import status
from rest_framework.test import APITestCase

from api.models import User
from api.models.partner_field import PartnerField


class PartnerFieldsViewSetTest(APITestCase):
    """
    Test cases for the partner fields API endpoint.
    """

    def setUp(self):
        self.user_email = "user@example.com"
        self.user_password = "password123"
        self.user = User.objects.create(email=self.user_email)
        self.user.set_password(self.user_password)
        self.user.save()

        self.superuser_email = "superuser@example.com"
        self.superuser_password = "superuser123"
        self.superuser = User.objects.create_superuser(
            self.superuser_email, self.superuser_password
        )

        self.url = "/api/partner-fields/"

    def _login_superuser(self):
        """Helper to login as superuser."""
        self.client.login(
            email=self.superuser_email,
            password=self.superuser_password,
        )

    def _login_user(self):
        """Helper to login as user."""
        self.client.login(
            email=self.user_email,
            password=self.user_password,
        )

    def _get_field_uuids(self, response):
        """Helper to get field uuids from response."""
        return [result["uuid"] for result in response.data["results"]]

    def _create_partner_field(
        self,
        name,
        field_type=PartnerField.STRING,
        active=True,
        system_field=False,
    ):
        """Helper to create a partner field."""
        return PartnerField.objects.get_all_including_inactive().create(
            name=name,
            type=field_type,
            active=active,
            system_field=system_field,
        )

    def test_returns_401_for_unauthenticated_request(self):
        """Verify endpoint returns 401 for unauthenticated requests."""
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_returns_403_for_non_superuser(self):
        """Verify endpoint returns 403 for non-superuser requests."""
        self._login_user()
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_returns_200_for_superuser(self):
        """Verify endpoint returns 200 for superuser requests."""
        self._login_superuser()
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_returns_partner_fields_for_superuser(self):
        """Verify endpoint returns paginated partner fields for superusers."""
        fields = [
            self._create_partner_field("test_field_1"),
            self._create_partner_field("test_field_2", PartnerField.INT),
        ]
        self._login_superuser()
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("results", response.data)

        result_uuids = self._get_field_uuids(response)

        for field in fields:
            self.assertIn(str(field.uuid), result_uuids)

    def test_limit_parameter_controls_page_size(self):
        """Verify ?limit= parameter controls page size."""
        for i in range(5):
            self._create_partner_field(f"limit_test_field_{i}")

        self._login_superuser()
        response = self.client.get(self.url, {"limit": 2})

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data["results"]), 2)

    def test_cursor_pagination_works_correctly(self):
        """Verify cursor pagination returns different results on next page."""
        for i in range(5):
            self._create_partner_field(f"cursor_test_field_{i}")

        self._login_superuser()

        first_response = self.client.get(self.url, {"limit": 2})
        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        first_page_uuids = self._get_field_uuids(first_response)

        next_url = first_response.data["next"]
        self.assertIsNotNone(next_url)

        second_response = self.client.get(next_url)
        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )
        second_page_uuids = self._get_field_uuids(second_response)

        self.assertTrue(
            set(first_page_uuids).isdisjoint(
                set(second_page_uuids),
            ),
        )

    def test_only_active_fields_are_returned(self):
        """Verify only active partner fields are returned."""
        active_field = self._create_partner_field(
            "active_field",
            active=True,
        )
        inactive_field = self._create_partner_field(
            "inactive_field",
            active=False,
        )

        self._login_superuser()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result_uuids = self._get_field_uuids(response)

        self.assertIn(str(active_field.uuid), result_uuids)
        self.assertNotIn(str(inactive_field.uuid), result_uuids)

    def test_max_page_size_is_enforced(self):
        """Verify max page size (100) is enforced."""
        for i in range(105):
            self._create_partner_field(f"max_size_test_field_{i}")

        self._login_superuser()
        response = self.client.get(self.url, {"limit": 200})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data["results"]), 100)

    def test_cant_update_partner_fields(self):
        """Verify partner fields can't be updated."""
        field = self._create_partner_field("test_field")
        self._login_superuser()
        response = self.client.put(
            f"{self.url}{field.uuid}/",
            {"name": "new_name"},
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_cant_delete_partner_fields(self):
        """Verify partner fields can't be deleted."""
        field = self._create_partner_field("test_field")
        self._login_superuser()
        response = self.client.delete(f"{self.url}{field.uuid}/")
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_cant_create_partner_fields(self):
        """Verify partner fields can't be created."""
        self._login_superuser()
        response = self.client.post(self.url, {"name": "new_field"})
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
