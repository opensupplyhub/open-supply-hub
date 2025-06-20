from api.tests.test_base_facility_list import BaseFacilityListTest


class DashboardListTest(BaseFacilityListTest):
    def test_superuser_can_list_all_lists(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.get("/api/admin-facility-lists/")

        self.assertEqual(200, response.status_code)

        lists = response.json()

        # Ensure we get the all lists
        self.assertEqual(4, len(lists["results"]))

    def test_superuser_can_list_other_contributors_lists(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.get(
            "/api/admin-facility-lists/?contributor={}".format(
                self.contributor.id
            )
        )

        self.assertEqual(200, response.status_code)

        lists = response.json()

        # Ensure we get all three lists, private and public,
        # active and inactive
        self.assertEqual(3, len(lists["results"]))
        self.assertEqual(
            ["First List", "Second List", "Third List"],
            [d["name"] for d in lists["results"]],
        )

    def test_user_cannot_list_other_contributors_lists(self):
        # Regular users cannot access this endpoint

        self.client.login(email=self.user_email, password=self.user_password)
        response = self.client.get(
            "/api/admin-facility-lists/?contributor={}".format(
                self.supercontributor.id
            )
        )

        self.assertEqual(403, response.status_code)
