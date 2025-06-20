import json

from api.models import Contributor, FacilityListItem
from api.tests.test_facility_api_case_base import FacilityAPITestCaseBase

from django.urls import reverse


class ContributorTypesTest(FacilityAPITestCaseBase):
    def get_contributor_types(self):
        return self.client.get(reverse("all_contributor_types"))

    def fetch_and_assert_all_counts_are_zero(self):
        response = self.get_contributor_types()
        data = json.loads(response.content)
        for id, label in data:
            self.assertEqual(id, label)

    def test_all_types_are_returned(self):
        response = self.get_contributor_types()
        data = json.loads(response.content)
        self.assertEqual(len(Contributor.CONTRIB_TYPE_CHOICES), len(data))

    def test_only_public_sources_are_counted(self):
        self.source.is_public = False
        self.source.save()
        self.fetch_and_assert_all_counts_are_zero()

    def test_only_active_sources_are_counted(self):
        self.source.is_active = False
        self.source.save()
        self.fetch_and_assert_all_counts_are_zero()

    def test_only_confirmed_items_are_counted(self):
        self.list_item.status = FacilityListItem.GEOCODED
        self.list_item.save()
        self.fetch_and_assert_all_counts_are_zero()
