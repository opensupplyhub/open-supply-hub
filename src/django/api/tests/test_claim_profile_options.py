from django.contrib.gis.geos import Point
from django.db import IntegrityError, transaction
from django.urls import reverse
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from api.constants import FacilityClaimStatuses
from api.models import (
    ClaimAffiliation,
    ClaimCertification,
    Contributor,
    Facility,
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)
from api.serializers.facility.approved_facility_claim_serializer import (
    ApprovedFacilityClaimSerializer,
)


class ClaimProfileOptionsTestBase(APITestCase):
    def setUp(self):
        self.email = 'claimant@example.com'
        self.password = 'example123'
        self.user = User.objects.create(email=self.email)
        self.user.set_password(self.password)
        self.user.save()
        self.contributor = Contributor.objects.create(
            name='Contributor', admin=self.user
        )
        self.facility = self._make_facility('one')

    def _make_facility(self, suffix):
        facility_list = FacilityList.objects.create(
            header='header', file_name=suffix, name=suffix
        )
        source = Source.objects.create(
            facility_list=facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        list_item = FacilityListItem.objects.create(
            name=f'name {suffix}',
            address='address',
            country_code='US',
            sector=['Apparel'],
            source=source,
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
        )
        return Facility.objects.create(
            name=f'name {suffix}',
            address='address',
            country_code='US',
            location=Point(0, 0),
            created_from=list_item,
        )

    def _make_claim(self, facility, affiliations=None, certifications=None):
        return FacilityClaim.objects.create(
            facility=facility,
            contributor=self.contributor,
            status=FacilityClaimStatuses.APPROVED,
            facility_affiliations=affiliations,
            facility_certifications=certifications,
        )


class SeededOptionsTest(ClaimProfileOptionsTestBase):
    def test_seeded_affiliations_offer_cascale_not_its_former_name(self):
        active = ClaimAffiliation.objects.active_names()
        self.assertIn('Cascale', active)
        self.assertNotIn('Sustainable Apparel Coalition', active)
        self.assertEqual(15, len(active))

    def test_european_outdoor_group_is_seeded_inactive(self):
        option = ClaimAffiliation.objects.get(name='European Outdoor Group')
        self.assertFalse(option.is_active)

    def test_seeded_certifications_keep_the_previous_list(self):
        active = ClaimCertification.objects.active_names()
        self.assertEqual(33, len(active))
        self.assertEqual('BCI', active[0])
        self.assertIn('Rainforest Alliance', active)

    def test_names_are_unique_ignoring_case(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            ClaimAffiliation.objects.create(name='cascale')


class ClaimProfileOptionsEndpointTest(ClaimProfileOptionsTestBase):
    url = '/api/claim-profile-options/'

    def test_returns_only_active_options_in_sort_order(self):
        ClaimAffiliation.objects.filter(name='SEDEX').update(is_active=False)
        ClaimAffiliation.objects.create(name='Aaa First', sort_order=0)

        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        affiliations = response.json()['affiliations']
        self.assertEqual('Aaa First', affiliations[0])
        self.assertNotIn('SEDEX', affiliations)
        self.assertNotIn('European Outdoor Group', affiliations)
        self.assertEqual(
            ClaimCertification.objects.active_names(),
            response.json()['certifications'],
        )

    def test_is_public(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)


@override_switch('claim_a_facility', active=True)
class CreateClaimValidationTest(ClaimProfileOptionsTestBase):
    def _submit(self, **extra):
        self.client.post(
            '/user-login/',
            {'email': self.email, 'password': self.password},
            format='json',
        )
        data = {
            'your_name': 'John Doe',
            'your_title': 'Manager',
            'your_business_website': 'https://example.com',
            'business_website': 'https://facility.com',
            'business_linkedin_profile': 'https://linkedin.com/company/f',
            **extra,
        }
        return self.client.post(
            f'/api/facilities/{self.facility.id}/claim/', data
        )

    def _claim(self):
        return FacilityClaim.objects.get(facility=self.facility)

    def test_accepts_an_option_added_in_the_admin(self):
        ClaimCertification.objects.create(name='LEED')

        response = self._submit(facility_certifications=['LEED', 'BCI'])

        self.assertEqual(200, response.status_code)
        self.assertEqual(['LEED', 'BCI'],
                         self._claim().facility_certifications)

    def test_rejects_an_inactive_option(self):
        ClaimAffiliation.objects.filter(name='SEDEX').update(is_active=False)

        response = self._submit(facility_affiliations=['SEDEX'])

        self.assertEqual(400, response.status_code)
        self.assertFalse(
            FacilityClaim.objects.filter(facility=self.facility).exists()
        )

    def test_rejects_the_superseded_affiliation_name(self):
        response = self._submit(
            facility_affiliations=['Sustainable Apparel Coalition']
        )
        self.assertEqual(400, response.status_code)

    def test_drops_repeated_values(self):
        response = self._submit(
            facility_affiliations=['Cascale', 'Canopy', 'Cascale']
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(['Cascale', 'Canopy'],
                         self._claim().facility_affiliations)


class RenamePropagationTest(ClaimProfileOptionsTestBase):
    def test_rename_rewrites_claims_history_and_bumps_the_facility(self):
        claim = self._make_claim(
            self.facility, affiliations=['Canopy', 'Cascale']
        )
        claim_updated_at = claim.updated_at
        facility_updated_at = self.facility.updated_at

        option = ClaimAffiliation.objects.get(name='Canopy')
        option.name = 'Canopy Planet'
        option.save()

        self.assertEqual(1, option.renamed_claims_count)
        claim.refresh_from_db()
        self.assertEqual(['Canopy Planet', 'Cascale'],
                         claim.facility_affiliations)
        self.assertEqual(
            ['Canopy Planet', 'Cascale'],
            claim.history.latest().facility_affiliations,
        )
        # The claim's own timestamp is the "claimed at" date in the search
        # index, so it must not move; the facility's is what triggers the
        # re-index.
        self.assertEqual(claim_updated_at, claim.updated_at)
        self.facility.refresh_from_db()
        self.assertGreater(self.facility.updated_at, facility_updated_at)

    def test_rename_only_touches_its_own_list(self):
        # "Canopy" is both an affiliation and a certification.
        claim = self._make_claim(
            self.facility,
            affiliations=['Canopy'],
            certifications=['Canopy'],
        )

        option = ClaimAffiliation.objects.get(name='Canopy')
        option.name = 'Canopy Planet'
        option.save()

        claim.refresh_from_db()
        self.assertEqual(['Canopy Planet'], claim.facility_affiliations)
        self.assertEqual(['Canopy'], claim.facility_certifications)

    def test_rename_never_duplicates_a_value(self):
        claim = self._make_claim(
            self.facility, affiliations=['SEDEX', 'Canopy']
        )
        ClaimAffiliation.objects.filter(name='Canopy').delete()

        option = ClaimAffiliation.objects.get(name='SEDEX')
        option.name = 'Canopy'
        option.save()

        claim.refresh_from_db()
        self.assertEqual(['Canopy'], claim.facility_affiliations)

    def test_rename_leaves_unrelated_claims_and_facilities_alone(self):
        other_facility = self._make_facility('two')
        other_claim = self._make_claim(other_facility, affiliations=['ZDHC'])
        other_updated_at = other_facility.updated_at

        option = ClaimAffiliation.objects.get(name='Canopy')
        option.name = 'Canopy Planet'
        option.save()

        self.assertEqual(0, option.renamed_claims_count)
        other_claim.refresh_from_db()
        self.assertEqual(['ZDHC'], other_claim.facility_affiliations)
        other_facility.refresh_from_db()
        self.assertEqual(other_updated_at, other_facility.updated_at)

    def test_saving_without_a_rename_touches_no_claims(self):
        claim = self._make_claim(self.facility, affiliations=['Canopy'])
        facility_updated_at = self.facility.updated_at

        option = ClaimAffiliation.objects.get(name='Canopy')
        option.is_active = False
        option.save()

        self.assertEqual(0, option.renamed_claims_count)
        claim.refresh_from_db()
        self.assertEqual(['Canopy'], claim.facility_affiliations)
        self.facility.refresh_from_db()
        self.assertEqual(facility_updated_at, self.facility.updated_at)


class ApprovedClaimChoicesTest(ClaimProfileOptionsTestBase):
    def test_choices_keep_a_value_the_claim_holds_that_is_not_offered(self):
        ClaimAffiliation.objects.filter(name='SEDEX').update(is_active=False)
        claim = self._make_claim(self.facility, affiliations=['SEDEX'])

        serializer = ApprovedFacilityClaimSerializer()
        choices = serializer.get_affiliation_choices(claim)

        self.assertIn(('SEDEX', 'SEDEX'), choices)
        self.assertIn(('Cascale', 'Cascale'), choices)
        self.assertEqual(choices[-1], ('SEDEX', 'SEDEX'))


class ClaimProfileOptionAdminTest(ClaimProfileOptionsTestBase):
    def setUp(self):
        super().setUp()
        self.superuser = User.objects.create_superuser(
            email='super@example.com', password='example123'
        )
        self.client.force_login(self.superuser)

    def test_renaming_in_the_admin_updates_claims_and_reports_it(self):
        claim = self._make_claim(self.facility, affiliations=['Canopy'])
        option = ClaimAffiliation.objects.get(name='Canopy')

        response = self.client.post(
            reverse('admin:api_claimaffiliation_change', args=[option.pk]),
            {
                'name': 'Canopy Planet',
                'is_active': 'on',
                'sort_order': option.sort_order,
            },
            follow=True,
        )

        self.assertEqual(200, response.status_code)
        claim.refresh_from_db()
        self.assertEqual(['Canopy Planet'], claim.facility_affiliations)
        messages = [str(m) for m in response.context['messages']]
        self.assertTrue(
            any('1 existing claim(s) updated' in m for m in messages),
            messages,
        )
        self.assertEqual(
            self.superuser,
            option.history.latest().history_user,
        )

    def test_options_cannot_be_deleted(self):
        option = ClaimCertification.objects.get(name='BCI')
        response = self.client.post(
            reverse('admin:api_claimcertification_delete', args=[option.pk]),
            {'post': 'yes'},
        )
        self.assertEqual(403, response.status_code)
        self.assertTrue(
            ClaimCertification.objects.filter(pk=option.pk).exists()
        )

    def test_changelist_loads(self):
        self._make_claim(self.facility, certifications=['BCI'])
        response = self.client.get(
            reverse('admin:api_claimcertification_changelist')
        )
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Claims using it')
