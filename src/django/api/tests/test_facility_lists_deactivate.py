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


class TestFacilityListsDeactivate(APITestCase):
    def setUp(self):
        self.user_email = 'contributor1@example.com'
        self.user_password = 'example123'
        self.user, self.contributor = self.__create_contributor(
            self.user_email, self.user_password, 'Contributor One'
        )
        self.facility_list, self.source = self.__create_list(
            self.contributor, 'Supplier List'
        )

        # A second contributor with their own list, used to prove a caller
        # cannot deactivate another contributor's list.
        self.other_email = 'contributor2@example.com'
        self.other_password = 'example456'
        self.other_user, self.other_contributor = self.__create_contributor(
            self.other_email, self.other_password, 'Contributor Two'
        )
        self.other_list, self.other_source = self.__create_list(
            self.other_contributor, 'Other Supplier List'
        )

        self.superuser_email = 'superadmin@example.com'
        self.superuser_password = 'superpass'
        self.superuser = User.objects.create_superuser(
            self.superuser_email, self.superuser_password
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
    def __create_list(contributor, name):
        facility_list = FacilityList.objects.create(
            header='header', file_name='file', name=name
        )
        source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=facility_list,
            contributor=contributor,
        )
        list_item = FacilityListItem.objects.create(
            name='Plant',
            address='1 St',
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
        FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=facility,
            results='',
            facility_list_item=list_item,
            is_active=True,
        )
        return facility_list, source

    def __deactivate_url(self, list_id):
        return reverse(
            URLNames.FACILITY_LISTS + '-deactivate',
            args=[list_id],
        )

    def login(self, email, password):
        self.client.logout()
        self.client.login(email=email, password=password)

    def test_deactivates_own_list(self):
        self.login(self.user_email, self.user_password)

        response = self.client.post(
            self.__deactivate_url(self.facility_list.id)
        )

        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)
        self.assertEqual(body['list_id'], self.facility_list.id)
        self.assertTrue(body['deactivated'])

        self.source.refresh_from_db()
        self.facility_list.refresh_from_db()
        self.assertFalse(self.source.is_active)
        self.assertEqual(self.facility_list.status, FacilityList.REJECTED)

    def test_deactivation_is_durable_across_list_updates(self):
        # The whole reason we set status=REJECTED (not just the source flag):
        # manual_list_reject_revert_trigger re-syncs Source.is_active from the
        # list status on every api_facilitylist update. A later, unrelated
        # update to the list row must NOT reactivate the source.
        self.login(self.user_email, self.user_password)
        self.client.post(self.__deactivate_url(self.facility_list.id))

        self.facility_list.refresh_from_db()
        self.facility_list.description = 'touched after deactivation'
        self.facility_list.save()

        self.source.refresh_from_db()
        self.assertFalse(self.source.is_active)

    def test_matches_admin_reject_effect(self):
        # Deactivate list A via the contributor endpoint.
        self.login(self.user_email, self.user_password)
        self.client.post(self.__deactivate_url(self.facility_list.id))
        self.source.refresh_from_db()
        self.facility_list.refresh_from_db()

        # Reject an identical list B via the superuser admin endpoint.
        list_b, source_b = self.__create_list(self.contributor, 'List B')
        self.login(self.superuser_email, self.superuser_password)
        admin_response = self.client.post(
            '/api/facility-lists/{}/reject/'.format(list_b.id)
        )
        self.assertEqual(admin_response.status_code, 200)
        source_b.refresh_from_db()
        list_b.refresh_from_db()

        # The contributor deactivation leaves the same durable state as admin.
        self.assertEqual(self.source.is_active, source_b.is_active)
        self.assertFalse(self.source.is_active)
        self.assertEqual(self.facility_list.status, list_b.status)
        self.assertEqual(self.facility_list.status, FacilityList.REJECTED)

    def test_404_when_already_inactive(self):
        self.source.is_active = False
        self.source.save()
        self.login(self.user_email, self.user_password)

        response = self.client.post(
            self.__deactivate_url(self.facility_list.id)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            json.loads(response.content)['detail'],
            'This list is already inactive.',
        )

    def test_cannot_deactivate_another_contributors_list(self):
        self.login(self.user_email, self.user_password)

        response = self.client.post(
            self.__deactivate_url(self.other_list.id)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            json.loads(response.content)['detail'],
            'The list with the given id was not found.',
        )
        # The other contributor's list must remain active.
        self.other_source.refresh_from_db()
        self.other_list.refresh_from_db()
        self.assertTrue(self.other_source.is_active)
        self.assertNotEqual(self.other_list.status, FacilityList.REJECTED)

    def test_404_when_list_unknown(self):
        self.login(self.user_email, self.user_password)

        response = self.client.post(self.__deactivate_url(9999999))

        self.assertEqual(response.status_code, 404)

    def test_requires_authentication(self):
        response = self.client.post(
            self.__deactivate_url(self.facility_list.id)
        )

        self.assertIn(response.status_code, (401, 403))
        self.source.refresh_from_db()
        self.assertTrue(self.source.is_active)

    def test_requires_confirmed_email(self):
        email_address = EmailAddress.objects.get_primary(self.user)
        email_address.verified = False
        email_address.save()
        self.login(self.user_email, self.user_password)

        response = self.client.post(
            self.__deactivate_url(self.facility_list.id)
        )

        self.assertEqual(response.status_code, 403)
        self.source.refresh_from_db()
        self.assertTrue(self.source.is_active)
