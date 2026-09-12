from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.contrib.gis.geos import Point
from django.core.cache import caches
from django.http import HttpResponse
from django.test import RequestFactory, TestCase, override_settings

from api.constants import MASKED_CONTRIBUTOR_LABEL
from api.models.contributor.contributor import Contributor
from api.models.facility.facility_index import FacilityIndex
from api.models.user import User
from api.views.facility.facilities_view_set import (
    FacilitiesViewSet,
    cache_page_by_auth_tier,
)
from api.serializers.facility.facility_download_serializer import (
    FacilityDownloadSerializer,
)
from api.serializers.facility.facility_index_details_serializer import (
    FacilityIndexDetailsSerializer,
)
from api.serializers.facility.facility_index_serializer import (
    FacilityIndexSerializer,
)
from api.serializers.facility.utils import (
    get_contributor_id_from_facilityindex,
    get_contributor_name_from_facilityindex,
    is_contribution_masked,
)
from api.serializers.utils import get_contributor_id, get_contributor_name
from api.services.contributor_masking_policy import ContributorMaskingPolicy
from api.services.masked_contributors import MaskedContributors


class MaskedContributorsTest(TestCase):
    """`MaskedContributors` decides masking by id or admin id."""

    def test_should_mask_by_contributor_id(self):
        masked = MaskedContributors(contributor_ids={1})
        self.assertTrue(masked.should_mask({'id': 1}))
        self.assertFalse(masked.should_mask({'id': 2}))

    def test_should_mask_by_admin_id_when_contributor_id_missing(self):
        # facility_locations / facility_list_items only carry `admin_id`.
        masked = MaskedContributors(admin_ids={9})
        self.assertTrue(masked.should_mask({'id': None, 'admin_id': 9}))
        self.assertTrue(masked.should_mask({'id': 5, 'admin_id': 9}))
        self.assertFalse(masked.should_mask({'id': 5, 'admin_id': 8}))

    def test_empty_never_masks(self):
        masked = MaskedContributors()
        self.assertFalse(masked.should_mask({'id': 1, 'admin_id': 1}))

    def test_does_not_mask_empty_contributor(self):
        masked = MaskedContributors(contributor_ids={1})
        self.assertFalse(masked.should_mask(None))
        self.assertFalse(masked.should_mask({}))

    def test_should_mask_name_for_created_from(self):
        # created_from_info carries only the contributor name.
        masked = MaskedContributors(names={'Union X'})
        self.assertTrue(masked.should_mask_name('Union X'))
        self.assertFalse(masked.should_mask_name('Brand Y'))
        self.assertFalse(masked.should_mask_name(None))


