import base64
import json
from unittest.mock import patch

import requests
from django.test import TestCase
from django.utils import timezone

from api.models import IdentityRecordAssociation
from api.services.identity_record_retrieval import (
    RetrievalFailureReason,
    find_integrity,
    is_encrypted,
    is_safe_resolver_uri,
    parse_resolver_redirect,
    retrieve_identity_record,
    unwrap_credential,
)

OS_ID = 'XX2000001AAAAA5'
RESOLVER_URI = (
    'https://resolver.example.test/records/REC-00000001'
)
DOCUMENT_URI = (
    'https://documents.example.test/'
    '00000000-0000-4000-8000-000000000001.json'
)
VIEWER = 'https://verify.example.test/verify'
DIGEST = 'zQmExampleDigestValueForTestsOnly000000000000'

RETRIEVE = 'api.services.identity_record_retrieval.requests.get'

# The credential a reader actually wants, as it sits inside the envelope.
CREDENTIAL = {
    'id': 'https://credentials.example.test/credentials/REC-00000001',
    'type': ['VerifiableCredential', 'DigitalFacilityRecord'],
    'issuer': {'id': 'did:web:issuer.example.org'},
    'validFrom': '2026-09-04T14:03:30.081Z',
    'name': 'Digital Facility Record - Example Facility',
    'credentialSubject': {
        'id': RESOLVER_URI,
        'name': 'Example Facility',
        'registeredId': 'REC-00000001',
        'countryOfOperation': {'countryCode': 'XX'},
    },
}


def make_jwt(claims):
    """A JWT-shaped token. Only the payload segment is ever read."""
    def seg(obj):
        raw = json.dumps(obj).encode()
        return base64.urlsafe_b64encode(raw).decode().rstrip('=')

    return '{}.{}.{}'.format(
        seg({'alg': 'EdDSA', 'typ': 'vc+jwt'}), seg(claims), 'not-a-signature'
    )


def envelope(claims=None):
    """
    The shape the issuer actually serves: an enveloped verifiable
    credential whose entire content is a signed JWT in a data URI.
    """
    return {
        '@context': ['https://www.w3.org/ns/credentials/v2'],
        'type': 'EnvelopedVerifiableCredential',
        'id': 'data:application/vc+jwt,{}'.format(
            make_jwt(CREDENTIAL if claims is None else claims)
        ),
    }


def redirect_location(uri=DOCUMENT_URI, digest=DIGEST):
    q = json.dumps({'payload': {'uri': uri, 'digestMultibase': digest}})
    return '{}?q={}&linkType=untp:dfr'.format(VIEWER, q)


class FakeResponse:
    def __init__(self, status_code=200, payload=None, headers=None,
                 content=None):
        self.status_code = status_code
        self._payload = payload
        self.headers = headers or {}
        self._content = content

    @property
    def content(self):
        """
        The encoded body, which the size check reads before parsing. Taken
        from the payload unless a test supplies its own bytes.
        """
        if self._content is not None:
            return self._content
        if self._payload is None:
            return b'not json'
        return json.dumps(self._payload).encode()

    def json(self):
        if self._payload is None:
            raise ValueError('not json')
        return self._payload


def two_hop(resolver=None, document=None):
    """
    Dispatch by URL so a test states what each hop returns rather than
    depending on call order.
    """
    resolver = resolver or FakeResponse(
        302, headers={'Location': redirect_location()}
    )
    document = document or FakeResponse(200, envelope())

    def _dispatch(url, **kwargs):
        if url == RESOLVER_URI:
            return resolver
        return document

    return _dispatch


class AssociationFixture:
    """Shared fixture for the retrieval tests."""

    def _associate(self, **overrides):
        fields = {
            'os_id': OS_ID,
            'resolver_uri': RESOLVER_URI,
            'record_type': 'untp:DigitalFacilityRecord',
            'issuer': 'did:web:issuer.example.org',
            'registrant_reference': 'REC-00000001',
            'live_from': timezone.now(),
        }
        fields.update(overrides)
        return IdentityRecordAssociation.objects.create(**fields)


