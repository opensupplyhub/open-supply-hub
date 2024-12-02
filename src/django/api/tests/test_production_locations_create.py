import json

from rest_framework.test import APITestCase
from django.urls import reverse
from allauth.account.models import EmailAddress

from api.models.moderation_event import ModerationEvent
from api.models.contributor.contributor import Contributor
from api.models.user import User
from api.views.v1.url_names import URLNames


class TestProductionLocationsCreate(APITestCase):
    def setUp(self):
        self.url = reverse(URLNames.PRODUCTION_LOCATIONS + '-list')

        user_email = "test@example.com"
        user_password = "example123"
        self.user = User.objects.create(email=user_email)
        self.user.set_password(user_password)
        self.user.save()

        EmailAddress.objects.create(
            user=self.user, email=user_email, verified=True, primary=True
        )

        Contributor.objects.create(
            admin=self.user,
            name="test contributor 1",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.login(user_email, user_password)

    def login(self, email: str, password: str) -> None:
        self.client.logout()
        self.client.login(email=email, password=password)

    def test_only_registered_and_confirmed_has_access(self):
        expected_response_body = {
            'detail': (
                'User must be registered and have confirmed their email to '
                'access.'
            )
        }

        saved_email_address = EmailAddress.objects.get_primary(self.user)
        # Purposely make the email address unverified to trigger a permission
        # error.
        saved_email_address.verified = False
        saved_email_address.save()

        response = self.client.post(self.url, content_type="application/json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            json.loads(response.content),
            expected_response_body
        )

    def test_default_throttling_is_applied(self):
        valid_request_body = json.dumps({
            "name": "Germany",
            'address': "Random street, 124",
            "country": "DE"
        })

        # Simulate 30 requests.
        for _ in range(30):
            response = self.client.post(
                self.url,
                valid_request_body,
                content_type="application/json"
            )
            self.assertEqual(response.status_code, 202)

            response_body_dict = json.loads(response.content)
            response_moderation_id = response_body_dict.get('moderation_id')
            moderation_event = ModerationEvent.objects.get(
                pk=response_moderation_id
            )

            self.assertIsNotNone(moderation_event)
            self.assertEqual(moderation_event.status, 'PENDING')

        # Now simulate the 31st request, which should be throttled.
        response = self.client.post(
            self.url,
            valid_request_body,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 429)
