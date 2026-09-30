from django.contrib.gis.geos import Point
from django.test import override_settings
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
    Sector,
    Source,
    User,
)
from api.serializers.facility.facility_create_claim_serializer import (
    FacilityCreateClaimSerializer,
)


@override_settings(DEBUG=True)
@override_switch('claim_a_facility', active=True)
class ClaimNameAddressFieldsTest(APITestCase):
    '''
    The claim form's name and address are accepted, validated and stored
    on the claim, and promote on the production location page once the
    claim is approved through the existing claim promotion.
    '''

    def setUp(self):
        Sector.objects.get_or_create(name='Apparel')

        self.claimant_email = 'claimant@example.com'
        self.password = 'example123'
        self.claimant_user = User.objects.create(email=self.claimant_email)
        self.claimant_user.set_password(self.password)
        self.claimant_user.save()
        self.claimant = Contributor.objects.create(
            admin=self.claimant_user,
            name='Claimant Co',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.superuser_email = 'admin@example.com'
        self.superuser = User.objects.create_superuser(
            email=self.superuser_email, password=self.password
        )

        list_user = User.objects.create(email='lister@example.com')
        list_contributor = Contributor.objects.create(
            admin=list_user,
            name='List Contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='List'
        )
        source = Source.objects.create(
            facility_list=facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=list_contributor,
        )
        self.list_item = FacilityListItem.objects.create(
            name='Original Name',
            address='1 Original Street',
            country_code='US',
            sector=['Apparel'],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )
        self.facility = Facility.objects.create(
            name='Original Name',
            address='1 Original Street',
            country_code='US',
            location=Point(0, 0),
            created_from=self.list_item,
        )
        self.list_item.facility = self.facility
        self.list_item.save()
        FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=self.facility,
            results='',
            facility_list_item=self.list_item,
        )

    def make_claim(self, **overrides):
        values = {
            'contributor': self.claimant,
            'facility': self.facility,
            'contact_person': 'Claimant',
            'job_title': 'Owner',
            'sector': ['Apparel'],
        }
        values.update(overrides)
        return FacilityClaim.objects.create(**values)

    def valid_form_data(self, **overrides):
        data = {
            'your_name': 'Claimant',
            'your_title': 'Owner',
            'your_business_website': '',
            'business_website': '',
            'business_linkedin_profile':
                'https://www.linkedin.com/company/example',
        }
        data.update(overrides)
        return data

    def serializer(self, **overrides):
        return FacilityCreateClaimSerializer(
            data=self.valid_form_data(**overrides),
            context={'facility': self.facility},
        )

    def test_serializer_accepts_and_strips_values(self):
        serializer = self.serializer(
            facility_name_english='  Claimed Name ',
            facility_address=' 2 New Street ',
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            'Claimed Name', serializer.validated_data['facility_name_english']
        )
        self.assertEqual(
            '2 New Street', serializer.validated_data['facility_address']
        )

    def test_serializer_normalizes_blank_to_none(self):
        serializer = self.serializer(
            facility_name_english='', facility_address='   '
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIsNone(serializer.validated_data['facility_name_english'])
        self.assertIsNone(serializer.validated_data['facility_address'])

    def test_serializer_rejects_punctuation_only_values(self):
        serializer = self.serializer(
            facility_name_english='Fine', facility_address='-- , / :'
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('facility_address', serializer.errors)
        self.assertIn(
            'punctuation or whitespace',
            str(serializer.errors['facility_address'][0]),
        )

    def test_serializer_rejects_values_over_200_characters(self):
        serializer = self.serializer(facility_name_english='a' * 201)
        self.assertFalse(serializer.is_valid())
        self.assertIn('facility_name_english', serializer.errors)

    def test_claim_post_stores_the_values(self):
        self.client.login(
            email=self.claimant_email, password=self.password
        )
        response = self.client.post(
            f'/api/facilities/{self.facility.id}/claim/',
            self.valid_form_data(
                facility_name_english='Claimed Name',
                facility_address='2 New Street',
                sectors='Apparel',
            ),
        )
        self.assertEqual(200, response.status_code, response.content)

        claim = FacilityClaim.objects.get(facility=self.facility)
        self.assertEqual('Claimed Name', claim.facility_name_english)
        self.assertEqual('2 New Street', claim.facility_address)
        self.assertEqual(FacilityClaimStatuses.PENDING, claim.status)

    def test_claim_post_without_the_values_stores_null(self):
        self.client.login(
            email=self.claimant_email, password=self.password
        )
        response = self.client.post(
            f'/api/facilities/{self.facility.id}/claim/',
            self.valid_form_data(sectors='Apparel'),
        )
        self.assertEqual(200, response.status_code, response.content)
        claim = FacilityClaim.objects.get(facility=self.facility)
        self.assertIsNone(claim.facility_name_english)
        self.assertIsNone(claim.facility_address)

    def test_pending_claim_patch_edits_and_clears_the_values(self):
        claim = self.make_claim(
            facility_name_english='Claimed Name',
            facility_address='1 Original Street',
        )
        self.client.login(
            email=self.claimant_email, password=self.password
        )
        url = f'/api/facility-claims/{claim.id}/pending/'

        response = self.client.patch(
            url, {'facility_address': '2 New Street'}, format='json'
        )
        self.assertEqual(200, response.status_code, response.content)
        self.assertEqual('2 New Street', response.json()['facility_address'])
        self.assertEqual(
            'Claimed Name', response.json()['facility_name_english']
        )
        claim.refresh_from_db()
        self.assertEqual('2 New Street', claim.facility_address)

        response = self.client.patch(
            url, {'facility_address': None}, format='json'
        )
        self.assertEqual(200, response.status_code, response.content)
        claim.refresh_from_db()
        self.assertIsNone(claim.facility_address)

        response = self.client.patch(
            url, {'facility_name_english': '-- , /'}, format='json'
        )
        self.assertEqual(400, response.status_code, response.content)

    def test_approved_claim_promotes_the_values(self):
        claim = self.make_claim(
            facility_name_english='Claimed Name',
            facility_address='2 New Street',
        )
        self.client.login(
            email=self.superuser_email, password=self.password
        )
        response = self.client.post(
            f'/api/facility-claims/{claim.id}/approve/',
            {'reason': 'documents verified'},
        )
        self.assertEqual(200, response.status_code, response.content)

        properties = self.client.get(
            f'/api/facilities/{self.facility.id}/'
        ).json()['properties']
        self.assertEqual('Claimed Name', properties['name'])
        self.assertEqual('2 New Street', properties['address'])
        details = self.client.get(
            f'/api/facility-claims/{claim.id}/'
        ).json()
        self.assertEqual('Claimed Name', details['facility_name_english'])
        self.assertEqual('2 New Street', details['facility_address'])
