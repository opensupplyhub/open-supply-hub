from datetime import timedelta

from allauth.account.models import EmailAddress
from django.contrib.auth.models import Group
from django.contrib.gis.geos import Point
from django.urls import reverse
from django.utils import timezone
from waffle.testutils import override_switch

from api.constants import FacilityClaimStatuses, FeatureGroups
from api.models import (
    ApiLimit,
    DownloadLog,
    FacilityClaim,
    FacilityListItem,
    FacilityMatch,
    ModerationEvent,
    Organization,
    OrganizationMembership,
    RequestLog,
)
from api.models.facility_download_limit import FacilityDownloadLimit
from api.services.organization_service import (
    ORGANIZATION_LEVEL_SWITCH,
    create_invitation,
    email_domain,
)
from api.tests.test_organization_level import OrganizationTestBase


@override_switch(ORGANIZATION_LEVEL_SWITCH, active=True)
class OrganizationDetailsTest(OrganizationTestBase):
    def test_a_new_organization_starts_with_three_seats(self):
        self.assertEqual(Organization.objects.create(name='New').seat_limit, 3)

    def test_members_see_the_legal_and_parent_entity_names(self):
        self.organization.legal_name = 'Brand Holdings Ltd'
        self.organization.parent_entity_name = 'Brand Group'
        self.organization.save()

        self.login(self.member_user)
        response = self.client.get(reverse('organization-current'))

        self.assertEqual(response.data['legal_name'], 'Brand Holdings Ltd')
        self.assertEqual(response.data['parent_entity_name'], 'Brand Group')


@override_switch(ORGANIZATION_LEVEL_SWITCH, active=True)
class OrganizationOnboardingTest(OrganizationTestBase):
    def progress(self, user, organization=None):
        self.login(user)
        response = self.client.get(
            self.url('organization-onboarding', organization=organization)
        )
        self.assertEqual(response.status_code, 200)
        return response.data

    def test_nothing_is_done_in_a_new_organization(self):
        self.assertEqual(
            self.progress(self.other_user, self.other_organization),
            {
                'has_contributions': False,
                'has_colleagues': False,
                'has_claims': False,
            },
        )

    def test_steps_are_ticked_as_the_organization_takes_them(self):
        progress = self.progress(self.member_user)
        self.assertTrue(progress['has_colleagues'])
        self.assertFalse(progress['has_contributions'])
        self.assertFalse(progress['has_claims'])

        _, _, facility = self.make_submission(self.member_contributor)
        claim = FacilityClaim.objects.create(
            contributor=self.admin_contributor,
            facility=facility,
            contact_person='Owner',
        )
        progress = self.progress(self.member_user)
        self.assertTrue(progress['has_contributions'])
        self.assertTrue(progress['has_claims'])

        claim.status = FacilityClaimStatuses.DENIED
        claim.save()
        self.assertFalse(self.progress(self.member_user)['has_claims'])

    def test_a_contribution_awaiting_moderation_counts(self):
        ModerationEvent.objects.create(
            contributor=self.other_contributor,
            request_type=ModerationEvent.RequestType.CREATE,
            source=ModerationEvent.Source.SLC,
        )
        progress = self.progress(self.other_user, self.other_organization)
        self.assertTrue(progress['has_contributions'])

    def test_only_members_see_it(self):
        self.login(self.outsider_user)
        response = self.client.get(self.url('organization-onboarding'))
        self.assertEqual(response.status_code, 403)


