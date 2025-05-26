from allauth.account.models import EmailAddress
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_auth.views import LoginView
from django.contrib.auth import authenticate, login

from ...serializers.user.user_serializer import UserSerializer


class LoginToOARClient(LoginView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        if email is None or password is None:
            raise AuthenticationFailed('Email and password are required')

        normalized_email = email.lower()
        user = authenticate(email=normalized_email, password=password)

        if user is None:
            raise AuthenticationFailed(
                'Unable to login with those credentials')

        login(request, user)

        if not request.user.did_register_and_confirm_email:
            # Mimic the behavior of django-allauth and resend the confirmation
            # email if an unconfirmed user tries to log in.
            email_address = EmailAddress.objects.get(email=normalized_email)
            email_address.send_confirmation(request)

            raise AuthenticationFailed(
                'Your account is not verified. '
                'Check your email for a confirmation link.'
            )

        serialized_data = UserSerializer(user).data

        return Response(serialized_data)

    def get(self, request, *args, **kwargs):
        if not request.user.is_active:
            raise AuthenticationFailed('Unable to sign in')
        if not request.user.did_register_and_confirm_email:
            raise AuthenticationFailed('Unable to sign in')

        return Response(UserSerializer(request.user).data)
