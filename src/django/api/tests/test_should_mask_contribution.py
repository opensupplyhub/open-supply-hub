from types import SimpleNamespace
from unittest.mock import patch

from django.core.cache import caches
from django.test import TestCase, override_settings

from api.constants import (
    MASKED_CONTRIBUTOR_IDS_CACHE_KEY,
    MASKED_CONTRIBUTOR_LABEL,
)
from api.models.contributor.contributor import Contributor
from api.models.user import User
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
from api.services.should_mask_contribution import (
    MaskedContributors,
    ShouldMaskContribution,
)


class MaskedContributorsTest(TestCase):
    """`MaskedContributors` matches a contribution by id or admin id."""

    def test_matches_by_contributor_id(self):
        masked = MaskedContributors(contributor_ids={1})
        self.assertTrue(masked.matches({'id': 1}))
        self.assertFalse(masked.matches({'id': 2}))

    def test_matches_by_admin_id_when_contributor_id_missing(self):
        # facility_locations / facility_list_items only carry `admin_id`.
        masked = MaskedContributors(admin_ids={9})
        self.assertTrue(masked.matches({'id': None, 'admin_id': 9}))
        self.assertTrue(masked.matches({'id': 5, 'admin_id': 9}))
        self.assertFalse(masked.matches({'id': 5, 'admin_id': 8}))

    def test_empty_is_falsy_and_never_matches(self):
        masked = MaskedContributors()
        self.assertFalse(masked)
        self.assertFalse(masked.matches({'id': 1, 'admin_id': 1}))

    def test_does_not_match_empty_contributor(self):
        masked = MaskedContributors(contributor_ids={1})
        self.assertFalse(masked.matches(None))
        self.assertFalse(masked.matches({}))

    def test_masks_name_for_created_from(self):
        # created_from_info carries only the contributor name.
        masked = MaskedContributors(names={'Union X'})
        self.assertTrue(masked)
        self.assertTrue(masked.masks_name('Union X'))
        self.assertFalse(masked.masks_name('Brand Y'))
        self.assertFalse(masked.masks_name(None))


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
class ShouldMaskContributionServiceTest(TestCase):
    """Resolving and caching the contributors to hide in paid products."""

    def setUp(self):
        caches['view_cache'].clear()

    def tearDown(self):
        caches['view_cache'].clear()

    @staticmethod
    def _make_contributor(contrib_type, hide=True, email='c@example.com'):
        user = User.objects.create(email=email)
        user.hide_in_paid_products = hide
        user.save()
        contributor = Contributor.objects.create(
            admin=user,
            name='Contributor {}'.format(contrib_type),
            contrib_type=contrib_type,
        )
        return contributor, user

    def test_union_with_hide_flag_is_masked(self):
        contributor, user = self._make_contributor(
            Contributor.UNION_CONTRIB_TYPE
        )
        masked = ShouldMaskContribution.get_masked_contributors()
        self.assertIn(contributor.id, masked.contributor_ids)
        self.assertIn(user.id, masked.admin_ids)
        self.assertIn(contributor.name, masked.names)

    def test_union_without_hide_flag_is_not_masked(self):
        contributor, _ = self._make_contributor(
            Contributor.UNION_CONTRIB_TYPE, hide=False
        )
        masked = ShouldMaskContribution.get_masked_contributors()
        self.assertNotIn(contributor.id, masked.contributor_ids)

    def test_non_union_is_not_masked(self):
        contributor, _ = self._make_contributor('Brand / Retailer')
        masked = ShouldMaskContribution.get_masked_contributors()
        self.assertNotIn(contributor.id, masked.contributor_ids)

    def test_for_request_is_empty_without_token(self):
        self._make_contributor(Contributor.UNION_CONTRIB_TYPE)
        self.assertFalse(
            ShouldMaskContribution.for_request(SimpleNamespace(auth=None))
        )
        self.assertFalse(ShouldMaskContribution.for_request(None))

    def test_for_request_masks_for_token_user(self):
        contributor, _ = self._make_contributor(
            Contributor.UNION_CONTRIB_TYPE
        )
        masked = ShouldMaskContribution.for_request(
            SimpleNamespace(auth='a-token')
        )
        self.assertTrue(masked)
        self.assertIn(contributor.id, masked.contributor_ids)

    def test_masked_contributors_are_cached(self):
        first, _ = self._make_contributor(Contributor.UNION_CONTRIB_TYPE)
        ShouldMaskContribution.get_masked_contributors()

        # A union added after the cache is warm is not seen until the cache
        # is invalidated.
        second, _ = self._make_contributor(
            Contributor.UNION_CONTRIB_TYPE, email='c2@example.com'
        )
        cached = ShouldMaskContribution.get_masked_contributors()
        self.assertIn(first.id, cached.contributor_ids)
        self.assertNotIn(second.id, cached.contributor_ids)

        caches['view_cache'].delete(MASKED_CONTRIBUTOR_IDS_CACHE_KEY)
        refreshed = ShouldMaskContribution.get_masked_contributors()
        self.assertIn(second.id, refreshed.contributor_ids)

    def test_toggling_hide_flag_invalidates_cache(self):
        contributor, user = self._make_contributor(
            Contributor.UNION_CONTRIB_TYPE
        )
        warm = ShouldMaskContribution.get_masked_contributors()
        self.assertIn(contributor.id, warm.contributor_ids)

        # Disabling the flag must drop the cached set on save so the next
        # paid request stops masking the contributor without waiting for TTL.
        user.hide_in_paid_products = False
        user.save()

        refreshed = ShouldMaskContribution.get_masked_contributors()
        self.assertNotIn(contributor.id, refreshed.contributor_ids)


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