@override_switch(ORGANIZATION_LEVEL_SWITCH, active=True)
class OrganizationDomainAccountsTest(OrganizationTestBase):
    def accounts(self, user=None):
        self.login(user or self.admin_user)
        return self.client.get(self.url('organization-domain-accounts'))

    def test_email_domain(self):
        self.assertEqual(email_domain(' Ana@Brand.Example '), 'brand.example')
        self.assertEqual(email_domain('not-an-address'), '')
        self.assertEqual(email_domain(None), '')

    def test_admin_sees_invitable_accounts_on_their_domain(self):
        self.make_account('Colleague@BRAND.example', 'Brand (Colleague)')
        # Already invited, on another domain, unconfirmed, deactivated
        # and already in an organization: none of these is suggested.
        invited, _ = self.make_account('invited@brand.example', 'Invited')
        create_invitation(
            self.organization, self.admin_user,
            invited.email, OrganizationMembership.MEMBER,
        )
        unconfirmed, _ = self.make_account('new@brand.example', 'New')
        EmailAddress.objects.create(
            user=unconfirmed, email=unconfirmed.email,
            primary=True, verified=False,
        )
        inactive, _ = self.make_account('gone@brand.example', 'Gone')
        inactive.is_active = False
        inactive.save()
        elsewhere, _ = self.make_account('rival@brand.example', 'In Rival')
        OrganizationMembership.objects.create(
            organization=self.other_organization, user=elsewhere
        )

        response = self.accounts()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['domain'], 'brand.example')
        self.assertEqual(
            response.data['accounts'],
            [{
                # Accounts store their address in lower case.
                'email': 'colleague@brand.example',
                'contributor_name': 'Brand (Colleague)',
            }],
        )

    def test_an_account_that_left_its_organization_is_suggested(self):
        former, _ = self.make_account('former@brand.example', 'Former')
        OrganizationMembership.objects.create(
            organization=self.other_organization,
            user=former,
            status=OrganizationMembership.REMOVED,
        )

        emails = [
            account['email'] for account in self.accounts().data['accounts']
        ]
        self.assertEqual(emails, ['former@brand.example'])

    def test_nothing_is_suggested_on_a_public_mail_provider(self):
        self.admin_user.email = 'ana@gmail.com'
        self.admin_user.save()
        self.make_account('stranger@gmail.com', 'Stranger')

        response = self.accounts()

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data['domain'])
        self.assertEqual(response.data['accounts'], [])

    def test_only_an_admin_sees_them(self):
        for user in (self.member_user, self.outsider_user):
            self.assertEqual(self.accounts(user).status_code, 403)


@override_switch(ORGANIZATION_LEVEL_SWITCH, active=True)
class OrganizationListMatchReportTest(OrganizationTestBase):
    def setUp(self):
        super().setUp()
        self.organization.dashboard_enabled = True
        self.organization.save()

    def add_row(self, source, status, row_index, facility=None,
                match_is_active=None):
        item = FacilityListItem.objects.create(
            name='Row {}'.format(row_index),
            address='1 Example Street',
            country_code='US',
            sector=['Apparel'],
            row_index=row_index,
            geocoded_point=Point(0, 0),
            status=status,
            source=source,
            facility=facility,
        )
        if match_is_active is not None:
            FacilityMatch.objects.create(
                facility_list_item=item,
                facility=facility,
                status=FacilityMatch.AUTOMATIC,
                is_active=match_is_active,
                results={},
                confidence=1,
            )
        return item

    def report(self, user=None):
        self.login(user or self.member_user)
        return self.client.get(self.url('organization-dashboard-lists'))

    def test_counts_what_became_of_each_row(self):
        # An existing production location another contributor created.
        _, _, existing = self.make_submission(
            self.outsider_contributor, name='Existing'
        )
        # The uploaded list: its first row creates a new location.
        source, _, _ = self.make_submission(
            self.member_contributor, name='Spring'
        )
        item = FacilityListItem
        self.add_row(source, item.MATCHED, 2, existing, True)
        self.add_row(source, item.CONFIRMED_MATCH, 3, existing, True)
        self.add_row(source, item.POTENTIAL_MATCH, 4)
        self.add_row(source, item.ERROR_GEOCODING, 5)
        self.add_row(source, item.GEOCODED_NO_RESULTS, 6)
        self.add_row(source, item.DUPLICATE, 7)
        self.add_row(source, item.MATCHED, 8, existing, False)
        self.add_row(source, item.ITEM_REMOVED, 9)
        self.add_row(source, item.UPLOADED, 10)
        self.add_row(source, item.GEOCODED, 11)

        response = self.report()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['lists']), 1)
        row = response.data['lists'][0]
        self.assertEqual(row['name'], 'Spring list')
        self.assertEqual(
            row['submitted_by']['email'], self.member_user.email
        )
        counts = {
            key: row[key] for key in (
                'total', 'matched_existing', 'new_locations',
                'needs_review', 'failed', 'duplicates', 'removed',
                'in_progress',
            )
        }
        self.assertEqual(counts, {
            'total': 11,
            'matched_existing': 2,
            'new_locations': 1,
            'needs_review': 1,
            'failed': 2,
            'duplicates': 1,
            'removed': 2,
            'in_progress': 2,
        })

    def test_lists_newest_first_and_only_the_organizations(self):
        self.make_submission(self.admin_contributor, name='Older')
        self.make_submission(self.member_contributor, name='Newer')
        self.make_submission(self.other_contributor, name='Rival')
        self.make_submission(
            self.member_contributor, name='Single',
            source_type='SINGLE',
        )

        names = [row['name'] for row in self.report().data['lists']]
        self.assertEqual(names, ['Newer list', 'Older list'])

    def test_no_lists(self):
        self.assertEqual(self.report().data, {'lists': []})

    def test_refused_without_the_dashboard_or_membership(self):
        self.assertEqual(self.report(self.outsider_user).status_code, 403)
        self.organization.dashboard_enabled = False
        self.organization.save()
        self.assertEqual(self.report().status_code, 403)


