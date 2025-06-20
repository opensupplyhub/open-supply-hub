import json

from api.models import Contributor, NonstandardField, User
from rest_framework import status
from rest_framework.test import APITestCase

from django.urls import reverse


class NonstandardFieldsApiTest(APITestCase):
    def setUp(self):
        self.url = reverse("nonstandard-fields-list")
        self.user_email = "test@example.com"
        self.user_pass = "example123"
        self.user = User.objects.create(email=self.user_email)
        self.user.set_password(self.user_pass)
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
        self.client.login(email=self.user_email, password=self.user_pass)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertEqual(7, len(content))
        self.assertIn("extra_1", content)
        self.assertIn("extra_2", content)
        self.assertIn("parent_company", content)

    def test_without_nonstandard_fields(self):
        self.client.login(email=self.user_email, password=self.user_pass)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertEqual(5, len(content))
        self.assertNotIn("extra_1", content)
        self.assertNotIn("extra_2", content)
        self.assertIn("parent_company", content)
