import json

from api.constants import FeatureGroups
from api.models import (
    Contributor,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase

from django.contrib import auth
from django.contrib.gis.geos import Point
from django.urls import reverse


class FacilitySearchContributorTest(FacilityAPITestCaseBase):
    def setUp(self):
        super(FacilitySearchContributorTest, self).setUp()
        self.url = reverse("facility-list")
        self.private_user = User.objects.create(email="shh@hush.com")
        self.private_user_password = "shhh"
        self.private_user.set_password(self.private_user_password)
        self.private_user.groups.set(
            auth.models.Group.objects.filter(
                name__in=[
                    FeatureGroups.CAN_SUBMIT_FACILITY,
                    FeatureGroups.CAN_SUBMIT_PRIVATE_FACILITY,
                ]
            ).values_list("id", flat=True)
        )
        self.private_user.save()
        self.client.logout()

    def fetch_facility_contributors(self, facility):
        facility_url = "{}{}/".format(self.url, facility.id)
        response = self.client.get(facility_url)
        data = json.loads(response.content)
        return data.get("properties", {}).get("contributors", [])

    def test_names(self):
        self.source.is_active = False
        self.source.save()

        self.contributor.contrib_type = (
            "Auditor / Certification Scheme / Service Provider"
        )
        self.contributor.save()
        contributors = self.fetch_facility_contributors(self.facility)
        self.assertEqual(1, len(contributors))
        self.assertEqual(
            "An Auditor / Certification Scheme / Service Provider",
            contributors[0].get("name"),
        )

        self.contributor.contrib_type = "Brand / Retailer"
        self.contributor.save()
        contributors = self.fetch_facility_contributors(self.facility)
        self.assertEqual(1, len(contributors))
        self.assertEqual("A Brand / Retailer", contributors[0].get("name"))

    def test_inactive_contributor(self):
        contributors = self.fetch_facility_contributors(self.facility)
        self.assertEqual(1, len(contributors))
        self.assertEqual(
            "test contributor 1 (First List)", contributors[0].get("name")
        )

        self.source.is_active = False
        self.source.save()
        contributors = self.fetch_facility_contributors(self.facility)
        self.assertEqual(1, len(contributors))
        self.assertEqual("One Other", contributors[0].get("name"))

    def test_private_contributor(self):
        contributors = self.fetch_facility_contributors(self.facility)
        self.assertEqual(1, len(contributors))
        self.assertEqual(
            "test contributor 1 (First List)", contributors[0].get("name")
        )

        self.source.is_public = False
        self.source.save()
        contributors = self.fetch_facility_contributors(self.facility)
        self.assertEqual(1, len(contributors))
        self.assertEqual("One Other", contributors[0].get("name"))

    def test_multiple(self):
        user_two = User.objects.create(email="2@two.com")
        user_two.set_password("shhh")
        user_two.save()

        contributor_two = Contributor.objects.create(
            admin=user_two,
            name="test contributor 2",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        source_two = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=contributor_two,
        )

        list_item_two = FacilityListItem.objects.create(
            name="Item 2",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=0,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source_two,
            facility=self.facility,
        )

        FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility,
            facility_list_item=list_item_two,
            confidence=0.85,
            results="",
        )

        source_three = Source.objects.create(
            source_type=Source.SINGLE, is_active=True, is_public=True
        )

        list_item_three = FacilityListItem.objects.create(
            name="Item 3",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=0,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source_three,
            facility=self.facility,
        )

        FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=self.facility,
            facility_list_item=list_item_three,
            confidence=0.85,
            results="",
        )

        contributors = self.fetch_facility_contributors(self.facility)
        self.assertEqual(2, len(contributors))

        source_two.is_active = False
        source_two.save()
        contributors = self.fetch_facility_contributors(self.facility)
        self.assertEqual(2, len(contributors))
        self.assertEqual(
            "test contributor 1 (First List)", contributors[0].get("name")
        )
        self.assertEqual("One Other", contributors[1].get("name"))

        self.match.is_active = False
        self.match.save()
        contributors = self.fetch_facility_contributors(self.facility)
        self.assertEqual(1, len(contributors))
        self.assertEqual("2 Others", contributors[0].get("name"))
        self.assertEqual(contributors[0]["contributor_type"], "Other")
        self.assertEqual(contributors[0]["count"], 2)

    def test_private_user(self):
        self.client.login(
            email=self.private_user.email, password=self.private_user_password
        )
        contributors = self.fetch_facility_contributors(self.facility)
        self.assertEqual(1, len(contributors))
        self.assertEqual("One Other", contributors[0].get("name"))

        self.private_user.groups.set(
            auth.models.Group.objects.filter(
                name__in=[
                    FeatureGroups.CAN_SUBMIT_FACILITY,
                    FeatureGroups.CAN_SUBMIT_PRIVATE_FACILITY,
                    FeatureGroups.CAN_VIEW_FULL_CONTRIB_DETAIL,
                ]
            ).values_list("id", flat=True)
        )
        self.private_user.save()
        contributors = self.fetch_facility_contributors(self.facility)
        self.assertEqual(1, len(contributors))
        self.assertEqual(
            "test contributor 1 (First List)", contributors[0].get("name")
        )

    def test_inactive_or_private_contributor_omitted(self):
        def get_facility_count():
            url = "{}?contributors={}".format(self.url, self.contributor.id)
            response = self.client.get(url)
            data = json.loads(response.content)
            return int(data.get("count"))

        self.assertEqual(1, get_facility_count())

        self.source.is_public = False
        self.source.is_active = True
        self.source.save()
        self.assertEqual(0, get_facility_count())

        self.source.is_public = True
        self.source.is_active = False
        self.source.save()
        self.assertEqual(0, get_facility_count())

    def test_public_contributor_has_count_and_contributor_type(self):
        self.contributor.contrib_type = "Brand / Retailer"
        self.contributor.name = "Public Contributor"
        self.contributor.save()
        contributors = self.fetch_facility_contributors(self.facility)
        self.assertEqual(1, len(contributors))
        self.assertEqual(
            contributors[0]["contributor_type"],
            "Brand / Retailer",
        )
        self.assertEqual(
            contributors[0]["contributor_name"],
            "Public Contributor",
        )
        self.assertEqual(contributors[0]["count"], 1)
