from django.http import QueryDict
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from api.views.v1.utils import (
    serialize_params,
    handle_errors_decorator,
    is_valid_uuid,
    handle_path_error
)
from api.permissions import IsRegisteredAndConfirmed
from api.services.opensearch.search import OpenSearchService
from api.views.v1.opensearch_query_builder.moderation_events_query_builder \
    import ModerationEventsQueryBuilder
from api.views.v1.opensearch_query_builder.opensearch_query_director \
    import OpenSearchQueryDirector
from api.serializers.v1.moderation_events_serializer \
    import ModerationEventsSerializer
from api.views.v1.index_names import OpenSearchIndexNames


class ModerationEvents(ViewSet):
    swagger_schema = None
    permission_classes = [IsRegisteredAndConfirmed]

    opensearch_service = OpenSearchService()
    moderation_events_query_builder = ModerationEventsQueryBuilder()
    opensearch_query_director = OpenSearchQueryDirector(
        moderation_events_query_builder
    )

    @handle_errors_decorator
    def list(self, request):
        params, error_response = serialize_params(
            ModerationEventsSerializer,
            request.GET
        )
        if error_response:
            return Response(
                error_response,
                status=status.HTTP_400_BAD_REQUEST
            )

        query_body = self.opensearch_query_director.build_query(
            request.GET
        )

        response = self.opensearch_service.search_index(
            OpenSearchIndexNames.MODERATION_EVENTS_INDEX,
            query_body
        )
        return Response(response)

    @handle_errors_decorator
    def retrieve(self, request,  pk=None):
        if not IsRegisteredAndConfirmed().has_permission(request, self):
            return Response(
                {
                    "detail": (
                        "Only an authorized user "
                        "can perform this action."
                    )
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not is_valid_uuid(pk):
            return handle_path_error(
                field="moderation_id",
                message="Invalid UUID format.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        query_params = QueryDict('', mutable=True)
        query_params.update({'moderation_id': pk})
        query_body = self.opensearch_query_director.build_query(
            query_params
        )
        response = self.opensearch_service.search_index(
            OpenSearchIndexNames.MODERATION_EVENTS_INDEX,
            query_body
        )
        return Response(response)
