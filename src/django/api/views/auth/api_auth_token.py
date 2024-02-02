from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from ...permissions import IsRegisteredAndConfirmed


class APIAuthToken(ObtainAuthToken):
    permission_classes = (IsRegisteredAndConfirmed,)

    def get(self, request, *args, **kwargs):
        try:
            token = Token.objects.get(user=request.user)

            token_data = {
                'token': token.key,
                'created': token.created.isoformat(),
            }

            return Response(token_data)
        except Token.DoesNotExist as exc:
            raise NotFound() from exc

    def post(self, request, *args, **kwargs):
        token, _ = Token.objects.get_or_create(user=request.user)

        token_data = {
            'token': token.key,
            'created': token.created.isoformat(),
        }

        return Response(token_data)

    def delete(self, request, *args, **kwargs):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Token.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)
