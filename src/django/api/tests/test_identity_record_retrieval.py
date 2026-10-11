from unittest.mock import patch

import requests
from django.test import TestCase
from django.utils import timezone

from api.models import IdentityRecordAssociation
from api.services.identity_record_retrieval import (
    RetrievalFailureReason,
    find_integrity,
    is_safe_resolver_uri,
    retrieve_identity_record,
)

OS_ID = 'XX2000001AAAAA5'
RESOLVER_URI = 'https://resolver.example.org/records/FAC-00000001'

RETRIEVE = 'api.services.identity_record_retrieval.requests.get'


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=None):
        self.status_code = status_code
        self._payload = payload
        self._text = text

    def json(self):
        if self._payload is None:
            raise ValueError('not json')
        return self._payload


class IdentityRecordRetrievalTest(TestCase):
    """
    Tests for retrieving a registered record (OSDEV-3583).

    The issuer is always mocked. These assert our handling of what comes
    back, not the issuer's behaviour, and a test that reached a real resolver
    would fail for reasons that are not about this code.
    """

    def _associate(self, **overrides):
        fields = {
            'os_id': OS_ID,
            'resolver_uri': RESOLVER_URI,
            'record_type': 'untp:DigitalFacilityRecord',
            'issuer': 'did:web:issuer.example.org',
            'registrant_reference': 'FAC-00000001',
            'live_from': timezone.now(),
        }
        fields.update(overrides)
        return IdentityRecordAssociation.objects.create(**fields)

    def test_retrieves_the_current_record(self):
        """AC#1: a responding issuer yields a record in a normalized shape."""
        self._associate()
        payload = {'type': 'DigitalFacilityRecord', 'hash': 'abc123'}

        with patch(RETRIEVE, return_value=FakeResponse(payload=payload)):
            outcome = retrieve_identity_record(OS_ID)

        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.record.os_id, OS_ID)
        self.assertEqual(outcome.record.resolver_uri, RESOLVER_URI)
        self.assertEqual(outcome.record.content, payload)
        self.assertIsNotNone(outcome.record.retrieved_at)

    def test_nothing_is_persisted(self):
        """
        NFR-04: retrieval must leave no copy of the record behind. The
        association count is unchanged and no content reaches the database.
        """
        self._associate()
        before = IdentityRecordAssociation.objects.count()

        with patch(RETRIEVE, return_value=FakeResponse(payload={'a': 1})):
            retrieve_identity_record(OS_ID)

        self.assertEqual(IdentityRecordAssociation.objects.count(), before)
        stored = IdentityRecordAssociation.objects.get(os_id=OS_ID)
        self.assertFalse(hasattr(stored, 'content'))

    def test_both_integrity_key_spellings_parse(self):
        """
        AC#2: records carrying digestMultibase and records carrying hash both
        parse. The two appear mixed within one facility, so neither can be
        treated as the old spelling to be migrated away.
        """
        self._associate()

        cases = (
            ({'digestMultibase': 'zQm123'}, 'digestMultibase', 'zQm123'),
            ({'hash': 'sha256-abc'}, 'hash', 'sha256-abc'),
            (
                {'credentialSubject': {'hash': 'nested-abc'}},
                'hash',
                'nested-abc',
            ),
        )

        for payload, algorithm, value in cases:
            with self.subTest(payload=payload):
                with patch(
                    RETRIEVE, return_value=FakeResponse(payload=payload)
                ):
                    outcome = retrieve_identity_record(OS_ID)

                self.assertTrue(outcome.ok)
                self.assertEqual(
                    outcome.record.integrity,
                    {'algorithm': algorithm, 'value': value},
                )

    def test_record_without_integrity_still_parses(self):
        """A missing digest is not a failure. It is a record we can show."""
        self._associate()

        with patch(RETRIEVE, return_value=FakeResponse(payload={'a': 1})):
            outcome = retrieve_identity_record(OS_ID)

        self.assertTrue(outcome.ok)
        self.assertIsNone(outcome.record.integrity)

    def test_timeout_returns_a_typed_failure(self):
        """
        AC#3: a slow issuer is an expected state of the world, so it returns
        a failure the page can render rather than propagating an exception.
        """
        self._associate()

        with patch(RETRIEVE, side_effect=requests.Timeout()):
            outcome = retrieve_identity_record(OS_ID)

        self.assertFalse(outcome.ok)
        self.assertEqual(
            outcome.failure.reason, RetrievalFailureReason.TIMEOUT
        )

    def test_connection_error_returns_a_typed_failure(self):
        self._associate()

        with patch(RETRIEVE, side_effect=requests.ConnectionError()):
            outcome = retrieve_identity_record(OS_ID)

        self.assertFalse(outcome.ok)
        self.assertEqual(
            outcome.failure.reason, RetrievalFailureReason.UNREACHABLE
        )

    def test_non_200_returns_a_typed_failure(self):
        self._associate()

        with patch(RETRIEVE, return_value=FakeResponse(status_code=503)):
            outcome = retrieve_identity_record(OS_ID)

        self.assertFalse(outcome.ok)
        self.assertEqual(
            outcome.failure.reason, RetrievalFailureReason.UPSTREAM_ERROR
        )

    def test_non_json_returns_a_typed_failure(self):
        self._associate()

        with patch(RETRIEVE, return_value=FakeResponse(payload=None)):
            outcome = retrieve_identity_record(OS_ID)

        self.assertFalse(outcome.ok)
        self.assertEqual(
            outcome.failure.reason, RetrievalFailureReason.MALFORMED
        )

    def test_unregistered_os_id_is_a_typed_failure_not_a_fetch(self):
        """
        An OS ID with no live association must not cause an outbound request
        at all. FR-14 makes this an ordinary state rather than an error.
        """
        with patch(RETRIEVE) as mocked:
            outcome = retrieve_identity_record(OS_ID)

        mocked.assert_not_called()
        self.assertFalse(outcome.ok)
        self.assertEqual(
            outcome.failure.reason, RetrievalFailureReason.NOT_REGISTERED
        )

    def test_pending_association_is_not_retrieved(self):
        """
        An association with no live_from is not yet resolving, so it must not
        be served as though it were.
        """
        self._associate(live_from=None)

        with patch(RETRIEVE) as mocked:
            outcome = retrieve_identity_record(OS_ID)

        mocked.assert_not_called()
        self.assertEqual(
            outcome.failure.reason, RetrievalFailureReason.NOT_REGISTERED
        )

    def test_internal_address_is_refused_without_fetching(self):
        """
        The Resolver URI is supplied from outside and fetched from inside, so
        an obviously internal target is refused before any request is made.
        See the limits documented on is_safe_resolver_uri.
        """
        self._associate(resolver_uri='https://127.0.0.1/records/1')

        with patch(RETRIEVE) as mocked:
            outcome = retrieve_identity_record(OS_ID)

        mocked.assert_not_called()
        self.assertEqual(
            outcome.failure.reason, RetrievalFailureReason.UNSAFE_URI
        )


class ResolverUriSafetyTest(TestCase):
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
        """
        A digest on the record itself describes the record. One nested inside
        some other object may well describe that object instead, so the outer
        value is preferred rather than whichever is found first.
        """
        payload = {'hash': 'outer', 'proof': {'digestMultibase': 'inner'}}

        self.assertEqual(
            find_integrity(payload), {'algorithm': 'hash', 'value': 'outer'}
        )
