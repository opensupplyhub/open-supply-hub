from types import SimpleNamespace

from django.contrib.auth.models import AnonymousUser, Group
from django.contrib.gis.geos import Point
from django.http import QueryDict
from django.test import (
    RequestFactory,
    SimpleTestCase,
    TestCase,
    override_settings,
)

from api.facilities_download_view_set import FacilitiesDownloadViewSet

from api.constants import FeatureGroups
from api.models import Contributor, User
from api.models.partner_field import PartnerField
from api.models.wage_indicator_country_data import WageIndicatorCountryData
from api.permissions import (
    can_get_union_linked_data,
    has_api_token,
    is_web_client_request,
    should_exclude_union_data,
)
from api.serializers.facility.facility_download_serializer import (
    FacilityDownloadSerializer,
)
from api.services.trade_union_exclusion_service import (
    TradeUnionExclusionService,
)
from api.trade_union import (
    strip_union_extended_fields,
    strip_union_sector_items,
    union_free_sector_values,
)

UNION_ID = 99
OTHER_ID = 2


def _ef(field_name, contributor_id, value):
    return {
        'field_name': field_name,
        'value': value,
        'contributor': {'id': contributor_id},
    }


class TradeUnionStripHelpersTest(SimpleTestCase):
    """Pure helpers that drop trade union-contributed fields."""

    def test_strips_union_extended_fields(self):
        fields = [
            _ef('number_of_workers', OTHER_ID, {'min': 50, 'max': 100}),
            _ef('number_of_workers', UNION_ID, {'min': 500, 'max': 1000}),
        ]
        result = strip_union_extended_fields(fields, {UNION_ID})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['contributor']['id'], OTHER_ID)

    def test_strips_union_primary_name_and_address(self):
        # Union-contributed name/address extended-field entries are stripped
        # too; the canonical identity columns are emitted separately and stay
        # intact (OSDEV-2786).
        fields = [
            _ef('name', UNION_ID, 'Union Name'),
            _ef('address', UNION_ID, 'Union Address'),
            _ef('parent_company', UNION_ID, {'name': 'Hidden'}),
            _ef('name', OTHER_ID, 'Public Name'),
        ]
        result = strip_union_extended_fields(fields, {UNION_ID})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['field_name'], 'name')
        self.assertEqual(result[0]['contributor']['id'], OTHER_ID)

    def test_extended_fields_no_op_without_union_ids(self):
        fields = [_ef('number_of_workers', UNION_ID, {'min': 1, 'max': 2})]
        self.assertIs(strip_union_extended_fields(fields, set()), fields)

    def test_strip_union_sector_items(self):
        items = [
            {'contributor': {'id': OTHER_ID}, 'sector': ['Apparel']},
            {'contributor': {'id': UNION_ID}, 'sector': ['Mining']},
        ]
        result = strip_union_sector_items(items, {UNION_ID})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['contributor']['id'], OTHER_ID)

    def test_union_free_sector_drops_union_only_value(self):
        facility = SimpleNamespace(
            sector=['Apparel', 'Mining'],
            item_sectors=[
                {'contributor': {'id': OTHER_ID}, 'sector': ['Apparel']},
                {'contributor': {'id': UNION_ID}, 'sector': ['Mining']},
            ],
            claim_sectors=[],
        )
        self.assertEqual(
            union_free_sector_values(facility, {UNION_ID}),
            ['Apparel'],
        )

    def test_union_free_sector_keeps_shared_value(self):
        facility = SimpleNamespace(
            sector=['Apparel', 'Mining'],
            item_sectors=[
                {'contributor': {'id': OTHER_ID},
                 'sector': ['Apparel', 'Mining']},
                {'contributor': {'id': UNION_ID}, 'sector': ['Mining']},
            ],
            claim_sectors=[],
        )
        self.assertEqual(
            union_free_sector_values(facility, {UNION_ID}),
            ['Apparel', 'Mining'],
        )

    def test_union_free_sector_no_op_without_union_ids(self):
        facility = SimpleNamespace(
            sector=['Apparel'], item_sectors=[], claim_sectors=[]
        )
        self.assertEqual(
            union_free_sector_values(facility, set()), ['Apparel']
        )


