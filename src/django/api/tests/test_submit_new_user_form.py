from unittest.mock import patch
from django.test import Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.serializers.user.user_serializer import UserSerializer


class SubmitNewUserFormTest(APITestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.signup_url = reverse('submit_new_user_form')
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'testpass123',
            'name': 'Test User',
            'description': 'A test description',
            'contributor_type': 'Civil Society Organization',
            'other_contributor_type': '',
            'website': '',
            'has_agreed_to_terms_of_service': True,
            'should_receive_newsletter': False,
        }

        # Monkey-patch to avoid error by assigning M2M fields
        # in validate for tests
        orig_validate = UserSerializer.validate

        def patched_validate(self, data):
            data = data.copy()
            data.pop('groups', None)
            data.pop('user_permissions', None) 
            return orig_validate(self, data)

        UserSerializer.validate = patched_validate

    @patch('api.views.user.submit_new_user_form.complete_signup')
    def test_signup_compare_csrf_token(self, mock_complete_signup):
        # Manually simulate CSRF token generation
        # inside mocked function
        def fake_complete_signup(request, user, *args, **kwargs):
            from django.middleware.csrf import rotate_token
            rotate_token(request)

        mock_complete_signup.side_effect = fake_complete_signup

        response = self.client.post(
            self.signup_url,
            data=self.user_data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        csrf_cookie = response.client.cookies.get('csrftoken')
        csrf_token_data = response.data['csrfToken']

        self.assertIsNotNone(csrf_cookie)
        self.assertEqual(csrf_cookie.value, csrf_token_data)
