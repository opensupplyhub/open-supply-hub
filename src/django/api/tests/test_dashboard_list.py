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
            "/api/admin-facility-lists/?status={}".format(
                FacilityList.APPROVED
            )
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

    def test_pending_filter_excludes_approved_lists(self):
        self.list.status = FacilityList.APPROVED
        self.list.save()

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
            "An APPROVED list must not appear in the Pending filter.",
        )

    def test_approved_filter_excludes_pending_lists(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.get(
            "/api/admin-facility-lists/?status={}".format(
                FacilityList.APPROVED
            )
        )

        self.assertEqual(200, response.status_code)
        names = [d["name"] for d in response.json()["results"]]
        self.assertNotIn(
            "First List",
            names,
            "A PENDING list must not appear in the Approved filter.",
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

    def test_default_ordering_is_created_at_ascending(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.get("/api/admin-facility-lists/")

        self.assertEqual(200, response.status_code)
        created_ats = [
            item["created_at"] for item in response.json()["results"]
        ]
        self.assertEqual(sorted(created_ats), created_ats)

    def test_ordering_by_id(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.get(
            "/api/admin-facility-lists/?ordering=id"
        )

        self.assertEqual(200, response.status_code)
        ids = [item["id"] for item in response.json()["results"]]
        self.assertEqual(sorted(ids), ids)

    def test_ordering_by_negative_id(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.get(
            "/api/admin-facility-lists/?ordering=-id"
        )

        self.assertEqual(200, response.status_code)
        ids = [item["id"] for item in response.json()["results"]]
        self.assertEqual(sorted(ids, reverse=True), ids)

    def test_returns_contributor_name_and_email(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.get(
            "/api/admin-facility-lists/?contributor={}".format(
                self.contributor.id
            )
        )

        self.assertEqual(200, response.status_code)

        for item in response.json()["results"]:
            self.assertEqual(self.contributor.id, item["contributor_id"])
            self.assertEqual(self.contributor.name, item["contributor_name"])
            self.assertEqual(self.user_email, item["contributor_email"])

    def test_id_gt_filter_excludes_earlier_lists(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        first_list_id = self.list.id

        response = self.client.get(
            "/api/admin-facility-lists/?id__gt={}&ordering=id".format(
                first_list_id
            )
        )

        self.assertEqual(200, response.status_code)
        ids = [item["id"] for item in response.json()["results"]]
        self.assertNotIn(first_list_id, ids)
        self.assertTrue(all(list_id > first_list_id for list_id in ids))

    def test_id_gt_filter_is_optional(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.get("/api/admin-facility-lists/")

        self.assertEqual(200, response.status_code)
        self.assertEqual(4, len(response.json()["results"]))
