from rest_framework import status
from rest_framework.response import Response
from dj_rest_auth.views import LogoutView
from django.contrib.auth import logout

from ...serializers.user.user_serializer import UserSerializer


class LogoutOfOARClient(LogoutView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        logout(request)

        return Response(status=status.HTTP_204_NO_CONTENT)
