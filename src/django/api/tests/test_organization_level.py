from datetime import timedelta
from io import StringIO

from django.contrib.gis.geos import Point
from django.core import mail
from django.core.cache import caches
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from api.constants import FacilityClaimStatuses
from api.models import (
    Contributor,
    Facility,
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    ModerationEvent,
    Organization,
    OrganizationInvitation,
    OrganizationMembership,
    Sector,
    Source,
    User,
)
from api.models.facility.facility_index import FacilityIndex as Index
from api.services.organization_service import (
    ORGANIZATION_LEVEL_SWITCH,
    accept_invitation,
    create_invitation,
    stamp_member_contributions,
)

PASSWORD = 'example123'


class OrganizationTestBase(APITestCase):
    """
    One organization with an Admin and a Member, an outsider with an
    account but no organization, and a second organization.
    """

    def setUp(self):
        # The invitation throttle keys on user id in the shared
        # 'api_throttling' cache, which outlives a test run.
        caches['api_throttling'].clear()
        Sector.objects.get_or_create(name='Apparel')

        self.admin_user, self.admin_contributor = self.make_account(
            'admin@brand.example', 'Brand (Admin account)'
        )
        self.member_user, self.member_contributor = self.make_account(
            'member@brand.example', 'Brand (Member account)'
        )
        self.outsider_user, self.outsider_contributor = self.make_account(
            'outsider@elsewhere.example', 'Elsewhere'
        )
        self.other_user, self.other_contributor = self.make_account(
            'admin@rival.example', 'Rival'
        )

        self.organization = Organization.objects.create(
            name='Brand', seat_limit=3
        )
        self.admin_membership = OrganizationMembership.objects.create(
            organization=self.organization,
            user=self.admin_user,
            role=OrganizationMembership.ADMIN,
        )
        self.member_membership = OrganizationMembership.objects.create(
            organization=self.organization,
            user=self.member_user,
            role=OrganizationMembership.MEMBER,
        )

        self.other_organization = Organization.objects.create(name='Rival')
        OrganizationMembership.objects.create(
            organization=self.other_organization,
            user=self.other_user,
            role=OrganizationMembership.ADMIN,
        )

    @staticmethod
    def make_account(email, contributor_name):
        user = User.objects.create(email=email)
        user.set_password(PASSWORD)
        user.save()
        contributor = Contributor.objects.create(
            admin=user,
            name=contributor_name,
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        return user, contributor

    def login(self, user):
        self.client.logout()
        self.client.login(email=user.email, password=PASSWORD)

    def url(self, name, *args, organization=None):
        organization = organization or self.organization
        return reverse(name, args=(organization.uuid, *args))

    def make_submission(self, contributor, name='Factory', country='US',
                        source_type=Source.LIST, facility=None,
                        is_active=True):
        """
        A source with one matched item pointing at a production
        location, the way a processed list or approved contribution
        leaves the database.
        """
        facility_list = None
        if source_type == Source.LIST:
            facility_list = FacilityList.objects.create(
                header='header', file_name='one', name='{} list'.format(name)
            )
        source = Source.objects.create(
            facility_list=facility_list,
            source_type=source_type,
            is_active=is_active,
            is_public=True,
            contributor=contributor,
        )
        item = FacilityListItem.objects.create(
            name=name,
            address='1 Example Street',
            country_code=country,
            sector=['Apparel'],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )
        if facility is None:
            facility = Facility.objects.create(
                name=name,
                address='1 Example Street',
                country_code=country,
                location=Point(0, 0),
                created_from=item,
            )
        item.facility = facility
        item.save()
        FacilityMatch.objects.create(
            facility_list_item=item,
            facility=facility,
            status=FacilityMatch.AUTOMATIC,
            is_active=True,
            results={},
            confidence=1,
        )
        return source, item, facility


class OrganizationSwitchOffTest(OrganizationTestBase):
    """With the switch off the feature does not exist."""

    def test_endpoints_answer_404(self):
        self.login(self.admin_user)
        urls = [
            reverse('organization-current'),
            self.url('organization-members'),
            self.url('organization-invitations'),
            self.url('organization-contributions'),
            self.url('organization-dashboard-summary'),
            reverse('organization-my-invitations'),
        ]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 404, url)

    def test_nothing_is_stamped(self):
        source = Source.objects.create(
            source_type=Source.SINGLE, contributor=self.member_contributor
        )
        self.assertIsNone(source.organization_id)

    def test_user_payload_has_no_organization(self):
        self.login(self.member_user)
        response = self.client.get(
            '/user-profile/{}/'.format(self.member_user.id)
        )
        self.assertEqual(response.status_code, 200)


