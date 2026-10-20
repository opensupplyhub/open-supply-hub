import base64
import json
from unittest.mock import patch

from allauth.account.models import EmailAddress
from django.contrib.gis.geos import Point
from django.core.cache import caches
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from waffle.testutils import override_switch

from api.models.contributor.contributor import Contributor
from api.models.facility.facility import Facility
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.identity_record_association import IdentityRecordAssociation
from api.models.source import Source
from api.models.user import User

OS_ID = 'XX2000001AAAAA5'
RESOLVER_URI = (
    'https://resolver.test-issuer.example/records/REC-00000001'
)
DOCUMENT_URI = (
    'https://documents.test-issuer.example/'
    '00000000-0000-4000-8000-000000000001.json'
)
RETRIEVE = 'api.services.identity_record_retrieval.requests.get'

CREDENTIAL = {
    'id': 'https://credentials.test-issuer.example/credentials/REC-00000001',
    'type': ['VerifiableCredential', 'DigitalFacilityRecord'],
    'issuer': {'id': 'did:web:issuer.example.org'},
    'name': 'Digital Facility Record - Example Facility',
    'credentialSubject': {
        'name': 'Example Facility',
        'registeredId': 'REC-00000001',
        'countryOfOperation': {'countryCode': 'XX'},
    },
}


def _envelope():
    def seg(obj):
        return base64.urlsafe_b64encode(
            json.dumps(obj).encode()
        ).decode().rstrip('=')

    token = '{}.{}.{}'.format(
        seg({'alg': 'EdDSA'}), seg(CREDENTIAL), 'sig'
    )
    return {
        'type': 'EnvelopedVerifiableCredential',
        'id': 'data:application/vc+jwt,{}'.format(token),
    }


class _Resp:
    def __init__(self, status_code=200, payload=None, headers=None):
        self.status_code = status_code
        self._payload = payload
        self.headers = headers or {}

    @property
    def content(self):
        """The encoded body, which the size check reads before parsing."""
        if self._payload is None:
            return b'not json'
        return json.dumps(self._payload).encode()

    def json(self):
        if self._payload is None:
            raise ValueError('not json')
        return self._payload


def _two_hop(url, **kwargs):
    if url == RESOLVER_URI:
        q = json.dumps(
            {'payload': {'uri': DOCUMENT_URI, 'digestMultibase': 'zQm1'}}
        )
        return _Resp(
            302,
            headers={
                'Location':
                    'https://verify.test-issuer.example/?q={}'.format(q)
            },
        )
    return _Resp(200, _envelope())


# The switch gates access, not behavior. These assert what the pilot
# does once it is on; the off case is asserted in
# test_identity_record_switches.py.
class ContentFixture:
    """
    The endpoint feeding the identity-record page (OSDEV-3584, FR-13).

    The literal path is asserted because the page is built against it.
    """

    def setUp(self):
        caches['api_throttling'].clear()

        email = 'test@example.com'
        self.user = User.objects.create(email=email)
        self.user.set_password('example123')
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
            name='Test Location',
            address='1 Test Street',
            country_code='XX',
            sector=['Apparel'],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )
        self.facility = Facility.objects.create(
            id=OS_ID,
            name=item.name,
            address=item.address,
            country_code=item.country_code,
            location=Point(0, 0),
            created_from=item,
        )
        self.url = (
            f'/api/v1/production-locations/{OS_ID}/identity-record/'
        )
        # Most of these assert on content rather than on access, so they
        # authenticate to keep the subject of each test clear. Anonymous
        # access is the real contract and is asserted on its own in
        # test_is_readable_without_an_account.
        self.client.force_authenticate(self.user)

    def _register(self):
        return IdentityRecordAssociation.objects.create(
            os_id=OS_ID,
            resolver_uri=RESOLVER_URI,
            record_type='untp:DigitalFacilityRecord',
            issuer='did:web:issuer.example.org',
            registrant_reference='REC-00000001',
            live_from=timezone.now(),
        )


