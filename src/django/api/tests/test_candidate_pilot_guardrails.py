import json
from unittest.mock import Mock, patch

from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)
from api.serializers.v1.production_location_post_schema_serializer import (
    ProductionLocationPostSchemaSerializer,
)
from api.services.candidate_guard import (
    CandidateCreationNotAllowed,
    assert_may_create_candidate,
    is_earth_genome_contributor,
)
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase
from contricleaner.lib.contri_cleaner import ContriCleaner
from contricleaner.tests.os_id_lookup_mock import OSIDLookupMock
from contricleaner.tests.sector_cache_mock import SectorCacheMock

from django.contrib.gis.geos import Point
from django.core.exceptions import PermissionDenied
from django.test import TestCase, override_settings
from django.urls import reverse

BLANK_NAME_ERROR = 'name cannot consist solely of punctuation or whitespace.'


class CandidateGuardFixtureMixin:
    """Two contributors: the designated Earth Genome one and another one."""

    def setUp(self):
        self.eg_user = User.objects.create(email='eg@example.com')
        self.eg_contributor = Contributor.objects.create(
            admin=self.eg_user,
            name='Earth Genome',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.eg_source = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=self.eg_contributor,
        )

        self.other_user = User.objects.create(email='other@example.com')
        self.other_contributor = Contributor.objects.create(
            admin=self.other_user,
            name='Some other contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        self.other_list = FacilityList.objects.create(
            header='header', file_name='one', name='First List'
        )
        self.other_source = Source.objects.create(
            facility_list=self.other_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.other_contributor,
        )
        self.next_row_index = 0

        guard_settings = override_settings(
            EARTH_GENOME_CONTRIBUTOR_ID=self.eg_contributor.id
        )
        guard_settings.enable()
        self.addCleanup(guard_settings.disable)

    def _create_list_item(self, list_source, **kwargs):
        self.next_row_index += 1
        defaults = {
            'name': 'Item',
            'address': 'Address',
            'country_code': 'US',
            'sector': ['Apparel'],
            'row_index': self.next_row_index,
            'geocoded_point': Point(0, 0),
            'status': FacilityListItem.CONFIRMED_MATCH,
            'source': list_source,
        }
        defaults.update(kwargs)
        return FacilityListItem.objects.create(**defaults)

    def _facility_kwargs(self, list_source, **kwargs):
        defaults = {
            'name': 'Name',
            'address': 'Address',
            'country_code': 'US',
            'location': Point(0, 0),
            'created_from': self._create_list_item(list_source),
        }
        defaults.update(kwargs)
        return defaults

    def _candidate_kwargs(self, list_source, **kwargs):
        defaults = {
            'name': '',
            'address': '',
            'is_candidate': True,
            'confidence': 0.9,
            'source': 'earth_genome',
            'external_id': 'eg-{}'.format(self.next_row_index + 1),
        }
        defaults.update(kwargs)
        return self._facility_kwargs(list_source, **defaults)


class CandidateGuardHelperTest(CandidateGuardFixtureMixin, TestCase):
    """api.services.candidate_guard in isolation."""

    def test_is_earth_genome_contributor_matches_the_configured_id(self):
        self.assertTrue(is_earth_genome_contributor(self.eg_contributor))
        self.assertTrue(is_earth_genome_contributor(self.eg_contributor.id))
        self.assertFalse(is_earth_genome_contributor(self.other_contributor))
        self.assertFalse(
            is_earth_genome_contributor(self.other_contributor.id)
        )
        self.assertFalse(is_earth_genome_contributor(None))

    @override_settings(EARTH_GENOME_CONTRIBUTOR_ID=None)
    def test_nobody_is_earth_genome_while_the_setting_is_unset(self):
        self.assertFalse(is_earth_genome_contributor(self.eg_contributor))
        self.assertFalse(is_earth_genome_contributor(self.eg_contributor.id))

    def test_assert_passes_for_a_row_created_from_an_eg_list_item(self):
        facility = Facility(**self._candidate_kwargs(self.eg_source))

        assert_may_create_candidate(facility)  # must not raise

    def test_assert_rejects_a_row_created_from_another_contributor(self):
        facility = Facility(**self._candidate_kwargs(self.other_source))

        with self.assertRaises(CandidateCreationNotAllowed) as ctx:
            assert_may_create_candidate(facility)

        message = str(ctx.exception)
        self.assertIn('Only the Earth Genome contributor', message)
        self.assertIn(
            'contributor_id={}'.format(self.other_contributor.id), message
        )
        self.assertIn(
            'EARTH_GENOME_CONTRIBUTOR_ID={}'.format(self.eg_contributor.id),
            message,
        )

    def test_assert_rejects_when_created_from_is_missing(self):
        kwargs = self._candidate_kwargs(self.eg_source)
        del kwargs['created_from']

        with self.assertRaises(CandidateCreationNotAllowed):
            assert_may_create_candidate(Facility(**kwargs))

    def test_assert_rejects_when_the_source_has_no_contributor(self):
        orphan_source = Source.objects.create(
            source_type=Source.SINGLE, contributor=None
        )
        facility = Facility(**self._candidate_kwargs(orphan_source))

        with self.assertRaises(CandidateCreationNotAllowed):
            assert_may_create_candidate(facility)

    def test_exception_is_a_permission_denied(self):
        """Django and DRF both turn PermissionDenied into a 403, so a
        misrouted caller gets a clear refusal instead of a 500."""
        self.assertTrue(
            issubclass(CandidateCreationNotAllowed, PermissionDenied)
        )