@override_switch(ORGANIZATION_LEVEL_SWITCH, active=True)
class OrganizationModelRulesTest(OrganizationTestBase):
    def test_a_user_has_one_active_membership(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            OrganizationMembership.objects.create(
                organization=self.other_organization,
                user=self.member_user,
            )

    def test_a_removed_membership_frees_the_user(self):
        self.member_membership.status = OrganizationMembership.REMOVED
        self.member_membership.save()
        OrganizationMembership.objects.create(
            organization=self.other_organization, user=self.member_user
        )

    def test_seats_count_members_and_open_invitations(self):
        self.assertEqual(self.organization.seats_used, 2)
        create_invitation(
            self.organization, self.admin_user,
            self.outsider_user.email, OrganizationMembership.MEMBER,
        )
        self.assertEqual(self.organization.seats_used, 3)
        self.assertFalse(self.organization.has_free_seat)

    def test_expired_invitation_frees_its_seat(self):
        invitation = create_invitation(
            self.organization, self.admin_user,
            self.outsider_user.email, OrganizationMembership.MEMBER,
        )
        invitation.expires_at = timezone.now() - timedelta(minutes=1)
        invitation.save()
        self.assertEqual(self.organization.seats_used, 2)


@override_switch(ORGANIZATION_LEVEL_SWITCH, active=True)
class OrganizationStampingTest(OrganizationTestBase):
    def test_new_source_of_a_member_is_stamped(self):
        source = Source.objects.create(
            source_type=Source.SINGLE, contributor=self.member_contributor
        )
        self.assertEqual(source.organization_id, self.organization.id)

    def test_new_source_of_a_non_member_is_not_stamped(self):
        source = Source.objects.create(
            source_type=Source.SINGLE, contributor=self.outsider_contributor
        )
        self.assertIsNone(source.organization_id)

    def test_moderation_event_and_claim_are_stamped(self):
        event = ModerationEvent.objects.create(
            contributor=self.member_contributor,
            request_type=ModerationEvent.RequestType.CREATE,
            source=ModerationEvent.Source.SLC,
        )
        self.assertEqual(event.organization_id, self.organization.id)

        _, _, facility = self.make_submission(self.outsider_contributor)
        claim = FacilityClaim.objects.create(
            contributor=self.member_contributor,
            facility=facility,
            contact_person='Name',
        )
        self.assertEqual(claim.organization_id, self.organization.id)

    def test_nothing_is_stamped_for_an_inactive_organization(self):
        self.organization.is_active = False
        self.organization.save()
        source = Source.objects.create(
            source_type=Source.SINGLE, contributor=self.member_contributor
        )
        self.assertIsNone(source.organization_id)

    def test_stamp_stays_after_the_member_leaves(self):
        source = Source.objects.create(
            source_type=Source.SINGLE, contributor=self.member_contributor
        )
        self.member_membership.status = OrganizationMembership.REMOVED
        self.member_membership.save()

        source.refresh_from_db()
        self.assertEqual(source.organization_id, self.organization.id)

        later = Source.objects.create(
            source_type=Source.SINGLE, contributor=self.member_contributor
        )
        self.assertIsNone(later.organization_id)

    def test_saving_an_existing_source_does_not_restamp(self):
        source = Source.objects.create(
            source_type=Source.SINGLE, contributor=self.outsider_contributor
        )
        OrganizationMembership.objects.create(
            organization=self.other_organization, user=self.outsider_user
        )
        source.is_public = False
        source.save()
        source.refresh_from_db()
        self.assertIsNone(source.organization_id)

    def test_joining_attributes_earlier_contributions(self):
        source, _, facility = self.make_submission(self.outsider_contributor)
        event = ModerationEvent.objects.create(
            contributor=self.outsider_contributor,
            request_type=ModerationEvent.RequestType.CREATE,
        )
        claim = FacilityClaim.objects.create(
            contributor=self.outsider_contributor,
            facility=facility,
            contact_person='Name',
        )
        invitation = create_invitation(
            self.organization, self.admin_user,
            self.outsider_user.email, OrganizationMembership.MEMBER,
        )
        accept_invitation(invitation, self.outsider_user)

        for row in (source, event, claim):
            row.refresh_from_db()
            self.assertEqual(row.organization_id, self.organization.id)

    def test_contributions_held_by_a_previous_organization_stay_there(self):
        source = Source.objects.create(
            source_type=Source.SINGLE, contributor=self.member_contributor
        )
        self.member_membership.status = OrganizationMembership.REMOVED
        self.member_membership.save()
        membership = OrganizationMembership.objects.create(
            organization=self.other_organization, user=self.member_user
        )

        counts = stamp_member_contributions(membership)

        source.refresh_from_db()
        self.assertEqual(source.organization_id, self.organization.id)
        self.assertEqual(counts['Source'], 0)

    def test_stamping_reindexes_production_locations(self):
        """
        The facility index names the organization a contribution is
        recorded against, so attributing a source to an organization
        has to refresh it: the guard that migration 0271 put on the
        indexing trigger is removed by migration 0272.
        """
        source, _, facility = self.make_submission(self.outsider_contributor)
        marker = timezone.now() - timedelta(days=30)
        Index.objects.filter(id=facility.id).update(updated_at=marker)

        Source.objects.filter(pk=source.pk).update(
            organization=self.organization
        )
        index = Index.objects.get(id=facility.id)
        self.assertGreater(index.updated_at, marker)
        self.assertEqual(
            [entry['contributor_name'] for entry in index.contributors],
            ['Brand'],
        )

    def test_command_reconciles_missed_rows(self):
        source = Source.objects.create(
            source_type=Source.SINGLE, contributor=self.member_contributor
        )
        Source.objects.filter(pk=source.pk).update(organization=None)

        out = StringIO()
        call_command('stamp_member_contributions', stdout=out)
        source.refresh_from_db()
        self.assertEqual(source.organization_id, self.organization.id)
        self.assertIn('1 Source', out.getvalue())

        out = StringIO()
        call_command('stamp_member_contributions', stdout=out)
        self.assertIn('Rows attributed: 0', out.getvalue())


@override_settings(DEBUG=True)
@override_switch(ORGANIZATION_LEVEL_SWITCH, active=True)
class OrganizationMembersApiTest(OrganizationTestBase):
    def test_current_organization(self):
        self.login(self.member_user)
        response = self.client.get(reverse('organization-current'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Brand')
        self.assertEqual(response.data['role'], 'MEMBER')
        self.assertEqual(response.data['seats_used'], 2)
        self.assertFalse(response.data['dashboard_enabled'])

    def test_current_organization_is_404_without_one(self):
        self.login(self.outsider_user)
        response = self.client.get(reverse('organization-current'))
        self.assertEqual(response.status_code, 404)

    def test_anonymous_is_refused(self):
        response = self.client.get(reverse('organization-current'))
        self.assertIn(response.status_code, (401, 403))

    def test_members_list_is_visible_to_members_only(self):
        self.login(self.member_user)
        response = self.client.get(self.url('organization-members'))
        self.assertEqual(response.status_code, 200)
        emails = [m['email'] for m in response.data['members']]
        self.assertEqual(
            emails, ['admin@brand.example', 'member@brand.example']
        )
        self.assertEqual(response.data['seat_limit'], 3)

        for user in (self.outsider_user, self.other_user):
            self.login(user)
            response = self.client.get(self.url('organization-members'))
            self.assertEqual(response.status_code, 403)

    def test_only_an_admin_changes_roles(self):
        url = self.url(
            'organization-member-detail', self.member_membership.uuid
        )
        self.login(self.member_user)
        response = self.client.patch(url, {'role': 'ADMIN'})
        self.assertEqual(response.status_code, 403)

        self.login(self.admin_user)
        response = self.client.patch(url, {'role': 'ADMIN'})
        self.assertEqual(response.status_code, 200)
        self.member_membership.refresh_from_db()
        self.assertTrue(self.member_membership.is_admin)

    def test_the_last_admin_cannot_be_demoted_or_leave(self):
        url = self.url(
            'organization-member-detail', self.admin_membership.uuid
        )
        self.login(self.admin_user)
        response = self.client.patch(url, {'role': 'MEMBER'})
        self.assertEqual(response.status_code, 400)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 400)
        self.admin_membership.refresh_from_db()
        self.assertTrue(self.admin_membership.is_active)

    def test_admin_removes_a_member(self):
        self.login(self.admin_user)
        response = self.client.delete(self.url(
            'organization-member-detail', self.member_membership.uuid
        ))
        self.assertEqual(response.status_code, 204)
        self.member_membership.refresh_from_db()
        self.assertEqual(
            self.member_membership.status, OrganizationMembership.REMOVED
        )
        self.assertEqual(self.member_membership.removed_by, self.admin_user)
        # The account and its contributor are untouched.
        self.assertTrue(
            Contributor.objects.filter(admin=self.member_user).exists()
        )

    def test_a_member_can_leave_but_not_remove_others(self):
        self.login(self.member_user)
        response = self.client.delete(self.url(
            'organization-member-detail', self.admin_membership.uuid
        ))
        self.assertEqual(response.status_code, 403)

        response = self.client.delete(self.url(
            'organization-member-detail', self.member_membership.uuid
        ))
        self.assertEqual(response.status_code, 204)

    def test_user_payload_carries_the_organization(self):
        self.login(self.member_user)
        response = self.client.get(
            '/user-profile/{}/'.format(self.member_user.id)
        )
        self.assertEqual(response.status_code, 200)

        from api.serializers import UserSerializer
        data = UserSerializer(self.member_user).data
        self.assertEqual(data['organization']['name'], 'Brand')
        self.assertEqual(data['organization']['role'], 'MEMBER')
        self.assertIsNone(
            UserSerializer(self.outsider_user).data['organization']
        )


@override_settings(DEBUG=True)
@override_switch(ORGANIZATION_LEVEL_SWITCH, active=True)
class OrganizationInvitationsApiTest(OrganizationTestBase):
    def invite(self, email, role='MEMBER'):
        return self.client.post(
            self.url('organization-invitations'),
            {'email': email, 'role': role},
        )

    def test_only_an_admin_invites(self):
        self.login(self.member_user)
        response = self.invite(self.outsider_user.email)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(OrganizationInvitation.objects.count(), 0)

    def test_admin_invites_an_existing_account(self):
        self.login(self.admin_user)
        response = self.invite(' Outsider@Elsewhere.example ')
        self.assertEqual(response.status_code, 201, response.data)

        invitation = OrganizationInvitation.objects.get()
        self.assertEqual(invitation.invited_user, self.outsider_user)
        self.assertEqual(invitation.invited_by, self.admin_user)
        self.assertEqual(invitation.status, OrganizationInvitation.PENDING)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.outsider_user.email])
        self.assertIn('Brand', mail.outbox[0].subject)
        self.assertIn('/organization', mail.outbox[0].body)
        self.assertNotIn('/settings', mail.outbox[0].body)

    def test_unknown_email_sends_nothing(self):
        self.login(self.admin_user)
        response = self.invite('nobody@nowhere.example')
        self.assertEqual(response.status_code, 400)
        self.assertIn('register', response.data['email'][0])
        self.assertEqual(OrganizationInvitation.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_someone_in_an_organization_cannot_be_invited(self):
        self.login(self.admin_user)
        response = self.invite(self.other_user.email)
        self.assertEqual(response.status_code, 400)
        response = self.invite(self.member_user.email)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(mail.outbox), 0)

    def test_no_second_invitation_while_one_waits(self):
        self.login(self.admin_user)
        self.assertEqual(
            self.invite(self.outsider_user.email).status_code, 201
        )
        self.assertEqual(
            self.invite(self.outsider_user.email).status_code, 400
        )

    def test_seat_limit_refuses_the_invitation(self):
        self.organization.seat_limit = 2
        self.organization.save()
        self.login(self.admin_user)
        response = self.invite(self.outsider_user.email)
        self.assertEqual(response.status_code, 400)
        self.assertIn('no free seat', response.data['email'][0])

    def test_admin_lists_and_revokes_invitations(self):
        self.login(self.admin_user)
        self.invite(self.outsider_user.email)
        invitation = OrganizationInvitation.objects.get()

        response = self.client.get(self.url('organization-invitations'))
        self.assertEqual(len(response.data), 1)

        response = self.client.delete(self.url(
            'organization-invitation-detail', invitation.uuid
        ))
        self.assertEqual(response.status_code, 204)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, OrganizationInvitation.REVOKED)

        self.login(self.outsider_user)
        response = self.client.post(reverse(
            'organization-invitation-accept', args=(invitation.uuid,)
        ))
        self.assertEqual(response.status_code, 400)

    def test_invitee_sees_and_accepts(self):
        self.login(self.admin_user)
        self.invite(self.outsider_user.email, role='ADMIN')
        invitation = OrganizationInvitation.objects.get()
        mail.outbox.clear()

        self.login(self.outsider_user)
        response = self.client.get(reverse('organization-my-invitations'))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['organization_name'], 'Brand')

        response = self.client.post(reverse(
            'organization-invitation-accept', args=(invitation.uuid,)
        ))
        self.assertEqual(response.status_code, 200, response.data)

        membership = OrganizationMembership.objects.get(
            user=self.outsider_user
        )
        self.assertEqual(membership.organization, self.organization)
        self.assertEqual(membership.role, OrganizationMembership.ADMIN)
        self.assertEqual(membership.invited_by, self.admin_user)

        # The inviting Admin is told.
        self.assertEqual(mail.outbox[0].to, [self.admin_user.email])
        self.assertIn('accepted', mail.outbox[0].subject)

        response = self.client.get(reverse('organization-my-invitations'))
        self.assertEqual(response.data, [])

    def test_invitee_declines(self):
        self.login(self.admin_user)
        self.invite(self.outsider_user.email)
        invitation = OrganizationInvitation.objects.get()

        self.login(self.outsider_user)
        response = self.client.post(reverse(
            'organization-invitation-decline', args=(invitation.uuid,)
        ))
        self.assertEqual(response.status_code, 200)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, OrganizationInvitation.DECLINED)
        self.assertFalse(
            OrganizationMembership.objects
            .filter(user=self.outsider_user).exists()
        )
        self.assertEqual(self.organization.seats_used, 2)

    def test_only_the_invited_user_can_answer(self):
        self.login(self.admin_user)
        self.invite(self.outsider_user.email)
        invitation = OrganizationInvitation.objects.get()

        third_user, _ = self.make_account('third@example.com', 'Third')
        self.login(third_user)
        response = self.client.post(reverse(
            'organization-invitation-accept', args=(invitation.uuid,)
        ))
        self.assertEqual(response.status_code, 404)

    def test_expired_invitation_cannot_be_accepted(self):
        self.login(self.admin_user)
        self.invite(self.outsider_user.email)
        invitation = OrganizationInvitation.objects.get()
        invitation.expires_at = timezone.now() - timedelta(minutes=1)
        invitation.save()

        self.login(self.outsider_user)
        self.assertEqual(
            self.client.get(reverse('organization-my-invitations')).data, []
        )
        response = self.client.post(reverse(
            'organization-invitation-accept', args=(invitation.uuid,)
        ))
        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            OrganizationMembership.objects
            .filter(user=self.outsider_user).exists()
        )

        # The seat is free again, so the Admin can invite once more,
        # which also closes the invitation that ran out.
        self.login(self.admin_user)
        self.assertEqual(
            self.invite(self.outsider_user.email).status_code, 201
        )
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, OrganizationInvitation.EXPIRED)


