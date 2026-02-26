"""
Tests for the PartnerFieldGroupsViewSet.
"""

from rest_framework import status
from rest_framework.test import APITestCase

from api.models.partner_field import PartnerField
from api.models.partner_field_group import PartnerFieldGroup


class PartnerFieldGroupsViewSetTest(APITestCase):
    """
    Test cases for the partner field groups API endpoint.
    """

    def setUp(self):
        self.url = "/api/partner-field-groups/"

    def _create_partner_field_group(self, name, order=0):
        """Helper to create a partner field group."""
        return PartnerFieldGroup.objects.create(
            name=name,
            order=order,
        )

    def _create_partner_field(
        self,
        name,
        group=None,
        field_type=PartnerField.STRING,
        active=True,
        system_field=False,
    ):
        """Helper to create a partner field."""
        return PartnerField.objects.get_all_including_inactive().create(
            name=name,
            group=group,
            type=field_type,
            active=active,
            system_field=system_field,
        )

    def test_returns_200_for_all_users(self):
        """Verify endpoint returns 200 for all users."""
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_returns_partner_field_groups(self):
        """Verify endpoint returns paginated partner field groups."""
        groups = [
            self._create_partner_field_group("Group 1", 1),
            self._create_partner_field_group("Group 2", 2),
        ]
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 2)

        result_uuids = [result["uuid"] for result in response.data["results"]]
        for group in groups:
            self.assertIn(str(group.uuid), result_uuids)

    def test_limit_parameter_controls_page_size(self):
        """Verify ?limit= parameter controls page size."""
        for i in range(5):
            self._create_partner_field_group(f"limit_test_group_{i}")

        limit = 2
        response = self.client.get(self.url, {"limit": limit})

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data["results"]), limit)

    def test_ordering_is_respected(self):
        """Verify partner field groups are ordered by 'order' field."""
        groups = [
            self._create_partner_field_group("Group 1", 1),
            self._create_partner_field_group("Group 3", 3),
            self._create_partner_field_group("Group 2", 2),
        ]
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data["results"]
        self.assertEqual(len(results), len(groups))
        response_uuids = [result["uuid"] for result in results]

        sorted_groups = sorted(groups, key=lambda group: group.order)
        sorted_uuids = [str(group.uuid) for group in sorted_groups]

        for sorted_uuid, response_uuid in zip(
            sorted_uuids, response_uuids, strict=True
        ):
            self.assertEqual(sorted_uuid, response_uuid)

    def test_returns_partner_fields_in_group(self):
        """Verify partner fields are returned in the group."""
        group = self._create_partner_field_group("Test Group")
        fields = [
            self._create_partner_field("Field 1", group=group),
            self._create_partner_field("Field 2", group=group),
        ]

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        (result,) = response.data["results"]
        self.assertEqual(result["uuid"], str(group.uuid))
        self.assertIn("partner_fields", result)
        self.assertEqual(len(result["partner_fields"]), len(fields))

        for field in fields:
            self.assertIn(field.name, result["partner_fields"])

    def test_cant_create_partner_field_groups(self):
        """Verify partner field groups can't be created via API."""
        response = self.client.post(
            self.url,
            {"name": "New Group"},
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