# The masked set is cached in ``view_cache``, which is a DummyCache in the
# test settings. Override it with a real local cache so the caching behaviour
# can be exercised.
@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'view_cache': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'masking-test',
    },
})
class ContributorMaskingPolicyServiceTest(TestCase):
    """Resolving and caching the contributors to hide in paid products."""

    def setUp(self):
        caches['view_cache'].clear()

    def tearDown(self):
        caches['view_cache'].clear()

    @staticmethod
    def _make_contributor(contrib_type, anonymise=True, email='c@example.com'):
        # Set the flag at creation time: a brand-new contributor does not
        # invalidate the cache on save, so warm-cache assertions stay
        # deterministic.
        user = User.objects.create(email=email)
        contributor = Contributor.objects.create(
            admin=user,
            name='Contributor {}'.format(contrib_type),
            contrib_type=contrib_type,
            anonymise_in_paid_products=anonymise,
        )
        return contributor, user

    def test_contributor_with_flag_is_masked(self):
        contributor, user = self._make_contributor(
            Contributor.UNION_CONTRIB_TYPE
        )
        masked = ContributorMaskingPolicy.flagged_contributors()
        self.assertIn(contributor.id, masked.contributor_ids)
        self.assertIn(user.id, masked.admin_ids)
        self.assertIn(contributor.name, masked.names)

    def test_contributor_without_flag_is_not_masked(self):
        contributor, _ = self._make_contributor(
            Contributor.UNION_CONTRIB_TYPE, anonymise=False
        )
        masked = ContributorMaskingPolicy.flagged_contributors()
        self.assertNotIn(contributor.id, masked.contributor_ids)

    def test_non_union_with_flag_is_masked(self):
        # The flag is the sole control now - it is not limited to unions.
        contributor, _ = self._make_contributor('Brand / Retailer')
        masked = ContributorMaskingPolicy.flagged_contributors()
        self.assertIn(contributor.id, masked.contributor_ids)

    def test_for_facilities_api_is_empty_without_token(self):
        self._make_contributor(Contributor.UNION_CONTRIB_TYPE)
        without_auth = ContributorMaskingPolicy.for_facilities_api(
            SimpleNamespace(auth=None)
        )
        self.assertFalse(without_auth.contributor_ids)
        no_request = ContributorMaskingPolicy.for_facilities_api(None)
        self.assertFalse(no_request.contributor_ids)

    def test_for_facilities_api_masks_for_token_user(self):
        contributor, _ = self._make_contributor(
            Contributor.UNION_CONTRIB_TYPE
        )
        masked = ContributorMaskingPolicy.for_facilities_api(
            SimpleNamespace(auth='a-token')
        )
        self.assertIn(contributor.id, masked.contributor_ids)

    def test_masked_contributors_are_cached(self):
        first, _ = self._make_contributor(Contributor.UNION_CONTRIB_TYPE)
        warm = ContributorMaskingPolicy.flagged_contributors()
        self.assertIn(first.id, warm.contributor_ids)

        # A non-masked contributor created after cache warm must not appear in
        # the cached set (no cache invalidation triggered for flag=False).
        user2 = User.objects.create(email='c2@example.com')
        non_masked = Contributor.objects.create(
            admin=user2,
            name='Brand X',
            contrib_type='Brand / Retailer',
            anonymise_in_paid_products=False,
        )
        still_cached = ContributorMaskingPolicy.flagged_contributors()
        self.assertIn(first.id, still_cached.contributor_ids)
        self.assertNotIn(non_masked.id, still_cached.contributor_ids)

    def test_toggling_flag_invalidates_cache(self):
        contributor, _ = self._make_contributor(
            Contributor.UNION_CONTRIB_TYPE
        )
        warm = ContributorMaskingPolicy.flagged_contributors()
        self.assertIn(contributor.id, warm.contributor_ids)

        # Disabling the flag must drop the cached set on save so the next
        # paid request stops masking the contributor without waiting for TTL.
        contributor.anonymise_in_paid_products = False
        contributor.save()

        refreshed = ContributorMaskingPolicy.flagged_contributors()
        self.assertNotIn(contributor.id, refreshed.contributor_ids)

    def test_insert_with_flag_on_invalidates_cache(self):
        # Warm the cache with no masked contributors.
        empty = ContributorMaskingPolicy.flagged_contributors()
        self.assertFalse(empty.contributor_ids)

        # Creating a new contributor with the flag already on must invalidate
        # the cache so the next request sees them masked immediately.
        user = User.objects.create(email='new@example.com')
        new_contributor = Contributor.objects.create(
            admin=user,
            name='New Masked Co',
            contrib_type='Brand / Retailer',
            anonymise_in_paid_products=True,
        )

        refreshed = ContributorMaskingPolicy.flagged_contributors()
        self.assertIn(new_contributor.id, refreshed.contributor_ids)

    def test_name_change_on_anonymised_contributor_invalidates_cache(self):
        contributor, _ = self._make_contributor(
            Contributor.UNION_CONTRIB_TYPE
        )
        original_name = contributor.name
        warm = ContributorMaskingPolicy.flagged_contributors()
        self.assertIn(original_name, warm.names)

        # Renaming an anonymised contributor must refresh the cached names set
        # so the new name is masked and the old one is dropped.
        contributor.name = 'Renamed Masked Co'
        contributor.save()

        refreshed = ContributorMaskingPolicy.flagged_contributors()
        self.assertIn('Renamed Masked Co', refreshed.names)
        self.assertNotIn(original_name, refreshed.names)


