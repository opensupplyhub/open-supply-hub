import json

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.cache import caches
from rest_framework import status
from rest_framework.test import APITestCase

from waffle.testutils import override_switch

from api.models.contributor.contributor import Contributor
from api.models.facility.facility import Facility
from api.models.facility.facility_alias import FacilityAlias
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.identity_record_association import IdentityRecordAssociation
from api.models.source import Source
from api.models.user import User

RESOLVER_URI = (
    'https://resolver.example.test/records/REC-00000001'
)
OTHER_RESOLVER_URI = (
    'https://resolver.example.test/records/REC-00000002'
)


class RegistrationFixture:
    """Shared fixtures for the two classes below."""

    def setUp(self):
        # Shared with other API tests: the throttling cache is Redis and
        # survives runs.
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
            'issuer': 'did:web:issuer.example.org',
            'registrant_reference': 'REC-00000001',
        }
        self.client.force_login(self.user)

    def _post(self, body=None, url=None):
        return self.client.post(
            url or self.url,
            json.dumps(self.body if body is None else body),
            content_type='application/json',
        )


# The switch gates access, not behavior. These assert what registration
# does once it is on; the off case is RegistrationSwitchOffTest below.
@override_switch('enable_identity_record_registration', active=True)
class TestIdentityRecordRegistration(RegistrationFixture, APITestCase):
    """
    The registration endpoint from OSDEV-3580.

    The literal paths are asserted rather than reversed, because the paths
    are the contract and cannot absorb a silent rename.
    """

    def test_registers_and_returns_live_immediately(self):
        """
        The pilot path returns 202 APPROVED with live_from set and no
        verification_url, because the association is Open Supply Hub's own
        construction and there is nothing for a member to confirm.
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
        """A different live resolver for the same OS ID is a 409."""
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
        """No credentials, no registration."""
        self.client.logout()

        response = self._post()

        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )
        self.assertFalse(IdentityRecordAssociation.objects.exists())

    def test_an_exact_repeat_is_idempotent(self):
        """
        Registering the same pair twice returns the existing
        registration rather than an error, because retry safety is the
        point. If a write commits but the response is lost, a conflict
        on the retry would be indistinguishable from someone else
        registering a different resolver.
        """
        first = self._post()
        self.assertEqual(first.status_code, status.HTTP_202_ACCEPTED)

        repeat = self._post()

        self.assertEqual(repeat.status_code, status.HTTP_200_OK)
        self.assertEqual(
            repeat.data['moderation_id'], first.data['moderation_id']
        )
        self.assertEqual(
            IdentityRecordAssociation.objects.filter(
                os_id=self.os_id
            ).count(),
            1,
        )

    def test_a_repeat_does_not_move_the_live_from_time(self):
        """
        The registration is unchanged, not refreshed. Moving live_from
        would make a retry look like a newer registration than it is.
        """
        first = self._post()
        original = IdentityRecordAssociation.objects.get(
            os_id=self.os_id
        ).live_from

        self._post()

        self.assertEqual(
            IdentityRecordAssociation.objects.get(
                os_id=self.os_id
            ).live_from,
            original,
        )
        self.assertEqual(first.data['live_from'], original)

    def test_same_resolver_with_changed_details_is_a_conflict(self):
        """
        Only an identical resubmission is a safe retry. Differing details
        are an attempted update, and answering 200 would report a change
        that did not happen.
        """
        self._post()

        body = dict(self.body, issuer='did:web:second.example.test')
        response = self._post(body)

        self.assertEqual(
            response.status_code, status.HTTP_409_CONFLICT
        )
        association = IdentityRecordAssociation.objects.get(
            os_id=self.os_id
        )
        self.assertEqual(association.issuer, self.body['issuer'])

    def test_origin_source_records_the_instance(self):
        """The field exists to tell OS Hub rows from private-instance
        rows, so it must not be left null."""
        self._post()

        association = IdentityRecordAssociation.objects.get(
            os_id=self.os_id
        )
        self.assertEqual(
            association.origin_source, settings.INSTANCE_SOURCE
        )

    def test_a_different_resolver_is_still_a_conflict(self):
        """
        Idempotency covers a repeated instruction, not a contradictory one.
        A second resolver for the same identifier is a real disagreement.
        """
        self._post()

        response = self._post(
            dict(self.body, resolver_uri=OTHER_RESOLVER_URI)
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_a_pending_association_does_not_block_registration(self):
        """
        The conflict check asks for a live association, which is what its
        409 says. Nothing writes a pending row today, so this builds one
        directly to pin that the live_from filter is what excludes it.
        """
        IdentityRecordAssociation.objects.create(
            os_id=self.os_id,
            resolver_uri=OTHER_RESOLVER_URI,
            record_type=self.body['record_type'],
            issuer=self.body['issuer'],
            live_from=None,
        )

        response = self._post()

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(
            IdentityRecordAssociation.objects
            .filter(os_id=self.os_id, resolver_uri=RESOLVER_URI)
            .exists()
        )

    def test_status_reports_a_pending_association(self):
        """
        `moderation_status` is derived from live_from rather than
        hardcoded. Nothing writes a pending row today, so this builds one
        directly.
        """
        association = IdentityRecordAssociation.objects.create(
            os_id=self.os_id,
            resolver_uri=RESOLVER_URI,
            record_type=self.body['record_type'],
            issuer=self.body['issuer'],
            live_from=None,
        )

        response = self.client.get(f'{self.url}{association.uuid}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['moderation_status'], 'PENDING')
        self.assertIsNone(response.data['live_from'])

    def test_malformed_os_id_is_rejected(self):
        """A bad checksum is a 400, and never reaches the database."""
        url = '/api/v1/production-locations/XX0000000BADID1/identity-records/'

        response = self._post(url=url)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_unknown_os_id_is_not_found(self):
        """
        A well-formed identifier this instance does not hold is a 404. A
        422 for "well formed but not resolvable here" is not used, since
        this instance cannot tell a private-instance identifier apart by
        design.
        """
        # A real minted identifier with a valid checksum, deliberately not
        # created in this test database.
        url = (
            '/api/v1/production-locations/XX2000002AAAAA6/identity-records/'
        )

        response = self._post(url=url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_superseded_os_id_is_accepted(self):
        """
        A merged-away identifier still registers. It keeps resolving to the
        surviving location through FacilityAlias, so refusing it here would
        break the link the reverse direction depends on.
        """
        alias_os_id = 'XX2000001AAAAA5'
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
        """The registered value must be an absolute HTTPS URI."""
        body = dict(self.body, resolver_uri='http://example.org/record')

        response = self._post(body)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_credential_url_is_rejected(self):
        """
        Registering a Credential URL would silently break the
        always-current guarantee, so the obvious shape of that mistake
        is refused.
        """
        body = dict(
            self.body,
            resolver_uri=(
                'https://documents.example.test/'
                '00000000-0000-4000-8000-000000000001.json'
            ),
        )

        response = self._post(body)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_unrecognized_record_type_is_rejected(self):
        """
        The resolver republishes record_type to third parties, so an
        unrecognized value would become a claim we make about another
        organization's record. It is refused at the boundary instead.
        """
        body = dict(self.body, record_type='untp:DigitalFacilityRecrod')

        response = self._post(body)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )
        self.assertFalse(
            IdentityRecordAssociation.objects.filter(
                os_id=self.os_id
            ).exists()
        )

    def test_the_rejection_names_what_is_accepted(self):
        """
        An allowlist fails closed, so the error has to tell the caller how
        to succeed rather than only that they failed.
        """
        body = dict(self.body, record_type='something:Else')

        response = self._post(body)

        self.assertIn(
            'untp:DigitalFacilityRecord', json.dumps(response.data)
        )

    def test_the_accepted_type_still_registers(self):
        """The allowlist must not reject the type the pilot uses."""
        response = self._post()

        self.assertEqual(
            response.status_code, status.HTTP_202_ACCEPTED
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
        """The current state, and once live, when it resolves."""
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
            '00000000-0000-4000-8000-000000000002',
            'not-a-uuid',
        ):
            with self.subTest(moderation_id=handle):
                response = self.client.get(f'{self.url}{handle}/')
                self.assertEqual(
                    response.status_code, status.HTTP_404_NOT_FOUND
                )


class RegistrationSwitchOffTest(RegistrationFixture, APITestCase):
    """Registration is closed until someone opens it."""

    def test_registering_is_not_found(self):
        """
        A 404 rather than a 403, so the route is indistinguishable from one
        that does not exist. A 403 would confirm the endpoint is there to
        anyone who probed it.
        """
        response = self._post()

        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )

    def test_registering_writes_nothing(self):
        self._post()

        self.assertFalse(
            IdentityRecordAssociation.objects.filter(
                os_id=self.os_id
            ).exists()
        )

    def test_anonymous_probe_cannot_tell_the_route_exists(self):
        """
        An anonymous caller gets the same 404 the switch gives everyone,
        not the 401 that would confirm the route is there. The parent
        class logs in, so only this test covers the unauthenticated path.
        """
        self.client.logout()

        response = self._post()
        missing = self.client.post(
            f'/api/v1/production-locations/{self.os_id}/no-such-route/',
            json.dumps(self.body),
            content_type='application/json',
        )

        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )
        self.assertEqual(response.status_code, missing.status_code)

    def test_reading_a_registration_is_not_found(self):
        response = self.client.get(
            f'{self.url}00000000-0000-4000-8000-000000000002/'
        )

        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )
