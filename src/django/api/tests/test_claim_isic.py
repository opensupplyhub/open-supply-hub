from django.test import SimpleTestCase
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from api.constants import FacilityClaimStatuses
from api.extended_fields import get_isic_extendedfield_value
from api.isic_taxonomy.revisions import isic_entry
from api.models import ExtendedField, FacilityClaim
from api.models.facility.facility_index import FacilityIndex
# The module, not the class: importing the class would run its tests here.
from api.tests import test_approved_facility_claim

VISIBILITY = {
    "facility_description": "description",
    "facility_phone_number_publicly_visible": False,
    "point_of_contact_publicly_visible": False,
    "office_info_publicly_visible": False,
    "facility_website_publicly_visible": False,
}


@override_switch("claim_a_facility", active=True)
class ClaimIsicTest(APITestCase):
    """Claimants submit ISIC 4 / ISIC 5 values and manage them once the
    claim is approved; edits publish like other claim fields."""

    setUp = test_approved_facility_claim.ApprovedFacilityClaimTest.setUp

    def _create_claim(self, **isic):
        FacilityClaim.objects.all().delete()
        return self.client.post(
            f"/api/facilities/{self.facility.id}/claim/",
            {
                "your_name": "John Doe",
                "your_title": "Facility Manager",
                "your_business_website": "https://example.com",
                "business_website": "https://facility.com",
                "business_linkedin_profile": "https://linkedin.com/c/f",
                **isic,
            },
        )

    def _edit(self, payload):
        FacilityClaim.objects.filter(id=self.facility_claim.id).update(
            status=FacilityClaimStatuses.APPROVED,
        )
        return self.client.put(
            f"/api/facility-claims/{self.facility_claim.id}/claimed/",
            {**VISIBILITY, **payload},
            format="json",
        )

    def test_a_claim_stores_isic_values_with_every_level(self):
        response = self._create_claim(
            isic_4=["class:1410"], isic_5=["class:1104"],
        )

        self.assertEqual(200, response.status_code)
        claim = FacilityClaim.objects.get(facility=self.facility)
        self.assertEqual(claim.isic_4, [isic_entry("1410", "4")])
        self.assertEqual(claim.isic_5, [isic_entry("1104", "5")])

    def test_a_claim_rejects_codes_its_revision_does_not_have(self):
        response = self._create_claim(isic_5=["class:9999"])

        self.assertEqual(400, response.status_code)
        self.assertIn("isic_5", response.json())

    def test_editing_an_approved_claim_publishes_isic(self):
        response = self._edit({"isic_5": ["class:1104"]})

        self.assertEqual(200, response.status_code)
        field = ExtendedField.objects.get(
            facility_claim=self.facility_claim,
            field_name=ExtendedField.ISIC_5,
        )
        self.assertEqual(
            field.value["raw_value"], [isic_entry("1104", "5")],
        )
        index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertEqual(index.isic5_class, ["1104"])

    def test_an_empty_list_clears_and_a_missing_one_keeps(self):
        self._edit({"isic_4": ["group:141"], "isic_5": ["class:1104"]})

        self._edit({"isic_4": [], "facility_description": "new"})

        claim = FacilityClaim.objects.get(id=self.facility_claim.id)
        self.assertIsNone(claim.isic_4)
        self.assertEqual(claim.isic_5, [isic_entry("1104", "5")])
        self.assertFalse(ExtendedField.objects.filter(
            facility_claim=claim, field_name=ExtendedField.ISIC_4,
        ).exists())

    def test_saving_back_what_the_editor_loaded_keeps_isic(self):
        # The editor sends back the claim as GET returned it: full entries.
        self._edit({"isic_4": ["class:1410"]})
        loaded = self.client.get(
            f"/api/facility-claims/{self.facility_claim.id}/claimed/"
        ).json()

        response = self._edit({"isic_4": loaded["isic_4"]})

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            FacilityClaim.objects.get(id=self.facility_claim.id).isic_4,
            [isic_entry("1410", "4")],
        )

    def test_editing_rejects_codes_its_revision_does_not_have(self):
        response = self._edit({"isic_4": ["section:Z"]})

        self.assertEqual(400, response.status_code)


class SingleLevelIsicValueTest(SimpleTestCase):
    def test_a_single_valid_level_gets_its_parents(self):
        # As the single-location form sends.
        self.assertEqual(
            get_isic_extendedfield_value(
                [{"class": "1410 - Manufacture of wearing apparel"}],
                ExtendedField.ISIC_4,
            )["raw_value"],
            [isic_entry("1410", "4")],
        )

    def test_other_isic_4_objects_are_stored_as_sent(self):
        # RBA sends full paths, and sometimes a group code as a class.
        for value in (
            {"section": "C - Manufacturing", "class": "1410 - Apparel"},
            {"class": "620 - Computer programming"},
        ):
            with self.subTest(value=value):
                self.assertEqual(
                    get_isic_extendedfield_value(
                        [value], ExtendedField.ISIC_4,
                    )["raw_value"],
                    [value],
                )