class ContributorHelperMaskingTest(TestCase):
    """Low-level serializer helpers relabel and de-identify masked unions."""

    def test_facilityindex_name_is_relabeled_to_other(self):
        masked = MaskedContributors(contributor_ids={7})
        contributor = {
            'id': 7,
            'name': 'Union X',
            'contrib_type': 'Union',
            'admin_id': 3,
        }
        self.assertTrue(is_contribution_masked(contributor, masked))
        self.assertEqual(
            get_contributor_name_from_facilityindex(contributor, True, masked),
            MASKED_CONTRIBUTOR_LABEL,
        )

    def test_facilityindex_id_is_removed_when_masked(self):
        masked = MaskedContributors(contributor_ids={7})
        contributor = {
            'id': 7,
            'name': 'Union X',
            'contrib_type': 'Union',
            'admin_id': 3,
        }
        self.assertIsNone(
            get_contributor_id_from_facilityindex(contributor, True, masked)
        )

    def test_unmasked_contributor_is_untouched(self):
        masked = MaskedContributors(contributor_ids={99})
        contributor = {
            'id': 7,
            'name': 'Union X',
            'contrib_type': 'Union',
            'admin_id': 3,
        }
        self.assertEqual(
            get_contributor_name_from_facilityindex(contributor, True, masked),
            'Union X',
        )
        self.assertEqual(
            get_contributor_id_from_facilityindex(contributor, True, masked),
            3,
        )

    def test_other_locations_helpers_match_by_admin_id(self):
        # facility_locations carry only admin_id; masking must still apply.
        masked = MaskedContributors(admin_ids={3})
        contributor = {
            'id': None,
            'name': 'Union X',
            'contrib_type': 'Union',
            'admin_id': 3,
        }
        self.assertEqual(
            get_contributor_name(contributor, True, masked),
            MASKED_CONTRIBUTOR_LABEL,
        )
        self.assertIsNone(get_contributor_id(contributor, True, masked))


class FacilityDownloadMaskingTest(TestCase):
    """The download contributor column hides masked unions."""

    @staticmethod
    def _facility(contributors, approved_claim=None):
        return SimpleNamespace(
            contributors=contributors,
            approved_claim=approved_claim,
        )

    def test_masked_union_contributor_shows_other(self):
        masked = MaskedContributors(contributor_ids={200})
        facility = self._facility([
            {
                'id': 200,
                'admin_id': 50,
                'name': 'Union X',
                'contrib_type': 'Union',
                'should_display_associations': True,
            },
        ])
        serializer = FacilityDownloadSerializer(masked_contributors=masked)
        cell = serializer.get_contributors(facility)
        self.assertEqual(cell, MASKED_CONTRIBUTOR_LABEL)
        self.assertNotIn('Union X', cell)

    def test_unmasked_contributor_shows_name(self):
        facility = self._facility([
            {
                'id': 200,
                'admin_id': 50,
                'name': 'Brand X',
                'contrib_type': 'Brand / Retailer',
                'should_display_associations': True,
            },
        ])
        serializer = FacilityDownloadSerializer()
        self.assertEqual(serializer.get_contributors(facility), 'Brand X')

    def test_masked_claim_contributor_shows_other(self):
        masked = MaskedContributors(contributor_ids={100})
        facility = self._facility(
            contributors=[],
            approved_claim={
                'contributor': {
                    'id': 100,
                    'admin_id': 9,
                    'name': 'Union Claimer',
                },
            },
        )
        serializer = FacilityDownloadSerializer(masked_contributors=masked)
        self.assertEqual(
            serializer.get_contributors(facility),
            '{} (Claimed)'.format(MASKED_CONTRIBUTOR_LABEL),
        )


