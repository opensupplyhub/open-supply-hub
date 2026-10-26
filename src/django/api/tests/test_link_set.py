import json

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
from api.views.v1.identity_resolver import UNTP_DFR_RELATION

LINKSET = 'application/linkset+json'
OS_ID = 'XX2000001AAAAA5'
RESOLVER_URI = (
    'https://resolver.example.test/records/REC-00000001'
)


# The switch gates access, not behavior. These assert what the pilot
# does once it is on; the off case is asserted in
# test_identity_record_switches.py.
@override_switch('enable_identity_resolver', active=True)
class LinkSetTest(APITestCase):
    """
    The link-set and the vocabulary its keys resolve to. UNTP defines
    `linkType` as a plain string and enumerates no values, so these pin
    that we publish our own terms and that the keys we emit are the ones
    we publish.
    """

    url = '/osid/{}'.format(OS_ID)

    def setUp(self):
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

    def _register(self, **overrides):
        fields = {
            'os_id': OS_ID,
            'resolver_uri': RESOLVER_URI,
            'record_type': 'untp:DigitalFacilityRecord',
            'issuer': 'did:web:issuer.example.org',
            'live_from': timezone.now(),
        }
        fields.update(overrides)
        return IdentityRecordAssociation.objects.create(**fields)

    def _linkset(self):
        response = self.client.get(self.url, HTTP_ACCEPT=LINKSET)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response, json.loads(response.content)['linkset'][0]

    def test_carries_both_records_when_one_is_registered(self):
        """
        Our location, and the registered record under two relations: our
        own term and the issuer's. Three keys, two distinct targets.
        """
        self._register()

        _, entry = self._linkset()
        relations = [k for k in entry if k != 'anchor']

        self.assertEqual(len(relations), 3)

        registered = [
            k for k in relations if k.endswith('registeredRecord')
        ]
        self.assertEqual(len(registered), 1)
        self.assertEqual(
            entry[registered[0]][0]['href'], RESOLVER_URI
        )
        self.assertEqual(len(entry[registered[0]]), 1)

    def test_the_record_is_also_offered_under_the_issuer_term(self):
        """
        A client written against the issuer's vocabulary looks for
        `untp:dfr` and nothing else. Carrying the same target under both
        terms is what stops it reading this link-set and finding no
        record. The two must not drift apart.
        """
        self._register()

        _, entry = self._linkset()

        self.assertIn(UNTP_DFR_RELATION, entry)

        ours = next(k for k in entry if k.endswith('registeredRecord'))
        self.assertEqual(entry[UNTP_DFR_RELATION], entry[ours])

    def test_no_issuer_term_when_nothing_is_registered(self):
        """
        The alias is the record, not a permanent fixture. With no record
        there is nothing for it to point at, and an empty entry would
        tell a client one exists.
        """
        _, entry = self._linkset()

        self.assertNotIn(UNTP_DFR_RELATION, entry)

    def test_the_registered_entry_is_the_resolver_not_a_version(self):
        """
        The stored value resolves rather than points, which
        is what lets a reissued record stay current without anyone
        re-registering. Emitting a document link here would quietly undo
        that.
        """
        self._register()

        _, entry = self._linkset()
        registered = next(
            k for k in entry if k.endswith('registeredRecord')
        )

        href = entry[registered][0]['href']

        self.assertEqual(href, RESOLVER_URI)
        self.assertFalse(href.endswith('.json'))

    def test_relation_keys_resolve_to_our_published_vocabulary(self):
        """
        The obligation that comes with minting our own terms: a stranger
        holding this link-set must be able to look up what the keys mean.

        The issuer's `untp:dfr` is excluded by name rather than by
        pattern, so a key that is neither ours nor that one still fails
        here instead of being waved through.
        """
        self._register()

        _, entry = self._linkset()
        relations = [
            k for k in entry
            if k != 'anchor' and k != UNTP_DFR_RELATION
        ]

        vocab = self.client.get('/api/v1/voc/')
        self.assertEqual(vocab.status_code, status.HTTP_200_OK)

        published = {t['linkType'] for t in vocab.data['linkTypes']}

        for relation in relations:
            with self.subTest(relation=relation):
                self.assertIn(relation, published)

    def test_vocabulary_defines_every_term_it_publishes(self):
        """A term without a definition is not a vocabulary entry."""
        vocab = self.client.get('/api/v1/voc/')

        for term in vocab.data['linkTypes']:
            with self.subTest(term=term['name']):
                self.assertTrue(term['title'])
                self.assertTrue(term['description'])
                self.assertTrue(
                    term['linkType'].startswith(vocab.data['namespace'])
                )

    def test_resolver_description_points_at_the_vocabulary(self):
        """
        A client should be able to find the vocabulary from the resolver
        description rather than being told about it out of band.
        """
        response = self.client.get('/.well-known/resolver')

        self.assertTrue(
            response.data['namespaceURI'].endswith('/api/v1/voc/')
        )
        self.assertIn('show=linktypes', response.data['profileUrl'])

    def test_description_advertises_every_relation_it_emits(self):
        """
        A client that checks the description before asking for a
        link-set is the one the issuer-term alias exists for. Leaving
        that term out here would tell it we have no record relation and
        stop it asking, which is the whole gap the alias closes.

        Publishing a definition is a separate matter: only our own terms
        dereference under namespaceURI.
        """
        response = self.client.get('/.well-known/resolver')
        supported = response.data['supportedLinkType']

        self.assertIn(UNTP_DFR_RELATION, supported)
        self.assertTrue(
            any(t.endswith('registeredRecord') for t in supported)
        )
        self.assertTrue(
            any(t.endswith('productionLocation') for t in supported)
        )

    def test_links_are_served_in_the_header_too(self):
        """
        The issuer serves the link-set both in the body and
        as a Link header, and commits us to matching.
        """
        self._register()

        response, entry = self._linkset()
        header = response['Link']

        self.assertIn(RESOLVER_URI, header)
        self.assertIn('rel=', header)
        self.assertIn(entry['anchor'], header)

        # The commitment is that a header-reading client sees what a
        # body-reading one sees. Without this, narrowing header
        # generation to our own namespace would drop the alias from the
        # header alone and every other test would still pass.
        self.assertIn(
            'rel="{}"'.format(UNTP_DFR_RELATION), header
        )
        ours = next(k for k in entry if k.endswith('registeredRecord'))
        self.assertIn('rel="{}"'.format(ours), header)

    def test_no_registered_record_is_a_normal_response(self):
        """
        Our own entry is still there, the record entry is
        absent, and nothing is an error.
        """
        response, entry = self._linkset()
        relations = [k for k in entry if k != 'anchor']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(relations), 1)
        self.assertTrue(relations[0].endswith('productionLocation'))

    def test_a_pending_registration_is_not_published(self):
        """
        An association that is not yet live must not appear, or a consumer
        would follow it to a record we are not yet serving.
        """
        self._register(live_from=None)

        _, entry = self._linkset()
        relations = [k for k in entry if k != 'anchor']

        self.assertEqual(len(relations), 1)
        self.assertTrue(relations[0].endswith('productionLocation'))

    def test_the_vocabulary_is_public(self):
        """
        Keys in a public link-set that only an authenticated caller can
        look up would not be a vocabulary.
        """
        self.client.credentials()

        response = self.client.get('/api/v1/voc/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
