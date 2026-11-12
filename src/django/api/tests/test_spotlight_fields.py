"""
Tests for Spotlight partner self-serve fields (OSDEV-3788): the model rules,
the partner API, the admin actions and the daily go-live command.
"""

import datetime
from io import StringIO

from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import RequestFactory, TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from api.models import Contributor, User
from api.models.spotlight_field import (
    SpotlightField,
    SpotlightFieldProperty,
    validate_internal_name,
)
from api.models.spotlight_field_admin import (
    EditedByPartnersFilter,
    SpotlightFieldAdmin,
)

URL = '/api/spotlight-fields/'


def make_contributor(email, name, partner=True, visibility=False):
    """Create a user with a contributor profile, optionally a partner."""
    user = User.objects.create(email=email)
    user.set_password('pw')
    user.save()
    contributor = Contributor.objects.create(
        admin=user,
        name=name,
        contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        is_spotlight_partner=partner,
        can_control_spotlight_visibility=visibility,
    )
    return user, contributor


def future():
    """A date one week from today."""
    return timezone.localdate() + datetime.timedelta(days=7)


def past():
    """A date one week before today."""
    return timezone.localdate() - datetime.timedelta(days=7)


class InternalNameRulesTest(TestCase):
    """The internal-name rules and the message shown when one is broken."""

    def test_accepts_lowercase_with_underscores(self):
        """A plain lowercase_with_underscores name passes."""
        validate_internal_name('certification_status')
        validate_internal_name('scope_3_emissions')

    def test_rejects_bad_names_with_a_clear_message(self):
        """Uppercase, spaces, dashes, leading digits and long names fail."""
        for bad in ['Certification', 'has space', 'dash-ed', '1abc', '',
                    'a' * 51]:
            with self.assertRaises(ValidationError) as ctx:
                validate_internal_name(bad)
            self.assertIn('lowercase letters', ctx.exception.messages[0])