@override_switch(ORGANIZATION_LEVEL_SWITCH, active=True)
class OrganizationUsageTest(OrganizationTestBase):
    def setUp(self):
        super().setUp()
        self.organization.dashboard_enabled = True
        self.organization.save()

    def usage(self, user=None):
        self.login(user or self.member_user)
        return self.client.get(self.url('organization-dashboard-usage'))

    @staticmethod
    def log_download(user, records, days_ago=0):
        log = DownloadLog.objects.create(
            user=user, path='/api/facilities-downloads/', record_count=records
        )
        if days_ago:
            DownloadLog.objects.filter(pk=log.pk).update(
                created_at=timezone.now() - timedelta(days=days_ago)
            )

    @staticmethod
    def log_api_call(user, days_ago=0, response_code=200):
        log = RequestLog.objects.create(
            user=user, token='token', method='GET',
            path='/api/facilities/', response_code=response_code,
        )
        if days_ago:
            RequestLog.objects.filter(pk=log.pk).update(
                created_at=timezone.now() - timedelta(days=days_ago)
            )

    def test_downloads_per_member_and_in_total(self):
        self.log_download(self.member_user, 100)
        self.log_download(self.member_user, 40, days_ago=5)
        # Outside the recent period, and in an earlier year.
        self.log_download(self.member_user, 7, days_ago=45)
        self.log_download(self.member_user, 9000, days_ago=800)
        self.log_download(self.admin_user, 10)
        self.log_download(self.outsider_user, 999)
        FacilityDownloadLimit.objects.create(
            user=self.member_user,
            free_download_records=4860,
            paid_download_records=250,
        )

        data = self.usage().data

        self.assertEqual(data['period_days'], 30)
        self.assertEqual(
            [member['email'] for member in data['members']],
            [self.admin_user.email, self.member_user.email],
        )
        admin, member = data['members']
        self.assertEqual(member['contributor_name'], 'Brand (Member account)')
        self.assertEqual(member['downloads']['count'], 2)
        self.assertEqual(member['downloads']['records'], 140)
        self.assertEqual(member['downloads']['free_records_left'], 4860)
        self.assertEqual(member['downloads']['paid_records_left'], 250)
        self.assertGreaterEqual(member['downloads']['records_this_year'], 140)
        self.assertLess(member['downloads']['records_this_year'], 9000)
        self.assertEqual(admin['downloads']['count'], 1)
        self.assertIsNone(admin['downloads']['free_records_left'])
        self.assertEqual(data['totals']['downloads'], 3)
        self.assertEqual(data['totals']['downloaded_records'], 150)

    def test_api_usage_only_for_members_with_api_access(self):
        group, _ = Group.objects.get_or_create(
            name=FeatureGroups.CAN_SUBMIT_FACILITY
        )
        self.member_user.groups.add(group)
        ApiLimit.objects.create(
            contributor=self.member_contributor,
            period_limit=500,
            renewal_period=ApiLimit.MONTHLY,
            period_start_date=timezone.now() - timedelta(days=400),
        )
        self.log_api_call(self.member_user)
        self.log_api_call(self.member_user, response_code=404)
        self.log_api_call(self.member_user, days_ago=200)
        self.log_api_call(self.admin_user)

        data = self.usage().data
        admin, member = data['members']

        self.assertIsNone(admin['api'])
        self.assertEqual(member['api']['calls'], 2)
        self.assertEqual(member['api']['limit'], 500)
        self.assertEqual(member['api']['renewal_period'], 'MONTHLY')
        self.assertLessEqual(member['api']['calls_this_period'], 1)
        self.assertEqual(data['totals']['api_calls'], 2)

    def test_api_access_without_a_limit(self):
        group, _ = Group.objects.get_or_create(
            name=FeatureGroups.CAN_SUBMIT_FACILITY
        )
        self.member_user.groups.add(group)

        member = self.usage().data['members'][1]

        self.assertEqual(
            member['api'],
            {
                'calls': 0,
                'limit': None,
                'renewal_period': None,
                'calls_this_period': None,
            },
        )

    def test_former_members_are_left_out(self):
        self.log_download(self.member_user, 100)
        self.member_membership.status = OrganizationMembership.REMOVED
        self.member_membership.save()

        data = self.usage(self.admin_user).data

        self.assertEqual(len(data['members']), 1)
        self.assertEqual(data['totals']['downloads'], 0)

    def test_refused_without_the_dashboard_or_membership(self):
        self.assertEqual(self.usage(self.outsider_user).status_code, 403)
        self.organization.dashboard_enabled = False
        self.organization.save()
        self.assertEqual(self.usage().status_code, 403)
