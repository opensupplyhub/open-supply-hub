import json

from api.models import Contributor, ExtendedField, NonstandardField, User
from rest_framework import status
from rest_framework.test import APITestCase

from django.urls import reverse


class NonstandardFieldsApiTest(APITestCase):
    def setUp(self):
        self.url = reverse("nonstandard-fields-list")
        self.user_email = "test@example.com"
        self.user_password = "example123"
        self.user = User.objects.create(email=self.user_email)
        self.user.set_password(self.user_password)
        self.user.save()

        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="test contributor 1",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

    def _add_extended_field(self, field_name):
        return ExtendedField.objects.create(
            contributor=self.contributor,
            field_name=field_name,
            value={"raw_value": "x"},
        )

    def _get_fields(self):
        self.client.login(email=self.user_email, password=self.user_password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return json.loads(response.content)

    def test_nonstandard_fields(self):
        NonstandardField.objects.create(
            column_name="extra_1", contributor=self.contributor
        )
        NonstandardField.objects.create(
            column_name="extra_2", contributor=self.contributor
        )
        self._add_extended_field("parent_company")

        self.assertEqual(
            ["extra_1", "extra_2", "parent_company"], self._get_fields()
        )

    def test_without_any_fields(self):
        """A contributor with no data for any field is offered none."""
        self.assertEqual([], self._get_fields())

    def test_standard_field_is_only_listed_with_data(self):
        self._add_extended_field("processing_type")
        self._add_extended_field("processing_type")

        content = self._get_fields()
        self.assertEqual(["processing_type"], content)
        self.assertNotIn("parent_company", content)

    def test_other_contributors_data_is_not_listed(self):
        other_user = User.objects.create(email="other@example.com")
        other = Contributor.objects.create(
            admin=other_user,
            name="test contributor 2",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        NonstandardField.objects.create(
            column_name="extra_3", contributor=other
        )
        ExtendedField.objects.create(
            contributor=other,
            field_name="facility_type",
            value={"raw_value": "x"},
        )

        self.assertEqual([], self._get_fields())
