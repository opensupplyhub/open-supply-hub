from datetime import timedelta

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


class TestDuplicateSubmissionProcessor(APITestCase):
    def setUp(self):
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

    def _submit(self, contributor, input_data):
        event_dto = CreateModerationEventDTO(
            contributor=contributor,
            raw_data=input_data,
            request_type=ModerationEvent.RequestType.CREATE.value
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

        override_input_data = {
            **self.base_input_data,
            'duplicate_override': True,
        }
        second_result = self._submit(self.contributor, override_input_data)

        self.assertEqual(second_result.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNotNone(second_result.moderation_event)
        # The override flag must not leak into ContriCleaner's cleaned
        # output (raw_json/fields), even though it stays in raw_data as
        # literally submitted (matching how "source" is handled).
        cleaned_data = second_result.moderation_event.cleaned_data
        self.assertNotIn('duplicate_override', cleaned_data['raw_json'])
        self.assertNotIn('duplicate_override', cleaned_data['fields'])

    def test_update_request_type_is_never_flagged(self):
        first_result = self._submit(self.contributor, self.base_input_data)
        self.assertEqual(first_result.status_code, status.HTTP_202_ACCEPTED)

        facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='New List Test'
        )
        source = Source.objects.create(
            source_type=Source.LIST,
            facility_list=facility_list,
            contributor=self.contributor
        )
        list_item = FacilityListItem.objects.create(
            name=self.base_input_data['name'],
            address=self.base_input_data['address'],
            country_code=self.base_input_data['country'],
            sector=['Apparel'],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source
        )
        existing_facility = Facility.objects.create(
            name=list_item.name,
            address=list_item.address,
            country_code=list_item.country_code,
            location=Point(0, 0),
            created_from=list_item
        )

        event_dto = CreateModerationEventDTO(
            contributor=self.contributor,
            raw_data=self.base_input_data,
            request_type=ModerationEvent.RequestType.UPDATE.value,
            os=existing_facility,
        )
        result = self.moderation_event_creator.perform_event_creation(
            event_dto
        )

        # Confirm the duplicate check itself never triggers for UPDATE
        # requests, even though an identical CREATE submission exists.
        self.assertNotEqual(result.status_code, status.HTTP_409_CONFLICT)
