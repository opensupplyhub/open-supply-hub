import json

from django.contrib.gis.geos import Point
from django.core.cache import caches
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from waffle.testutils import override_switch

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


# The switch gates access, not behavior. These assert what the pilot
# does once it is on; the off case is asserted in
# test_identity_record_switches.py.
class ResolverFixture:
    """
    Shared fixtures for the resolver tests.
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


# The switch gates access, not behavior. These assert what the resolver
# does once it is on; the off case is ResolverSwitchOffTest below.
@override_switch('enable_identity_resolver', active=True)
class IdentityResolverTest(ResolverFixture, APITestCase):
    """
    The resolver path, content negotiation and the not-resolvable-here
    answer (OSDEV-3581).

    The literal path is asserted rather than reversed. /osid/{os_id} is a
    published contract, so a rename has to break a test.
    """

    def test_html_request_redirects(self):
        """A browser is sent to the production location page."""
        response = self.client.get(self.url, HTTP_ACCEPT='text/html')

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertTrue(response['Location'].endswith('/{}'.format(OS_ID)))

    def test_linkset_request_returns_a_linkset(self):
        """Software asking for a link-set gets one."""
        response = self.client.get(self.url, HTTP_ACCEPT=LINKSET)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], LINKSET)

        body = json.loads(response.content)

        self.assertIn('linkset', body)
        self.assertEqual(len(body['linkset']), 1)

        entry = body['linkset'][0]

        self.assertTrue(entry['anchor'].endswith('/osid/{}'.format(OS_ID)))

        location = next(
            v for k, v in entry.items()
            if k.endswith('productionLocation')
        )

        self.assertTrue(location[0]['href'].endswith(OS_ID))
        self.assertEqual(location[0]['type'], 'text/html')

    def test_malformed_os_id_is_rejected(self):
        """
        A malformed identifier is a 400 rather than a 404.

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
        A location with no registered record is not an error; it
        resolves to the ordinary page. The resolver never depends on a
        record existing, only on the location existing.
        """
        response = self.client.get(self.url, HTTP_ACCEPT='text/html')

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_superseded_os_id_still_resolves(self):
        """
        A merged-away identifier keeps resolving through
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

    def _register(self, os_id=None, resolver_uri=None):
        return IdentityRecordAssociation.objects.create(
            os_id=os_id or OS_ID,
            resolver_uri=resolver_uri or (
                'https://resolver.example.test'
                '/records/REC-00000001'
            ),
            record_type='untp:DigitalFacilityRecord',
            issuer='did:web:issuer.example.org',
            live_from=timezone.now(),
        )

    def test_a_hyphenated_identifier_resolves(self):
        """
        validate_os_id accepts the hyphenated spelling, so the lookup has
        to use the normalized form. Otherwise a hyphenated identifier
        passes validation and then answers not-resolvable-here for a
        location we hold.
        """
        hyphenated = '{}-{}-{}'.format(OS_ID[:2], OS_ID[2:9], OS_ID[9:])

        response = self.client.get(
            '/osid/{}'.format(hyphenated), HTTP_ACCEPT='text/html'
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_link_header_cannot_carry_forged_relations(self):
        """
        A resolver URI is supplied by a registrant and URLValidator
        accepts the characters that separate fields in a Link header, so
        the header would otherwise be forgeable by whoever registered.
        """
        self._register(
            resolver_uri=(
                'https://resolver.example.test/a>; rel="forged'
            )
        )

        response = self.client.get(self.url, HTTP_ACCEPT=LINKSET)

        self.assertNotIn('rel="forged"', response['Link'])

    def test_registered_identifier_goes_to_the_record_page(self):
        """
        An identifier that has a record resolves to
        the page showing that record, not to the ordinary location page.
        Sending a holder of a registered identifier to the plain profile
        would drop the thing they followed the identifier for.
        """
        self._register()

        response = self.client.get(self.url, HTTP_ACCEPT='text/html')

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertTrue(
            response['Location'].endswith(
                '/facilities/{}/identity-record'.format(OS_ID)
            )
        )

    @override_switch('enable_production_location_page', active=True)
    def test_record_page_redirect_ignores_the_location_page_switch(self):
        """
        The record page is mounted under `facilities` only. Composing the
        redirect from the location page URL would follow that switch to a
        path the web app does not serve, and the visitor would land on
        the ordinary profile with no sign anything was missed.
        """
        self._register()

        response = self.client.get(self.url, HTTP_ACCEPT='text/html')

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertTrue(
            response['Location'].endswith(
                '/facilities/{}/identity-record'.format(OS_ID)
            )
        )

    def test_a_lower_case_identifier_resolves(self):
        """
        Crockford base 32 is case-insensitive on decode, and lowercasing
        the country code leaves the checksum unchanged, so a lower-case
        spelling validates and then misses a case-sensitive lookup unless
        it is folded first.
        """
        response = self.client.get(
            '/osid/{}'.format(OS_ID.lower()), HTTP_ACCEPT='text/html'
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertTrue(response['Location'].endswith(OS_ID))

    def test_a_trailing_slash_is_still_our_answer(self):
        """
        Unmatched paths are answered by the SPA middleware with
        index.html, so a near-miss has to be a route we own or it is a
        200 carrying the web app instead of the resolver's answer.
        """
        resolved = self.client.get(
            '{}/'.format(self.url), HTTP_ACCEPT='text/html'
        )
        self.assertEqual(resolved.status_code, status.HTTP_302_FOUND)

        description = self.client.get('/.well-known/resolver/')
        self.assertEqual(description.status_code, status.HTTP_200_OK)

    def test_the_linkset_body_is_json_whatever_else_is_accepted(self):
        """
        The link-set branch is chosen from the raw Accept header while
        DRF selects a renderer independently. A parameterized HTML type
        outranks the bare link-set type and selects the HTML renderer,
        which hands the dict to Django to iterate, sending the bare key
        `linkset` under a JSON media type.
        """
        response = self.client.get(
            self.url,
            HTTP_ACCEPT='{}, text/html;charset=utf-8'.format(LINKSET),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], LINKSET)
        # Parses, rather than being a repr that merely looks like JSON.
        self.assertIn('linkset', json.loads(response.content))

    def test_production_location_relation_points_at_the_location(self):
        """
        The published vocabulary defines this relation as the location
        page, so it stays the location page once a record exists.
        Retargeting it at the record would leave the link-set with no link
        to the location at all.
        """
        self._register()

        response = self.client.get(self.url, HTTP_ACCEPT=LINKSET)
        entry = json.loads(response.content)['linkset'][0]

        location = next(
            v for k, v in entry.items()
            if k.endswith('productionLocation')
        )
        record = next(
            v for k, v in entry.items()
            if k.endswith('registeredRecord')
        )

        self.assertTrue(location[0]['href'].endswith('/{}'.format(OS_ID)))
        self.assertTrue(record)

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
        instead of hard-coding it.
        """
        response = self.client.get('/.well-known/resolver')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['resolverRoot'].endswith('/osid/'))

        # Link relation types, which is what the field enumerates. The
        # link-set media type is advertised through content negotiation.
        self.assertTrue(
            all(
                link_type.endswith(('productionLocation', 'registeredRecord'))
                for link_type in response.data['supportedLinkType']
            )
        )
        self.assertEqual(len(response.data['supportedLinkType']), 2)

    def test_each_published_link_type_dereferences(self):
        """
        The link-set keys are these URIs. A key that 404s is not a
        vocabulary, which is the whole obligation of minting our own.
        """
        description = self.client.get('/.well-known/resolver')

        for link_type in description.data['supportedLinkType']:
            with self.subTest(link_type=link_type):
                definition = self.client.get(
                    link_type.replace('https://testserver', '')
                )
                self.assertEqual(
                    definition.status_code, status.HTTP_200_OK
                )
                self.assertIn('description', definition.data)


# The switch gates access, not behavior. These assert what the pilot
# does once it is on; the off case is asserted in
# test_identity_record_switches.py.
@override_switch('enable_identity_resolver', active=True)
class PrivateInstanceIdentifierTest(APITestCase):
    """
    The not-resolvable-here answer (OSDEV-3581).

    No fixtures: every identifier in these tests is absent from this
    instance, which is exactly the condition under test.
    """

    def setUp(self):
        caches['api_throttling'].clear()

    def test_identifier_not_here_is_not_resolvable(self):
        """
        A well-formed identifier this instance did not issue returns
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
        A resolver that hinted an
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


class ResolverSwitchOffTest(ResolverFixture, APITestCase):
    """
    The resolver is dark until someone opens it, and these run
    undecorated against the switch exactly as it ships. Turning it on is
    what makes /osid/{os_id} answer for every OS ID on the instance
    rather than only those carrying a record.
    """

    def test_resolver_does_not_answer(self):
        response = self.client.get(self.url, HTTP_ACCEPT='text/html')

        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )

    def test_a_registered_record_does_not_open_it(self):
        """
        Registration and resolution are separate switches precisely so the
        pilot records can exist in a deployed environment before anything
        about them is reachable.
        """
        IdentityRecordAssociation.objects.create(
            os_id=OS_ID,
            resolver_uri=(
                'https://resolver.example.test/osid/{}'
                .format(OS_ID)
            ),
            record_type='untp:DigitalFacilityRecord',
            issuer='did:web:issuer.example.org',
            live_from=timezone.now(),
        )

        response = self.client.get(self.url, HTTP_ACCEPT='text/html')

        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )

    def test_the_dark_answer_matches_the_unresolvable_one(self):
        """
        The switch-off answer for a real OS ID has to match the answer a
        running resolver gives for an identifier it cannot resolve. The
        two have to be compared across the switch: comparing two
        switch-off responses passes no matter what either says.
        """
        dark = self.client.get(self.url)

        with override_switch('enable_identity_resolver', active=True):
            running = self.client.get('/osid/{}'.format(ELSEWHERE_OS_ID))

        self.assertEqual(dark.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(dark.status_code, running.status_code)
        self.assertEqual(dark.json(), running.json())

    def test_a_malformed_identifier_shows_the_switch_state(self):
        """
        The gate's limit, pinned rather than described. A malformed
        identifier is a 400 once the resolver is live and a 404 while it
        is dark, so one probe distinguishes them. Recorded rather than
        closed, because the 400 is the routing contract.
        """
        with override_switch('enable_identity_resolver', active=True):
            live = self.client.get('/osid/{}'.format(BAD_OS_ID))
        dark = self.client.get('/osid/{}'.format(BAD_OS_ID))

        self.assertEqual(live.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(dark.status_code, status.HTTP_404_NOT_FOUND)

    def test_resolver_description_is_not_published(self):
        response = self.client.get('/.well-known/resolver')

        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )

    def test_link_type_vocabulary_is_not_published(self):
        response = self.client.get('/api/v1/voc/')

        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )
