from api.models import (
    Contributor,
    ExtendedField,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
)
from api.models.user import User

from django.contrib.gis.geos import Point
from django.test import TestCase


class FacilityNamesAddressesAndContributorsTest(TestCase):
    def setUp(self):
        self.name_one = "name_one"
        self.name_two = "name_two"
        self.address_one = "address_one"
        self.address_two = "address_two"
        self.email_one = "one@example.com"
        self.email_two = "two@example.com"
        self.contrib_one_name = "contributor one"
        self.contrib_two_name = "contributor two"
        self.country_code = "US"
        self.list_one_name = "one"
        self.list_two_name = "two"
        self.user_one = User.objects.create(email=self.email_one)
        self.user_two = User.objects.create(email=self.email_two)

        self.contrib_one = Contributor.objects.create(
            admin=self.user_one,
            name=self.contrib_one_name,
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.contrib_two = Contributor.objects.create(
            admin=self.user_two,
            name=self.contrib_two_name,
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.list_one = FacilityList.objects.create(
            header="header", file_name="one", name=self.list_one_name
        )

        self.source_one = Source.objects.create(
            facility_list=self.list_one,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contrib_one,
        )

        self.list_item_one = FacilityListItem.objects.create(
            name=self.name_one,
            address=self.address_one,
            country_code=self.country_code,
            sector=["Apparel"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source_one,
            source_uuid=self.source_one,
        )

        self.list_two = FacilityList.objects.create(
            header="header", file_name="two", name=self.list_two_name
        )

        self.source_two = Source.objects.create(
            facility_list=self.list_two,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contrib_two,
        )

        self.list_item_two = FacilityListItem.objects.create(
            name=self.name_two,
            address=self.address_two,
            country_code=self.country_code,
            sector=["Apparel"],
            row_index="2",
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source_two,
            source_uuid=self.source_two,
        )

        self.facility = Facility.objects.create(
            name=self.name_one,
            address=self.address_one,
            country_code=self.country_code,
            location=Point(0, 0),
            created_from=self.list_item_one,
        )
        self.list_item_one.facility = self.facility
        self.list_item_one.save()
        self.list_item_two.facility = self.facility
        self.list_item_two.save()

        self.list_item_one.facility = self.facility
        self.list_item_one.save()
        self.list_item_two.facility = self.facility
        self.list_item_two.save()

        self.extended_field_one = ExtendedField.objects.create(
            field_name="native_language_name",
            value=self.name_one,
            contributor=self.contrib_one,
            facility=self.facility,
            facility_list_item=self.list_item_one,
        )

        self.extended_field_two = ExtendedField.objects.create(
            field_name="native_language_name",
            value=self.name_two,
            contributor=self.contrib_two,
            facility=self.facility,
            facility_list_item=self.list_item_two,
        )

        self.facility_match_one = FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=self.facility,
            results="",
            facility_list_item=self.list_item_one,
        )

        self.facility_match_two = FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=self.facility,
            results="",
            facility_list_item=self.list_item_two,
        )

    def test_returns_contributors(self):
        sources = self.facility.sources()
        self.assertIn(self.source_one, sources)
        self.assertIn(self.source_two, sources)
        self.assertEqual(len(sources), 2)

    def test_returns_extended_fields(self):
        fields = self.facility.extended_fields()
        self.assertIn(self.extended_field_one, fields)
        self.assertIn(self.extended_field_two, fields)
        self.assertEqual(len(fields), 2)

    def test_excludes_canonical_name_from_other_names(self):
        other_names = self.facility.other_names()
        self.assertIn(self.name_two, other_names)
        self.assertNotIn(self.name_one, other_names)

    def test_excludes_canonical_address_from_other_addresses(self):
        other_addresses = self.facility.other_addresses()
        self.assertIn(self.address_two, other_addresses)
        self.assertNotIn(self.address_one, other_addresses)

    def test_excludes_other_names_from_inactive_lists(self):
        self.source_two.is_active = False
        self.source_two.save()
        other_names = self.facility.other_names()
        self.assertNotIn(self.name_two, other_names)
        self.assertEqual(len(other_names), 0)

    def test_excludes_other_addresses_from_inactive_lists(self):
        self.source_two.is_active = False
        self.source_two.save()
        other_addresses = self.facility.other_addresses()
        self.assertNotIn(self.address_two, other_addresses)
        self.assertEqual(len(other_addresses), 0)

    def test_excludes_contributors_from_inactive_lists(self):
        self.source_two.is_active = False
        self.source_two.save()
        sources = self.facility.sources()
        self.assertIn(self.source_one, sources)
        self.assertNotIn(self.source_two, sources)

    def test_excludes_other_names_from_non_public_lists(self):
        self.source_two.is_active = False
        self.source_two.save()
        other_names = self.facility.other_names()
        self.assertNotIn(self.name_two, other_names)
        self.assertEqual(len(other_names), 0)

    def test_excludes_other_addresses_from_non_public_lists(self):
        self.source_two.is_active = False
        self.source_two.save()
        other_addresses = self.facility.other_addresses()
        self.assertNotIn(self.address_two, other_addresses)
        self.assertEqual(len(other_addresses), 0)

    def test_excludes_contributors_from_non_public_lists(self):
        self.source_two.is_active = False
        self.source_two.save()
        sources = self.facility.sources()
        self.assertIn(self.source_one, sources)
        self.assertNotIn(self.source_two, sources)

    def test_excludes_unmatched_facilities_from_other_names(self):
        self.facility_match_two.status = FacilityMatch.REJECTED
        self.facility_match_two.save()
        other_names = self.facility.other_names()
        self.assertNotIn(self.name_two, other_names)
        self.assertEqual(len(other_names), 0)

    def test_excludes_unmatched_facilities_from_other_addresses(self):
        self.facility_match_two.status = FacilityMatch.REJECTED
        self.facility_match_two.save()
        other_addresses = self.facility.other_addresses()
        self.assertNotIn(self.name_one, other_addresses)
        self.assertEqual(len(other_addresses), 0)

    def test_excludes_unmatched_facilities_from_contributors(self):
        self.facility_match_two.status = FacilityMatch.REJECTED
        self.facility_match_two.save()
        sources = self.facility.sources()
        self.assertIn(self.source_one, sources)
        self.assertNotIn(self.source_two, sources)
        self.assertEqual(len(sources), 1)

    def test_excludes_inactive_facility_matches_from_details(self):
        self.facility_match_two.is_active = False
        self.facility_match_two.save()

        sources = self.facility.sources()
        self.assertIn(self.source_one, sources)
        self.assertNotIn(self.source_two, sources)
        self.assertIn("One Other", sources)
        self.assertEqual(len(sources), 2)

        other_names = self.facility.other_names()
        self.assertNotIn(self.name_two, other_names)
        self.assertEqual(len(other_names), 0)

        other_addresses = self.facility.other_addresses()
        self.assertNotIn(self.address_two, other_addresses)
        self.assertEqual(len(other_addresses), 0)

        fields = self.facility.extended_fields()
        self.assertIn(self.extended_field_one, fields)
        self.assertNotIn(self.extended_field_two, fields)
        self.assertEqual(len(fields), 1)

    def test_excludes_private_matches_from_details(self):
        self.source_two.is_public = False
        self.source_two.save()

        sources = self.facility.sources()
        self.assertIn(self.source_one, sources)
        self.assertNotIn(self.source_two, sources)
        self.assertIn("One Other", sources)
        self.assertEqual(len(sources), 2)

        other_names = self.facility.other_names()
        self.assertNotIn(self.name_two, other_names)
        self.assertEqual(len(other_names), 0)

        other_addresses = self.facility.other_addresses()
        self.assertNotIn(self.address_two, other_addresses)
        self.assertEqual(len(other_addresses), 0)
