"""
Tests for how the Contributor admin page handles inactive partner fields.
"""

from unittest.mock import Mock

from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase

from api.admin import ContributorAdmin, ContributorAdminForm
from api.models import Contributor, User
from api.models.partner_field import PartnerField


class ContributorAdminPartnerFieldsTest(TestCase):
    """
    Test cases for assigning active and inactive partner fields to a
    contributor in Django admin.
    """

    def setUp(self):
        """Create a contributor plus one active and one inactive field."""
        user = User.objects.create(email='partner_admin@example.com')
        self.contributor = Contributor.objects.create(
            admin=user,
            name='partner admin contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        all_fields = PartnerField.objects.get_all_including_inactive()
        self.active_field = all_fields.create(
            name='active_field',
            type=PartnerField.STRING,
            active=True,
        )
        self.inactive_field = all_fields.create(
            name='inactive_field',
            type=PartnerField.STRING,
            active=False,
        )

        self.model_admin = ContributorAdmin(Contributor, AdminSite())
        self.request = RequestFactory().get('/')

    def _get_partner_fields_form_field(self):
        """Helper to get the admin's form field for partner fields."""
        return self.model_admin.formfield_for_manytomany(
            Contributor._meta.get_field('partner_fields'),
            self.request,
        )

    def _save_with_selected_fields(self, selected_fields):
        """
        Helper to save the contributor the way the admin page does, where
        selected_fields are the partner fields left in the "chosen" box.
        """
        form = Mock()
        form.instance = self.contributor
        form.cleaned_data = {'partner_fields': selected_fields}
        self.model_admin.save_related(self.request, form, [], True)

    def test_pick_list_includes_inactive_fields(self):
        """Verify inactive fields can be picked for a contributor."""
        form_field = self._get_partner_fields_form_field()

        self.assertIn(self.active_field, form_field.queryset)
        self.assertIn(self.inactive_field, form_field.queryset)

    def test_inactive_fields_are_labelled_inactive(self):
        """Verify inactive fields show '(inactive)' after their name."""
        form_field = self._get_partner_fields_form_field()
        labels = [label for _, label in form_field.choices]

        self.assertIn('active_field', labels)
        self.assertIn('inactive_field (inactive)', labels)
        self.assertNotIn('active_field (inactive)', labels)

    def test_assigned_inactive_field_shows_as_chosen(self):
        """Verify an assigned inactive field is in the "chosen" box."""
        self.contributor.partner_fields.add(self.inactive_field)

        form = ContributorAdminForm(instance=self.contributor)

        self.assertIn(
            self.inactive_field.pk,
            form.initial['partner_fields'],
        )

    def test_saving_keeps_inactive_field_that_is_still_chosen(self):
        """Verify an inactive field left in the "chosen" box stays."""
        self.contributor.partner_fields.add(self.inactive_field)

        self._save_with_selected_fields(
            PartnerField.objects.get_all_including_inactive().filter(
                pk=self.inactive_field.pk
            )
        )

        self.assertIn(
            self.inactive_field,
            self.contributor.all_partner_fields_including_inactive,
        )

    def test_saving_removes_inactive_field_taken_out_of_chosen(self):
        """Verify an inactive field moved out of "chosen" is removed."""
        self.contributor.partner_fields.add(self.inactive_field)

        self._save_with_selected_fields(
            PartnerField.objects.get_all_including_inactive().none()
        )

        self.assertNotIn(
            self.inactive_field,
            self.contributor.all_partner_fields_including_inactive,
        )
