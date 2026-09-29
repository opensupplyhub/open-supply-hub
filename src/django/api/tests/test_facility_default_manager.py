from unittest.mock import patch

from api.models import (
    Contributor,
    Facility,
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.models.facility.facility_manager import (
    FacilityIncludingCandidatesManager,
    FacilityManager,
)
from django.contrib.gis.geos import GEOSGeometry, Point
from django.db.models import Manager
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.test import TestCase
from rest_framework import serializers

CANDIDATE_POLYGON_WKT = 'POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))'


class FacilityDefaultManagerTest(TestCase):
    """Facility.objects hides candidates; including_candidates opts in.

    These tests pin the related-object traversal semantics documented on
    FacilityManager (OSDEV-3380). If one of them fails after a Django
    upgrade the docstring there is out of date, not just the test.
    """

    def setUp(self):
        self.user = User.objects.create(email='one@example.com')
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='test contributor 1',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.list = FacilityList.objects.create(
            header='header', file_name='one', name='First List'
        )
        self.source = Source.objects.create(
            facility_list=self.list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        self.next_row_index = 0

        self.facility = self._create_facility(name='Confirmed')
        self.candidate = self._create_candidate()

    def _create_list_item(self):
        self.next_row_index += 1
        return FacilityListItem.objects.create(
            name='Item',
            address='Address',
            country_code='US',
            sector=['Apparel'],
            row_index=self.next_row_index,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )

    def _create_facility(self, **kwargs):
        defaults = {
            'name': 'Name',
            'address': 'Address',
            'country_code': 'US',
            'location': Point(0, 0),
            'created_from': self._create_list_item(),
        }
        defaults.update(kwargs)
        return Facility.including_candidates.create(**defaults)

    def _create_candidate(self, **kwargs):
        defaults = {
            'name': '',
            'address': '',
            'is_candidate': True,
            'polygon': GEOSGeometry(CANDIDATE_POLYGON_WKT, srid=4326),
            'confidence': 0.87,
            'external_id': 'eg-facility-0001',
            'source': 'earth_genome',
        }
        defaults.update(kwargs)
        return self._create_facility(**defaults)

    # --- Manager wiring ---------------------------------------------------

    def test_objects_is_the_default_manager(self):
        self.assertIs(Facility._default_manager, Facility.objects)
        self.assertIsInstance(Facility.objects, FacilityManager)
        self.assertIsInstance(
            Facility.including_candidates, FacilityIncludingCandidatesManager
        )

    def test_base_manager_is_a_plain_manager(self):
        """Forward FK access and save() rely on this staying unfiltered."""
        self.assertIs(type(Facility._base_manager), Manager)

    # --- AC #1 / #2: default exclusion and explicit opt-in ---------------

    def test_objects_excludes_candidates(self):
        ids = set(Facility.objects.values_list('id', flat=True))

        self.assertEqual(ids, {self.facility.id})
        self.assertEqual(Facility.objects.count(), 1)
        self.assertFalse(
            Facility.objects.filter(pk=self.candidate.id).exists()
        )
        with self.assertRaises(Facility.DoesNotExist):
            Facility.objects.get(pk=self.candidate.id)

    def test_including_candidates_includes_candidates(self):
        ids = set(Facility.including_candidates.values_list('id', flat=True))

        self.assertEqual(ids, {self.facility.id, self.candidate.id})
        self.assertEqual(
            Facility.including_candidates.get(pk=self.candidate.id),
            self.candidate,
        )

    def test_objects_can_still_create_a_candidate(self):
        """create() never checks the manager filter, so ingest code that
        hasn't opted in still writes candidates; the point of the manager
        is what gets read back."""
        candidate = Facility.objects.create(
            name='',
            address='',
            country_code='US',
            location=Point(0, 0),
            created_from=self._create_list_item(),
            is_candidate=True,
            source='earth_genome',
            external_id='eg-facility-0002',
        )

        self.assertFalse(Facility.objects.filter(pk=candidate.id).exists())
        self.assertTrue(
            Facility.including_candidates.filter(pk=candidate.id).exists()
        )

    def test_os_id_generation_avoids_candidate_ids(self):
        """save() checks new IDs against including_candidates."""
        with patch(
            'api.models.facility.facility.make_os_id',
            side_effect=[self.candidate.id, 'US2026999ZZZZZ'],
        ):
            facility = self._create_facility()

        self.assertEqual(facility.id, 'US2026999ZZZZZ')

    # --- Django entry points that use _default_manager --------------------

    def test_get_object_or_404_hides_candidates(self):
        self.assertEqual(
            get_object_or_404(Facility, pk=self.facility.id), self.facility
        )
        with self.assertRaises(Http404):
            get_object_or_404(Facility, pk=self.candidate.id)

    def test_model_serializer_fk_field_rejects_candidates(self):
        """DRF builds auto FK fields from _default_manager."""
        class ClaimSerializer(serializers.ModelSerializer):
            class Meta:
                model = FacilityClaim
                fields = ['facility']

        field = ClaimSerializer().fields['facility']

        self.assertEqual(
            field.to_internal_value(self.facility.id), self.facility
        )
        with self.assertRaises(serializers.ValidationError):
            field.to_internal_value(self.candidate.id)

    # --- AC #4: related-object traversal semantics -----------------------

    def test_forward_fk_access_reaches_a_candidate(self):
        """claim.facility goes through _base_manager, not objects."""
        claim = FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.candidate,
        )
        claim = FacilityClaim.objects.get(pk=claim.pk)

        self.assertEqual(claim.facility, self.candidate)
        self.assertTrue(claim.facility.is_candidate)

    def test_reverse_one_to_one_access_reaches_a_candidate(self):
        list_item = FacilityListItem.objects.get(
            pk=self.candidate.created_from_id
        )

        self.assertEqual(list_item.created_facility, self.candidate)

    def test_fk_join_filters_do_not_apply_the_manager(self):
        """Joins from another model see candidate rows; callers that need
        to exclude them must filter facility__is_candidate=False."""
        FacilityClaim.objects.create(
            contributor=self.contributor, facility=self.candidate
        )
        FacilityClaim.objects.create(
            contributor=self.contributor, facility=self.facility
        )

        self.assertEqual(
            FacilityClaim.objects.filter(facility__country_code='US').count(),
            2,
        )
        self.assertEqual(
            FacilityClaim.objects.filter(
                facility__country_code='US', facility__is_candidate=False
            ).count(),
            1,
        )

    def test_select_related_and_prefetch_reach_a_candidate(self):
        claim = FacilityClaim.objects.create(
            contributor=self.contributor, facility=self.candidate
        )

        joined = FacilityClaim.objects.select_related('facility').get(
            pk=claim.pk
        )
        prefetched = FacilityClaim.objects.prefetch_related('facility').get(
            pk=claim.pk
        )

        self.assertEqual(joined.facility, self.candidate)
        self.assertEqual(prefetched.facility, self.candidate)

    def test_reverse_fk_managers_on_a_candidate_are_unaffected(self):
        list_item = self._create_list_item()
        FacilityMatch.objects.create(
            facility_list_item=list_item,
            facility=self.candidate,
            status=FacilityMatch.AUTOMATIC,
            results={},
            confidence=1,
        )

        self.assertEqual(self.candidate.facilitymatch_set.count(), 1)
        self.assertEqual(self.candidate.facilitylistitem_set.count(), 0)

    def test_candidate_can_be_refreshed_and_saved(self):
        """refresh_from_db() and the UPDATE in save() use _base_manager."""
        self.candidate.confidence = 0.42
        self.candidate.save()

        self.candidate.refresh_from_db()
        self.assertEqual(self.candidate.confidence, 0.42)

        self.candidate.save(update_fields=['updated_at'])
        self.assertEqual(
            Facility.including_candidates.get(pk=self.candidate.id).confidence,
            0.42,
        )

    def test_queryset_update_and_delete_respect_the_manager(self):
        Facility.objects.update(is_closed=True)
        self.candidate.refresh_from_db()
        self.assertIsNone(self.candidate.is_closed)

        Facility.objects.filter(pk=self.candidate.id).delete()
        self.assertTrue(
            Facility.including_candidates.filter(pk=self.candidate.id).exists()
        )

    # --- Existing FacilityManager behavior is preserved -------------------

    def test_filter_by_query_params_still_returns_facility_queryset(self):
        from django.http import QueryDict

        qs = Facility.objects.filter_by_query_params(QueryDict('countries=US'))

        self.assertIs(qs.model, Facility)
        self.assertNotIn(self.candidate, qs)
