import json

from django.contrib.gis.geos import Point
from django.core.cache import caches
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.contributor.contributor import Contributor
from api.models.facility.facility import Facility
from api.models.facility.facility_alias import FacilityAlias
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.identity_record_association import (
    IdentityRecordAssociation,
)
from api.models.source import Source
from api.models.user import User

LINKSET = 'application/linkset+json'

# Synthetic, checksum-valid. Never a real pilot identifier: this repository
# is public.
OS_ID = 'XX2000001AAAAA5'
SUPERSEDED_OS_ID = 'XX2000002AAAAA6'

# Checksum-valid and well formed, but not a location on this instance. This
# is the shape of an identifier issued only on a private instance.
ELSEWHERE_OS_ID = 'XX2000003AAAAA7'

# Fails the checksum, and also carries an 'I', which is outside Crockford
# base 32. Both are ways an identifier can be malformed and neither may
# reach the database.
BAD_OS_ID = 'XX2000001AAAAAI'


class IdentityResolverTest(APITestCase):
    """
    Tests for the resolver path, content negotiation and the
    not-resolvable-here answer (OSDEV-3581, OSDEV-3586).

    The literal path is asserted rather than reversed. /osid/{os_id} is a
    published contract in scope doc 3.1, so a rename has to break a test.
    """

    url = '/osid/{}'.format(OS_ID)

    def setUp(self):
        # Shared with the other API tests: the throttling cache is Redis and
        # survives runs, so a stale key can turn an expected 200 into a 429.
        caches['api_throttling'].clear()

        user = User.objects.create(email='test@example.com')
        contributor = Contributor.objects.create(
            admin=user,
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

    def test_html_request_redirects(self):
        """AC#1: a browser is sent to the production location page."""
        response = self.client.get(self.url, HTTP_ACCEPT='text/html')

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertTrue(response['Location'].endswith('/{}'.format(OS_ID)))

    def test_linkset_request_returns_a_linkset(self):
        """AC#2: software asking for a link-set gets one."""
        response = self.client.get(self.url, HTTP_ACCEPT=LINKSET)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], LINKSET)

        body = json.loads(response.content)

        self.assertIn('linkset', body)
        self.assertEqual(len(body['linkset']), 1)

        entry = body['linkset'][0]

        self.assertTrue(entry['anchor'].endswith('/osid/{}'.format(OS_ID)))
        self.assertTrue(entry['item'][0]['href'].endswith(OS_ID))
        self.assertEqual(entry['item'][0]['type'], 'text/html')

    def test_malformed_os_id_is_rejected(self):
        """
        AC#3: a malformed identifier is a 400 rather than a 404.

        The distinction matters more here than it usually would. 404 is the
        answer for a well-formed identifier this instance cannot resolve, so
        reusing it for a malformed one would blur the only signal a caller
        has for telling a typo from an identifier issued elsewhere.
        """
        for accept in ('text/html', LINKSET):
            with self.subTest(accept=accept):
                response = self.client.get(
                    '/osid/{}'.format(BAD_OS_ID), HTTP_ACCEPT=accept
                )
                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST
                )

    def test_unregistered_os_id_still_resolves(self):
        """
        FR-14: a location with no registered record is not an error. It
        resolves to the ordinary page, so the resolver never depends on a
        record existing. Only the location has to exist.
        """
        response = self.client.get(self.url, HTTP_ACCEPT='text/html')

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_superseded_os_id_still_resolves(self):
        """
        Scope doc 2.7: a merged-away identifier keeps resolving through
        FacilityAlias. It is present here, so it must not fall into the
        not-resolvable-here answer.
        """
        FacilityAlias.objects.create(
            os_id=SUPERSEDED_OS_ID,
            facility=self.facility,
            reason=FacilityAlias.MERGE,
        )

        response = self.client.get(
            '/osid/{}'.format(SUPERSEDED_OS_ID), HTTP_ACCEPT='text/html'
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def _register(self, os_id=None):
        return IdentityRecordAssociation.objects.create(
            os_id=os_id or OS_ID,
            resolver_uri='https://resolver.example.org/records/FAC-00000001',
            record_type='untp:DigitalFacilityRecord',
            issuer='did:web:issuer.example.org',
            live_from=timezone.now(),
        )

    def test_registered_identifier_goes_to_the_record_page(self):
        """
        Scope doc 3.1 and 2.6: an identifier that has a record resolves to
        the page showing that record, not to the ordinary location page.
        Sending a holder of a registered identifier to the plain profile
        would drop the thing they followed the identifier for.
        """
        self._register()

        response = self.client.get(self.url, HTTP_ACCEPT='text/html')

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertTrue(
            response['Location'].endswith(
                '/{}/identity-record'.format(OS_ID)
            )
        )

    def test_linkset_entry_points_at_the_record_page_too(self):
        """The machine path and the browser path agree on the target."""
        self._register()

        response = self.client.get(self.url, HTTP_ACCEPT=LINKSET)
        entry = json.loads(response.content)['linkset'][0]

        self.assertTrue(
            entry['item'][0]['href'].endswith(
                '/{}/identity-record'.format(OS_ID)
            )
        )

    def test_a_pending_registration_does_not_redirect_to_the_record(self):
        """
        An association with no live_from is not resolving yet, so it must
        not divert the visitor to a page with nothing on it.
        """
        self._register().__class__.objects.filter(os_id=OS_ID).update(
            live_from=None
        )

        response = self.client.get(self.url, HTTP_ACCEPT='text/html')

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertTrue(response['Location'].endswith('/{}'.format(OS_ID)))

    def test_bare_request_redirects_rather_than_returning_json(self):
        """
        A client sending no preference, or the */* that command line tools
        send by default, behaves like a browser. The link-set is an explicit
        opt-in, so a casual request never lands on a machine format.
        """
        for accept in ('*/*', ''):
            with self.subTest(accept=accept):
                response = self.client.get(self.url, HTTP_ACCEPT=accept)
                self.assertEqual(
                    response.status_code, status.HTTP_302_FOUND
                )

    def test_resolution_requires_no_authentication(self):
        """
        An identifier anyone can hold must be resolvable by anyone holding
        it, so this path overrides the project default permission. If that
        override is ever dropped the default would make the resolver useless
        to the public, hence an explicit test.
        """
        self.client.credentials()

        response = self.client.get(self.url, HTTP_ACCEPT=LINKSET)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_resolver_description_is_served(self):
        """
        The description document lets a client discover the identifier path
        instead of hard-coding it (scope doc 3.1).
        """
        response = self.client.get('/.well-known/resolver')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['resolverRoot'].endswith('/osid/'))
        self.assertIn(LINKSET, response.data['supportedLinkType'])


