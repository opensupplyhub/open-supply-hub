import json
from django.test import override_settings
from api.models import (
    ModerationEvent,
    User,
    Contributor
)
from django.utils.timezone import now
from rest_framework.test import APITestCase


@override_settings(DEBUG=True)
class ModerationEventsUpdateTest(APITestCase):
    def setUp(self):
        super().setUp()

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
            contributor=self.contributor
        )

    def test_moderation_event_permission(self):
        self.client.login(
            email=self.email,
            password=self.password
        )
        response = self.client.patch(
            "/api/v1/moderation-events/{}/"
            .format("f65ec710-f7b9-4f50-b960-135a7ab24ee6"),
            data=json.dumps({"status": "ACCEPTED"}),
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
            data=json.dumps({"status": "ACCEPTED"}),
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
            data=json.dumps({"status": "ACCEPTED"}),
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

    def test_moderation_event_status_changed(self):
        self.client.login(
            email=self.superemail,
            password=self.superpassword
        )
        response = self.client.patch(
            "/api/v1/moderation-events/{}/"
            .format("f65ec710-f7b9-4f50-b960-135a7ab24ee6"),
            data=json.dumps({"status": "ACCEPTED"}),
            content_type="application/json"
        )

        self.assertEqual(200, response.status_code)
        self.moderation_event.refresh_from_db()
        self.assertEqual(self.moderation_event.status, "ACCEPTED")
        self.assertIsNotNone(self.moderation_event.status_change_date)
