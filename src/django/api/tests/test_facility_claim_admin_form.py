from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase

from api.admin import FacilityClaimAdmin
from api.models.facility.facility_claim import FacilityClaim


class FacilityClaimAdminFormTest(TestCase):
    """Tests for the admin form moderators use to correct claim data."""

    def setUp(self):
        self.form_class = FacilityClaimAdmin(
            FacilityClaim, AdminSite()
        ).get_form(RequestFactory().get('/'))

    def test_location_is_optional(self):
        """A claim with no stored point must still be saveable.

        These columns are nullable, so requiring them on the form forced
        moderators to invent data to get past validation (OSDEV-1065).
        """
        self.assertFalse(
            self.form_class.base_fields['facility_location'].required)

    def test_parent_company_is_optional(self):
        """Parent company is supplementary and must never block a save."""
        self.assertFalse(
            self.form_class.base_fields['parent_company'].required)

    def test_status_fields_stay_out_of_the_form(self):
        """Status bookkeeping is readonly, which is why it needs no blank."""
        for field in ('status_change_by', 'status_change_date'):
            self.assertNotIn(field, self.form_class.base_fields)
