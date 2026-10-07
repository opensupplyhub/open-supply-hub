import json

from allauth.account.models import EmailAddress
from django.contrib.gis.geos import Point
from django.core.cache import caches
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.contributor.contributor import Contributor
from api.models.facility.facility import Facility
from api.models.facility.facility_alias import FacilityAlias
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.identity_record_association import IdentityRecordAssociation
from api.models.source import Source
from api.models.user import User

RESOLVER_URI = (
    'https://idr.credentials.responsiblebusiness.org/rba/G-FA-10017485'
)
OTHER_RESOLVER_URI = (
    'https://idr.credentials.responsiblebusiness.org/rba/G-FA-10017486'
)


class TestIdentityRecordRegistration(APITestCase):
    """
    The registration endpoint from scope doc 3.2 (OSDEV-3580).

    The literal paths are asserted rather than reversed, because the paths
    are the contract: Pyx and Unosquare are building their FR-05 call
    against them and have had them since 24 September.
    """

    def setUp(self):
        # Shared with other API tests: the throttling cache is Redis and
        # survives runs, so a stale key can turn an expected 202 into a
        # spurious 429.
        caches['api_throttling'].clear()

        email = 'test@example.com'
        password = 'example123'
        self.user = User.objects.create(email=email)
        self.user.set_password(password)
        self.user.save()
        EmailAddress.objects.create(
            user=self.user, email=email, verified=True, primary=True
        )
        contributor = Contributor.objects.create(
            admin=self.user,
            name='test contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='Test List'
        )
        source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=facility_list,
            contributor=contributor,
        )
        item = FacilityListItem.objects.create(
            name='Blue Elephant Microchips Factory',
            address='8899/47 Thanon Chalong Krung, Bangkok',
            country_code='TH',
            sector=['Electronics'],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )
        self.facility = Facility.objects.create(
            name=item.name,
            address=item.address,
            country_code=item.country_code,
            location=Point(0, 0),
            created_from=item,
        )
        self.os_id = self.facility.id
        self.url = (
            f'/api/v1/production-locations/{self.os_id}/identity-records/'
        )
        self.body = {
            'resolver_uri': RESOLVER_URI,
            'record_type': 'untp:DigitalFacilityRecord',
            'issuer': 'did:web:credentials.responsiblebusiness.org',
            'registrant_reference': 'G-FA-10017485',
        }
        self.client.force_login(self.user)

    def _post(self, body=None, url=None):
        return self.client.post(
            url or self.url,
            json.dumps(self.body if body is None else body),
            content_type='application/json',
        )

    def test_registers_and_returns_live_immediately(self):
        """
        AC#1: the pilot path returns 202 APPROVED with live_from set and no
        verification_url, because the association is Open Supply Hub's own
        construction and there is nothing for a member to confirm (3.2).
        """
        response = self._post()

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['moderation_status'], 'APPROVED')
        self.assertIsNotNone(response.data['live_from'])
        self.assertIsNotNone(response.data['moderation_id'])
        self.assertNotIn('verification_url', response.data)

        association = IdentityRecordAssociation.objects.get(
            os_id=self.os_id
        )
        self.assertEqual(association.resolver_uri, RESOLVER_URI)
        self.assertEqual(
            str(association.uuid), response.data['moderation_id']
        )

    def test_conflicting_resolver_is_rejected_and_changes_nothing(self):
        """AC#2: a different live resolver for the same OS ID is a 409."""
        self._post()

        body = dict(self.body, resolver_uri=OTHER_RESOLVER_URI)
        response = self._post(body)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        associations = IdentityRecordAssociation.objects.filter(
            os_id=self.os_id
        )
        self.assertEqual(associations.count(), 1)
        self.assertEqual(associations.first().resolver_uri, RESOLVER_URI)

    def test_unauthenticated_request_is_rejected(self):
        """AC#3: no credentials, no registration."""
        self.client.logout()

        response = self._post()

        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )
        self.assertFalse(IdentityRecordAssociation.objects.exists())

    def test_exact_repeat_is_a_conflict_not_a_server_error(self):
        """
        The unique constraint must not surface as a 500. Idempotency is out
        of scope for the pilot, so an exact repeat is a conflict rather
        than a quiet success.
        """
        self._post()

        response = self._post()

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            IdentityRecordAssociation.objects.filter(
                os_id=self.os_id
            ).count(),
            1,
        )

    def test_malformed_os_id_is_rejected(self):
        """A bad checksum is a 400, and never reaches the database."""
        url = '/api/v1/production-locations/XX0000000BADID1/identity-records/'

        response = self._post(url=url)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_unknown_os_id_is_not_found(self):
        """
        A well-formed identifier this instance does not hold is a 404.

        Section 3.2 also lists a 422 for "well formed but not resolvable
        here", which 3.4 ties to private-instance identifiers. This
        instance cannot tell that case apart by design, so the write path
        returns 404 and OSDEV-3586 owns the distinction.
        """
        # A real minted identifier with a valid checksum, deliberately not
        # created in this test database.
        url = (
            '/api/v1/production-locations/AT2026278BXJ6AT/identity-records/'
        )

        response = self._post(url=url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_superseded_os_id_is_accepted(self):
        """
        A merged-away identifier still registers. It keeps resolving to the
        surviving location through FacilityAlias, which is the behaviour
        Section 2.7 promises, so refusing it here would break the link the
        reverse direction depends on.
        """
        alias_os_id = 'TH2026278GC5XXJ'
        FacilityAlias.objects.create(
            os_id=alias_os_id,
            facility=self.facility,
            reason=FacilityAlias.MERGE,
        )
        url = (
            f'/api/v1/production-locations/{alias_os_id}/identity-records/'
        )

        response = self._post(url=url)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_non_https_resolver_uri_is_rejected(self):
        """FR-06: the registered value must be an absolute HTTPS URI."""
        body = dict(self.body, resolver_uri='http://example.org/record')

        response = self._post(body)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_credential_url_is_rejected(self):
        """
        Registering a Credential URL would silently break the
        always-current guarantee, so the obvious shape of that mistake is
        refused (FR-06, 3.3, 3.5).
        """
        body = dict(
            self.body,
            resolver_uri=(
                'https://documents.credentials.responsiblebusiness.org/'
                'b157c46d-1e54-424d-8f96-14ab192c4d1f.json'
            ),
        )

        response = self._post(body)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_missing_required_field_is_rejected(self):
        """A body without a resolver_uri is malformed."""
        body = dict(self.body)
        del body['resolver_uri']

        response = self._post(body)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_registrant_reference_is_optional(self):
        """
        Open Supply Hub resolves on the OS ID alone, so the registrant's
        own handle is carried if given and not required.
        """
        body = dict(self.body)
        del body['registrant_reference']

        response = self._post(body)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_status_is_readable(self):
        """3.2: the current state, and once live, when it resolves."""
        created = self._post()
        moderation_id = created.data['moderation_id']

        response = self.client.get(f'{self.url}{moderation_id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['moderation_status'], 'APPROVED')
        self.assertEqual(response.data['moderation_id'], moderation_id)
        self.assertIsNotNone(response.data['live_from'])

    def test_status_for_unknown_registration_is_not_found(self):
        """An unknown or malformed handle is a miss, not a crash."""
        for handle in (
            '1d4f7c2e-9b31-4a6d-8f10-2c5e7a9b0d44',
            'not-a-uuid',
        ):
            with self.subTest(moderation_id=handle):
                response = self.client.get(f'{self.url}{handle}/')
                self.assertEqual(
                    response.status_code, status.HTTP_404_NOT_FOUND
                )
