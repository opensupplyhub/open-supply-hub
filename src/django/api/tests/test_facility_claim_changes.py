from api.models import (
    Contributor,
    Facility,
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)

from django.contrib.gis.geos import Point
from django.test import TestCase


class FacilityClaimChangesTest(TestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "password"
        self.name = "Test User"
        self.user = User(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

        self.contributor = Contributor.objects.create(
            name=self.name, admin=self.user
        )

        self.facility_list = FacilityList.objects.create(
            header="header", file_name="one", name="one"
        )

        self.source = Source.objects.create(
            facility_list=self.facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )

        self.list_item = FacilityListItem.objects.create(
            name="Name",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
            source_uuid=self.source,
        )

        self.facility = Facility.objects.create(
            name=self.list_item.name,
            address=self.list_item.address,
            country_code=self.list_item.country_code,
            location=Point(0, 0),
            created_from=self.list_item,
        )

        self.claim = FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            facility_name_english="Facility Name",
            facility_name_native_language="Објекат Име",
        )

    def test_no_changes(self):
        self.assertIsNone(self.claim.get_changes())

    def test_changes(self):
        prev_name = self.claim.facility_name_english
        new_name = "Changed"
        self.claim.facility_name_english = new_name
        self.claim.save()
        changes = self.claim.get_changes()
        self.assertIsNotNone(changes)
        self.assertEqual(1, len(changes))
        self.assertEqual("facility_name_english", changes[0]["name"])
        self.assertEqual(prev_name, changes[0]["previous"])
        self.assertEqual(new_name, changes[0]["current"])
        self.assertEqual(
            "facility name in English", changes[0]["verbose_name"]
        )

    def test_do_not_include_field_change(self):
        self.claim.facility_name = "Changed"
        self.claim.save()
        changes = self.claim.get_changes(include="foo")
        self.assertIsNone(changes)

    def test_non_public_changes(self):
        self.claim.facility_phone_number = "Changed"
        self.claim.point_of_contact_person_name = "Changed"
        self.claim.office_official_name = "Changed"
        self.claim.office_address = "Changed"
        self.claim.office_country_code = "CN"
        self.claim.office_phone_number = "Changed"
        self.claim.save()
        self.assertIsNone(self.claim.get_changes())

        self.claim.office_info_publicly_visible = True
        self.claim.office_official_name = "Changed again"
        self.claim.office_address = "Changed again"
        self.claim.office_country_code = "GB"
        self.claim.office_phone_number = "Changed again"
        self.claim.save()
        changes = self.claim.get_changes()
        self.assertIsNotNone(changes)
        field_names = [c["name"] for c in changes]
        self.assertIn("office_official_name", field_names)
        self.assertIn("office_address", field_names)
        self.assertIn("office_country_code", field_names)
        self.assertIn("office_phone_number", field_names)
        self.assertNotIn("facility_phone_number", field_names)
        self.assertNotIn("point_of_contact_person_name", field_names)

    def test_change_serializers(self):
        self.claim.parent_company = self.contributor
        self.claim.save()
        changes = self.claim.get_changes()
        self.assertIsNotNone(changes)
        self.assertEqual(1, len(changes))
        change = changes[0]
        self.assertEqual(change["name"], "parent_company")
        self.assertEqual(change["current"], self.name)
