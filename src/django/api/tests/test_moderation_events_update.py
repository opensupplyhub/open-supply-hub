import json

from django.db.models.signals import post_save
from django.test import override_settings
from django.utils.timezone import now
from rest_framework.test import APITestCase

from api.models import (
    ModerationEvent,
    User,
    Contributor,
)
from api.signals import moderation_event_update_handler_for_opensearch


@override_settings(DEBUG=True)
class ModerationEventsUpdateTest(APITestCase):
    def setUp(self):
        super().setUp()

        post_save.disconnect(
            moderation_event_update_handler_for_opensearch,
            ModerationEvent
        )

        self.email = "test@example.com"
        self.password = "example123"
        self.user = User.objects.create(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="test contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.superemail = "admin@example.com"
        self.superpassword = "example123"
        self.superuser = User.objects.create_superuser(
            email=self.superemail,
            password=self.superpassword
        )

        self.moderation_event = ModerationEvent.objects.create(
            uuid='f65ec710-f7b9-4f50-b960-135a7ab24ee6',
            created_at=now(),
            updated_at=now(),
            request_type='UPDATE',
            raw_data={"name": "raw_name", "country_code": "UK"},
            cleaned_data={"name": "cleaned_name", "country_code": "UK"},
            geocode_result={"latitude": -53, "longitude": 142},
            status='PENDING',
            source='API',
            contributor=self.contributor,
        )

    def test_moderation_event_permission(self):
        self.client.login(
            email=self.email,
            password=self.password
        )
        response = self.client.patch(
            "/api/v1/moderation-events/{}/"
            .format("f65ec710-f7b9-4f50-b960-135a7ab24ee6"),
            data=json.dumps({"status": "APPROVED"}),
            content_type="application/json"
        )
        self.assertEqual(403, response.status_code)

        self.client.login(
            email=self.superemail,
            password=self.superpassword
        )
        response = self.client.patch(
            "/api/v1/moderation-events/{}/"
            .format("f65ec710-f7b9-4f50-b960-135a7ab24ee6"),
            data=json.dumps({"status": "APPROVED"}),
            content_type="application/json"
        )
        self.assertEqual(200, response.status_code)

    def test_moderation_event_not_found(self):
        self.client.login(
            email=self.superemail,
            password=self.superpassword
        )
        response = self.client.patch(
            "/api/v1/moderation-events/{}/"
            .format("f65ec710-f7b9-4f50-b960-135a7ab24ee1"),
            data=json.dumps({"status": "APPROVED"}),
            content_type="application/json"
        )

        self.assertEqual(404, response.status_code)

    def test_moderation_event_invalid_status(self):
        self.client.login(
            email=self.superemail,
            password=self.superpassword
        )
        response = self.client.patch(
            "/api/v1/moderation-events/{}/"
            .format("f65ec710-f7b9-4f50-b960-135a7ab24ee6"),
            data=json.dumps({"status": "NEW"}),
            content_type="application/json"
        )

        self.assertEqual(400, response.status_code)

    def test_moderation_event_status_changed_with_reason(self):
        self.client.login(
            email=self.superemail,
            password=self.superpassword
        )
        response = self.client.patch(
            "/api/v1/moderation-events/{}/"
            .format("f65ec710-f7b9-4f50-b960-135a7ab24ee6"),
            data=json.dumps({
                "status": "REJECTED",
                "action_reason_text_cleaned": "cleaned reason",
                "action_reason_text_raw": "raw reason"
            }),
            content_type="application/json"
        )

        self.assertEqual(200, response.status_code)
        self.moderation_event.refresh_from_db()
        self.assertEqual(self.moderation_event.status, "REJECTED")
        self.assertEqual(self.moderation_event.action_type, "REJECTED")
        self.assertEqual(
            self.moderation_event.action_perform_by.id,
            self.superuser.id
        )
        self.assertIsNotNone(self.moderation_event.status_change_date)
        self.assertEqual(
            self.moderation_event.action_reason_text_cleaned,
            "cleaned reason"
        )
        self.assertEqual(
            self.moderation_event.action_reason_text_raw,
            "raw reason"
        )