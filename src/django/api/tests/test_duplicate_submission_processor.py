from datetime import timedelta
from unittest.mock import patch

from django.contrib.gis.geos import Point
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.moderation_event import ModerationEvent
from api.models.contributor.contributor import Contributor
from api.models.user import User
from api.models.facility.facility import Facility
from api.models.facility.facility_list import FacilityList
from api.models.facility.facility_list_item import FacilityListItem
from api.models.source import Source
from api.moderation_event_actions.creation.moderation_event_creator \
    import ModerationEventCreator
from api.moderation_event_actions.creation.location_contribution \
    .location_contribution import LocationContribution
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.moderation_event_actions.creation.location_contribution \
    .processors.duplicate_submission_processor \
    import ADVISORY_LOCK_NAMESPACE, DUPLICATE_CHECK_WINDOW_MINUTES


class TestDuplicateSubmissionProcessor(APITestCase):
    def setUp(self):
        # This chain also runs SubmissionQualityProcessor after the
        # duplicate check, which would otherwise make a real Bedrock call
        # for every non-duplicate submission in this file. These tests
        # only care about duplicate-check behavior, so the quality check
        # is neutralized here (fail-open "no verdict") rather than in each
        # individual test.
        quality_check_patcher = patch(
            'api.moderation_event_actions.creation.location_contribution'
            '.processors.submission_quality_processor'
            '.SubmissionQualityService.evaluate',
            return_value=None,
        )
        quality_check_patcher.start()
        self.addCleanup(quality_check_patcher.stop)

        user = User.objects.create(email='test@example.com')
        user.set_password('example123')
        user.save()

        self.contributor = Contributor.objects.create(
            admin=user,
            name='test contributor 1',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        other_user = User.objects.create(email='other@example.com')
        other_user.set_password('example123')
        other_user.save()

        self.other_contributor = Contributor.objects.create(
            admin=other_user,
            name='test contributor 2',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        location_contribution_strategy = LocationContribution()
        self.moderation_event_creator = ModerationEventCreator(
            location_contribution_strategy
        )

        self.base_input_data = {
            'source': 'SLC',
            'name': 'Blue Horizon Facility',
            'address': '990 Spring Garden St., Philadelphia PA 19123',
            'country': 'US',
            'coordinates': {
                'lat': 51.078389,
                'lng': 16.978477
            }
        }

    def _submit(self, contributor, input_data, duplicate_override=False):
        event_dto = CreateModerationEventDTO(
            contributor=contributor,
            raw_data=input_data,
            request_type=ModerationEvent.RequestType.CREATE.value,
            duplicate_override=duplicate_override,
        )
        return self.moderation_event_creator.perform_event_creation(
            event_dto
        )

    def _age_most_recent_event(self, contributor, minutes):
        event = ModerationEvent.objects.filter(
            contributor=contributor
        ).latest('created_at')
        # Use a queryset update (not instance.save()) so the OpenSearch
        # post_save signal, which needs AWS credentials unavailable in
        # tests, isn't triggered.
        ModerationEvent.objects.filter(pk=event.pk).update(
            created_at=timezone.now() - timedelta(minutes=minutes)
        )
        return event

    def _reject_most_recent_event(self, contributor):
        event = ModerationEvent.objects.filter(
            contributor=contributor
        ).latest('created_at')
        # Use a queryset update (not instance.save()) so the OpenSearch
        # post_save signal, which needs AWS credentials unavailable in
        # tests, isn't triggered.
        ModerationEvent.objects.filter(pk=event.pk).update(
            status=ModerationEvent.Status.REJECTED.value
        )
        return event

    def test_first_submission_is_not_flagged(self):
        result = self._submit(self.contributor, self.base_input_data)

        self.assertEqual(result.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNotNone(result.moderation_event)

    @patch(
        'api.moderation_event_actions.creation.location_contribution'
        '.processors.duplicate_submission_processor.connection'
    )
    def test_advisory_lock_is_acquired_for_the_contributor(
        self, mock_connection
    ):
        mock_cursor = \
            mock_connection.cursor.return_value.__enter__.return_value

        result = self._submit(self.contributor, self.base_input_data)

        self.assertEqual(result.status_code, status.HTTP_202_ACCEPTED)
        mock_cursor.execute.assert_called_once_with(
            'SELECT pg_advisory_xact_lock(%s, %s)',
            [ADVISORY_LOCK_NAMESPACE, self.contributor.pk]
        )

    @patch(
        'api.moderation_event_actions.creation.location_contribution'
        '.processors.duplicate_submission_processor.connection'
    )
    def test_advisory_lock_is_not_acquired_with_duplicate_override(
        self, mock_connection
    ):
        self._submit(
            self.contributor, self.base_input_data, duplicate_override=True
        )

        mock_connection.cursor.assert_not_called()

    @patch(
        'api.moderation_event_actions.creation.location_contribution'
        '.processors.duplicate_submission_processor.connection'
    )
    def test_advisory_lock_is_not_acquired_for_non_slc_source(
        self, mock_connection
    ):
        api_input_data = {
            **self.base_input_data,
            'source': ModerationEvent.Source.API.value,
        }
        self._submit(self.contributor, api_input_data)

        mock_connection.cursor.assert_not_called()

    def test_identical_resubmission_within_window_is_flagged(self):
        first_result = self._submit(self.contributor, self.base_input_data)
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)

        second_result = self._submit(self.contributor, self.base_input_data)

        self.assertEqual(second_result.status_code, status.HTTP_409_CONFLICT)
        self.assertIsNone(second_result.moderation_event)
        self.assertIn('duplicate_of', second_result.errors)
        self.assertEqual(
            second_result.errors['duplicate_of']['moderation_id'],
            str(first_result.moderation_event.uuid)
        )
        self.assertEqual(
            second_result.errors['duplicate_of']['name'],
            'Blue Horizon Facility'
        )
        self.assertEqual(
            second_result.errors['duplicate_of']['country'], 'US'
        )
        self.assertEqual(
            second_result.errors['duplicate_of']
            ['duplicate_check_window_minutes'],
            DUPLICATE_CHECK_WINDOW_MINUTES
        )

    def test_near_duplicate_name_typo_is_flagged(self):
        first_result = self._submit(self.contributor, self.base_input_data)
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)

        typo_input_data = {
            **self.base_input_data,
            'name': 'Blue Horizon Facilty',
        }
        second_result = self._submit(self.contributor, typo_input_data)

        self.assertEqual(second_result.status_code, status.HTTP_409_CONFLICT)
        self.assertIsNone(second_result.moderation_event)

    def test_different_unit_number_in_name_is_not_flagged(self):
        first_unit_data = {
            **self.base_input_data,
            'name': 'Blue Horizon Facility Unit 1',
        }
        first_result = self._submit(self.contributor, first_unit_data)
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)

        # Same address, and the name as a whole is >0.9 similar (single-digit
        # change), but it's a different unit at the same complex, not a typo
        # of the same unit.
        second_unit_data = {
            **self.base_input_data,
            'name': 'Blue Horizon Facility Unit 2',
        }
        second_result = self._submit(self.contributor, second_unit_data)

        self.assertEqual(second_result.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNotNone(second_result.moderation_event)

    def test_same_unit_number_in_name_is_still_flagged(self):
        first_unit_data = {
            **self.base_input_data,
            'name': 'Blue Horizon Facility Unit 1',
        }
        first_result = self._submit(self.contributor, first_unit_data)
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)

        # Same unit number, only a typo elsewhere in the name.
        typo_unit_data = {
            **self.base_input_data,
            'name': 'Blue Horizon Facilty Unit 1',
        }
        second_result = self._submit(self.contributor, typo_unit_data)

        self.assertEqual(second_result.status_code, status.HTTP_409_CONFLICT)
        self.assertIsNone(second_result.moderation_event)

    def test_different_street_number_is_not_flagged_despite_high_similarity(
        self
    ):
        first_result = self._submit(self.contributor, self.base_input_data)
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)

        # Same name, and the address string as a whole is >0.9 similar
        # (single-digit change), but it's the building next door, not a typo
        # of the same address.
        next_door_data = {
            **self.base_input_data,
            'address': '992 Spring Garden St., Philadelphia PA 19123',
        }
        second_result = self._submit(self.contributor, next_door_data)

        self.assertEqual(second_result.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNotNone(second_result.moderation_event)

    def test_different_suite_number_is_not_flagged_despite_same_street_number(
        self
    ):
        first_suite_data = {
            **self.base_input_data,
            'address': (
                '990 Spring Garden St. Suite 200, Philadelphia PA 19123'
            ),
        }
        first_result = self._submit(self.contributor, first_suite_data)
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)

        # Same leading street number, but a different suite in the same
        # building - the address as a whole is still >0.9 similar.
        second_suite_data = {
            **self.base_input_data,
            'address': (
                '990 Spring Garden St. Suite 300, Philadelphia PA 19123'
            ),
        }
        second_result = self._submit(self.contributor, second_suite_data)

        self.assertEqual(second_result.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNotNone(second_result.moderation_event)

    def test_punctuation_only_address_difference_is_still_flagged(self):
        first_result = self._submit(self.contributor, self.base_input_data)
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)

        # Same leading street number, only punctuation/formatting differs.
        reformatted_address_data = {
            **self.base_input_data,
            'address': '990 Spring Garden St, Philadelphia, PA 19123',
        }
        second_result = self._submit(
            self.contributor, reformatted_address_data
        )

        self.assertEqual(second_result.status_code, status.HTTP_409_CONFLICT)
        self.assertIsNone(second_result.moderation_event)

    def test_different_country_is_not_flagged(self):
        first_result = self._submit(self.contributor, self.base_input_data)
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)

        different_country_data = {
            **self.base_input_data,
            'country': 'CA',
        }
        second_result = self._submit(self.contributor, different_country_data)

        self.assertEqual(second_result.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNotNone(second_result.moderation_event)

    def test_clearly_different_name_and_address_is_not_flagged(self):
        first_result = self._submit(self.contributor, self.base_input_data)
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)

        different_location_data = {
            **self.base_input_data,
            'name': 'Green Valley Warehouse',
            'address': '42 Ocean Drive, Miami FL 33139',
        }
        second_result = self._submit(self.contributor, different_location_data)

        self.assertEqual(second_result.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNotNone(second_result.moderation_event)

    def test_other_contributors_submission_is_not_flagged(self):
        first_result = self._submit(self.contributor, self.base_input_data)
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)

        second_result = self._submit(
            self.other_contributor, self.base_input_data
        )

        self.assertEqual(second_result.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNotNone(second_result.moderation_event)

    def test_rejected_submission_is_not_flagged(self):
        first_result = self._submit(self.contributor, self.base_input_data)
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)
        self._reject_most_recent_event(self.contributor)

        second_result = self._submit(self.contributor, self.base_input_data)

        self.assertEqual(second_result.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNotNone(second_result.moderation_event)

    def test_submission_within_extended_window_is_still_flagged(self):
        first_result = self._submit(self.contributor, self.base_input_data)
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)
        # Still within the 30-minute window (covers auto-approval lag plus
        # the Logstash reindex lag), unlike the old 15-minute window.
        self._age_most_recent_event(self.contributor, minutes=20)

        second_result = self._submit(self.contributor, self.base_input_data)

        self.assertEqual(second_result.status_code, status.HTTP_409_CONFLICT)
        self.assertIsNone(second_result.moderation_event)

    def test_submission_outside_time_window_is_not_flagged(self):
        first_result = self._submit(self.contributor, self.base_input_data)
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)
        self._age_most_recent_event(self.contributor, minutes=35)

        second_result = self._submit(self.contributor, self.base_input_data)

        self.assertEqual(second_result.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNotNone(second_result.moderation_event)

    def test_duplicate_override_bypasses_the_check(self):
        first_result = self._submit(self.contributor, self.base_input_data)
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)

        second_result = self._submit(
            self.contributor, self.base_input_data, duplicate_override=True
        )

        self.assertEqual(second_result.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNotNone(second_result.moderation_event)
        # duplicate_override is request-processing metadata (arrives as a
        # query parameter, not part of the submitted location data), so it
        # must never appear in ContriCleaner's cleaned output.
        cleaned_data = second_result.moderation_event.cleaned_data
        self.assertNotIn('duplicate_override', cleaned_data['raw_json'])
        self.assertNotIn('duplicate_override', cleaned_data['fields'])

    def test_api_submission_after_slc_submission_is_not_flagged(self):
        first_result = self._submit(self.contributor, self.base_input_data)
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)

        api_input_data = {
            **self.base_input_data,
            'source': ModerationEvent.Source.API.value,
        }
        second_result = self._submit(self.contributor, api_input_data)

        # Confirm the duplicate check itself never triggers for non-SLC
        # sources, even though an identical SLC CREATE submission exists.
        self.assertEqual(
            second_result.status_code, status.HTTP_202_ACCEPTED
        )
        self.assertIsNotNone(second_result.moderation_event)

    def _create_existing_facility(self, name=None):
        facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='New List Test'
        )
        source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=facility_list,
            contributor=self.contributor
        )
        list_item = FacilityListItem.objects.create(
            name=name or self.base_input_data['name'],
            address=self.base_input_data['address'],
            country_code=self.base_input_data['country'],
            sector=['Apparel'],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source
        )
        return Facility.objects.create(
            name=list_item.name,
            address=list_item.address,
            country_code=list_item.country_code,
            location=Point(0, 0),
            created_from=list_item
        )

    def _submit_update(
        self, contributor, facility, input_data=None,
        duplicate_override=False,
    ):
        event_dto = CreateModerationEventDTO(
            contributor=contributor,
            raw_data=input_data or self.base_input_data,
            request_type=ModerationEvent.RequestType.UPDATE.value,
            os=facility,
            duplicate_override=duplicate_override,
        )
        return self.moderation_event_creator.perform_event_creation(
            event_dto
        )

    def test_update_after_create_of_same_location_is_flagged(self):
        # The fuzzy name/address match applies across request types: a
        # CREATE followed minutes later by an UPDATE for the same
        # name/address is the same location submitted twice.
        first_result = self._submit(self.contributor, self.base_input_data)
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)

        existing_facility = self._create_existing_facility()
        result = self._submit_update(self.contributor, existing_facility)

        self.assertEqual(result.status_code, status.HTTP_409_CONFLICT)
        self.assertIsNone(result.moderation_event)
        self.assertEqual(
            result.errors['duplicate_of']['moderation_id'],
            str(first_result.moderation_event.uuid)
        )
        self.assertIsNone(result.errors['duplicate_of']['os_id'])

    def test_create_after_update_of_same_location_is_flagged(self):
        existing_facility = self._create_existing_facility()
        first_result = self._submit_update(
            self.contributor, existing_facility
        )
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)

        result = self._submit(self.contributor, self.base_input_data)

        self.assertEqual(result.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            result.errors['duplicate_of']['os_id'], existing_facility.id
        )

    def test_first_update_for_a_location_is_not_flagged(self):
        existing_facility = self._create_existing_facility()

        result = self._submit_update(self.contributor, existing_facility)

        self.assertEqual(result.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNotNone(result.moderation_event)

    def test_repeat_update_for_same_location_within_window_is_flagged(
        self
    ):
        existing_facility = self._create_existing_facility()
        first_result = self._submit_update(
            self.contributor, existing_facility
        )
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)

        second_result = self._submit_update(
            self.contributor, existing_facility
        )

        self.assertEqual(second_result.status_code, status.HTTP_409_CONFLICT)
        self.assertIsNone(second_result.moderation_event)
        duplicate_of = second_result.errors['duplicate_of']
        self.assertEqual(
            duplicate_of['moderation_id'],
            str(first_result.moderation_event.uuid)
        )
        self.assertEqual(duplicate_of['os_id'], existing_facility.id)
        self.assertEqual(
            duplicate_of['duplicate_check_window_minutes'],
            DUPLICATE_CHECK_WINDOW_MINUTES
        )

    def test_repeat_update_with_clearly_different_data_is_not_flagged(
        self
    ):
        # The match is on what the contributor submitted, not on the
        # target os_id: an UPDATE event can end up attached to a different
        # production location than the one the contributor picked, so the
        # os_id isn't a reliable identity for the submission.
        existing_facility = self._create_existing_facility()
        first_result = self._submit_update(
            self.contributor, existing_facility
        )
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)

        second_result = self._submit_update(
            self.contributor,
            existing_facility,
            {
                **self.base_input_data,
                'name': 'Completely Different Name',
                'address': '12 Other Road, Springfield IL 62701',
            },
        )

        self.assertEqual(second_result.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNotNone(second_result.moderation_event)

    def test_similar_update_for_a_different_os_id_is_still_flagged(self):
        # Same name/address sent against two different os_ids in quick
        # succession is treated as the same submission twice (the
        # contributor may have picked the wrong search result the first
        # time); duplicate_override is available if both were intended.
        first_facility = self._create_existing_facility()
        second_facility = self._create_existing_facility()
        first_result = self._submit_update(self.contributor, first_facility)
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)

        second_result = self._submit_update(
            self.contributor, second_facility
        )

        self.assertEqual(second_result.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            second_result.errors['duplicate_of']['os_id'],
            first_facility.id
        )

    def test_other_contributors_update_is_not_flagged(self):
        existing_facility = self._create_existing_facility()
        first_result = self._submit_update(
            self.contributor, existing_facility
        )
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)

        second_result = self._submit_update(
            self.other_contributor, existing_facility
        )

        self.assertEqual(second_result.status_code, status.HTTP_202_ACCEPTED)

    def test_rejected_update_is_not_flagged(self):
        existing_facility = self._create_existing_facility()
        self._submit_update(self.contributor, existing_facility)
        self._reject_most_recent_event(self.contributor)

        second_result = self._submit_update(
            self.contributor, existing_facility
        )

        self.assertEqual(second_result.status_code, status.HTTP_202_ACCEPTED)

    def test_update_outside_time_window_is_not_flagged(self):
        existing_facility = self._create_existing_facility()
        self._submit_update(self.contributor, existing_facility)
        self._age_most_recent_event(
            self.contributor, DUPLICATE_CHECK_WINDOW_MINUTES + 1
        )

        second_result = self._submit_update(
            self.contributor, existing_facility
        )

        self.assertEqual(second_result.status_code, status.HTTP_202_ACCEPTED)

    def test_duplicate_override_bypasses_the_check_for_update(self):
        existing_facility = self._create_existing_facility()
        first_result = self._submit_update(
            self.contributor, existing_facility
        )
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)

        second_result = self._submit_update(
            self.contributor, existing_facility, duplicate_override=True
        )

        self.assertEqual(second_result.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNotNone(second_result.moderation_event)
        self.assertEqual(
            ModerationEvent.objects.filter(
                contributor=self.contributor,
                request_type=ModerationEvent.RequestType.UPDATE.value,
            ).count(),
            2
        )

    def test_api_update_is_not_flagged(self):
        existing_facility = self._create_existing_facility()
        api_input_data = {
            **self.base_input_data,
            'source': ModerationEvent.Source.API.value,
        }
        first_result = self._submit_update(
            self.contributor, existing_facility, api_input_data
        )
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)

        second_result = self._submit_update(
            self.contributor, existing_facility, api_input_data
        )

        self.assertEqual(second_result.status_code, status.HTTP_202_ACCEPTED)

    def test_advisory_lock_is_acquired_for_update(self):
        existing_facility = self._create_existing_facility()
        with patch(
            'api.moderation_event_actions.creation.location_contribution'
            '.processors.duplicate_submission_processor.connection'
        ) as mock_connection:
            mock_connection.in_atomic_block = True
            mock_cursor = (
                mock_connection.cursor.return_value.__enter__.return_value
            )
            self._submit_update(self.contributor, existing_facility)

        mock_cursor.execute.assert_called_once_with(
            'SELECT pg_advisory_xact_lock(%s, %s)',
            [ADVISORY_LOCK_NAMESPACE, self.contributor.pk]
        )