class IdentityRecordRetrievalTest(AssociationFixture, TestCase):
    """
    Tests for retrieving a registered record (OSDEV-3583).

    The issuer is always mocked, but the shapes are not invented: they
    mirror what the pilot issuer's resolver was observed to return, with
    synthetic values throughout.
    """

    def test_retrieves_the_current_record(self):
        """
        Two hops: the resolver names the current document in its redirect,
        and that document is fetched and unwrapped.
        """
        self._associate()

        with patch(RETRIEVE, side_effect=two_hop()):
            outcome = retrieve_identity_record(OS_ID)

        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.record.os_id, OS_ID)
        self.assertEqual(outcome.record.document_uri, DOCUMENT_URI)
        self.assertEqual(
            outcome.record.content['credentialSubject']['name'],
            'Example Facility',
        )
        self.assertIn('DigitalFacilityRecord', outcome.record.content['type'])

    def test_version_choice_comes_from_the_issuer(self):
        """
        A link-set can list many versions under identical titles, and
        first-listed is no guarantee of currency. We never choose: the
        document fetched is whichever one the redirect named.
        """
        self._associate()
        other = 'https://documents.example.test/other-version.json'

        fetched = []

        def _dispatch(url, **kwargs):
            fetched.append(url)
            if url == RESOLVER_URI:
                return FakeResponse(
                    302,
                    headers={'Location': redirect_location(uri=other)},
                )
            return FakeResponse(200, envelope())

        with patch(RETRIEVE, side_effect=_dispatch):
            outcome = retrieve_identity_record(OS_ID)

        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.record.document_uri, other)
        self.assertEqual(fetched, [RESOLVER_URI, other])

    def test_integrity_comes_from_the_link_not_the_record(self):
        """
        The digest sits beside the link in the issuer's redirect, not inside
        the credential, which is where an earlier version of this service
        looked for it.
        """
        self._associate()

        with patch(RETRIEVE, side_effect=two_hop()):
            outcome = retrieve_identity_record(OS_ID)

        self.assertEqual(
            outcome.record.integrity,
            {'algorithm': 'digestMultibase', 'value': DIGEST},
        )

    def test_hash_spelling_is_accepted_too(self):
        """
        Both spellings appear mixed within one facility, so neither is the
        old one to migrate away from.
        """
        self._associate()
        q = json.dumps(
            {'payload': {'uri': DOCUMENT_URI, 'hash': 'sha256-abc'}}
        )
        resolver = FakeResponse(
            302, headers={'Location': '{}?q={}'.format(VIEWER, q)}
        )

        with patch(RETRIEVE, side_effect=two_hop(resolver=resolver)):
            outcome = retrieve_identity_record(OS_ID)

        self.assertEqual(
            outcome.record.integrity,
            {'algorithm': 'hash', 'value': 'sha256-abc'},
        )

    def test_encrypted_record_is_reported_not_rendered(self):
        """
        BRD 8 puts encrypted records out of scope, and at least one pilot
        facility is encrypted today, so this is a real state rather than a
        defensive branch.
        """
        self._associate()
        ciphertext = FakeResponse(
            200,
            {
                'cipherText': 'Z3U98...',
                'iv': 'abc',
                'tag': 'def',
                'type': 'EncryptedCredential',
            },
        )

        with patch(RETRIEVE, side_effect=two_hop(document=ciphertext)):
            outcome = retrieve_identity_record(OS_ID)

        self.assertFalse(outcome.ok)
        self.assertEqual(
            outcome.failure.reason, RetrievalFailureReason.ENCRYPTED
        )

    def test_resolver_serving_the_record_directly_still_works(self):
        """
        An issuer that answers the Resolver URI with the record itself is
        not what the pilot issuer does, but nothing forbids it and rejecting
        it would fail a correct implementation.
        """
        self._associate()
        direct = FakeResponse(200, envelope())

        with patch(RETRIEVE, return_value=direct):
            outcome = retrieve_identity_record(OS_ID)

        self.assertTrue(outcome.ok)
        self.assertIsNone(outcome.record.document_uri)
        self.assertEqual(
            outcome.record.content['credentialSubject']['registeredId'],
            'REC-00000001',
        )

    def test_unreadable_redirect_is_a_typed_failure(self):
        """A redirect we cannot read a document out of is not a crash."""
        self._associate()

        for location in (
            None,
            'https://verify.example.test/verify',
            'https://verify.example.test/verify?q=not-json',
            'https://verify.example.test/verify?q={}',
            'https://verify.example.test/verify?q={"payload":{}}',
        ):
            with self.subTest(location=location):
                resolver = FakeResponse(
                    302, headers={} if location is None
                    else {'Location': location}
                )
                with patch(RETRIEVE, side_effect=two_hop(resolver=resolver)):
                    outcome = retrieve_identity_record(OS_ID)

                self.assertFalse(outcome.ok)
                self.assertEqual(
                    outcome.failure.reason, RetrievalFailureReason.MALFORMED
                )

    def test_document_uri_from_the_redirect_is_checked_too(self):
        """
        The document address comes from the issuer's response rather than
        from anything we stored, so it gets the same safety check as the
        Resolver URI. Otherwise a redirect would be a way to aim this server
        at an internal address.
        """
        self._associate()
        resolver = FakeResponse(
            302,
            headers={
                'Location': redirect_location(
                    uri='https://169.254.169.254/latest/meta-data/'
                )
            },
        )

        calls = []

        def _dispatch(url, **kwargs):
            calls.append(url)
            return resolver

        with patch(RETRIEVE, side_effect=_dispatch):
            outcome = retrieve_identity_record(OS_ID)

        self.assertEqual(calls, [RESOLVER_URI])
        self.assertEqual(
            outcome.failure.reason, RetrievalFailureReason.UNSAFE_URI
        )

    def test_timeout_on_either_hop_is_a_typed_failure(self):
        """
        A slow issuer is an expected state of the world, so it returns a
        failure the page can render rather than propagating an exception.
        """
        self._associate()

        def _slow_document(url, **kwargs):
            if url == RESOLVER_URI:
                return FakeResponse(
                    302, headers={'Location': redirect_location()}
                )
            raise requests.Timeout()

        for label, effect in (
            ('resolver', requests.Timeout()),
            ('document', _slow_document),
        ):
            with self.subTest(hop=label):
                kwargs = (
                    {'side_effect': effect}
                    if callable(effect)
                    else {'side_effect': effect}
                )
                with patch(RETRIEVE, **kwargs):
                    outcome = retrieve_identity_record(OS_ID)

                self.assertFalse(outcome.ok)
                self.assertEqual(
                    outcome.failure.reason, RetrievalFailureReason.TIMEOUT
                )

    def test_connection_error_returns_a_typed_failure(self):
        self._associate()

        with patch(RETRIEVE, side_effect=requests.ConnectionError()):
            outcome = retrieve_identity_record(OS_ID)

        self.assertEqual(
            outcome.failure.reason, RetrievalFailureReason.UNREACHABLE
        )

    def test_upstream_error_on_either_hop(self):
        self._associate()

        with patch(RETRIEVE, side_effect=two_hop(
            resolver=FakeResponse(503)
        )):
            outcome = retrieve_identity_record(OS_ID)
        self.assertEqual(
            outcome.failure.reason, RetrievalFailureReason.UPSTREAM_ERROR
        )

        with patch(RETRIEVE, side_effect=two_hop(
            document=FakeResponse(404)
        )):
            outcome = retrieve_identity_record(OS_ID)
        self.assertEqual(
            outcome.failure.reason, RetrievalFailureReason.UPSTREAM_ERROR
        )

    def test_non_json_document_is_a_typed_failure(self):
        self._associate()

        with patch(RETRIEVE, side_effect=two_hop(
            document=FakeResponse(200, None)
        )):
            outcome = retrieve_identity_record(OS_ID)

        self.assertEqual(
            outcome.failure.reason, RetrievalFailureReason.MALFORMED
        )

    def test_nothing_is_persisted(self):
        """
        Retrieval leaves no copy of the record behind. Only the association
        remains, and it is unchanged.
        """
        self._associate()
        before = IdentityRecordAssociation.objects.count()

        with patch(RETRIEVE, side_effect=two_hop()):
            retrieve_identity_record(OS_ID)

        self.assertEqual(IdentityRecordAssociation.objects.count(), before)
        stored = IdentityRecordAssociation.objects.get(os_id=OS_ID)
        self.assertEqual(stored.resolver_uri, RESOLVER_URI)
        self.assertFalse(hasattr(stored, 'content'))

    def test_unregistered_os_id_is_a_typed_failure_not_a_fetch(self):
        """
        An OS ID with no live association must not cause an outbound request
        at all, since that is an ordinary state rather than an error.
        """
        with patch(RETRIEVE) as mocked:
            outcome = retrieve_identity_record(OS_ID)

        mocked.assert_not_called()
        self.assertEqual(
            outcome.failure.reason, RetrievalFailureReason.NOT_REGISTERED
        )

    def test_pending_association_is_not_retrieved(self):
        """
        An association with no live_from is not yet resolving, so it must
        not be served as though it were.
        """
        self._associate(live_from=None)

        with patch(RETRIEVE) as mocked:
            outcome = retrieve_identity_record(OS_ID)

        mocked.assert_not_called()
        self.assertEqual(
            outcome.failure.reason, RetrievalFailureReason.NOT_REGISTERED
        )

    def test_internal_resolver_uri_is_refused_without_fetching(self):
        self._associate(resolver_uri='https://127.0.0.1/records/1')

        with patch(RETRIEVE) as mocked:
            outcome = retrieve_identity_record(OS_ID)

        mocked.assert_not_called()
        self.assertEqual(
            outcome.failure.reason, RetrievalFailureReason.UNSAFE_URI
        )


