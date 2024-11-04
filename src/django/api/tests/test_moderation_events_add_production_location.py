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
class ModerationEventsAddProductionLocationTest(APITestCase):
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

        self.superuser_email = "admin@example.com"
        self.superuser_password = "example123"
        self.superuser = User.objects.create_superuser(
            email=self.superuser_email,
            password=self.superuser_password
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

    def test_permission_denied(self):
        self.client.login(
            email=self.email,
            password=self.password
        )
        response = self.client.post(
            "/api/v1/moderation-events/{}/add-production-location/"
            .format("f65ec710-f7b9-4f50-b960-135a7ab24ee6"),
            data=json.dumps({}),
            content_type="application/json"
        )
        self.assertEqual(403, response.status_code)

    def test_invalid_uuid_format(self):
        self.client.login(
            email=self.superuser_email,
            password=self.superuser_password
        )
        response = self.client.post(
            "/api/v1/moderation-events/{}/add-production-location/"
            .format("invalid_uuid"),
            data=json.dumps({}),
            content_type="application/json"
        )
        self.assertEqual(400, response.status_code)

    def test_moderation_event_not_found(self):
        self.client.login(
            email=self.superuser_email,
            password=self.superuser_password
        )
        response = self.client.post(
            "/api/v1/moderation-events/{}/add-production-location/"
            .format("f65ec710-f7b9-4f50-b960-135a7ab24ee7"),
            data=json.dumps({}),
            content_type="application/json"
        )
        self.assertEqual(404, response.status_code)

    def test_moderation_event_not_pending(self):
        self.moderation_event.status = 'RESOLVED'
        self.moderation_event.save()

        self.client.login(
            email=self.superuser_email,
            password=self.superuser_password
        )
        response = self.client.post(
            "/api/v1/moderation-events/{}/add-production-location/"
            .format("f65ec710-f7b9-4f50-b960-135a7ab24ee6"),
            data=json.dumps({}),
            content_type="application/json"
        )
        self.assertEqual(400, response.status_code)
