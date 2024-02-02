from unittest.mock import Mock, patch

from api.constants import FacilityHistoryActions
from api.models import (
    Contributor,
    ContributorWebhook,
    Event,
    Facility,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase

from django.contrib.gis.geos import Point
from django.core.management import call_command
from django.utils import timezone


class NotificationTest(FacilityAPITestCaseBase):
    def notify(self, *args, **kwargs):
        call_command(
            "notify",
            *args,
            **kwargs,
        )

    def create_another_facility(self):
        user_email = "test2@example.com"
        user_password = "example123"
        user = User.objects.create(email=user_email)
        user.set_password(user_password)
        user.save()

        contributor = Contributor.objects.create(
            admin=user,
            name="test contributor 2",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        contributor.save()

        list = FacilityList.objects.create(
            header="header", file_name="two", name="Second List"
        )
        list.save()

        source = Source.objects.create(
            facility_list=list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=contributor,
        )
        source.save()

        list_item = FacilityListItem.objects.create(
            name="Cat",
            address="Dog",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(10, 10),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )

        facility = Facility.objects.create(
            name="Cat",
            address="Dog",
            country_code="US",
            location=Point(10, 10),
            created_from=list_item,
        )
        facility.save()

        match = FacilityMatch.objects.create(
            status=FacilityMatch.AUTOMATIC,
            facility=facility,
            facility_list_item=list_item,
            confidence=0.85,
            results="",
        )
        match.save()

        list_item.facility = facility
        list_item.save()

        return facility

    def test_notifications_with_no_event_match(self):
        self.assertRaises(Event.DoesNotExist, self.notify, event_id="2")

    @patch("requests.post")
    def test_notifications_with_all_facility_matches(self, mock_post):
        mock_post.return_value = Mock(ok=True, status_code=200)

        facility = self.create_another_facility()

        contributor_webhook = ContributorWebhook(
            contributor=self.contributor,
            notification_type=ContributorWebhook.ALL_FACILITIES,
        )
        contributor_webhook.save()

        e = Event(
            content_object=facility,
            event_type=FacilityHistoryActions.UPDATE,
            event_time=timezone.now(),
            event_details={},
        )
        e.save()

        with self.assertLogs() as cm:
            self.notify(event_id=e.id)
            self.assertEqual(1, len(cm.output))
            self.assertIn("ContributorWebhook DELIVERED", cm.output[0])

    @patch("requests.post")
    def test_notifications_with_associated_facility_matches(self, mock_post):
        mock_post.return_value = Mock(ok=True, status_code=200)

        contributor_webhook = ContributorWebhook(
            contributor=self.contributor,
            notification_type=ContributorWebhook.ASSOCIATED,
        )
        contributor_webhook.save()

        e = Event(
            content_object=self.facility,
            event_type=FacilityHistoryActions.UPDATE,
            event_time=timezone.now(),
            event_details={},
        )
        e.save()

        with self.assertLogs() as cm:
            self.notify(event_id=e.id)
            self.assertEqual(1, len(cm.output))
            self.assertIn("ContributorWebhook DELIVERED", cm.output[0])

    @patch("requests.post")
    def test_notifications_with_no_associated_facility_matches(
        self, mock_post
    ):
        mock_post.return_value = Mock(ok=True, status_code=200)

        facility = self.create_another_facility()

        contributor_webhook = ContributorWebhook(
            contributor=self.contributor,
            notification_type=ContributorWebhook.ASSOCIATED,
        )
        contributor_webhook.save()

        e = Event(
            content_object=facility,
            event_type=FacilityHistoryActions.UPDATE,
            event_time=timezone.now(),
            event_details={},
        )
        e.save()

        with self.assertLogs() as cm:
            self.notify(event_id=e.id)
            self.assertEqual(1, len(cm.output))
            self.assertIn("ContributorWebhook SKIPPED", cm.output[0])

    @patch("requests.post")
    def test_bad_response_leads_to_failed_status(self, mock_post):
        mock_post.return_value = Mock(ok=True, status_code=500)

        contributor_webhook = ContributorWebhook(
            contributor=self.contributor,
            notification_type=ContributorWebhook.ALL_FACILITIES,
        )
        contributor_webhook.save()

        e = Event(
            content_object=self.facility,
            event_type=FacilityHistoryActions.UPDATE,
            event_time=timezone.now(),
            event_details={},
        )
        e.save()

        with self.assertLogs() as cm:
            self.notify(event_id=e.id)
            self.assertEqual(1, len(cm.output))
            self.assertIn("ContributorWebhook FAILED", cm.output[0])

    @patch("requests.post")
    def test_one_failure_doesnt_stop_execution(self, mock_post):
        mock_post.side_effect = [
            Mock(ok=True, status_code=500),
            Mock(ok=True, status_code=200),
        ]

        ContributorWebhook.objects.create(
            contributor=self.contributor,
            notification_type=ContributorWebhook.ALL_FACILITIES,
        )
        ContributorWebhook.objects.create(
            contributor=self.contributor,
            notification_type=ContributorWebhook.ALL_FACILITIES,
        )

        e = Event(
            content_object=self.facility,
            event_type=FacilityHistoryActions.UPDATE,
            event_time=timezone.now(),
            event_details={},
        )
        e.save()

        with self.assertLogs() as cm:
            self.notify(event_id=e.id)
            self.assertEqual(2, len(cm.output))
            self.assertIn("ContributorWebhook FAILED", cm.output[0])
            self.assertIn("ContributorWebhook DELIVERED", cm.output[1])
