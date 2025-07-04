from api.models import User
from rest_framework.test import APITestCase
from api.constants import FacilitiesDownloadSettings
from api.models.facility_download_limit import FacilityDownloadLimit


class UserSerializerTest(APITestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.test_pass = "example123"
        self.user = User.objects.create(email=self.email)
        self.user.set_password(self.test_pass)
        self.user.save()
        self.client.login(email=self.email, password=self.test_pass)

    def test_get_default_allowed_records_number(self):
        response = self.client.post(
            "/user-login/",
            {'email': self.email, 'password': self.test_pass},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["allowed_records_number"],
            FacilitiesDownloadSettings.FREE_FACILITIES_DOWNLOAD_LIMIT
        )

    def test_get_free_records_number(self):
        FacilityDownloadLimit.objects.create(user=self.user)
        response = self.client.post(
            "/user-login/",
            {'email': self.email, 'password': self.test_pass},
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        number_from_db = response.json()["allowed_records_number"]

        self.assertEqual(
            number_from_db,
            FacilitiesDownloadSettings.FREE_FACILITIES_DOWNLOAD_LIMIT
        )