class TradeUnionDownloadSerializerTest(TestCase):
    """Field-level stripping in the full (non-embed) download serializer."""

    fixtures = ['facilities_index']

    def setUp(self):
        WageIndicatorCountryData.objects.all().delete()

    def _facility(self):
        return SimpleNamespace(
            id='MOCK_1',
            name='Mock Facility',
            address='1 Mock St',
            country_code='US',
            location=Point(0.0, 0.0),
            sector=['Apparel', 'Mining'],
            item_sectors=[
                {'contributor': {'id': OTHER_ID}, 'sector': ['Apparel']},
                {'contributor': {'id': UNION_ID}, 'sector': ['Mining']},
            ],
            claim_sectors=[],
            is_closed=False,
            created_from_info={'created_at': '2024-01-01T00:00:00+00:00'},
            approved_claim=None,
            contributors=[],
            extended_fields=[
                _ef('number_of_workers', OTHER_ID, {'min': 50, 'max': 100}),
                _ef('number_of_workers', UNION_ID, {'min': 500, 'max': 1000}),
            ],
        )

    def test_download_strips_union_extended_field(self):
        serializer = FacilityDownloadSerializer(
            exclude_contributor_ids={UNION_ID}
        )
        row = serializer.get_row(self._facility())
        # index 10 == number_of_workers column
        self.assertEqual(row[10], '50-100')

    def test_download_keeps_union_field_without_exclusion(self):
        serializer = FacilityDownloadSerializer()
        row = serializer.get_row(self._facility())
        self.assertEqual(row[10], '50-100|500-1000')

    def test_download_strips_union_only_sector(self):
        serializer = FacilityDownloadSerializer(
            exclude_contributor_ids={UNION_ID}
        )
        row = serializer.get_row(self._facility())
        # index 8 == sector column, title-cased
        self.assertEqual(row[8], 'Apparel')

    def test_download_keeps_sector_without_exclusion(self):
        serializer = FacilityDownloadSerializer()
        row = serializer.get_row(self._facility())
        self.assertEqual(row[8], 'Apparel|Mining')

    def test_download_system_partner_columns_unaffected(self):
        """MIT/wage system columns are derived from facility data, not
        extended_fields, so they are identical with and without stripping."""
        facility = self._facility()
        no_strip = FacilityDownloadSerializer().get_row(facility)
        stripped = FacilityDownloadSerializer(
            exclude_contributor_ids={UNION_ID}
        ).get_row(facility)
        # The trailing system partner-field columns (mit_living_wage.*,
        # wage_indicator.*) are unchanged.
        self.assertEqual(no_strip[-8:], stripped[-8:])

    def _facility_with_contributors(self):
        facility = self._facility()
        facility.contributors = [
            {
                'id': OTHER_ID,
                'name': 'Public Org',
                'should_display_associations': True,
                'contrib_type': 'Brand / Retailer',
            },
            {
                'id': UNION_ID,
                'name': 'A Union',
                'should_display_associations': True,
                'contrib_type': 'Union',
            },
        ]
        return facility

    def test_download_strips_union_from_contributor_list(self):
        row = FacilityDownloadSerializer(
            exclude_contributor_ids={UNION_ID}
        ).get_row(self._facility_with_contributors())
        # index 9 == "contributor (list)" column
        self.assertEqual(row[9], 'Public Org')

    def test_download_keeps_contributor_list_without_exclusion(self):
        row = FacilityDownloadSerializer().get_row(
            self._facility_with_contributors()
        )
        self.assertEqual(row[9], 'Public Org|A Union')

    def test_download_strips_union_contributor_partner_field(self):
        bsci_field = SimpleNamespace(
            name='bsci_audit',
            type=PartnerField.OBJECT,
            json_schema={
                'properties': {
                    'submission_date': {'type': 'string'},
                    'expiration_date': {'type': 'string'},
                }
            },
        )
        facility = self._facility()
        facility.extended_fields.append(
            _ef('bsci_audit', UNION_ID, {
                'raw_values': {
                    'submission_date': '2024-10-15',
                    'expiration_date': '2026-10-15',
                }
            })
        )

        stripped = FacilityDownloadSerializer(
            partner_fields=[bsci_field],
            exclude_contributor_ids={UNION_ID},
        ).get_row(facility)
        # Only partner columns are the two bsci_audit cells (system fields are
        # absent when partner_fields is overridden).
        self.assertEqual(stripped[-2:], ['', ''])

        kept = FacilityDownloadSerializer(
            partner_fields=[bsci_field],
        ).get_row(facility)
        self.assertEqual(kept[-2:], ['2024-10-15', '2026-10-15'])


