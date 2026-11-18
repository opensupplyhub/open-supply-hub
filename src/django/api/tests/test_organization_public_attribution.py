import json

from django.utils import timezone
from waffle.testutils import override_switch

from api.constants import FacilityClaimStatuses
from api.facility_history import (
    claim_contributor_name,
    source_contributor_name,
)
from api.models import (
    FacilityClaim,
    Organization,
    OrganizationMembership,
    Source,
)
from api.models.facility.facility_index import FacilityIndex as Index
from api.serializers.facility.facility_download_serializer import (
    FacilityDownloadSerializer,
)
from api.serializers.facility.utils import (
    get_contributor_id_from_facilityindex,
    get_contributor_name_from_facilityindex,
    get_user_id_from_facilityindex,
)
from api.serializers.utils import get_contributor_id, get_contributor_name
from api.services.organization_service import (
    ORGANIZATION_LEVEL_SWITCH,
    accept_invitation,
    create_invitation,
)
from api.tests.test_organization_level import OrganizationTestBase

MEMBER_NAME = 'Brand (Member account)'
ADMIN_NAME = 'Brand (Admin account)'


@override_switch(ORGANIZATION_LEVEL_SWITCH, active=True)
@override_switch('claim_a_facility', active=True)
class OrganizationPublicAttributionTest(OrganizationTestBase):
    """
    What the public is told about who contributed: a contribution
    recorded against an organization is shown under the organization's
    name, without a link to the member who submitted it.
    """

    def details(self, facility):
        self.client.logout()
        response = self.client.get('/api/facilities/{}/'.format(facility.id))
        self.assertEqual(response.status_code, 200)
        return response.json()['properties']

    @staticmethod
    def contributors_count(facility):
        return Index.objects.get(id=facility.id).contributors_count

    def test_a_members_list_is_shown_under_the_organization(self):
        _, _, facility = self.make_submission(
            self.member_contributor, name='Mill'
        )

        properties = self.details(facility)

        self.assertEqual(len(properties['contributors']), 1)
        entry = properties['contributors'][0]
        self.assertEqual(entry['name'], 'Brand (Mill list)')
        self.assertEqual(entry['contributor_name'], 'Brand')
        self.assertEqual(entry['list_name'], 'Mill list')
        self.assertIsNone(entry['id'])
        self.assertTrue(entry['is_organization'])

        for field in ('name', 'address'):
            attributions = properties['extended_fields'][field]
            self.assertEqual(len(attributions), 1)
            self.assertEqual(attributions[0]['contributor_name'], 'Brand')
            self.assertIsNone(attributions[0]['contributor_id'])

        self.assertEqual(properties['created_from']['contributor'], 'Brand')
        self.assertEqual(properties['sector'][0]['contributor_name'], 'Brand')
        self.assertIsNone(properties['sector'][0]['contributor_id'])

        # Neither the member's contributor name nor their profile id is
        # published anywhere in the response.
        self.assertNotIn(MEMBER_NAME, json.dumps(properties))

    def test_a_non_members_contribution_is_unchanged(self):
        _, _, facility = self.make_submission(
            self.outsider_contributor, name='Mill'
        )

        properties = self.details(facility)

        entry = properties['contributors'][0]
        self.assertEqual(entry['name'], 'Elsewhere (Mill list)')
        self.assertEqual(entry['contributor_name'], 'Elsewhere')
        self.assertEqual(entry['id'], self.outsider_user.id)
        self.assertNotIn('is_organization', entry)
        self.assertEqual(
            properties['extended_fields']['name'][0]['contributor_id'],
            self.outsider_user.id,
        )
        self.assertEqual(
            properties['created_from']['contributor'], 'Elsewhere'
        )

    def test_members_of_one_organization_count_as_one_contributor(self):
        _, _, facility = self.make_submission(
            self.admin_contributor, name='Mill', source_type=Source.SINGLE
        )
        self.make_submission(
            self.member_contributor, name='Mill', facility=facility,
            source_type=Source.SINGLE,
        )

        names = [
            entry['name']
            for entry in self.details(facility)['contributors']
        ]
        self.assertEqual(names, ['Brand'])
        self.assertEqual(self.contributors_count(facility), 1)

        self.make_submission(
            self.outsider_contributor, name='Mill', facility=facility,
            source_type=Source.SINGLE,
        )
        names = sorted(
            entry['name']
            for entry in self.details(facility)['contributors']
        )
        self.assertEqual(names, ['Brand', 'Elsewhere'])
        self.assertEqual(self.contributors_count(facility), 2)

    def test_a_hidden_contribution_stays_anonymous(self):
        source, _, facility = self.make_submission(
            self.member_contributor, name='Mill'
        )
        source.is_public = False
        source.save()

        properties = self.details(facility)

        self.assertNotIn('Brand', json.dumps(properties['contributors']))
        self.assertNotEqual(properties['created_from']['contributor'], 'Brand')

    def test_joining_puts_earlier_contributions_under_the_organization(self):
        _, _, facility = self.make_submission(
            self.outsider_contributor, name='Mill'
        )
        self.assertEqual(
            self.details(facility)['contributors'][0]['contributor_name'],
            'Elsewhere',
        )

        invitation = create_invitation(
            self.organization, self.admin_user,
            self.outsider_user.email, OrganizationMembership.MEMBER,
        )
        accept_invitation(invitation, self.outsider_user)

        entry = self.details(facility)['contributors'][0]
        self.assertEqual(entry['contributor_name'], 'Brand')
        self.assertIsNone(entry['id'])

    def test_the_name_stays_after_the_member_leaves(self):
        _, _, facility = self.make_submission(
            self.member_contributor, name='Mill'
        )
        self.member_membership.status = OrganizationMembership.REMOVED
        self.member_membership.save()

        self.assertEqual(
            self.details(facility)['contributors'][0]['contributor_name'],
            'Brand',
        )

    def test_renaming_the_organization_updates_what_is_shown(self):
        _, _, facility = self.make_submission(
            self.member_contributor, name='Mill'
        )
        _, _, untouched = self.make_submission(
            self.outsider_contributor, name='Other Mill'
        )
        untouched_updated_at = Index.objects.get(id=untouched.id).updated_at

        self.organization.name = 'Brand Group'
        self.organization.save()

        properties = self.details(facility)
        self.assertEqual(
            properties['contributors'][0]['name'], 'Brand Group (Mill list)'
        )
        self.assertEqual(
            properties['created_from']['contributor'], 'Brand Group'
        )
        self.assertEqual(
            Index.objects.get(id=untouched.id).updated_at,
            untouched_updated_at,
        )

    def test_other_changes_to_the_organization_do_not_reindex(self):
        _, _, facility = self.make_submission(
            self.member_contributor, name='Mill'
        )
        updated_at = Index.objects.get(id=facility.id).updated_at

        self.organization.seat_limit = 9
        self.organization.save()

        self.assertEqual(
            Index.objects.get(id=facility.id).updated_at, updated_at
        )

    def test_deleting_the_organization_restores_the_contributor(self):
        organization = Organization.objects.create(name='Short Lived')
        source, _, facility = self.make_submission(
            self.outsider_contributor, name='Mill'
        )
        Source.objects.filter(pk=source.pk).update(organization=organization)
        self.assertEqual(
            self.details(facility)['contributors'][0]['contributor_name'],
            'Short Lived',
        )

        organization.delete()

        entry = self.details(facility)['contributors'][0]
        self.assertEqual(entry['contributor_name'], 'Elsewhere')
        self.assertEqual(entry['id'], self.outsider_user.id)

    def approve_claim(self, contributor, facility):
        return FacilityClaim.objects.create(
            contributor=contributor,
            facility=facility,
            contact_person='Owner',
            sector=['Apparel'],
            status=FacilityClaimStatuses.APPROVED,
            status_change_date=timezone.now(),
        )

    def test_a_members_claim_is_shown_under_the_organization(self):
        _, _, facility = self.make_submission(
            self.outsider_contributor, name='Mill'
        )
        claim = self.approve_claim(self.member_contributor, facility)
        self.assertEqual(claim.organization_id, self.organization.id)

        properties = self.details(facility)

        self.assertEqual(properties['claim_info']['contributor'], 'Brand')
        self.assertIsNone(properties['claim_info']['user_id'])
        claimed_sector = properties['sector'][0]
        self.assertTrue(claimed_sector['is_from_claim'])
        self.assertEqual(claimed_sector['contributor_name'], 'Brand')
        self.assertIsNone(claimed_sector['contributor_id'])
        self.assertNotIn(MEMBER_NAME, json.dumps(properties))

    def test_a_non_members_claim_is_unchanged(self):
        _, _, facility = self.make_submission(
            self.member_contributor, name='Mill'
        )
        self.approve_claim(self.outsider_contributor, facility)

        claim_info = self.details(facility)['claim_info']

        self.assertEqual(claim_info['contributor'], 'Elsewhere')
        self.assertEqual(claim_info['user_id'], self.outsider_user.id)

    def test_download_names_the_organization(self):
        _, _, facility = self.make_submission(
            self.member_contributor, name='Mill'
        )
        self.make_submission(
            self.outsider_contributor, name='Mill', facility=facility
        )
        self.approve_claim(self.admin_contributor, facility)

        cell = FacilityDownloadSerializer().get_contributors(
            Index.objects.get(id=facility.id)
        )

        self.assertEqual(
            sorted(cell.split('|')),
            ['Brand (Claimed)', 'Brand (Mill list)', 'Elsewhere (Mill list)'],
        )

    def test_history_names_the_organization(self):
        source, _, facility = self.make_submission(
            self.member_contributor, name='Mill'
        )
        other_source, _, _ = self.make_submission(
            self.outsider_contributor, name='Mill', facility=facility
        )
        claim = self.approve_claim(self.member_contributor, facility)

        self.assertEqual(source_contributor_name(source), 'Brand')
        self.assertEqual(source_contributor_name(other_source), 'Elsewhere')
        self.assertEqual(claim_contributor_name(claim), 'Brand')
        self.assertEqual(
            claim_contributor_name(
                self.approve_claim(self.outsider_contributor, facility)
            ),
            'Elsewhere',
        )