class FacilityIndexContributorsMaskingTest(TestCase):
    """The API `contributors` array collapses masked unions into "Other"."""

    def test_union_is_relabeled_and_de_identified(self):
        facility = SimpleNamespace(contributors=[
            {
                'id': 200,
                'admin_id': 50,
                'name': 'Union X',
                'contrib_type': 'Union',
                'contributor_name': 'Union X',
                'should_display_associations': True,
                'is_verified': False,
                'list_name': 'Union Member List',
            },
            {
                'id': 201,
                'admin_id': 51,
                'name': 'Brand Y',
                'contrib_type': 'Brand / Retailer',
                'contributor_name': 'Brand Y',
                'should_display_associations': True,
                'is_verified': False,
                'list_name': None,
            },
        ])

        serializer = FacilityIndexSerializer()
        module = 'api.serializers.facility.facility_index_serializer'
        with patch.object(
            FacilityIndexSerializer,
            '_masked_contributor_ids',
            return_value=MaskedContributors(contributor_ids={200}),
        ), patch(
            '{}.is_embed_mode_active'.format(module), return_value=False
        ), patch(
            '{}.can_user_see_detail'.format(module), return_value=True
        ):
            result = serializer.get_contributors(facility)

        names = [entry['name'] for entry in result]
        self.assertIn(MASKED_CONTRIBUTOR_LABEL, names)
        self.assertNotIn('Union X', names)
        self.assertIn('Brand Y', names)

        other_entry = next(
            entry for entry in result
            if entry['name'] == MASKED_CONTRIBUTOR_LABEL
        )
        self.assertEqual(
            other_entry['contributor_type'], Contributor.OTHER_CONTRIB_TYPE
        )
        self.assertNotIn('id', other_entry)
        self.assertNotIn('list_name', other_entry)
        self.assertNotIn('contributor_name', other_entry)


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'view_cache': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'create-flow-masking-test',
    },
})
class CreateFlowContributorMaskingTest(TestCase):
    """POST /api/facilities serializes its matches with
    FacilityIndexDetailsSerializer using a context of just
    ``{'request': request}`` (see api.processing.handle_external_match_
    process_result) - it never pre-resolves ``masked_contributors`` the way the
    list view does. This guards that an API (token) caller still gets union
    contributors masked on that path via the ``for_facilities_api``
    fallback."""

    def setUp(self):
        caches['view_cache'].clear()

    def tearDown(self):
        caches['view_cache'].clear()

    def test_token_request_masks_union_via_context_fallback(self):
        admin = User.objects.create(email='union-admin@example.com')
        anonymised = Contributor.objects.create(
            admin=admin,
            name='Union X',
            contrib_type=Contributor.UNION_CONTRIB_TYPE,
            anonymise_in_paid_products=True,
        )

        facility = SimpleNamespace(contributors=[
            {
                'id': anonymised.id,
                'admin_id': admin.id,
                'name': 'Union X',
                'contrib_type': 'Union',
                'contributor_name': 'Union X',
                'should_display_associations': True,
                'is_verified': False,
                'list_name': 'Union Member List',
            },
        ])

        # Mirror the create flow exactly: the serializer context carries only
        # the authenticated request, NOT a pre-resolved masked set.
        request = SimpleNamespace(auth='a-token')
        serializer = FacilityIndexSerializer(context={'request': request})

        module = 'api.serializers.facility.facility_index_serializer'
        with patch(
            '{}.is_embed_mode_active'.format(module), return_value=False
        ), patch(
            '{}.can_user_see_detail'.format(module), return_value=True
        ):
            result = serializer.get_contributors(facility)

        names = [entry['name'] for entry in result]
        self.assertIn(MASKED_CONTRIBUTOR_LABEL, names)
        self.assertNotIn('Union X', names)

    def test_non_api_request_keeps_union_visible(self):
        admin = User.objects.create(email='union-admin2@example.com')
        anonymised = Contributor.objects.create(
            admin=admin,
            name='Union X',
            contrib_type=Contributor.UNION_CONTRIB_TYPE,
            anonymise_in_paid_products=True,
        )

        facility = SimpleNamespace(contributors=[
            {
                'id': anonymised.id,
                'admin_id': admin.id,
                'name': 'Union X',
                'contrib_type': 'Union',
                'contributor_name': 'Union X',
                'should_display_associations': True,
                'is_verified': False,
                'list_name': 'Union Member List',
            },
        ])

        # A web/session caller (no token) must still see the real name.
        request = SimpleNamespace(auth=None)
        serializer = FacilityIndexSerializer(context={'request': request})

        module = 'api.serializers.facility.facility_index_serializer'
        with patch(
            '{}.is_embed_mode_active'.format(module), return_value=False
        ), patch(
            '{}.can_user_see_detail'.format(module), return_value=True
        ):
            result = serializer.get_contributors(facility)

        names = [entry['name'] for entry in result]
        self.assertIn('Union X', names)
        self.assertNotIn(MASKED_CONTRIBUTOR_LABEL, names)


