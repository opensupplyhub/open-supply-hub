import json

from django.core.cache import caches
from rest_framework import status
from rest_framework.test import APITestCase

LINKSET = 'application/linkset+json'

# Synthetic, checksum-valid. Never a real pilot identifier: this repository
# is public.
OS_ID = 'XX2000001AAAAA5'

# Fails the checksum, and also carries an 'I', which is outside Crockford
# base 32. Both are ways an identifier can be malformed and neither may
# reach the database.
BAD_OS_ID = 'XX2000001AAAAAI'


class IdentityResolverTest(APITestCase):
    """
    Tests for the resolver path and content negotiation (OSDEV-3581).

    The literal path is asserted rather than reversed. /osid/{os_id} is a
    published contract in scope doc 3.1, so a rename has to break a test.
    """

    url = '/osid/{}'.format(OS_ID)

    def setUp(self):
        # Shared with the other API tests: the throttling cache is Redis and
        # survives runs, so a stale key can turn an expected 200 into a 429.
        caches['api_throttling'].clear()

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

        404 would assert the identifier does not exist. 400 says only that it
        is not a well-formed OS ID, which is the honest answer and the one
        that does not require a lookup to give.
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
        FR-14: an OS ID with no registered record is not an error. It
        resolves to the ordinary page, so the resolver never depends on a
        record existing.
        """
        response = self.client.get(self.url, HTTP_ACCEPT='text/html')

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

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