class CandidateGuardModelBoundaryTest(CandidateGuardFixtureMixin, TestCase):
    """Facility.save() enforces the guard on every ORM creation path."""

    # --- AC #2: the Earth Genome contributor may create candidates --------

    def test_eg_contributor_creates_a_candidate_via_objects_create(self):
        candidate = Facility.objects.create(
            **self._candidate_kwargs(self.eg_source)
        )

        self.assertTrue(
            Facility.including_candidates.filter(pk=candidate.pk).exists()
        )

    def test_eg_contributor_creates_a_candidate_via_including_candidates(
        self,
    ):
        candidate = Facility.including_candidates.create(
            **self._candidate_kwargs(self.eg_source)
        )

        self.assertTrue(candidate.is_candidate)

    def test_eg_contributor_creates_a_candidate_via_instance_save(self):
        candidate = Facility(**self._candidate_kwargs(self.eg_source))

        candidate.save()

        self.assertTrue(candidate.id.startswith('US'))

    # --- AC #3: everyone else is rejected --------------------------------

    def test_other_contributor_cannot_create_a_candidate(self):
        with self.assertRaises(CandidateCreationNotAllowed):
            Facility.objects.create(
                **self._candidate_kwargs(self.other_source)
            )

        self.assertEqual(Facility.including_candidates.count(), 0)

    def test_other_contributor_cannot_create_a_candidate_via_save(self):
        facility = Facility(**self._candidate_kwargs(self.other_source))

        with self.assertRaises(CandidateCreationNotAllowed):
            facility.save()

        self.assertEqual(Facility.including_candidates.count(), 0)

    def test_other_contributor_cannot_create_a_named_candidate(self):
        """is_candidate=True alone trips the guard, name or no name."""
        with self.assertRaises(CandidateCreationNotAllowed):
            Facility.objects.create(
                **self._candidate_kwargs(
                    self.other_source, name='Named', address='Addressed'
                )
            )

    def test_other_contributor_cannot_create_a_nameless_non_candidate(self):
        """An empty name alone trips the guard, even with is_candidate off."""
        with self.assertRaises(CandidateCreationNotAllowed):
            Facility.objects.create(
                **self._facility_kwargs(self.other_source, name='')
            )

    def test_other_contributor_cannot_create_an_addressless_non_candidate(
        self,
    ):
        with self.assertRaises(CandidateCreationNotAllowed):
            Facility.objects.create(
                **self._facility_kwargs(self.other_source, address='')
            )

    def test_whitespace_only_name_counts_as_empty(self):
        with self.assertRaises(CandidateCreationNotAllowed):
            Facility.objects.create(
                **self._facility_kwargs(self.other_source, name='   ')
            )

    @override_settings(EARTH_GENOME_CONTRIBUTOR_ID=None)
    def test_nobody_can_create_a_candidate_while_the_setting_is_unset(self):
        with self.assertRaises(CandidateCreationNotAllowed):
            Facility.objects.create(
                **self._candidate_kwargs(self.eg_source)
            )

    def test_missing_created_from_is_rejected_before_the_db_is_hit(self):
        kwargs = self._candidate_kwargs(self.eg_source)
        del kwargs['created_from']

        with self.assertRaises(CandidateCreationNotAllowed):
            Facility.objects.create(**kwargs)

    # --- Normal facilities are untouched ---------------------------------

    def test_named_non_candidate_from_any_contributor_is_untouched(self):
        facility = Facility.objects.create(
            **self._facility_kwargs(self.other_source)
        )

        self.assertFalse(facility.is_candidate)
        self.assertEqual(Facility.objects.count(), 1)

    @override_settings(EARTH_GENOME_CONTRIBUTOR_ID=None)
    def test_named_non_candidate_is_untouched_while_the_setting_is_unset(
        self,
    ):
        Facility.objects.create(**self._facility_kwargs(self.other_source))

        self.assertEqual(Facility.objects.count(), 1)

    def test_named_non_candidate_never_touches_the_guard(self):
        with patch(
            'api.models.facility.facility.assert_may_create_candidate'
        ) as guard:
            Facility.objects.create(
                **self._facility_kwargs(self.other_source)
            )

        guard.assert_not_called()

    def test_updates_to_an_existing_candidate_are_not_rechecked(self):
        """The guard is a creation guard: a candidate that exists stays
        saveable even if the setting later changes."""
        candidate = Facility.objects.create(
            **self._candidate_kwargs(self.eg_source)
        )

        with override_settings(EARTH_GENOME_CONTRIBUTOR_ID=None):
            candidate.confidence = 0.5
            candidate.save()
            candidate.save(update_fields=['updated_at'])

        candidate.refresh_from_db()
        self.assertEqual(candidate.confidence, 0.5)


