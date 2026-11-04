from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.models.announcement_banner import AnnouncementBanner


@api_view(['GET'])
@permission_classes((AllowAny,))
def announcement_banner(_):
    banner = AnnouncementBanner.objects.first()
    is_active = bool(banner and banner.is_active and banner.content)
    return Response({
        'is_active': is_active,
        'content': banner.content if is_active else '',
    })
