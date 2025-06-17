from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

from api.constants import LogDownloadQueryParams
from api.models.download_log import DownloadLog
from api.permissions import IsRegisteredAndConfirmed
from api.serializers.log_download_query_params import (
    LogDownloadQueryParamsSerializer
)


@swagger_auto_schema(methods=['POST'], auto_schema=None)
@api_view(['POST'])
@permission_classes([IsRegisteredAndConfirmed])
def log_download(request):
    params = LogDownloadQueryParamsSerializer(data=request.query_params)
    if not params.is_valid():
        raise ValidationError(params.errors)

    path = request.query_params.get(LogDownloadQueryParams.PATH)
    record_count = request.query_params.get(
        LogDownloadQueryParams.RECORD_COUNT
    )
    DownloadLog.objects.create(
        user=request.user,
        path=path,
        record_count=record_count,
    )
    return Response(status=HTTP_204_NO_CONTENT)
