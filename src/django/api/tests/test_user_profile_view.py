import json
from api.models import (
    FacilityList,
    Source,
)
from api.tests.test_base_facility_list import BaseFacilityListTest


class UserProfileViewTest(BaseFacilityListTest):
    def test_user_profile_with_pending_list(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.get("/user-profile/{}/".format(self.user.id))

        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        # Ensure we get the zero list
        self.assertEqual(0, len(data["facility_lists"]))

    def test_user_profile_with_approved_list(self):
        approved_list = FacilityList.objects.create(
            header="header",
            file_name="one",
            name="Approved List",
            status=FacilityList.APPROVED
        )

        Source.objects.create(
            source_type=Source.LIST,
            facility_list=approved_list,
            is_public=True,
            contributor=self.contributor,
        )

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.get("/user-profile/{}/".format(self.user.id))

        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        # Ensure we get the one list
        self.assertEqual(1, len(data["facility_lists"]))

    def test_user_profile_with_rejected_list(self):
        rejected_list = FacilityList.objects.create(
            header="header",
            file_name="one",
            name="Rejected List",
            status=FacilityList.REJECTED
        )

        Source.objects.create(
            source_type=Source.LIST,
            facility_list=rejected_list,
            is_public=True,
            contributor=self.contributor,
        )

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.get("/user-profile/{}/".format(self.user.id))

        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        # Ensure we get the zero list
        self.assertEqual(0, len(data["facility_lists"]))