class OrganizationAttributionHelpersTest(OrganizationTestBase):
    """
    The helpers that turn a contributor blob of the facility index into
    what is published.
    """

    ORGANIZATION_BLOB = {
        'id': 7,
        'admin_id': 70,
        'user_id': 70,
        'name': 'Brand',
        'contrib_type': 'Other',
        'organization_id': 3,
    }
    CONTRIBUTOR_BLOB = {
        'id': 7,
        'admin_id': 70,
        'user_id': 70,
        'name': 'Brand (Member account)',
        'contrib_type': 'Other',
        'organization_id': None,
    }

    def test_no_profile_id_is_published_for_an_organization(self):
        blob = self.ORGANIZATION_BLOB
        self.assertIsNone(get_contributor_id(blob, True))
        self.assertIsNone(get_contributor_id_from_facilityindex(blob, True))
        self.assertIsNone(get_user_id_from_facilityindex(blob, True))
        self.assertEqual(get_contributor_name(blob, True), 'Brand')
        self.assertEqual(
            get_contributor_name_from_facilityindex(blob, True), 'Brand'
        )

    def test_a_contributor_keeps_its_profile_id(self):
        blob = self.CONTRIBUTOR_BLOB
        self.assertEqual(get_contributor_id(blob, True), 70)
        self.assertEqual(get_contributor_id_from_facilityindex(blob, True), 70)
        self.assertEqual(get_user_id_from_facilityindex(blob, True), 70)

    def test_blobs_written_before_the_organization_level_still_work(self):
        blob = {
            key: value for key, value in self.CONTRIBUTOR_BLOB.items()
            if key != 'organization_id'
        }
        self.assertEqual(get_contributor_id(blob, True), 70)
        self.assertEqual(get_contributor_id_from_facilityindex(blob, True), 70)

    def test_an_organization_is_anonymous_to_a_restricted_viewer(self):
        self.assertEqual(
            get_contributor_name(self.ORGANIZATION_BLOB, False), 'an Other'
        )
