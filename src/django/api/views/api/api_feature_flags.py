from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from waffle import switch_is_active
from waffle.models import Switch


@api_view(['GET'])
@permission_classes((AllowAny,))
def api_feature_flags(_):
    response_data = {
        s.name: switch_is_active(s.name) for s in Switch.objects.all()
    }
    return Response(response_data)
