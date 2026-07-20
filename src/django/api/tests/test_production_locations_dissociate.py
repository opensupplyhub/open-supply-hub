import json

from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.gis.geos import Point
from allauth.account.models import EmailAddress

from api.models.user import User
from api.models.contributor.contributor import Contributor
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.source import Source
from api.models.facility.facility import Facility
from api.models.facility.facility_match import FacilityMatch
from api.views.v1.url_names import URLNames


class TestProductionLocationsDissociate(APITestCase):
    def setUp(self):
        self.user_email = 'contributor1@example.com'
        self.user_password = 'example123'
        self.user, self.contributor = self.__create_contributor(
            self.user_email, self.user_password, 'Contributor One'
        )
        self.facility, self.match = self.__create_contribution(
            self.contributor, 'Alpha Plant', '1 Alpha St'
        )

        # A second contributor with their own contribution, used to prove a
        # caller can never affect another contributor's data.
        self.other_email = 'contributor2@example.com'
        self.other_password = 'example456'
        self.other_user, self.other_contributor = self.__create_contributor(
            self.other_email, self.other_password, 'Contributor Two'
        )
        self.other_facility, self.other_match = self.__create_contribution(
            self.other_contributor, 'Beta Plant', '2 Beta St'
        )

    @staticmethod
    def __create_contributor(email, password, name):
        user = User.objects.create(email=email)
        user.set_password(password)
        user.save()
        EmailAddress.objects.create(
            user=user, email=email, verified=True, primary=True
        )
        contributor = Contributor.objects.create(
            admin=user,
            name=name,
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        return user, contributor

    @staticmethod
    def __create_contribution(contributor, name, address):
        facility_list = FacilityList.objects.create(
            header='header',
            file_name='file',
            name=f'{name} List',
            status=FacilityList.APPROVED,
        )
        source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=facility_list,
            contributor=contributor,
        )
        list_item = FacilityListItem.objects.create(
            name=name,
            address=address,
            country_code='US',
            sector=['Apparel'],
            row_index=0,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )
        facility = Facility.objects.create(
            name=list_item.name,
            address=list_item.address,
            country_code='US',
            location=Point(0, 0),
            created_from=list_item,
        )
        match = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=facility,
            results='',
            facility_list_item=list_item,
            is_active=True,
        )
        return facility, match

    def __dissociate_url(self, os_id):
        return reverse(
            URLNames.PRODUCTION_LOCATIONS + '-dissociate',
            args=[os_id],
        )

    def login(self, email, password):
        self.client.logout()
        self.client.login(email=email, password=password)

    def test_dissociates_own_active_contribution(self):
        original_updated_at = self.facility.updated_at
        self.login(self.user_email, self.user_password)

        response = self.client.post(self.__dissociate_url(self.facility.id))

        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)
        self.assertEqual(body['os_id'], self.facility.id)
        self.assertEqual(body['dissociated_contributions'], 1)

        self.match.refresh_from_db()
        self.assertFalse(self.match.is_active)

        self.facility.refresh_from_db()
        self.assertGreater(self.facility.updated_at, original_updated_at)

    def test_404_and_no_change_when_no_active_contribution(self):
        self.match.is_active = False
        self.match.save()
        self.login(self.user_email, self.user_password)

        response = self.client.post(self.__dissociate_url(self.facility.id))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            json.loads(response.content)['detail'],
            'You have no active contribution from an approved list to '
            'dissociate from this location.',
        )

    def test_does_not_dissociate_contribution_from_pending_list(self):
        facility_list = self.match.facility_list_item.source.facility_list
        facility_list.status = FacilityList.PENDING
        facility_list.save()
        self.login(self.user_email, self.user_password)

        response = self.client.post(self.__dissociate_url(self.facility.id))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            json.loads(response.content)['detail'],
            'You have no active contribution from an approved list to '
            'dissociate from this location.',
        )
        self.match.refresh_from_db()
        self.assertTrue(self.match.is_active)

    def test_cannot_affect_another_contributors_data(self):
        self.login(self.user_email, self.user_password)

        response = self.client.post(
            self.__dissociate_url(self.other_facility.id)
        )

        self.assertEqual(response.status_code, 404)
        # The other contributor's match must remain untouched.
        self.other_match.refresh_from_db()
        self.assertTrue(self.other_match.is_active)

    def test_404_when_location_unknown(self):
        self.login(self.user_email, self.user_password)

        response = self.client.post(
            self.__dissociate_url('US0000000000000')
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            json.loads(response.content)['detail'],
            'The location with the given id was not found.',
        )

    def test_requires_authentication(self):
        response = self.client.post(self.__dissociate_url(self.facility.id))

        self.assertIn(response.status_code, (401, 403))
        self.match.refresh_from_db()
        self.assertTrue(self.match.is_active)

    def test_requires_confirmed_email(self):
        email_address = EmailAddress.objects.get_primary(self.user)
        email_address.verified = False
        email_address.save()
        self.login(self.user_email, self.user_password)

        response = self.client.post(self.__dissociate_url(self.facility.id))

        self.assertEqual(response.status_code, 403)
        self.match.refresh_from_db()
        self.assertTrue(self.match.is_active)