# The switch gates access, not behavior. These assert what the endpoint
# returns once it is on; the off case is ContentSwitchOffTest below.
@override_switch('enable_identity_resolver', active=True)
class IdentityRecordContentTest(ContentFixture, APITestCase):
    """
    The endpoint backing the identity record page (OSDEV-3584, FR-13).
    """

    def test_returns_the_decoded_record(self):
        """AC#1: the page gets a readable record, attributed to its issuer."""
        self._register()

        with patch(RETRIEVE, side_effect=_two_hop):
            response = self.client.get(self.url)

        # Asserts reachability, not content. Whether the issuer's record
        # could be fetched is a separate axis, mocked and asserted in the
        # tests above; an anonymous caller must get the same answer an
        # authenticated one would, whatever that answer is.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['os_id'], OS_ID)
        self.assertEqual(response.data['issuer'], 'did:web:issuer.example.org')
        self.assertEqual(response.data['resolver_uri'], RESOLVER_URI)
        self.assertEqual(response.data['document_uri'], DOCUMENT_URI)
        self.assertEqual(
            response.data['credential']['credentialSubject']['name'],
            'Example Facility',
        )

    def test_a_failure_is_a_200_carrying_the_reason(self):
        """
        The request to Open Supply Hub did not fail, the issuer's did,
        so this is a 200 with a typed reason rather than an error
        status. The page needs to say which failure it was.
        """
        self._register()

        with patch(RETRIEVE, side_effect=_two_hop) as mocked:
            mocked.side_effect = lambda url, **kw: _Resp(503)
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['available'])
        self.assertEqual(response.data['reason'], 'upstream_error')
        self.assertIn('detail', response.data)

    def test_unregistered_identifier_reports_rather_than_errors(self):
        """
        FR-14: no registered record is an ordinary state. The page shows
        that rather than a dead end.
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['available'])
        self.assertEqual(response.data['reason'], 'not_registered')

    def test_encrypted_record_is_reported_as_such(self):
        """BRD 8: encrypted records are out of scope and say so."""
        self._register()

        def _encrypted(url, **kwargs):
            if url == RESOLVER_URI:
                return _two_hop(url)
            return _Resp(200, {'cipherText': 'x', 'iv': 'y'})

        with patch(RETRIEVE, side_effect=_encrypted):
            response = self.client.get(self.url)

        self.assertFalse(response.data['available'])
        self.assertEqual(response.data['reason'], 'encrypted')

    def test_nothing_is_written_to_the_facility(self):
        """
        AC#3: none of the issuer's values reach Open Supply Hub's own
        record of the location.
        """
        self._register()

        with patch(RETRIEVE, side_effect=_two_hop):
            self.client.get(self.url)

        self.facility.refresh_from_db()

        self.assertEqual(self.facility.name, 'Test Location')
        self.assertEqual(self.facility.address, '1 Test Street')

    def test_is_readable_without_an_account(self):
        """
        Readable anonymously, because the resolver sends a browser here
        that holds one of our identifiers and nothing else. Requiring an
        account would leave exactly those visitors on a page that cannot
        load its own content.
        """
        self._register()
        self.client.force_authenticate(None)

        response = self.client.get(self.url)

        # Asserts reachability, not content. Whether the issuer's record
        # could be fetched is a separate axis, mocked and asserted in the
        # tests above; an anonymous caller must get the same answer an
        # authenticated one would, whatever that answer is.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['os_id'], OS_ID)


class ContentSwitchOffTest(ContentFixture, APITestCase):
    """
    The record content endpoint is dark with the resolver.

    Gated with resolution rather than registration because this is the
    read side: it backs a page the public reaches by following an
    identifier, so it opens when that path opens.
    """

    def test_is_not_found_while_the_resolver_is_off(self):
        self._register()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )

    def test_is_not_found_for_an_authenticated_caller_either(self):
        """
        The gate is on the feature, not on the audience. An account does
        not buy early access to an unannounced pilot.
        """
        self._register()
        self.client.force_authenticate(self.user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )
