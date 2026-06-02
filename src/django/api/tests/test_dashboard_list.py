from api.models import FacilityList, Source
from api.tests.base_facility_list_test import BaseFacilityListTest


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

    def test_pending_filter_excludes_replaced_lists(self):
        replacement = FacilityList.objects.create(
            header="header",
            file_name="replacement.csv",
            name="Replacement List",
            replaces=self.list,
        )
        Source.objects.create(
            source_type=Source.LIST,
            facility_list=replacement,
            contributor=self.contributor,
        )

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.get(
            "/api/admin-facility-lists/?status={}".format(FacilityList.PENDING)
        )

        self.assertEqual(200, response.status_code)
        names = [d["name"] for d in response.json()["results"]]
        self.assertNotIn(
            "First List",
            names,
            "A PENDING list that has been replaced must not appear in the "
            "Pending filter.",
        )

    def test_approved_filter_excludes_replaced_lists(self):
        self.list.status = FacilityList.APPROVED
        self.list.save()

        replacement = FacilityList.objects.create(
            header="header",
            file_name="replacement.csv",
            name="Replacement List",
            replaces=self.list,
        )
        Source.objects.create(
            source_type=Source.LIST,
            facility_list=replacement,
            contributor=self.contributor,
        )
        self.source.is_active = False
        self.source.save()

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.get(
            "/api/admin-facility-lists/?status={}".format(FacilityList.APPROVED)
        )

        self.assertEqual(200, response.status_code)
        names = [d["name"] for d in response.json()["results"]]
        self.assertNotIn(
            "First List",
            names,
            "An APPROVED list that has been replaced must not appear in the "
            "Approved filter.",
        )

    def test_pending_filter_excludes_inactive_pending_lists(self):
        self.source.is_active = False
        self.source.save()

        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.get(
            "/api/admin-facility-lists/?status={}".format(FacilityList.PENDING)
        )

        self.assertEqual(200, response.status_code)
        names = [d["name"] for d in response.json()["results"]]
        self.assertNotIn(
            "First List",
            names,
            "A PENDING list with is_active=False (broken replacement link) "
            "must not appear in the Pending filter.",
        )

    def test_pending_filter_includes_non_replaced_pending_lists(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.get(
            "/api/admin-facility-lists/?status={}".format(FacilityList.PENDING)
        )

        self.assertEqual(200, response.status_code)
        names = [d["name"] for d in response.json()["results"]]
        self.assertIn(
            "First List",
            names,
            "A PENDING list with no replacement must still appear in the "
            "Pending filter.",
        )