@override_settings(DEBUG=True)
@override_switch(ORGANIZATION_LEVEL_SWITCH, active=True)
class OrganizationContributionsApiTest(OrganizationTestBase):
    def test_members_see_each_others_lists_with_who_submitted(self):
        self.make_submission(self.admin_contributor, name='Admin Factory')
        self.make_submission(self.member_contributor, name='Member Factory')
        self.make_submission(self.other_contributor, name='Rival Factory')

        self.login(self.member_user)
        response = self.client.get(self.url('organization-contributions'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        names = {row['name'] for row in response.data['results']}
        self.assertEqual(names, {'Admin Factory list', 'Member Factory list'})
        submitters = {
            row['submitted_by']['email'] for row in response.data['results']
        }
        self.assertEqual(
            submitters, {'admin@brand.example', 'member@brand.example'}
        )

        response = self.client.get(
            self.url('organization-contributions'),
            {'member': self.admin_contributor.id},
        )
        self.assertEqual(response.data['count'], 1)

    def test_moderation_events_and_claims(self):
        ModerationEvent.objects.create(
            contributor=self.member_contributor,
            request_type=ModerationEvent.RequestType.CREATE,
            source=ModerationEvent.Source.SLC,
            cleaned_data={'name': 'New Mill', 'country_code': 'IN'},
        )
        _, _, facility = self.make_submission(self.other_contributor)
        FacilityClaim.objects.create(
            contributor=self.admin_contributor,
            facility=facility,
            contact_person='Name',
        )

        self.login(self.member_user)
        response = self.client.get(
            self.url('organization-contributions'), {'type': 'contributions'}
        )
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'New Mill')

        response = self.client.get(
            self.url('organization-contributions'), {'type': 'claims'}
        )
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['os_id'], facility.id)

    def test_outsiders_are_refused(self):
        self.login(self.other_user)
        response = self.client.get(self.url('organization-contributions'))
        self.assertEqual(response.status_code, 403)