class RetrievalSafetyTest(AssociationFixture, TestCase):
    """
    The cases review found: a redirect that escapes the address check, a
    body too large to read, JSON that is not a credential, and an
    encrypted envelope spelled a way the probe did not know.
    """

    def test_redirect_from_the_document_host_is_checked(self):
        """
        The address check has to apply to every hop. Checking only the
        first one lets an issuer reach a private address by redirecting
        after it has passed.
        """
        responses = {
            RESOLVER_URI: FakeResponse(
                302, headers={'Location': redirect_location()}
            ),
            DOCUMENT_URI: FakeResponse(
                302, headers={'Location': 'https://169.254.169.254/latest/'}
            ),
        }
        self._associate()

        with patch(RETRIEVE, side_effect=lambda url, **kw: responses[url]):
            outcome = retrieve_identity_record(OS_ID)

        self.assertFalse(outcome.ok)
        self.assertEqual(
            outcome.failure.reason, RetrievalFailureReason.UNSAFE_URI
        )

    def test_a_body_too_large_is_refused(self):
        """
        The body comes from a third party, so its size is not ours to
        trust. Declared length alone is enough to refuse it.
        """
        self._associate()
        oversized = FakeResponse(
            200, envelope(),
            headers={'Content-Length': str(50 * 1024 * 1024)},
        )

        with patch(RETRIEVE, side_effect=two_hop(document=oversized)):
            outcome = retrieve_identity_record(OS_ID)

        self.assertFalse(outcome.ok)
        self.assertEqual(
            outcome.failure.reason, RetrievalFailureReason.MALFORMED
        )

    def test_json_that_is_not_a_credential_is_refused(self):
        """
        An issuer answering 200 with an error object would otherwise have
        that object rendered as the record.
        """
        self._associate()
        not_a_credential = FakeResponse(
            200, {'error': 'record not found'}
        )

        with patch(RETRIEVE, side_effect=two_hop(document=not_a_credential)):
            outcome = retrieve_identity_record(OS_ID)

        self.assertFalse(outcome.ok)
        self.assertEqual(
            outcome.failure.reason, RetrievalFailureReason.MALFORMED
        )

    def test_jwe_json_serialization_is_reported_as_encrypted(self):
        """
        A JWE in JSON serialization spells the field `ciphertext`. Missing
        that spelling renders ciphertext as though it were the record.
        """
        self._associate()
        jwe = FakeResponse(200, {
            'protected': 'eyJhbGciOiJF',
            'recipients': [{'encrypted_key': 'x'}],
            'ciphertext': 'DwKiKLDFE',
        })

        with patch(RETRIEVE, side_effect=two_hop(document=jwe)):
            outcome = retrieve_identity_record(OS_ID)

        self.assertFalse(outcome.ok)
        self.assertEqual(
            outcome.failure.reason, RetrievalFailureReason.ENCRYPTED
        )


