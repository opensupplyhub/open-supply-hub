from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from api.models import IdentityRecordAssociation

OS_ID = 'TH2026278GC5XXJ'
RESOLVER_URI = (
    'https://idr.credentials.responsiblebusiness.org/rba/G-FA-10017485'
)
OTHER_RESOLVER_URI = (
    'https://idr.credentials.responsiblebusiness.org/rba/G-FA-10017486'
)


class IdentityRecordAssociationTest(TestCase):
    """
    Tests for the OS ID to Resolver URI association (OSDEV-3579).

    The association is all Open Supply Hub stores: no credential body is
    copied, cached or re-published (NFR-04, scope doc 2.4).
    """

    def _make(self, **overrides):
        fields = {
            'os_id': OS_ID,
            'resolver_uri': RESOLVER_URI,
            'record_type': 'untp:DigitalFacilityRecord',
            'issuer': 'did:web:credentials.responsiblebusiness.org',
            'registrant_reference': 'G-FA-10017485',
        }
        fields.update(overrides)
        return IdentityRecordAssociation(**fields)

    def test_persists_and_is_retrievable_by_os_id(self):
        """AC#1: a valid association persists and is found by its OS ID."""
        association = self._make(live_from=timezone.now())
        association.full_clean()
        association.save()

        found = IdentityRecordAssociation.objects.get(os_id=OS_ID)

        self.assertEqual(found.resolver_uri, RESOLVER_URI)
        self.assertEqual(found.record_type, 'untp:DigitalFacilityRecord')
        self.assertEqual(
            found.issuer, 'did:web:credentials.responsiblebusiness.org'
        )
        self.assertEqual(found.registrant_reference, 'G-FA-10017485')
        self.assertIsNotNone(found.uuid)

    def test_same_os_id_and_resolver_twice_is_rejected(self):
        """AC#2: the pair is unique, so an exact duplicate cannot be stored."""
        self._make().save()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self._make().save()

    def test_conflicting_resolver_for_same_os_id_is_detectable(self):
        """
        AC#2: a second association for the same OS ID pointing at a
        *different* resolver is storable, and must be detectable so the
        registration endpoint can return the 409 described in 3.2.

        It is deliberately not a database constraint. Section 5 leaves
        issuers other than RBA open, so forbidding a second issuer outright
        would foreclose a decision that is explicitly out of scope.
        """
        self._make(live_from=timezone.now()).save()
        self._make(
            resolver_uri=OTHER_RESOLVER_URI, live_from=timezone.now()
        ).save()

        conflicting = IdentityRecordAssociation.objects.filter(
            os_id=OS_ID, live_from__isnull=False
        ).exclude(resolver_uri=RESOLVER_URI)

        self.assertEqual(conflicting.count(), 1)
        self.assertEqual(conflicting.first().resolver_uri, OTHER_RESOLVER_URI)

    def test_non_https_resolver_uri_is_rejected(self):
        """AC#3: the Resolver URI must be an absolute HTTPS URI."""
        for bad in (
            'http://idr.credentials.responsiblebusiness.org/rba/G-FA-1',
            '/rba/G-FA-10017485',
            'idr.credentials.responsiblebusiness.org/rba/G-FA-10017485',
            'ftp://example.org/record',
            'not a uri at all',
        ):
            with self.subTest(resolver_uri=bad):
                with self.assertRaises(ValidationError):
                    self._make(resolver_uri=bad).full_clean()

    def test_https_resolver_uri_is_accepted(self):
        """The validator must not reject a well-formed Resolver URI."""
        self._make(resolver_uri=RESOLVER_URI).full_clean()

    def test_is_live_reflects_live_from(self):
        """
        Pilot-set registrations are live on creation; the pending path that
        leaves live_from null is the general case and is out of scope for
        November, but the model supports it so it needs no later migration.
        """
        pending = self._make()
        self.assertFalse(pending.is_live)

        live = self._make(live_from=timezone.now())
        self.assertTrue(live.is_live)

    def test_history_is_recorded(self):
        """Changes are tracked, so a bad batch can be unwound."""
        association = self._make()
        association.save()
        association.resolver_uri = OTHER_RESOLVER_URI
        association.save()

        self.assertEqual(association.history.count(), 2)
        self.assertEqual(
            association.history.earliest().resolver_uri, RESOLVER_URI
        )