@override_settings(DEBUG=True)
@override_switch(ORGANIZATION_LEVEL_SWITCH, active=True)
@override_switch('claim_a_facility', active=True)
class OrganizationDashboardApiTest(OrganizationTestBase):
    def setUp(self):
        super().setUp()
        self.organization.dashboard_enabled = True
        self.organization.save()

        # Two members submit the same production location, the Member
        # submits a second one alone, and a rival submits a third.
        _, _, self.shared = self.make_submission(
            self.admin_contributor, name='Shared Factory', country='US'
        )
        self.make_submission(
            self.member_contributor, name='Shared Factory',
            facility=self.shared, source_type=Source.SINGLE,
        )
        _, _, self.solo = self.make_submission(
            self.member_contributor, name='Solo Mill', country='IN'
        )
        self.make_submission(self.other_contributor, name='Rival Factory')

        self.claim = FacilityClaim.objects.create(
            contributor=self.outsider_contributor,
            facility=self.solo,
            contact_person='Owner',
            facility_description='A mill',
            facility_website='https://mill.example',
            facility_website_publicly_visible=False,
            point_of_contact_person_name='Private Person',
            point_of_contact_email='private@mill.example',
            point_of_contact_publicly_visible=False,
            facility_workers_count='120',
            status=FacilityClaimStatuses.APPROVED,
            status_change_date=timezone.now(),
        )

    def test_dashboard_is_refused_until_switched_on(self):
        self.organization.dashboard_enabled = False
        self.organization.save()
        self.login(self.admin_user)
        for name in ('organization-dashboard-summary',
                     'organization-dashboard-facilities'):
            response = self.client.get(self.url(name))
            self.assertEqual(response.status_code, 403, name)

    def test_every_member_sees_it_and_outsiders_do_not(self):
        for user in (self.admin_user, self.member_user):
            self.login(user)
            response = self.client.get(
                self.url('organization-dashboard-summary')
            )
            self.assertEqual(response.status_code, 200)

        for user in (self.other_user, self.outsider_user):
            self.login(user)
            response = self.client.get(
                self.url('organization-dashboard-summary')
            )
            self.assertEqual(response.status_code, 403)

    def test_summary_counts_a_shared_location_once(self):
        ModerationEvent.objects.create(
            contributor=self.member_contributor,
            request_type=ModerationEvent.RequestType.CREATE,
        )
        self.login(self.member_user)
        data = self.client.get(
            self.url('organization-dashboard-summary')
        ).data

        self.assertEqual(data['total_facilities'], 2)
        self.assertEqual(data['total_submissions'], 3)
        self.assertEqual(data['claimed_facilities'], 1)
        self.assertEqual(data['unclaimed_facilities'], 1)
        self.assertEqual(data['pending_moderation'], 1)

        by_member = {
            row['contributor_id']: row for row in data['by_member']
        }
        self.assertEqual(
            by_member[self.admin_contributor.id]['facilities'], 1
        )
        self.assertEqual(
            by_member[self.member_contributor.id]['facilities'], 2
        )
        self.assertEqual(
            {row['country_code']: row['facilities']
             for row in data['by_country']},
            {'US': 1, 'IN': 1},
        )
        self.assertEqual(
            data['by_sector'], [{'sector': 'Apparel', 'facilities': 2}]
        )
        self.assertEqual(data['by_source_type']['list']['submissions'], 2)
        self.assertEqual(data['by_source_type']['single']['submissions'], 1)
        self.assertEqual(len(data['by_month']), 1)
        self.assertEqual(data['by_month'][0]['submissions'], 3)

    def test_summary_filters(self):
        self.login(self.admin_user)
        data = self.client.get(
            self.url('organization-dashboard-summary'),
            {'member': self.admin_contributor.id},
        ).data
        self.assertEqual(data['total_facilities'], 1)

        data = self.client.get(
            self.url('organization-dashboard-summary'), {'claimed': 'true'}
        ).data
        self.assertEqual(data['total_facilities'], 1)

        tomorrow = (timezone.now() + timedelta(days=1)).date().isoformat()
        data = self.client.get(
            self.url('organization-dashboard-summary'),
            {'date_from': tomorrow},
        ).data
        self.assertEqual(data['total_facilities'], 0)

    def test_replaced_lists_do_not_count(self):
        self.make_submission(
            self.admin_contributor, name='Old Factory', is_active=False
        )
        self.login(self.admin_user)
        data = self.client.get(
            self.url('organization-dashboard-summary')
        ).data
        self.assertEqual(data['total_facilities'], 2)

    def test_facilities_table(self):
        self.login(self.member_user)
        response = self.client.get(
            self.url('organization-dashboard-facilities')
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)

        rows = {
            (row['os_id'], row['submitted_by']['contributor_id']): row
            for row in response.data['results']
        }
        solo = rows[(self.solo.id, self.member_contributor.id)]
        self.assertTrue(solo['is_claimed'])
        self.assertIsNotNone(solo['claimed_at'])
        self.assertEqual(solo['country_name'], 'India')
        self.assertEqual(solo['list']['name'], 'Solo Mill list')

        shared_single = rows[(self.shared.id, self.member_contributor.id)]
        self.assertFalse(shared_single['is_claimed'])
        self.assertIsNone(shared_single['list'])
        self.assertEqual(shared_single['source_type'], Source.SINGLE)

        response = self.client.get(
            self.url('organization-dashboard-facilities'), {'country': 'in'}
        )
        self.assertEqual(response.data['count'], 1)

    def test_a_former_members_submissions_stay(self):
        self.member_membership.status = OrganizationMembership.REMOVED
        self.member_membership.save()
        self.login(self.admin_user)
        data = self.client.get(
            self.url('organization-dashboard-summary')
        ).data
        self.assertEqual(data['total_facilities'], 2)

    def test_facility_detail_shows_only_public_claim_data(self):
        self.login(self.admin_user)
        response = self.client.get(self.url(
            'organization-dashboard-facility-detail', self.solo.id
        ))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_claimed'])
        self.assertEqual(len(response.data['submissions']), 1)

        claim = response.data['claim']
        self.assertEqual(claim['facility']['description'], 'A mill')
        self.assertEqual(claim['facility']['workers_count'], '120')
        # What the claimant did not publish is not shown.
        self.assertIsNone(claim['facility']['website'])
        self.assertIsNone(claim['contact'])
        self.assertNotIn('contributor', claim)
        self.assertNotIn('private@mill.example', str(response.data))
        self.assertEqual(claim['claimed_by'], 'Elsewhere')

    def test_facility_detail_of_an_unclaimed_location(self):
        self.login(self.member_user)
        response = self.client.get(self.url(
            'organization-dashboard-facility-detail', self.shared.id
        ))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['is_claimed'])
        self.assertIsNone(response.data['claim'])
        self.assertEqual(len(response.data['submissions']), 2)

    def test_facility_detail_of_a_location_not_submitted_is_404(self):
        _, _, rival = self.make_submission(
            self.other_contributor, name='Rival Two'
        )
        self.login(self.admin_user)
        response = self.client.get(self.url(
            'organization-dashboard-facility-detail', rival.id
        ))
        self.assertEqual(response.status_code, 404)