class UnwrapCredentialTest(TestCase):
    def test_decodes_the_jwt_inside_an_envelope(self):
        claims = unwrap_credential(envelope())

        self.assertEqual(claims['credentialSubject']['name'],
                         'Example Facility')

    def test_a_plain_credential_passes_through(self):
        plain = {'type': ['VerifiableCredential'], 'name': 'Plain'}

        self.assertEqual(unwrap_credential(plain), plain)

    def test_unreadable_envelopes_return_none(self):
        for document in (
            {'type': 'EnvelopedVerifiableCredential',
             'id': 'data:application/vc+jwt,notajwt'},
            {'type': 'EnvelopedVerifiableCredential',
             'id': 'data:application/vc+jwt,aaa.!!!not-base64!!!.ccc'},
            {'type': 'EnvelopedVerifiableCredential', 'id': 'data:'},
            None,
        ):
            with self.subTest(document=document):
                self.assertIsNone(unwrap_credential(document))


class ParseResolverRedirectTest(TestCase):
    def test_reads_the_document_and_digest(self):
        uri, integrity = parse_resolver_redirect(redirect_location())

        self.assertEqual(uri, DOCUMENT_URI)
        self.assertEqual(
            integrity, {'algorithm': 'digestMultibase', 'value': DIGEST}
        )

    def test_a_shape_it_does_not_recognize_returns_nothing(self):
        for location in (None, '', 'https://other.example.test/',
                         'https://other.example.test/?q=[]'):
            with self.subTest(location=location):
                self.assertEqual(
                    parse_resolver_redirect(location), (None, None)
                )


