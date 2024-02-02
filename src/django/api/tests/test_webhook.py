from api.constants import FacilityHistoryActions
from api.models import (
    Contributor,
    ContributorWebhook,
    Event,
    Facility,
    FacilityListItem,
    Source,
    User,
)
from rest_framework.test import APITestCase

from django.contrib.gis.geos import Point
from django.utils import timezone


class WebhookTest(APITestCase):
    def test_log_event(self):
        user = User.objects.create(email="test@test.com")
        c = Contributor.objects.create(
            admin=user,
            name="TESTING",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        source = Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=c,
        )

        list_item = FacilityListItem.objects.create(
            name="Item",
            address="Address",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )

        facility = Facility.objects.create(
            name="Towel Factory 42",
            address="42 Dolphin St",
            country_code="US",
            created_from=list_item,
            location=Point(0, 0),
        )
        event = Event(
            content_object=facility,
            event_type=FacilityHistoryActions.UPDATE,
            event_time=timezone.now(),
            event_details={},
        )
        webhook = ContributorWebhook(contributor=c)
        with self.assertLogs() as cm:
            webhook.log_event(event, "DELIVERED")
            self.assertEqual(1, len(cm.output))
            self.assertIn("ContributorWebhook DELIVERED", cm.output[0])
