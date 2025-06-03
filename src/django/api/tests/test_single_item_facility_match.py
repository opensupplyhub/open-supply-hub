from api.models import Contributor, FacilityListItem, FacilityMatch, Source
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase

from django.contrib.gis.geos import Point
from django.urls import reverse


class SingleItemFacilityMatchTest(FacilityAPITestCaseBase):
    def setUp(self):
        super(SingleItemFacilityMatchTest, self).setUp()
        self.contributor_two = Contributor.objects.create(
            admin=self.superuser,
            name="test contributor 2",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.source_two = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=self.contributor_two,
        )

        self.list_item_two = FacilityListItem.objects.create(
            name="Item 2",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.POTENTIAL_MATCH,
            source=self.source_two,
            source_uuid=self.source_two,
        )

        self.match_two = FacilityMatch.objects.create(
            status=FacilityMatch.PENDING,
            facility=self.facility,
            facility_list_item=self.list_item_two,
            confidence=0.75,
            results="",
        )

        self.list_item_two.facility = self.facility
        self.list_item_two.save()

    def match_url(self, match, action="detail"):
        return reverse(
            "facility-match-{}".format(action), kwargs={"pk": match.pk}
        )

    def test_get_match_detail(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        response = self.client.get(self.match_url(self.match_two))
        self.assertEqual(200, response.status_code)

    def test_only_contributor_can_get_match_detail(self):
        self.client.login(email=self.user_email, password=self.user_password)

        response = self.client.get(self.match_url(self.match_two))
        self.assertEqual(404, response.status_code)

    def test_confirm(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        response = self.client.post(
            self.match_url(self.match_two, action="confirm")
        )
        self.assertEqual(200, response.status_code)

    def test_only_contributor_can_confirm(self):
        self.client.login(email=self.user_email, password=self.user_password)

        response = self.client.post(
            self.match_url(self.match_two, action="confirm")
        )
        self.assertEqual(404, response.status_code)

    def test_reject(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )
        response = self.client.post(
            self.match_url(self.match_two, action="reject")
        )
        self.assertEqual(200, response.status_code)

    def test_only_contributor_can_reject(self):
        self.client.login(email=self.user_email, password=self.user_password)
        response = self.client.post(
            self.match_url(self.match_two, action="reject")
        )
        self.assertEqual(404, response.status_code)