class CreatedFromMaskingTest(TestCase):
    """`created_from` is matched by name and relabeled to "Other"."""

    @staticmethod
    def _get_created_from(created_from_info, masked):
        serializer = FacilityIndexDetailsSerializer()
        module = 'api.serializers.facility.facility_index_details_serializer'
        with patch.object(
            FacilityIndexDetailsSerializer,
            '_masked_contributor_ids',
            return_value=masked,
        ), patch(
            '{}.can_user_see_detail'.format(module), return_value=True
        ), patch(
            '{}.is_embed_mode_active'.format(module), return_value=False
        ):
            return serializer.get_created_from(
                SimpleNamespace(created_from_info=created_from_info)
            )

    def test_masked_union_created_from_shows_other(self):
        info = {
            'should_display_associations': True,
            'created_at': None,
            'contributor_name': 'Union X',
            'contrib_type': 'Union',
        }
        result = self._get_created_from(
            info, MaskedContributors(names={'Union X'})
        )
        self.assertEqual(result['contributor'], MASKED_CONTRIBUTOR_LABEL)

    def test_unmasked_created_from_shows_name(self):
        info = {
            'should_display_associations': True,
            'created_at': None,
            'contributor_name': 'Brand X',
            'contrib_type': 'Brand / Retailer',
        }
        result = self._get_created_from(
            info, MaskedContributors(names={'Union X'})
        )
        self.assertEqual(result['contributor'], 'Brand X')


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'view_cache': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'anonymised-only-test',
    },
})
class AnonymisedOnlyAggregateTest(TestCase):
    """
    `FacilitiesViewSet.__is_anonymised_only` decides whether a whole search
    result is attributed only to anonymised contributors (front-end download
    button signal). It resolves from the cached anonymised set against the
    denormalized `contributors_id` array, with no query when nothing is
    anonymised.
    """

    # Resolve the name-mangled static method once for readability.
    _is_anonymised_only = staticmethod(
        FacilitiesViewSet._FacilitiesViewSet__is_anonymised_only
    )

    def setUp(self):
        caches['view_cache'].clear()
        self.union_user = User.objects.create(email='union@example.com')
        self.anonymised = Contributor.objects.create(
            admin=self.union_user,
            name='Anonymised Co',
            contrib_type=Contributor.UNION_CONTRIB_TYPE,
            anonymise_in_paid_products=True,
        )
        self.other = Contributor.objects.create(
            admin=User.objects.create(email='brand@example.com'),
            name='Brand Co',
            contrib_type='Brand / Retailer',
        )

    def tearDown(self):
        caches['view_cache'].clear()

    def _make_index(self, idx, contributors_id):
        return FacilityIndex.objects.create(
            id=str(idx),
            name='Name',
            address='Address',
            country_code='US',
            location=Point(0, 0),
            contributors_count=len(contributors_id),
            contributors_id=contributors_id,
            contrib_types=[],
            contributors=[],
            lists=[],
            approved_claim_ids=[],
            facility_names=[],
            facility_addresses=[],
            extended_fields=[],
            sector=[],
        )

    def test_all_anonymised_returns_true(self):
        self._make_index(1, [self.anonymised.id])
        queryset = FacilityIndex.objects.all()
        masked = ContributorMaskingPolicy.flagged_contributors()
        self.assertTrue(
            self._is_anonymised_only(queryset, masked, queryset.count())
        )

    def test_mixed_result_returns_false(self):
        self._make_index(1, [self.anonymised.id])
        self._make_index(2, [self.anonymised.id, self.other.id])
        queryset = FacilityIndex.objects.all()
        masked = ContributorMaskingPolicy.flagged_contributors()
        self.assertFalse(
            self._is_anonymised_only(queryset, masked, queryset.count())
        )

    def test_no_anonymised_contributors_returns_false(self):
        self.anonymised.anonymise_in_paid_products = False
        self.anonymised.save()
        caches['view_cache'].clear()
        self._make_index(1, [self.anonymised.id])
        queryset = FacilityIndex.objects.all()
        masked = ContributorMaskingPolicy.flagged_contributors()
        self.assertFalse(
            self._is_anonymised_only(queryset, masked, queryset.count())
        )

    def test_empty_result_returns_false(self):
        self._make_index(1, [self.anonymised.id])
        masked = ContributorMaskingPolicy.flagged_contributors()
        self.assertFalse(
            self._is_anonymised_only(FacilityIndex.objects.all(), masked, 0)
        )


class DownloadViewMaskingTest(TestCase):
    """
    `FacilitiesDownloadViewSet.get_serializer` must pass the pre-resolved
    `MaskedContributors` set to `FacilityDownloadSerializer` so that
    contributor names are masked in CSV/XLSX downloads.
    """

    def test_get_serializer_passes_masked_contributors(self):
        from api.facilities_download_view_set import FacilitiesDownloadViewSet

        fake_masked = MaskedContributors(contributor_ids={42})

        view = FacilitiesDownloadViewSet()
        # Simulate a non-embed request
        view.request = MagicMock()
        view.request.query_params.get = MagicMock(return_value=None)

        with patch(
            'api.facilities_download_view_set'
            '.ContributorMaskingPolicy.for_download',
            return_value=fake_masked,
        ) as mock_get, patch(
            'api.facilities_download_view_set.FacilityDownloadSerializer',
        ) as mock_cls:
            view.get_serializer([])

        mock_get.assert_called_once()
        mock_cls.assert_called_once_with(
            [],
            many=True,
            masked_contributors=fake_masked,
        )


