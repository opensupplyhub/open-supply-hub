from django.http import Http404
from django.core import signing
from allauth.account.models import EmailAddress
from allauth.account import app_settings as allauth_settings
from rest_framework import status
from rest_framework.response import Response
from dj_rest_auth.registration.views import (
    VerifyEmailView as BaseVerifyEmailView,
)

ALREADY_CONFIRMED_CODE = 'already_confirmed'

SECONDS_PER_DAY = 60 * 60 * 24


class VerifyEmailView(BaseVerifyEmailView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        key = serializer.validated_data['key']
        self.kwargs['key'] = key
        try:
            confirmation = self.get_object()
        except Http404:
            try:
                # allauth signs confirmation keys with the same expiry window;
                # max_age must match so we can decode the pk and distinguish
                # "already verified" from expired or invalid keys.
                max_age = (
                    SECONDS_PER_DAY
                    * allauth_settings.EMAIL_CONFIRMATION_EXPIRE_DAYS
                )
                pk = signing.loads(
                    key, max_age=max_age, salt=allauth_settings.SALT
                )
                if EmailAddress.objects.filter(pk=pk, verified=True).exists():
                    return Response(
                        {'detail': ALREADY_CONFIRMED_CODE},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except (signing.SignatureExpired, signing.BadSignature):
                pass
            raise
        confirmation.confirm(self.request)
        return Response({'detail': 'ok'}, status=status.HTTP_200_OK)