@override_settings(DEBUG=True)
@override_switch(ORGANIZATION_LEVEL_SWITCH, active=True)
class OrganizationAdminSiteTest(OrganizationTestBase):
    def setUp(self):
        super().setUp()
        self.staff = User.objects.create(
            email='staff@oshub.example', is_staff=True, is_superuser=True
        )
        self.staff.set_password(PASSWORD)
        self.staff.save()
        self.client.login(email=self.staff.email, password=PASSWORD)

    def post_new_organization(self, name, user, role):
        return self.client.post(
            reverse('admin:api_organization_add'),
            {
                'name': name,
                'legal_name': '',
                'parent_entity_name': '',
                'seat_limit': 5,
                'dashboard_enabled': 'on',
                'is_active': 'on',
                'notes': '',
                'memberships-TOTAL_FORMS': 1,
                'memberships-INITIAL_FORMS': 0,
                'memberships-MIN_NUM_FORMS': 0,
                'memberships-MAX_NUM_FORMS': 1000,
                'memberships-0-user': user.id,
                'memberships-0-role': role,
                'memberships-0-status': 'ACTIVE',
                'memberships-0-joined_at_0': '2026-11-12',
                'memberships-0-joined_at_1': '10:00:00',
                'invitations-TOTAL_FORMS': 0,
                'invitations-INITIAL_FORMS': 0,
                'invitations-MIN_NUM_FORMS': 0,
                'invitations-MAX_NUM_FORMS': 0,
            },
        )

    def test_staff_create_an_organization_with_its_first_admin(self):
        source = Source.objects.create(
            source_type=Source.SINGLE, contributor=self.outsider_contributor
        )
        response = self.post_new_organization(
            'New Org', self.outsider_user, 'ADMIN'
        )
        self.assertEqual(response.status_code, 302, response.content[:2000])

        organization = Organization.objects.get(name='New Org')
        self.assertEqual(organization.created_by, self.staff)
        self.assertTrue(organization.dashboard_enabled)
        membership = organization.memberships.get()
        self.assertEqual(membership.user, self.outsider_user)
        self.assertTrue(membership.is_admin)

        # The new member's earlier contributions follow them in.
        source.refresh_from_db()
        self.assertEqual(source.organization, organization)
        self.assertEqual(mail.outbox[-1].to, [self.outsider_user.email])

    def test_an_organization_needs_an_admin(self):
        response = self.post_new_organization(
            'No Admin Org', self.outsider_user, 'MEMBER'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Organization.objects.filter(name='No Admin Org').exists()
        )

    def test_a_user_already_in_an_organization_is_refused(self):
        response = self.post_new_organization(
            'Second Org', self.member_user, 'ADMIN'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Organization.objects.filter(name='Second Org').exists()
        )