class ContributorUploadBlankNameStillRejectedTest(TestCase):
    """AC #1: a blank name is still rejected at the API boundary, exactly
    as before this change, so the model guard is a backstop and never the
    first line of defence for contributor uploads.

    Paths and where their existing coverage lives:

    * List upload and the legacy ``POST /api/facilities/`` both run
      ContriCleaner, whose ``RowCleanFieldSerializer('name', ...)`` flags a
      blank name (``contricleaner/tests/test_row_clean_field_serializer.py``
      and ``test_source_parser_xlsx.py``).
    * SLC / API v1 ``POST /api/v1/production-locations/`` runs
      ``ProductionLocationPostSchemaSerializer`` first
      (``api/tests/test_location_contribution_strategy.py``,
      ``test_production_locations_create.py``) and ContriCleaner after it.
    """

    def test_contricleaner_rejects_a_blank_name(self):
        processed = ContriCleaner(
            {'country': 'US', 'name': '', 'address': '1234 Main St'},
            SectorCacheMock(),
            OSIDLookupMock(),
        ).process_data()

        row = processed.rows[0]
        self.assertEqual(
            [e['message'] for e in row.errors], [BLANK_NAME_ERROR]
        )
        self.assertEqual(row.errors[0]['field'], 'name')

    def test_contricleaner_rejects_a_whitespace_only_name(self):
        processed = ContriCleaner(
            {'country': 'US', 'name': '   ', 'address': '1234 Main St'},
            SectorCacheMock(),
            OSIDLookupMock(),
        ).process_data()

        self.assertEqual(
            [e['message'] for e in processed.rows[0].errors],
            [BLANK_NAME_ERROR],
        )

    def test_v1_post_schema_serializer_rejects_a_blank_name(self):
        serializer = ProductionLocationPostSchemaSerializer(
            data={'name': '', 'address': '1234 Main St', 'country': 'US'}
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            [str(e) for e in serializer.errors['name']],
            ['This field may not be blank.'],
        )

    def test_v1_post_schema_serializer_rejects_a_missing_name(self):
        serializer = ProductionLocationPostSchemaSerializer(
            data={'address': '1234 Main St', 'country': 'US'}
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            [str(e) for e in serializer.errors['name']],
            ['Field name is required!'],
        )


class LegacyFacilityPostBlankNameTest(FacilityAPITestCaseBase):
    """AC #1 end to end for the legacy ``POST /api/facilities/`` route."""

    fixtures = ['sectors']

    @patch('api.geocoding.requests.get')
    def test_blank_name_is_rejected_with_400(self, mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        self.join_group_and_login()
        facilities_before = Facility.including_candidates.count()

        response = self.client.post(
            reverse('facility-list'),
            json.dumps({
                'country': 'US',
                'name': '',
                'address': '990 Spring Garden St., Philadelphia PA 19123',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        errors = json.loads(response.content)['errors']
        self.assertIn(BLANK_NAME_ERROR, [e['message'] for e in errors])
        self.assertEqual(
            Facility.including_candidates.count(), facilities_before
        )
        mock_get.assert_not_called()