class PrivateInstanceIdentifierTest(APITestCase):
    """
    The not-resolvable-here answer (OSDEV-3586, scope doc 3.4).

    No fixtures: every identifier in these tests is absent from this
    instance, which is exactly the condition under test.
    """

    def setUp(self):
        caches['api_throttling'].clear()

    def test_identifier_not_here_is_not_resolvable(self):
        """
        AC#1: a well-formed identifier this instance did not issue returns
        404 saying it is not resolvable here, not that it is invalid. It may
        be perfectly valid on another instance and we are in no position to
        say otherwise.
        """
        for accept in ('text/html', LINKSET):
            with self.subTest(accept=accept):
                response = self.client.get(
                    '/osid/{}'.format(ELSEWHERE_OS_ID), HTTP_ACCEPT=accept
                )

                self.assertEqual(
                    response.status_code, status.HTTP_404_NOT_FOUND
                )
                self.assertEqual(
                    json.loads(response.content)['detail'],
                    'This identifier is not resolvable here.',
                )

    def test_response_discloses_nothing_about_another_instance(self):
        """
        AC#2, and the whole point of NFR-08. A resolver that hinted an
        identifier exists elsewhere would leak the private instance one
        probe at a time, so the body must not carry the suggestion in any
        form, including a helpful one.
        """
        response = self.client.get(
            '/osid/{}'.format(ELSEWHERE_OS_ID), HTTP_ACCEPT=LINKSET
        )

        body = response.content.decode().lower()

        for leak in (
            'private',
            'rba',
            'another instance',
            'other instance',
            'elsewhere',
            'exists',
        ):
            with self.subTest(term=leak):
                self.assertNotIn(leak, body)

    def test_answer_is_identical_whether_or_not_it_exists_elsewhere(self):
        """
        Two identifiers absent from this instance must be indistinguishable
        in the response, otherwise the difference itself is the disclosure.
        """
        first = self.client.get(
            '/osid/{}'.format(ELSEWHERE_OS_ID), HTTP_ACCEPT=LINKSET
        )
        second = self.client.get(
            '/osid/{}'.format(SUPERSEDED_OS_ID), HTTP_ACCEPT=LINKSET
        )

        self.assertEqual(first.status_code, second.status_code)
        self.assertEqual(first.content, second.content)

    def test_no_linkset_is_emitted_for_an_identifier_not_here(self):
        """
        A link-set would anchor on a URI this resolver does not answer for,
        which asserts more than a 404 does.
        """
        response = self.client.get(
            '/osid/{}'.format(ELSEWHERE_OS_ID), HTTP_ACCEPT=LINKSET
        )

        self.assertNotIn('linkset', response.content.decode())
