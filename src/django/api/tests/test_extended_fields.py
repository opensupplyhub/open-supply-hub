"""
Tests for extended_fields.py helper functions.
"""

from django.contrib.gis.geos import Point
from django.test import TestCase

from api.extended_fields import create_partner_extendedfields_for_single_item
from api.models import ExtendedField
from api.models.contributor.contributor import Contributor
from api.models.facility.facility import Facility
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.partner_field import PartnerField
from api.models.source import Source
from api.models.user import User


class CreatePartnerExtendedfieldsForSingleItemTest(TestCase):
    """Tests for create_partner_extendedfields_for_single_item."""

    def setUp(self):
        """Set up a contributor with an associated source and list item."""
        user = User.objects.create(email="test_ef@example.com")
        user.set_password("password123")
        user.save()

        self.contributor = Contributor.objects.create(
            admin=user,
            name="Test Contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        facility_list = FacilityList.objects.create(
            header="name,address,country",
            file_name="test.csv",
            name="Test List",
        )
        source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=facility_list,
            contributor=self.contributor,
        )
        self.item = FacilityListItem.objects.create(
            name="Test Facility",
            address="123 Test St",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )
        Facility.objects.create(
            name=self.item.name,
            address=self.item.address,
            country_code=self.item.country_code,
            location=Point(0, 0),
            created_from=self.item,
        )

    def test_inactive_partner_field_value_is_written_at_approval_time(self):
        """
        AC#4: Partner field values submitted while the field is inactive are
        written to api_extendedfield at approval time.

        Without this, activating the field later would require partners to
        resubmit their data rather than triggering a logstash reindex.
        """
        inactive_field = PartnerField.objects.get_all_including_inactive().create(
            name="ac4_inactive_field",
            type=PartnerField.STRING,
            active=False,
        )
        self.contributor.partner_fields.add(inactive_field)

        create_partner_extendedfields_for_single_item(
            self.item,
            {"ac4_inactive_field": "test value"},
        )

        self.assertTrue(
            ExtendedField.objects.filter(
                facility_list_item=self.item,
                field_name="ac4_inactive_field",
            ).exists(),
            "ExtendedField should be created even when the partner field is inactive.",
        )
        ef = ExtendedField.objects.get(
            facility_list_item=self.item,
            field_name="ac4_inactive_field",
        )
        self.assertEqual(ef.value, {"raw_value": "test value"})

    def test_active_partner_field_value_is_still_written(self):
        """Active partner fields continue to produce ExtendedField rows."""
        active_field = PartnerField.objects.get_all_including_inactive().create(
            name="ac4_active_field",
            type=PartnerField.STRING,
            active=True,
        )
        self.contributor.partner_fields.add(active_field)

        create_partner_extendedfields_for_single_item(
            self.item,
            {"ac4_active_field": "active value"},
        )

        ef = ExtendedField.objects.get(
            facility_list_item=self.item,
            field_name="ac4_active_field",
        )
        self.assertEqual(ef.value, {"raw_value": "active value"})

    def test_unassigned_inactive_field_is_not_written(self):
        """
        A field the contributor is not assigned to is silently skipped —
        the permission check happens upstream in the processor chain, not here.
        """
        PartnerField.objects.get_all_including_inactive().create(
            name="ac4_unassigned_field",
            type=PartnerField.STRING,
            active=False,
        )

        create_partner_extendedfields_for_single_item(
            self.item,
            {"ac4_unassigned_field": "should not appear"},
        )

        self.assertFalse(
            ExtendedField.objects.filter(
                facility_list_item=self.item,
                field_name="ac4_unassigned_field",
            ).exists(),
        )
