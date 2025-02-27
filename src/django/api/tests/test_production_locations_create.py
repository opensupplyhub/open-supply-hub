import json
import logging
import time

logger = logging.getLogger(__name__)

from unittest.mock import Mock, patch
from rest_framework.test import APITestCase
from django.urls import reverse
from allauth.account.models import EmailAddress
from waffle.testutils import override_switch
from rest_framework import status

from api.models.moderation_event import ModerationEvent
from api.models.contributor.contributor import Contributor
from api.models.user import User
from api.views.v1.url_names import URLNames
from api.tests.test_data import geocoding_data


class TestProductionLocationsCreate(APITestCase):
    def setUp(self):
        self.url = reverse(URLNames.PRODUCTION_LOCATIONS + '-list')
        self.common_valid_req_body = json.dumps({
            'name': 'Blue Horizon Facility',
            'address': '990 Spring Garden St., Philadelphia PA 19123',
            'country': 'US'
        })

        user_email = 'test@example.com'
        user_password = 'example123'
        self.user = User.objects.create(email=user_email)
        self.user.set_password(user_password)
        self.user.save()

        EmailAddress.objects.create(
            user=self.user, email=user_email, verified=True, primary=True
        )

        Contributor.objects.create(
            admin=self.user,
            name='test contributor 1',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.login(user_email, user_password)

    def login(self, email: str, password: str) -> None:
        self.client.logout()
        self.client.login(email=email, password=password)

    time.sleep(5)
    @patch('api.geocoding.requests.get')
    def test_moderation_event_created_with_valid_parent_company(
            self,
            mock_get):
        mock_get.return_value = Mock(ok=True, status_code=200)
        mock_get.return_value.json.return_value = geocoding_data

        special_characters = '&@, \' " #()'
        numbers = '1234567890'
        multi_lang_letters = '贾建龙ÖrmeTİCіїъыParent_companyการผลิตהפָקָהผลิต'
        valid_parent_company = special_characters + numbers + multi_lang_letters

        valid_req_body = json.dumps({
            'source': 'SLC',
            'name': 'Blue Horizon Facility',
            'address': '990 Spring Garden St., Philadelphia PA 19123',
            'country': 'US',
            'parent_company': valid_parent_company
        })

        response = self.client.post(
            self.url,
            valid_req_body,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 202)

        response_body_dict = json.loads(response.content)
        logger.info(f'@@@@ expect VALID response but got: {response_body_dict}')
        response_moderation_id = response_body_dict.get('moderation_id')
        moderation_event = ModerationEvent.objects.get(
            pk=response_moderation_id
        )
        stringified_created_at = moderation_event.created_at.strftime(
            '%Y-%m-%dT%H:%M:%S.%f'
        ) + 'Z'

        self.assertEqual(
            response_body_dict.get('moderation_status'),
            'PENDING'
        )
        self.assertEqual(
            response_body_dict.get('created_at'),
            stringified_created_at
        )
        self.assertEqual(
            response_moderation_id,
            str(moderation_event.uuid)
        )
        self.assertIn("cleaned_data", response_body_dict)
        parent_company = response_body_dict.get('cleaned_data', {}).get('fields', {}).get('parent_company')
        self.assertEqual(len(response_body_dict), 4)
        self.assertEqual(parent_company, valid_parent_company)