class EncryptionAndSafetyTest(TestCase):
    def test_detects_an_encrypted_envelope(self):
        self.assertTrue(is_encrypted({'cipherText': 'x', 'iv': 'y'}))
        self.assertFalse(is_encrypted(envelope()))
        self.assertFalse(is_encrypted(None))

    def test_rejects_internal_and_non_https_targets(self):
        for uri in (
            'https://127.0.0.1/r',
            'https://10.0.0.5/r',
            'https://192.168.1.1/r',
            'https://169.254.169.254/latest/meta-data/',
            'http://resolver.example.org/r',
            'ftp://resolver.example.org/r',
            'not a uri',
        ):
            with self.subTest(uri=uri):
                self.assertFalse(is_safe_resolver_uri(uri))

    def test_accepts_an_ordinary_https_host(self):
        self.assertTrue(is_safe_resolver_uri(RESOLVER_URI))


class FindIntegrityTest(TestCase):
    def test_returns_none_for_non_dict_input(self):
        self.assertIsNone(find_integrity(['hash']))
        self.assertIsNone(find_integrity(None))

    def test_top_level_wins_over_nested(self):
        payload = {'hash': 'outer', 'proof': {'digestMultibase': 'inner'}}

        self.assertEqual(
            find_integrity(payload), {'algorithm': 'hash', 'value': 'outer'}
        )
