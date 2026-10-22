from urllib.parse import urlparse

from rest_framework import status
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from api.views.v1.link_type_vocabulary import LINK_TYPES


# The switch gates access, not content. These assert what the vocabulary
# says once it is on; the off case is VocabularySwitchOffTest below.
@override_switch('enable_identity_resolver', active=True)
class LinkTypeVocabularyTest(APITestCase):
    """
    The link type vocabulary (OSDEV-3582).

    UNTP defines `linkType` as a plain string and enumerates no values, so
    each resolver declares its own terms at a resolvable namespace. These
    assert that ours are published and that each one dereferences.
    """

    def test_the_namespace_lists_every_term(self):
        response = self.client.get('/api/v1/voc/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        published = {entry['name'] for entry in response.data['linkTypes']}
        self.assertEqual(
            published, {entry['name'] for entry in LINK_TYPES}
        )

    def test_every_published_term_dereferences(self):
        """
        The link-set keys are these URIs. A key that 404s is not a
        vocabulary, which is the obligation that comes with minting our
        own rather than using a registry.

        Follows the published `linkType` rather than rebuilding the path,
        so that moving the route without moving the published URI fails
        here instead of silently killing every key we emit.
        """
        listing = self.client.get('/api/v1/voc/')

        for entry in listing.data['linkTypes']:
            with self.subTest(term=entry['name']):
                published = urlparse(entry['linkType']).path

                response = self.client.get(published)

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data['name'], entry['name'])
                self.assertTrue(response.data['description'])

    def test_a_trailing_slash_is_still_our_answer(self):
        """
        Unmatched paths are answered by the SPA middleware with
        index.html, so a near-miss has to be a route we own or it is a
        200 carrying the web app instead of a 404.
        """
        known = self.client.get('/api/v1/voc/productionLocation/')
        unknown = self.client.get('/api/v1/voc/notOurTerm/')

        self.assertEqual(known.status_code, status.HTTP_200_OK)
        self.assertEqual(unknown.status_code, status.HTTP_404_NOT_FOUND)

    def test_a_linked_data_client_is_not_refused(self):
        """
        These URIs are published for dereferencing, and a client told to
        dereference them asks for `application/ld+json`. Without a
        renderer for that type, negotiation refuses before the view runs.
        """
        response = self.client.get(
            '/api/v1/voc/productionLocation',
            HTTP_ACCEPT='application/ld+json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response['Content-Type'], 'application/ld+json'
        )

    def test_a_term_that_is_not_ours_is_not_found(self):
        """A 404 rather than the whole vocabulary, so a client can tell."""
        response = self.client.get('/api/v1/voc/notOurTerm')

        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )

    def test_the_profile_form_returns_the_same_document(self):
        """
        `?show=linktypes` is the shape the reference resolver gives for a
        profile URL. We accept it and answer the same way, so a client
        written against that convention reads ours without a special case.
        """
        plain = self.client.get('/api/v1/voc/')
        profile = self.client.get('/api/v1/voc/?show=linktypes')

        self.assertEqual(profile.status_code, status.HTTP_200_OK)
        self.assertEqual(profile.data, plain.data)

    def test_a_bad_token_does_not_refuse_the_vocabulary(self):
        """
        A stranger holding one of our link-sets has to be able to look up
        what its keys mean. Sent with a credential the project default
        would reject, which is what `authentication_classes = ()` buys;
        an unauthenticated request alone would pass either way.
        """
        response = self.client.get(
            '/api/v1/voc/', HTTP_AUTHORIZATION='Token not-a-real-token'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class VocabularySwitchOffTest(APITestCase):
    """The vocabulary is dark with the resolver it explains."""

    def test_the_namespace_is_not_published(self):
        response = self.client.get('/api/v1/voc/')

        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )

    def test_no_term_is_published(self):
        response = self.client.get('/api/v1/voc/productionLocation')

        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )
