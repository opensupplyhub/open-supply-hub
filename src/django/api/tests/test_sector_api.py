import json
from datetime import timedelta

from api.constants import FacilityClaimStatuses
from api.models import (
    Contributor,
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.models.facility.facility_index import FacilityIndex
from api.serializers.facility.facility_index_details_serializer import (
    FacilityIndexDetailsSerializer,
)
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase

from django.contrib.gis.geos import Point
from django.urls import reverse
from django.utils import timezone


class SectorAPITest(FacilityAPITestCaseBase):
    fixtures = ["sectors"]

    def setUp(self):
        super(SectorAPITest, self).setUp()
        self.url = reverse("facility-list")

    def test_search(self):
        self.join_group_and_login()

        response = self.client.get(
            self.url + '?detail=true'
        )
        data = json.loads(response.content)

        self.assertEqual(data['count'], 1)
        self.assertEqual(data['features'][0]['id'], self.facility.id)
        self.assertEqual(len(data['features'][0]['properties']['sector']), 1)
        self.assertEqual(data['features'][0]['properties']
                         ['sector'][0]['values'],
                         ['Apparel'])

    def test_search_without_detail(self):
        self.join_group_and_login()

        response = self.client.get(
            self.url
        )
        data = json.loads(response.content)

        self.assertEqual(data['count'], 1)
        self.assertEqual(data['features'][0]['id'], self.facility.id)
        self.assertNotIn('sector', data['features'][0]['properties'])


class SectorSearchIndexAlignmentTest(FacilityAPITestCaseBase):
    """
    Regression tests for OSDEV-992: the searchable FacilityIndex.sector
    column must contain only the sectors shown on the location profile,
    which displays one list item per contributor plus approved claim
    sectors.
    """

    fixtures = ["sectors"]

    def setUp(self):
        super(SectorSearchIndexAlignmentTest, self).setUp()
        self.url = reverse("facility-list")

    def _create_matched_item(self, source, sector, row_index,
                             updated_at=None):
        item = FacilityListItem.objects.create(
            name="Item {}".format(row_index),
            address="Address",
            country_code="US",
            sector=sector,
            row_index=row_index,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
            facility=self.facility,
        )
        FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility,
            facility_list_item=item,
            confidence=0.85,
            results="",
        )
        if updated_at is not None:
            # Bypass auto_now to control the ordering; the database UPDATE
            # trigger still refreshes FacilityIndex.
            FacilityListItem.objects.filter(id=item.id).update(
                updated_at=updated_at
            )
        return item

    def _create_second_contributor_source(self, is_active=True):
        user = User.objects.create(email="test2@example.com")
        contributor = Contributor.objects.create(
            admin=user,
            name="test contributor 2",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        facility_list = FacilityList.objects.create(
            header="header", file_name="two", name="Second List"
        )
        return Source.objects.create(
            facility_list=facility_list,
            source_type=Source.LIST,
            is_active=is_active,
            is_public=True,
            contributor=contributor,
        )

    def _search_ids(self, sector):
        response = self.client.get(self.url + "?sectors=" + sector)
        data = json.loads(response.content)
        return [feature["id"] for feature in data["features"]]

    def test_superseded_sector_of_same_contributor_is_not_searchable(self):
        # An older item of the same contributor no longer shown on the
        # profile must not keep its sectors searchable.
        self._create_matched_item(
            self.source,
            ["Toys"],
            row_index=2,
            updated_at=timezone.now() - timedelta(days=1),
        )

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertIn("Apparel", facility_index.sector)
        self.assertNotIn("Toys", facility_index.sector)

        self.assertEqual([], self._search_ids("Toys"))
        self.assertEqual([self.facility.id], self._search_ids("Apparel"))

    def test_latest_sector_of_same_contributor_is_searchable(self):
        # The newest item of a contributor is the one the profile shows, so
        # its sectors replace the older item's sectors in the search index.
        self._create_matched_item(self.source, ["Toys"], row_index=2)

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertIn("Toys", facility_index.sector)
        self.assertNotIn("Apparel", facility_index.sector)

        self.assertEqual([self.facility.id], self._search_ids("Toys"))
        self.assertEqual([], self._search_ids("Apparel"))

    def test_sectors_of_all_contributors_are_searchable(self):
        # Each contributor's displayed item contributes its sectors.
        source_two = self._create_second_contributor_source()
        self._create_matched_item(source_two, ["Toys"], row_index=2)

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertIn("Apparel", facility_index.sector)
        self.assertIn("Toys", facility_index.sector)

        self.assertEqual([self.facility.id], self._search_ids("Toys"))
        self.assertEqual([self.facility.id], self._search_ids("Apparel"))

    def test_active_source_preferred_over_newer_inactive_source(self):
        # The profile prefers items from active sources, so a newer item
        # whose source was deactivated must not override the active one.
        inactive_source = Source.objects.create(
            facility_list=FacilityList.objects.create(
                header="header", file_name="two", name="Second List"
            ),
            source_type=Source.LIST,
            is_active=False,
            is_public=True,
            contributor=self.contributor,
        )
        self._create_matched_item(inactive_source, ["Toys"], row_index=2)

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertIn("Apparel", facility_index.sector)
        self.assertNotIn("Toys", facility_index.sector)

        self.assertEqual([], self._search_ids("Toys"))
        self.assertEqual([self.facility.id], self._search_ids("Apparel"))

    def test_search_index_matches_profile_display_parity(self):
        # Parity guard: the searchable FacilityIndex.sector column and the
        # profile's sector field are computed by two separate
        # implementations (index_sector() in SQL, get_sector() in Python).
        # Build one facility exercising every selection rule - superseded
        # items, a second contributor, an inactive source, and an approved
        # claim - and assert both implementations produce the same values.
        # If display logic changes without index_sector(), this fails.
        self._create_matched_item(
            self.source, ["Toys", "Footwear"], row_index=2
        )

        source_two = self._create_second_contributor_source()
        self._create_matched_item(source_two, ["Electronics"], row_index=3)
        inactive_source_two = Source.objects.create(
            facility_list=FacilityList.objects.create(
                header="header", file_name="three", name="Third List"
            ),
            source_type=Source.LIST,
            is_active=False,
            is_public=True,
            contributor=source_two.contributor,
        )
        self._create_matched_item(
            inactive_source_two, ["Mining"], row_index=4
        )

        FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            contact_person="test",
            sector=["Health"],
            status=FacilityClaimStatuses.APPROVED,
        )

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        serialized = FacilityIndexDetailsSerializer(facility_index).data
        displayed = {
            value
            for entry in serialized["properties"]["sector"]
            for value in entry["values"]
        }

        self.assertTrue(displayed)
        self.assertEqual(displayed, set(facility_index.sector))

    def test_approved_claim_sectors_are_searchable(self):
        FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            contact_person="test",
            sector=["Toys"],
            status=FacilityClaimStatuses.APPROVED,
        )

        facility_index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertIn("Toys", facility_index.sector)
        self.assertIn("Apparel", facility_index.sector)

        self.assertEqual([self.facility.id], self._search_ids("Toys"))