class SpotlightApiTest(TestCase):
    """The partner dashboard API."""

    def setUp(self):
        """Create a partner, a non-partner and a second partner."""
        self.user, self.contributor = make_contributor(
            'p1@example.com', 'Partner One')
        self.other_user, self.other = make_contributor(
            'p2@example.com', 'Partner Two')
        self.plain_user, _ = make_contributor(
            'plain@example.com', 'Plain', partner=False)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def _create(self, name='certification_status',
                display='Certification Status', client=None):
        """Post a new field and return the response."""
        return (client or self.client).post(
            URL, {'name': name, 'display_name': display}, format='json')

    def test_non_partner_is_denied(self):
        """A contributor without the flag gets a permission error."""
        client = APIClient()
        client.force_authenticate(self.plain_user)
        self.assertEqual(client.get(URL).status_code, 403)
        self.assertEqual(self._create(client=client).status_code, 403)

    def test_anonymous_is_denied(self):
        """Logged-out requests are rejected."""
        self.assertIn(APIClient().get(URL).status_code, (401, 403))

    def test_create_starts_unapproved_inactive_and_links_partner(self):
        """A new field is stored in the JSON, linked and awaiting approval."""
        response = self._create()
        self.assertEqual(response.status_code, 201)
        self.assertIn('inactive until', response.data['message'])
        prop = SpotlightFieldProperty.objects.get(name='certification_status')
        self.assertFalse(prop.approved)
        self.assertFalse(prop.active)
        spotlight = self.contributor.spotlight_field
        schema = spotlight.partner_field.json_schema
        self.assertEqual(
            schema['properties']['certification_status'],
            {'title': 'Certification Status', 'approved': False,
             'active': False},
        )
        self.assertEqual(spotlight.partner_field.type, 'object')
        self.assertTrue(
            self.contributor.partner_fields.filter(
                pk=spotlight.partner_field.pk).exists())

    def test_bad_names_return_clear_errors(self):
        """Broken internal and display names are rejected with messages."""
        response = self._create(name='Bad Name', display='x' * 51)
        self.assertEqual(response.status_code, 400)
        self.assertIn('lowercase letters', response.data['name'][0])
        self.assertIn('50 characters', response.data['display_name'][0])
        self.assertFalse(SpotlightFieldProperty.objects.exists())

    def test_duplicate_name_is_rejected(self):
        """Internal names are unique within a partner."""
        self._create()
        self.assertEqual(self._create().status_code, 400)

    def test_internal_name_cannot_change_but_display_name_can(self):
        """Only the display name is editable after saving."""
        self._create()
        rename = self.client.patch(
            f'{URL}certification_status/',
            {'display_name': 'Certified?'}, format='json')
        self.assertEqual(rename.status_code, 200)
        prop = SpotlightFieldProperty.objects.get()
        self.assertEqual(prop.display_name, 'Certified?')
        self.assertEqual(prop.name, 'certification_status')
        blocked = self.client.patch(
            f'{URL}certification_status/', {'name': 'other'}, format='json')
        self.assertEqual(blocked.status_code, 400)

    def test_no_delete(self):
        """There is no way to delete a field through the API."""
        self._create()
        self.assertEqual(
            self.client.delete(f'{URL}certification_status/').status_code,
            405)
        self.assertEqual(SpotlightFieldProperty.objects.count(), 1)

    def test_cannot_activate_before_approval(self):
        """Activating an unapproved field is blocked."""
        self._create()
        response = self.client.patch(
            f'{URL}certification_status/', {'active': True}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(SpotlightFieldProperty.objects.get().active)

    def test_partner_toggles_after_approval_without_date(self):
        """With no go-live date, an approved field can be switched on/off."""
        self._create()
        prop = SpotlightFieldProperty.objects.get()
        prop.approve(user=None)
        on = self.client.patch(
            f'{URL}certification_status/', {'active': True}, format='json')
        self.assertEqual(on.status_code, 200)
        self.assertTrue(SpotlightFieldProperty.objects.get().active)
        off = self.client.patch(
            f'{URL}certification_status/', {'active': False}, format='json')
        self.assertEqual(off.status_code, 200)
        self.assertFalse(SpotlightFieldProperty.objects.get().active)

    def test_partner_blocked_before_go_live_date(self):
        """While a go-live date is pending, the partner cannot activate."""
        self._create()
        prop = SpotlightFieldProperty.objects.get()
        prop.approve(user=None)
        prop.spotlight_field.set_go_live_date(future())
        response = self.client.patch(
            f'{URL}certification_status/', {'active': True}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(SpotlightFieldProperty.objects.get().active)

    def test_partners_only_see_their_own_fields(self):
        """One partner never sees or edits another partner's fields."""
        self._create()
        other_client = APIClient()
        other_client.force_authenticate(self.other_user)
        self.assertEqual(other_client.get(URL).data['fields'], [])
        response = other_client.patch(
            f'{URL}certification_status/', {'display_name': 'x'},
            format='json')
        self.assertEqual(response.status_code, 400)

    def test_edit_by_partner_is_recorded(self):
        """A partner edit stamps the field set for the admin filter."""
        self._create()
        self.client.patch(
            f'{URL}certification_status/', {'display_name': 'New'},
            format='json')
        self.assertIsNotNone(
            SpotlightField.objects.get().last_partner_edit_at)

    def test_history_records_who_and_old_new_values(self):
        """Each change is kept in history with the user who made it."""
        self._create()
        self.client.patch(
            f'{URL}certification_status/', {'display_name': 'Newer'},
            format='json')
        prop = SpotlightFieldProperty.objects.get()
        latest, earlier = prop.history.all()[:2]
        self.assertEqual(latest.display_name, 'Newer')
        self.assertEqual(earlier.display_name, 'Certification Status')
        self.assertEqual(latest.history_user, self.user)

    def test_visibility_needs_permission(self):
        """Visibility controls are admin-granted; default is visible."""
        self.assertTrue(self.client.get(URL).data['available_in_api'])
        denied = self.client.patch(
            f'{URL}visibility/', {'available_in_api': False}, format='json')
        self.assertEqual(denied.status_code, 403)
        self.contributor.can_control_spotlight_visibility = True
        self.contributor.save()
        allowed = self.client.patch(
            f'{URL}visibility/', {'available_in_api': False}, format='json')
        self.assertEqual(allowed.status_code, 200)
        self.assertFalse(allowed.data['available_in_api'])


class GoLiveTest(TestCase):
    """The go-live date rules and the daily command."""

    def setUp(self):
        """Create a partner with one approved, one unapproved field."""
        _, self.contributor = make_contributor('gl@example.com', 'GoLive')
        self.spotlight = SpotlightField.get_or_create_for(self.contributor)
        self.approved = SpotlightFieldProperty.objects.create(
            spotlight_field=self.spotlight, name='a', display_name='A')
        self.approved.approve(user=None)
        self.unapproved = SpotlightFieldProperty.objects.create(
            spotlight_field=self.spotlight, name='b', display_name='B')

    def test_command_activates_approved_fields_once(self):
        """On the date approved fields go active; a later opt-out sticks."""
        self.spotlight.set_go_live_date(past())
        self.approved.refresh_from_db()
        self.assertTrue(self.approved.active)
        self.assertFalse(
            SpotlightFieldProperty.objects.get(pk=self.unapproved.pk).active)
        self.approved.set_active(False, None, is_admin=False)
        call_command('apply_spotlight_go_live', stdout=StringIO())
        self.approved.refresh_from_db()
        self.assertFalse(self.approved.active)

    def test_command_applies_when_date_arrives(self):
        """A date that has just come due is applied by the command."""
        SpotlightField.objects.filter(pk=self.spotlight.pk).update(
            go_live_date=timezone.localdate(), go_live_applied=False)
        call_command('apply_spotlight_go_live', stdout=StringIO())
        self.approved.refresh_from_db()
        self.assertTrue(self.approved.active)

    def test_moving_date_later_deactivates_active_fields(self):
        """Pushing the date into the future switches active fields off."""
        self.approved.set_active(True, None, is_admin=True)
        self.spotlight.set_go_live_date(future())
        self.approved.refresh_from_db()
        self.assertFalse(self.approved.active)

    def test_admin_may_activate_before_the_date(self):
        """Admins are not held back by a pending go-live date."""
        self.spotlight.set_go_live_date(future())
        self.approved.set_active(True, None, is_admin=True)
        self.approved.refresh_from_db()
        self.assertTrue(self.approved.active)

    def test_new_field_after_go_live_starts_inactive(self):
        """Fields added after the date wait for approval, inactive."""
        self.spotlight.set_go_live_date(past())
        new = SpotlightFieldProperty.objects.create(
            spotlight_field=self.spotlight, name='c', display_name='C')
        self.assertFalse(new.approved)
        self.assertFalse(new.active)
        new.approve(user=None, activate=True)
        new.refresh_from_db()
        self.assertTrue(new.active)


class SpotlightAdminTest(TestCase):
    """The admin actions and the Edited-by-partners filter."""

    def setUp(self):
        """Create a partner with two unapproved fields."""
        self.admin_user = User.objects.create(
            email='admin@example.com', is_staff=True, is_superuser=True)
        _, self.contributor = make_contributor('ad@example.com', 'AdminTest')
        self.spotlight = SpotlightField.get_or_create_for(self.contributor)
        for name in ('a', 'b'):
            SpotlightFieldProperty.objects.create(
                spotlight_field=self.spotlight, name=name,
                display_name=name.upper())
        self.model_admin = SpotlightFieldAdmin(SpotlightField, AdminSite())
        self.request = RequestFactory().get('/')
        self.request.user = self.admin_user
        self.request._messages = type(
            'M', (), {'add': lambda *a, **k: None})()
        self.queryset = SpotlightField.objects.all()

    def test_activate_all_skips_unapproved(self):
        """Activate all only switches on fields that are approved."""
        self.model_admin.activate_all(self.request, self.queryset)
        self.assertEqual(
            SpotlightFieldProperty.objects.filter(active=True).count(), 0)

    def test_approve_then_activate_all(self):
        """Approve all and Activate all are separate steps."""
        self.model_admin.approve_all(self.request, self.queryset)
        self.assertEqual(
            SpotlightFieldProperty.objects.filter(
                approved=True, active=False).count(), 2)
        self.model_admin.activate_all(self.request, self.queryset)
        self.assertEqual(
            SpotlightFieldProperty.objects.filter(active=True).count(), 2)
        self.model_admin.deactivate_all(self.request, self.queryset)
        self.assertEqual(
            SpotlightFieldProperty.objects.filter(active=True).count(), 0)

    def test_approve_and_activate_all(self):
        """The combined action approves and switches on in one step."""
        self.model_admin.approve_and_activate_all(
            self.request, self.queryset)
        self.assertEqual(
            SpotlightFieldProperty.objects.filter(
                approved=True, active=True).count(), 2)

    def test_json_mirrors_active_state(self):
        """The partner field's JSON tracks each field's active setting."""
        self.model_admin.approve_and_activate_all(
            self.request, self.queryset)
        props = self.spotlight.partner_field.json_schema['properties']
        self.assertTrue(props['a']['active'])
        self.model_admin.deactivate_all(self.request, self.queryset)
        self.spotlight.partner_field.refresh_from_db()
        self.assertFalse(
            self.spotlight.partner_field.json_schema['properties']['a'][
                'active'])

    def test_admin_can_not_activate_unapproved_directly(self):
        """The model refuses to save an active-but-unapproved field."""
        prop = SpotlightFieldProperty.objects.get(name='a')
        prop.active = True
        with self.assertRaises(ValidationError):
            prop.save()

    def test_edited_by_partners_filter_and_ordering(self):
        """The filter keeps edited sets and orders newest edit first."""
        _, other = make_contributor('o@example.com', 'Other')
        older = SpotlightField.get_or_create_for(other)
        now = timezone.now()
        SpotlightField.objects.filter(pk=older.pk).update(
            last_partner_edit_at=now - datetime.timedelta(days=2))
        SpotlightField.objects.filter(pk=self.spotlight.pk).update(
            last_partner_edit_at=now)
        ordered = list(self.model_admin.get_queryset(self.request))
        self.assertEqual(ordered[0].pk, self.spotlight.pk)
        spot_filter = EditedByPartnersFilter(
            self.request, {'edited_by_partners': 'yes'}, SpotlightField,
            self.model_admin)
        self.assertEqual(
            spot_filter.queryset(self.request, self.queryset).count(), 2)

    def test_cannot_delete(self):
        """Spotlight fields cannot be deleted, in admin or in code."""
        self.assertFalse(
            self.model_admin.has_delete_permission(self.request))
        with self.assertRaises(ValidationError):
            SpotlightFieldProperty.objects.first().delete()