class TradeUnionPermissionTest(TestCase):
    """Decision of when union-linked fields must be stripped."""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(email='union-perm@example.com')
        Contributor.objects.create(
            admin=self.user,
            name='A Union',
            contrib_type=Contributor.UNION_CONTRIB_TYPE,
        )

    def test_union_ids_manager(self):
        ids = Contributor.objects.union_ids()
        self.assertTrue(
            Contributor.objects.filter(
                contrib_type=Contributor.UNION_CONTRIB_TYPE
            ).first().id in ids
        )

    def test_has_api_token(self):
        request = self.factory.get('/api/facilities/',
                                   HTTP_AUTHORIZATION='Token abc123')
        self.assertTrue(has_api_token(request))

        request = self.factory.get('/api/facilities/')
        self.assertFalse(has_api_token(request))

    @override_settings(DEBUG=False, OAR_CLIENT_KEY='secret-key')
    def test_token_request_excludes_union(self):
        request = self.factory.get('/api/facilities/',
                                   HTTP_AUTHORIZATION='Token abc123')
        self.assertTrue(should_exclude_union_data(request))

    @override_settings(DEBUG=False, OAR_CLIENT_KEY='secret-key')
    def test_web_client_request_keeps_union(self):
        request = self.factory.get(
            '/api/facilities/',
            HTTP_X_OAR_CLIENT_KEY='secret-key',
            HTTP_REFERER='http://localhost/facilities',
        )
        self.assertTrue(is_web_client_request(request))
        self.assertFalse(should_exclude_union_data(request))

    @override_settings(DEBUG=False, OAR_CLIENT_KEY='secret-key')
    def test_non_web_client_without_token_excludes_union(self):
        request = self.factory.get('/api/facilities/')
        self.assertFalse(is_web_client_request(request))
        self.assertTrue(should_exclude_union_data(request))

    @override_settings(DEBUG=True)
    def test_local_env_keeps_union_for_browser(self):
        request = self.factory.get('/api/facilities/')
        self.assertTrue(is_web_client_request(request))
        self.assertFalse(should_exclude_union_data(request))

    @override_settings(DEBUG=False, OAR_CLIENT_KEY='secret-key')
    def test_exempt_group_member_keeps_union(self):
        group = Group.objects.get(
            name=FeatureGroups.CAN_GET_UNION_LINKED_DATA
        )
        self.user.groups.add(group)
        request = self.factory.get('/api/facilities/',
                                   HTTP_AUTHORIZATION='Token abc123')
        request.user = self.user
        self.assertTrue(can_get_union_linked_data(request))
        self.assertFalse(should_exclude_union_data(request))

    @override_settings(DEBUG=False, OAR_CLIENT_KEY='secret-key')
    def test_service_for_list_excludes_token_request(self):
        request = self.factory.get('/api/facilities/',
                                   HTTP_AUTHORIZATION='Token abc123')
        self.assertTrue(TradeUnionExclusionService.for_list(request))

    @override_settings(DEBUG=False, OAR_CLIENT_KEY='secret-key')
    def test_service_for_list_keeps_web_client(self):
        request = self.factory.get(
            '/api/facilities/',
            HTTP_X_OAR_CLIENT_KEY='secret-key',
            HTTP_REFERER='http://localhost/facilities',
        )
        self.assertEqual(TradeUnionExclusionService.for_list(request), set())


class TradeUnionDownloadViewGateTest(TestCase):
    """Downloads strip union fields for every caller except exempt users."""

    def setUp(self):
        self.user = User.objects.create(email='dl-union@example.com')
        self.union = Contributor.objects.create(
            admin=self.user,
            name='A Union',
            contrib_type=Contributor.UNION_CONTRIB_TYPE,
        )

    def _exclude_ids_for(self, user):
        view = FacilitiesDownloadViewSet()
        view.request = SimpleNamespace(query_params=QueryDict(''), user=user)
        serializer = view.get_serializer([])
        return serializer.child.exclude_contributor_ids

    def test_browser_download_strips_union(self):
        # Anonymous/browser download (no token) still strips union fields.
        exclude_ids = self._exclude_ids_for(AnonymousUser())
        self.assertIn(self.union.id, exclude_ids)

    def test_non_exempt_user_download_strips_union(self):
        exclude_ids = self._exclude_ids_for(self.user)
        self.assertIn(self.union.id, exclude_ids)

    def test_exempt_user_download_keeps_union(self):
        group = Group.objects.get(
            name=FeatureGroups.CAN_GET_UNION_LINKED_DATA
        )
        self.user.groups.add(group)
        exclude_ids = self._exclude_ids_for(self.user)
        self.assertEqual(exclude_ids, set())
