from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from django.urls import reverse
from api.models import (
    User,
    Contributor,
    RequestLog,
    )
from django.db import IntegrityError


class UserEmailLowerTestCase(APITestCase):
    def setUp(self):
        self.email = 'TEST@example.com'
        self.lower_email = 'test@example.com'
        self.password = 'password'
        self.name = 'Test User'
        self.user = User(email=self.email)
        self.user.set_password(self.password)
        self.user.save()
        Contributor.objects.create(name=self.name, admin=self.user)

        self.accented_email = 'Étienne@example.com'
        self.lower_accented_email = 'étienne@example.com'
        self.password_for_accented_email = 'password_two'
        self.name_for_accented_email = 'Test User Two'
        self.user_with_accented_email = User(email=self.accented_email)
        self.user_with_accented_email.set_password(
            self.password_for_accented_email)
        self.user_with_accented_email.save()
        Contributor.objects.create(name=self.name_for_accented_email,
                                   admin=self.user_with_accented_email)

    def test_email_case(self, **kwargs):
        token = Token.objects.create(user=self.user)
        path = reverse('facility-list-list')
        response = self.client.get(
            path,
            HTTP_AUTHORIZATION='Token {0}'.format(token))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, RequestLog.objects.filter(user=self.user).count())

        user = User.objects.get(email__iexact=self.email)
        self.assertEqual(self.lower_email, user.email)

    def test_lower_email_with_accented_characters(self, **kwargs):
        user = User.objects.get(email__iexact=self.accented_email)
        self.assertEqual(self.lower_accented_email, user.email)

    def test_django_not_allow_create_duplicates(self, **kwargs):
        with self.assertRaises(IntegrityError):
            User.objects.create(email=self.lower_accented_email)
