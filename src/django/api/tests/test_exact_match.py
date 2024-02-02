from api.matching import sort_exact_matches
from api.models import Contributor, User
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase

from django.utils import timezone


class ExactMatchTest(FacilityAPITestCaseBase):
    def setUp(self):
        super(ExactMatchTest, self).setUp()
        self.contributor = Contributor.objects.first()

        self.email = "test2@example.com"
        self.password = "password"
        self.name = "Test User 2"
        self.user = User(email=self.email)
        self.user.set_password(self.password)
        self.user.save()
        self.contributor_2 = Contributor.objects.create(
            name=self.name, admin=self.user
        )

        self.active_item_ids = [1, 2, 4]
        self.contributor.save()

    def test_sorting_match_contrib(self):
        matches = [
            {
                "id": 1,
                "facility_id": 1,
                "source__contributor_id": self.contributor_2.id,
                "updated_at": timezone.now(),
            },
            {
                "id": 2,
                "facility_id": 2,
                "source__contributor_id": self.contributor.id,
                "updated_at": timezone.now(),
            },
        ]
        results = sort_exact_matches(
            matches, self.active_item_ids, self.contributor
        )
        self.assertEqual(results[0]["facility_id"], 2)
        self.assertEqual(results[1]["facility_id"], 1)

    def test_sorting_active(self):
        matches = [
            {
                "id": 1,
                "facility_id": 3,
                "source__contributor_id": self.contributor.id,
                "updated_at": timezone.now(),
            },
            {
                "id": 1,
                "facility_id": 1,
                "source__contributor_id": self.contributor.id,
                "updated_at": timezone.now(),
            },
        ]
        results = sort_exact_matches(
            matches, self.active_item_ids, self.contributor
        )
        self.assertEqual(results[0]["facility_id"], 1)
        self.assertEqual(results[1]["facility_id"], 3)

    def test_sorting_newest(self):
        matches = [
            {
                "id": 1,
                "facility_id": 2,
                "source__contributor_id": self.contributor.id,
                "updated_at": timezone.now().replace(year=2020),
            },
            {
                "id": 1,
                "facility_id": 1,
                "source__contributor_id": self.contributor.id,
                "updated_at": timezone.now(),
            },
        ]
        results = sort_exact_matches(
            matches, self.active_item_ids, self.contributor
        )
        self.assertEqual(results[0]["facility_id"], 1)
        self.assertEqual(results[1]["facility_id"], 2)
