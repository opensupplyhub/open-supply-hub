import numpy as np
from api.constants import MatchResponsibility
from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.processing import save_match_details

from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone


class PPEFieldTest(TestCase):
    def setUp(self):
        self.email_one = "one@example.com"
        self.email_two = "two@example.com"
        self.user_one = User.objects.create(email=self.email_one)
        self.user_two = User.objects.create(email=self.email_two)
        self.user_two.set_password("password")
        self.user_two.save()

        self.contrib_one = Contributor.objects.create(
            admin=self.user_one,
            name="contributor one",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.contrib_two = Contributor.objects.create(
            admin=self.user_two,
            name="contributor two",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.list_one = FacilityList.objects.create(
            header="header", file_name="one", name="list_one"
        )

        self.list_two = FacilityList.objects.create(
            header="header",
            file_name="two",
            name="list_two",
            match_responsibility=MatchResponsibility.CONTRIBUTOR,
        )

        self.source_one = Source.objects.create(
            facility_list=self.list_one,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contrib_one,
        )

        self.source_two = Source.objects.create(
            facility_list=self.list_two,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            create=True,
            contributor=self.contrib_two,
        )

        self.list_item_one = FacilityListItem.objects.create(
            name="name",
            address="address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source_one,
        )

        self.list_item_two = FacilityListItem.objects.create(
            name="name",
            address="address",
            country_code="US",
            sector=["Apparel"],
            ppe_product_types=["Masks_Two", "Gloves_Two"],
            ppe_contact_phone="222-222-2222",
            ppe_contact_email="two@example.com",
            ppe_website="http://example.com/two",
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source_two,
            geocoded_point=Point(0, 0),
        )

        self.facility = Facility.objects.create(
            name="name",
            address="address",
            country_code="US",
            location=Point(0, 0),
            created_from=self.list_item_one,
        )

        self.facility_match_one = FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=self.facility,
            results="",
            facility_list_item=self.list_item_one,
        )

    def make_match_results(self, list_item_id, facility_id, score):
        return {
            "processed_list_item_ids": [list_item_id],
            "item_matches": {list_item_id: [(facility_id, np.float32(score))]},
            "results": {
                "gazetteer_threshold": 50,
                "automatic_threshold": 80,
                "recall_weight": 0.5,
                "code_version": "abcd1234",
            },
            "started": str(timezone.now()),
            "finished": str(timezone.now()),
        }

    def test_match_populates_ppe(self):
        results = self.make_match_results(
            self.list_item_two.id, self.facility.id, 100
        )
        save_match_details(results)
        self.facility.refresh_from_db()

        self.assertEqual(
            self.list_item_two.ppe_product_types,
            self.facility.ppe_product_types,
        )
        self.assertEqual(
            self.list_item_two.ppe_contact_phone,
            self.facility.ppe_contact_phone,
        )
        self.assertEqual(
            self.list_item_two.ppe_contact_email,
            self.facility.ppe_contact_email,
        )
        self.assertEqual(
            self.list_item_two.ppe_website, self.facility.ppe_website
        )

    def test_match_does_not_overwrite_ppe_product_types(self):
        self.facility.ppe_product_types = ["TEST"]
        self.facility.save()

        results = self.make_match_results(
            self.list_item_two.id, self.facility.id, 100
        )
        save_match_details(results)
        self.facility.refresh_from_db()

        self.assertEqual(["TEST"], self.facility.ppe_product_types)
        self.assertEqual(
            self.list_item_two.ppe_contact_phone,
            self.facility.ppe_contact_phone,
        )
        self.assertEqual(
            self.list_item_two.ppe_contact_email,
            self.facility.ppe_contact_email,
        )
        self.assertEqual(
            self.list_item_two.ppe_website, self.facility.ppe_website
        )

    def test_match_does_not_overwrite_ppe_contact_phone(self):
        self.facility.ppe_contact_phone = "ttt-ttt-tttt"
        self.facility.save()

        results = self.make_match_results(
            self.list_item_two.id, self.facility.id, 100
        )
        save_match_details(results)
        self.facility.refresh_from_db()

        self.assertEqual(
            self.list_item_two.ppe_product_types,
            self.facility.ppe_product_types,
        )
        self.assertEqual("ttt-ttt-tttt", self.facility.ppe_contact_phone)
        self.assertEqual(
            self.list_item_two.ppe_contact_email,
            self.facility.ppe_contact_email,
        )
        self.assertEqual(
            self.list_item_two.ppe_website, self.facility.ppe_website
        )

    def test_match_does_not_overwrite_ppe_contact_email(self):
        self.facility.ppe_contact_email = "TTT@TT.COM"
        self.facility.save()

        results = self.make_match_results(
            self.list_item_two.id, self.facility.id, 100
        )
        save_match_details(results)
        self.facility.refresh_from_db()

        self.assertEqual(
            self.list_item_two.ppe_product_types,
            self.facility.ppe_product_types,
        )
        self.assertEqual(
            self.list_item_two.ppe_contact_phone,
            self.facility.ppe_contact_phone,
        )
        self.assertEqual("TTT@TT.COM", self.facility.ppe_contact_email)
        self.assertEqual(
            self.list_item_two.ppe_website, self.facility.ppe_website
        )

    def test_match_does_not_overwrite_ppe_website(self):
        self.facility.ppe_website = "HTTP://TEST.COM"
        self.facility.save()

        results = self.make_match_results(
            self.list_item_two.id, self.facility.id, 100
        )
        save_match_details(results)
        self.facility.refresh_from_db()

        self.assertEqual(
            self.list_item_two.ppe_product_types,
            self.facility.ppe_product_types,
        )
        self.assertEqual(
            self.list_item_two.ppe_contact_phone,
            self.facility.ppe_contact_phone,
        )
        self.assertEqual(
            self.list_item_two.ppe_contact_email,
            self.facility.ppe_contact_email,
        )
        self.assertEqual("HTTP://TEST.COM", self.facility.ppe_website)

    def match_url(self, match, action="detail"):
        return reverse(
            "facility-match-{}".format(action), kwargs={"pk": match.pk}
        )

    def test_confirm_match_populates_ppe(self):
        results = self.make_match_results(
            self.list_item_two.id, self.facility.id, 70
        )
        save_match_details(results)

        pending_qs = self.facility.facilitymatch_set.filter(
            status=FacilityMatch.PENDING
        )
        self.assertEqual(1, pending_qs.count())
        match = pending_qs[0]
        self.assertEqual(FacilityMatch.PENDING, match.status)

        self.client.login(email=self.email_two, password="password")
        response = self.client.post(self.match_url(match, action="confirm"))
        self.assertEqual(200, response.status_code)

        self.facility.refresh_from_db()

        self.assertEqual(
            self.list_item_two.ppe_product_types,
            self.facility.ppe_product_types,
        )
        self.assertEqual(
            self.list_item_two.ppe_contact_phone,
            self.facility.ppe_contact_phone,
        )
        self.assertEqual(
            self.list_item_two.ppe_contact_email,
            self.facility.ppe_contact_email,
        )
        self.assertEqual(
            self.list_item_two.ppe_website, self.facility.ppe_website
        )

    def reject_match_and_assert(self):
        """
        This helper creates a potential match for line_item_two, submits a
        request to reject it, and asserts that a new facility is created from
        line_item_two. The newly created `Facility` object is returned.
        """
        results = self.make_match_results(
            self.list_item_two.id, self.facility.id, 70
        )
        save_match_details(results)

        pending_qs = self.facility.facilitymatch_set.filter(
            status=FacilityMatch.PENDING
        )
        self.assertEqual(1, pending_qs.count())
        match = pending_qs[0]
        self.assertEqual(FacilityMatch.PENDING, match.status)

        self.client.login(email=self.email_two, password="password")
        response = self.client.post(self.match_url(match, action="reject"))
        self.assertEqual(200, response.status_code)

        facility = Facility.objects.get(created_from=self.list_item_two)

        self.assertEqual(
            self.list_item_two.ppe_product_types, facility.ppe_product_types
        )
        self.assertEqual(
            self.list_item_two.ppe_contact_phone, facility.ppe_contact_phone
        )
        self.assertEqual(
            self.list_item_two.ppe_contact_email, facility.ppe_contact_email
        )
        self.assertEqual(self.list_item_two.ppe_website, facility.ppe_website)

        return facility

    def test_reject_match_creates_facility_with_ppe(self):
        self.reject_match_and_assert()

    def test_deactivating_created_from_source_clears_ppe(self):
        facility = self.reject_match_and_assert()

        facility.created_from.source.is_active = False
        facility.created_from.source.save()
        facility.refresh_from_db()

        self.assertEqual([], facility.ppe_product_types)
        self.assertEqual("", facility.ppe_contact_phone)
        self.assertEqual("", facility.ppe_contact_email)
        self.assertEqual("", facility.ppe_website)

    def test_deactivating_created_from_match_clears_ppe(self):
        facility = self.reject_match_and_assert()

        for match in facility.created_from.facilitymatch_set.all():
            match.is_active = False
            match.save()
        facility.refresh_from_db()

        self.assertEqual([], facility.ppe_product_types)
        self.assertEqual("", facility.ppe_contact_phone)
        self.assertEqual("", facility.ppe_contact_email)
        self.assertEqual("", facility.ppe_website)