class FacilitiesListAnonymisedOnlyKeyTest(TestCase):
    """
    `GET /api/facilities/` must include an `anonymised_only` key in the
    response so the front-end can decide whether to disable the download
    button.
    """

    def _make_list_response(self, request):
        """Call FacilitiesViewSet.list() and return the response data."""
        from api.views.facility.facilities_view_set import FacilitiesViewSet
        view = FacilitiesViewSet()
        view.request = request
        view.kwargs = {}
        view.format_kwarg = None
        view.action = 'list'
        return view.list(request)

    def test_anonymised_only_key_present_in_response(self):
        from rest_framework.request import Request
        from rest_framework.test import APIRequestFactory

        factory = APIRequestFactory()
        request = Request(factory.get('/api/facilities/'))

        with patch(
            'api.views.facility.facilities_view_set'
            '.ContributorMaskingPolicy.flagged_contributors',
            return_value=MaskedContributors(),
        ), patch(
            'api.views.facility.facilities_view_set.FacilityIndexSerializer'
        ) as mock_ser, patch(
            'api.views.facility.facilities_view_set'
            '.FacilityQueryParamsSerializer'
        ) as mock_params, patch(
            'api.views.facility.facilities_view_set'
            '.FacilityListPageParameterSerializer'
        ) as mock_page_params, patch(
            'api.views.facility.facilities_view_set.FacilityIndex'
            '.objects.filter_by_query_params',
            return_value=FacilityIndex.objects.none(),
        ), patch.object(
            FacilitiesViewSet, 'paginate_queryset', return_value=None
        ):
            mock_page_params.return_value.is_valid.return_value = True
            mock_params.return_value.is_valid.return_value = True
            mock_params.return_value.validated_data = {
                'sort_by': None,
                'detail': False,
                'number_of_public_contributors': False,
            }
            mock_ser.return_value.data = []

            response = self._make_list_response(request)

        self.assertIn('anonymised_only', response.data)


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'view_cache': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'auth-tier-cache-test',
    },
})
class CachePageByAuthTierTest(TestCase):
    """
    `cache_page_by_auth_tier` collapses the `Authorization` dimension into two
    buckets - `paid` (token API callers) and `regular` (everyone else) - so the
    view is cached in at most two entries per URL instead of one per token.
    """

    def setUp(self):
        caches['view_cache'].clear()
        self.factory = RequestFactory()
        self.seen = []

        @cache_page_by_auth_tier(60, cache='view_cache')
        def view(_self, request):
            self.seen.append(request.META.get('HTTP_AUTHORIZATION'))
            return HttpResponse('body-{}'.format(len(self.seen)))

        self.view = view

    def tearDown(self):
        caches['view_cache'].clear()

    def _get(self, auth_header=None, is_paid=False):
        request = self.factory.get('/api/facilities/OS123/')
        if auth_header is not None:
            request.META['HTTP_AUTHORIZATION'] = auth_header
        request.auth = 'token-obj' if is_paid else None
        response = self.view(SimpleNamespace(), request)
        return response, request

    def test_two_tokens_share_one_paid_bucket(self):
        response_a, _ = self._get(auth_header='Token AAA', is_paid=True)
        response_b, _ = self._get(auth_header='Token BBB', is_paid=True)

        # The view runs once; the second token is served from the same entry.
        self.assertEqual(self.seen, ['paid'])
        self.assertEqual(response_a.content, b'body-1')
        self.assertEqual(response_b.content, b'body-1')

    def test_regular_and_paid_use_separate_buckets(self):
        paid_response, _ = self._get(auth_header='Token AAA', is_paid=True)
        regular_response, _ = self._get()

        # Two distinct buckets => the view runs twice with different content.
        self.assertEqual(self.seen, ['paid', None])
        self.assertEqual(paid_response.content, b'body-1')
        self.assertEqual(regular_response.content, b'body-2')

        # Subsequent same-bucket requests are served from cache.
        cached_regular, _ = self._get()
        self.assertEqual(self.seen, ['paid', None])
        self.assertEqual(cached_regular.content, b'body-2')

    def test_response_still_varies_on_authorization(self):
        response, _ = self._get(auth_header='Token AAA', is_paid=True)

        self.assertIn('Authorization', response.get('Vary', ''))

    def test_original_authorization_header_is_restored(self):
        _, request = self._get(auth_header='Token AAA', is_paid=True)

        self.assertEqual(request.META['HTTP_AUTHORIZATION'], 'Token AAA')
