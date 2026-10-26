from django.contrib.gis.geos import Point
from django.test import TestCase
from django.utils import timezone

from waffle.testutils import override_switch

from api.models.contributor.contributor import Contributor
from api.models.facility.facility import Facility
from api.models.facility.facility_index import FacilityIndex
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.identity_record_association import IdentityRecordAssociation
from api.models.source import Source
from api.models.user import User
from api.serializers.facility.facility_index_details_serializer \
    import FacilityIndexDetailsSerializer
from api.services.identity_record_retrieval import has_live_record

OS_ID = 'XX2000001AAAAA5'
RESOLVER_URI = 'https://resolver.test-issuer.example/records/REC-00000001'


class FlagFixture:
    """
    The facility page needs to know whether to offer a link to a registered
    record (OSDEV-3585, FR-12).

    A boolean rather than the record itself: reading the record means a
    live call to the issuer, which is right for the page dedicated to it
    and wrong for a profile loaded far more often that does not show it.
    """

    def setUp(self):
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


class FacilityIdentityRecordFlagTest(FlagFixture, TestCase):
    """
    The profile flag that decides whether to offer the identity record
    page (OSDEV-3585, FR-12).
    """

    def test_false_when_nothing_is_registered(self):
        """
        FR-14: no registered record is the ordinary case. The page shows no
        entry point and no empty section.
        """
        self.assertFalse(has_live_record(OS_ID))

    def test_true_once_a_record_is_registered(self):
        self._register()

        self.assertTrue(has_live_record(OS_ID))

    def test_a_pending_registration_does_not_count(self):
        """
        An association with no live_from is not resolving yet, so offering
        a link would lead somewhere with nothing on it.
        """
        self._register(live_from=None)

        self.assertFalse(has_live_record(OS_ID))

    def test_another_location_registration_does_not_leak(self):
        self._register(os_id='XX2000002AAAAA6')

        self.assertFalse(has_live_record(OS_ID))

    def test_the_check_makes_no_outbound_request(self):
        """
        The profile is loaded far more often than the record is read, so
        this must stay a database lookup. If it ever starts calling the
        issuer, every facility page view would wait on a third party.
        """
        self._register()

        with self.assertNumQueries(1):
            has_live_record(OS_ID)


class SerializedFlagTest(FlagFixture, TestCase):
    """
    What the public profile actually says. The tests above exercise
    has_live_record, which is ungated on purpose because the switch
    belongs on what is exposed rather than on what is known.
    """

    def _serialized_flag(self):
        index = FacilityIndex.objects.get(id=OS_ID)
        data = FacilityIndexDetailsSerializer(index).data
        return data['properties']['has_identity_record']

    @override_switch('enable_identity_resolver', active=True)
    def test_true_once_the_resolver_is_on(self):
        self._register()

        self.assertTrue(self._serialized_flag())

    def test_false_while_the_resolver_is_off(self):
        """
        The profile is public, so a true here would announce that a record
        exists for this location before the pilot is announced, and the
        page it offers would not answer anyway.
        """
        self._register()

        self.assertFalse(self._serialized_flag())
