from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase, override_settings

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

# The admin templates reference hashed static files, which are not built
# in the test environment.
PLAIN_STATIC_STORAGE = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}


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

        User.objects.create_superuser('moderator@example.com', 'example123')
        self.client.login(
            email='moderator@example.com', password='example123')

    def _unchanged_post_data(self):
        """What the change page submits when nothing is edited."""
        form_class = self.admin.get_form(
            self.request, obj=self.claim, change=True)
        rendered = form_class(instance=self.claim)
        data = {}
        for name in rendered.fields:
            value = rendered[name].value()
            data[name] = '' if value is None else value
        return data

    @override_settings(STORAGES=PLAIN_STATIC_STORAGE)
    def test_saving_an_unedited_claim_succeeds(self):
        """The regression test for the reported bug.

        A moderator opens a claim that left the optional fields empty and
        presses Save without editing anything. Before the fix this came
        back as a 200 carrying "No geometry value provided." on Location,
        plus required-field errors on parent company and description.
        """
        url = '/admin/api/facilityclaim/{}/change/'.format(self.claim.id)
        data = self._unchanged_post_data()
        data['_save'] = 'Save'

        response = self.client.post(url, data)

        if response.status_code == 200:
            errors = response.context_data['adminform'].form.errors.as_data()
            self.fail('the claim could not be saved: {}'.format(errors))
        self.assertEqual(response.status_code, 302)

        # Saving must not invent values for the empty fields.
        self.claim.refresh_from_db()
        self.assertEqual(self.claim.facility_description, '')
        self.assertIsNone(self.claim.facility_location)
        self.assertIsNone(self.claim.parent_company)

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
