import json

from api.constants import UpdateLocationParams
from api.models import FacilityLocation
from api.tests.test_facility_api_case_base import FacilityAPITestCaseBase

from django.urls import reverse


class UpdateLocationTest(FacilityAPITestCaseBase):
    def setUp(self):
        super(UpdateLocationTest, self).setUp()
        self.url = reverse(
            "facility-update-location", kwargs={"pk": self.facility.id}
        )

    def test_requires_auth(self):
        response = self.client.post(self.url)
        self.assertEqual(401, response.status_code)

    def test_requires_superuser(self):
        self.client.login(email=self.user_email, password=self.user_password)
        response = self.client.post(self.url)
        self.assertEqual(403, response.status_code)

    def test_facility_exists(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        self.url = reverse(
            "facility-update-location", kwargs={"pk": "DOES_NOT_EXIST"}
        )
        response = self.client.post(self.url)
        self.assertEqual(404, response.status_code)

    def test_required_arguments(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(self.url)
        self.assertEqual(400, response.status_code)
        data = json.loads(response.content)
        self.assertIn("lat", data)
        self.assertIn("lng", data)

    def test_valid_arguments(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        response = self.client.post(self.url, {"lat": 1000, "lng": 0})
        self.assertEqual(400, response.status_code)
        data = json.loads(response.content)
        self.assertIn("lat", data)
        self.assertNotIn("lng", data)

        response = self.client.post(self.url, {"lat": 0, "lng": 1000})
        self.assertEqual(400, response.status_code)
        data = json.loads(response.content)
        self.assertIn("lng", data)
        self.assertNotIn("lat", data)

    def test_updates_location(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        response = self.client.post(
            self.url,
            {
                UpdateLocationParams.LAT: 41,
                UpdateLocationParams.LNG: 43,
                UpdateLocationParams.NOTES: "A note",
                UpdateLocationParams.CONTRIBUTOR_ID: self.contributor.id,
            },
        )
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        self.assertEqual(data["id"], self.facility.id)
        self.assertEqual(data["geometry"]["coordinates"], [43.0, 41.0])

        facility_locations = FacilityLocation.objects.filter(
            facility=self.facility
        )
        self.assertTrue(facility_locations.count() == 1)
        facility_location = facility_locations.first()
        self.assertEqual(facility_location.facility, self.facility)
        self.assertEqual(facility_location.created_by, self.superuser)
        self.assertEqual(facility_location.location.x, 43.0)
        self.assertEqual(facility_location.location.y, 41.0)
        self.assertEqual(facility_location.contributor, self.contributor)
        self.assertEqual(facility_location.notes, "A note")
