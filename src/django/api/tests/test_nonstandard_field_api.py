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

    def test_nonstandard_fields(self):
        NonstandardField.objects.create(
            column_name="extra_1", contributor=self.contributor
        )
        NonstandardField.objects.create(
            column_name="extra_2", contributor=self.contributor
        )
        self.client.login(email=self.user_email, password=self.user_password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertEqual(7, len(content))
        self.assertIn("extra_1", content)
        self.assertIn("extra_2", content)
        self.assertIn("parent_company", content)

    def test_without_nonstandard_fields(self):
        self.client.login(email=self.user_email, password=self.user_password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertEqual(5, len(content))
        self.assertNotIn("extra_1", content)
        self.assertNotIn("extra_2", content)
        self.assertIn("parent_company", content)

    # ------------------------------------------------------------------ #
    # ?detail=true: which fields the contributor has data for             #
    # ------------------------------------------------------------------ #
    STANDARD_FIELDS = sorted(NonstandardField.EXTENDED_FIELDS.keys())

    def _add_extended_field(self, field_name, contributor=None):
        return ExtendedField.objects.create(
            contributor=contributor or self.contributor,
            field_name=field_name,
            value={"raw_value": "x"},
        )

    def _get_detail(self):
        self.client.login(email=self.user_email, password=self.user_password)
        response = self.client.get(self.url + "?detail=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return json.loads(response.content)

    def test_detail_lists_every_field_and_marks_those_with_data(self):
        NonstandardField.objects.create(
            column_name="extra_1", contributor=self.contributor
        )
        self._add_extended_field("processing_type")
        self._add_extended_field("processing_type")

        content = self._get_detail()
        self.assertEqual(
            sorted(self.STANDARD_FIELDS + ["extra_1"]), content["fields"]
        )
        self.assertEqual(["extra_1", "processing_type"], content["with_data"])

    def test_detail_without_any_data(self):
        """The standard fields are still listed; none is marked."""
        content = self._get_detail()
        self.assertEqual(self.STANDARD_FIELDS, content["fields"])
        self.assertEqual([], content["with_data"])

    def test_detail_ignores_other_contributors_data(self):
        other_user = User.objects.create(email="other@example.com")
        other = Contributor.objects.create(
            admin=other_user,
            name="test contributor 2",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        NonstandardField.objects.create(
            column_name="extra_3", contributor=other
        )
        self._add_extended_field("facility_type", contributor=other)

        content = self._get_detail()
        self.assertEqual(self.STANDARD_FIELDS, content["fields"])
        self.assertEqual([], content["with_data"])
