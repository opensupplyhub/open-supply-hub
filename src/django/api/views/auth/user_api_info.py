from api.serializers.user_api_info_serializer import UserApiInfoSerializer
from rest_framework.response import Response
from rest_framework.views import APIView

from ...permissions import IsRegisteredAndConfirmed


class UserAPIInfo(APIView):
    permission_classes = (IsRegisteredAndConfirmed,)

    def get(self, request, uid=None):
        data = UserApiInfoSerializer(uid).data

        return Response(data)
