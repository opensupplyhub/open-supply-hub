from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from api.serializers.user_api_info_serializer import UserApiInfoSerializer
from ...permissions import IsRegisteredAndConfirmed
from api.models.contributor.contributor import Contributor


class UserAPIInfo(APIView):
    permission_classes = (IsRegisteredAndConfirmed,)

    def get(self, request, uid=None):
        if not request.user.has_groups:
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            contributor_id = Contributor.objects.get(admin_id=uid).id
        except Contributor.DoesNotExist:
            raise ValidationError((
                    f"User with id = {uid} doesn't has a contributor"
            ))

        data = UserApiInfoSerializer(uid, contributor_id).data

        return Response(data)
