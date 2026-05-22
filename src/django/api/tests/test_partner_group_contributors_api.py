from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Contributor, PartnerField, PartnerFieldGroup, User


class PartnerGroupContributorsAPITest(APITestCase):
    """Test cases for the partner group contributors API endpoint."""

    def setUp(self):
        self.url = "/api/partner-group-contributors/"

    def _create_group(self, name, order=0):
        return PartnerFieldGroup.objects.create(name=name, order=order)

    def _create_field(
        self,
        name,
        group,
        field_type=PartnerField.STRING,
        active=True,
        system_field=False,
    ):
        return PartnerField.objects.get_all_including_inactive().create(
            name=name,
            group=group,
            type=field_type,
            active=active,
            system_field=system_field,
        )

    def _create_contributor(self, email, name):
        admin = User.objects.create(email=email)
        return Contributor.objects.create(
            admin=admin,
            name=name,
            contrib_type="Brand / Retailer",
        )

    def _result_by_group_uuid(self, response, group):
        for result in response.data["results"]:
            if result["uuid"] == str(group.uuid):
                return result
        return None

    def _create_group_with_active_contributor(self, name, order=0):
        group = self._create_group(name, order=order)
        field = self._create_field(f"{name}_active_field", group=group)
        contributor = self._create_contributor(
            f"{name}@example.com", f"{name} Contributor"
        )
        contributor.partner_fields.add(field)
        return group, contributor

    def test_returns_200_for_unauthenticated_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_returns_groups_ordered_with_expected_shape(self):
        (
            early_group,
            early_contributor,
        ) = self._create_group_with_active_contributor(
            "Early Group",
            order=1,
        )
        (
            late_group,
            late_contributor,
        ) = self._create_group_with_active_contributor(
            "Late Group",
            order=2,
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(
            response.data["results"][0]["uuid"], str(early_group.uuid)
        )
        self.assertEqual(
            response.data["results"][1]["uuid"], str(late_group.uuid)
        )
        self.assertEqual(
            response.data["results"][0]["label"], early_group.name
        )
        self.assertEqual(response.data["results"][1]["label"], late_group.name)
        self.assertEqual(
            response.data["results"][0]["contributors"],
            [{"id": early_contributor.id, "name": early_contributor.name}],
        )
        self.assertEqual(
            response.data["results"][1]["contributors"],
            [{"id": late_contributor.id, "name": late_contributor.name}],
        )

    def test_returns_contributors_for_active_fields_in_each_group(self):
        group_one = self._create_group("Group 1", order=1)
        group_two = self._create_group("Group 2", order=2)
        field_one = self._create_field("active_field_1", group=group_one)
        field_two = self._create_field("active_field_2", group=group_two)
        contributor_one = self._create_contributor(
            "one@example.com", "Contributor One"
        )
        contributor_two = self._create_contributor(
            "two@example.com", "Contributor Two"
        )

        contributor_one.partner_fields.add(field_one)
        contributor_two.partner_fields.add(field_two)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        group_one_result = self._result_by_group_uuid(response, group_one)
        group_two_result = self._result_by_group_uuid(response, group_two)
        self.assertEqual(
            group_one_result["contributors"],
            [{"id": contributor_one.id, "name": contributor_one.name}],
        )
        self.assertEqual(
            group_two_result["contributors"],
            [{"id": contributor_two.id, "name": contributor_two.name}],
        )

    def test_deduplicates_contributors_when_linked_to_multiple_fields_in_group(
        self,
    ):
        group = self._create_group("Dedup Group", order=1)
        field_one = self._create_field("dedup_field_1", group=group)
        field_two = self._create_field("dedup_field_2", group=group)
        contributor = self._create_contributor(
            "dedup@example.com", "Dedup Contributor"
        )

        contributor.partner_fields.add(field_one, field_two)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = self._result_by_group_uuid(response, group)
        self.assertEqual(
            result["contributors"],
            [{"id": contributor.id, "name": contributor.name}],
        )

    def test_excludes_contributors_linked_only_to_inactive_fields(self):
        group = self._create_group("Inactive Group", order=1)
        inactive_field = self._create_field(
            "inactive_field",
            group=group,
            active=False,
        )
        contributor = self._create_contributor(
            "inactive@example.com", "Inactive Contributor"
        )
        contributor.partner_fields.add(inactive_field)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = self._result_by_group_uuid(response, group)
        self.assertIsNone(result)

    def test_limit_parameter_controls_number_of_returned_groups(self):
        for i in range(5):
            self._create_group_with_active_contributor(
                f"Limit Group {i}",
                order=i,
            )

        response = self.client.get(self.url, {"limit": 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertIsNotNone(response.data["next"])
