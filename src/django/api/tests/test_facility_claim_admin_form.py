from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase

from api.admin import FacilityClaimAdmin
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


class FacilityClaimAdminFormTest(TestCase):
    """Tests for the admin form moderators use to correct claim data."""

    def setUp(self):
        self.admin = FacilityClaimAdmin(FacilityClaim, AdminSite())
        self.request = RequestFactory().get('/')
        self.form_class = self.admin.get_form(self.request)

        user = User.objects.create(email='claimant@example.com')
        contributor = Contributor.objects.create(
            admin=user,
            name='test contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='List')
        source = Source.objects.create(
            facility_list=facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=contributor,
        )
        list_item = FacilityListItem.objects.create(
            name='Item',
            address='Address',
            country_code='US',
            sector=['Apparel'],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )
        facility = Facility.objects.create(
            name='NameFacility',
            address='Address',
            country_code='US',
            location=Point(0, 0),
            created_from=list_item,
        )
        # Built the way facilities_view_set.claim builds one when the
        # claimant skips the optional steps: no point, no parent company
        # and an empty description.
        self.claim = FacilityClaim.objects.create(
            contributor=contributor,
            facility=facility,
            contact_person='Contact Person',
            job_title='Manager',
            company_name='Test',
            website='http://example.com',
            facility_description='',
            facility_location=None,
            parent_company=None,
        )

    def _resave_unchanged(self, claim):
        """Bind the change form to what it renders for an existing claim.

        This is a moderator opening the claim and pressing Save without
        editing anything, which is the action OSDEV-1065 reported as
        impossible.
        """
        form_class = self.admin.get_form(
            self.request, obj=claim, change=True)
        rendered = form_class(instance=claim)
        data = {}
        for name in rendered.fields:
            value = rendered[name].value()
            data[name] = '' if value is None else value
        return form_class(data, instance=claim)

    def test_a_claim_with_every_optional_field_empty_can_be_saved(self):
        """The regression test for the reported bug.

        Asserting the form validates, rather than asserting individual
        required flags, is what catches a field the audit missed.
        """
        form = self._resave_unchanged(self.claim)
        self.assertTrue(
            form.is_valid(),
            'claim admin form rejected an unedited claim: {}'.format(
                form.errors.as_data()))

    def test_location_is_optional(self):
        """A claim with no stored point must still be saveable."""
        self.assertFalse(
            self.form_class.base_fields['facility_location'].required)

    def test_parent_company_is_optional(self):
        """Parent company is supplementary and must never block a save."""
        self.assertFalse(
            self.form_class.base_fields['parent_company'].required)

    def test_description_is_optional(self):
        """Description is optional at submission and stored as ''."""
        self.assertFalse(
            self.form_class.base_fields['facility_description'].required)

    def test_status_fields_stay_out_of_the_form(self):
        """Status bookkeeping is readonly, which is why it needs no blank."""
        for field in ('status_change_by', 'status_change_date'):
            self.assertNotIn(field, self.form_class.base_fields)

    def test_only_fields_a_claim_always_has_stay_required(self):
        """Guards against a fourth field blocking saves unnoticed.

        Both of these are required at submission and non-empty on every
        row in production, so they are safe to leave required here.
        """
        required = sorted(
            name for name, field in self.form_class.base_fields.items()
            if field.required)
        self.assertEqual(required, ['contact_person', 'job_title'])
