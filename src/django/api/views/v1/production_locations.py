from typing import Tuple, List

from django.http import QueryDict
from django.db import transaction

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from waffle import switch_is_active
from api.models.settings import Settings

from api.views.v1.utils import (
    serialize_params,
    handle_errors_decorator,
)
from api.services.record_linkage.record_linkage import RecordLinker
from api.services.opensearch.search import OpenSearchService
from api.views.v1.opensearch_query_builder.production_locations_query_builder \
    import ProductionLocationsQueryBuilder
from api.views.v1.opensearch_query_builder.opensearch_query_director \
    import OpenSearchQueryDirector
from api.serializers.v1.production_locations_serializer \
    import ProductionLocationsSerializer
from api.views.v1.index_names import OpenSearchIndexNames
from api.permissions import IsRegisteredAndConfirmed
from api.moderation_event_actions.creation.moderation_event_creator \
    import ModerationEventCreator
from api.moderation_event_actions.creation.location_contribution \
    .location_contribution import LocationContribution
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.models.moderation_event import ModerationEvent
from api.models.facility.facility import Facility
from api.throttles import (
    DataUploadThrottle,
    DuplicateThrottle
)
from api.constants import (
    APIV1CommonErrorMessages,
    NON_FIELD_ERRORS_KEY,
    APIV1LocationContributionErrorMessages
)
from api.exceptions import ServiceUnavailableException
from api.mail import (
    send_slc_new_location_confirmation_email,
    send_slc_additional_info_confirmation_email
)


class ProductionLocations(ViewSet):
    swagger_schema = None

    @staticmethod
    def __init_opensearch(
        model_id: str = None,
    ) -> Tuple[OpenSearchService, OpenSearchQueryDirector]:
        opensearch_service = OpenSearchService()
        opensearch_query_builder = ProductionLocationsQueryBuilder(
            model_id=model_id,
        )
        opensearch_query_director = OpenSearchQueryDirector(
            opensearch_query_builder
        )

        return (opensearch_service, opensearch_query_director)

    def get_permissions(self):
        '''
        Redefines the parent method and returns the list of permissions for
        the ViewSet action methods.
        '''
        action_permissions = self.__get_action_permissions()

        # Combine custom permissions with global application-level permissions
        # set via the DEFAULT_PERMISSION_CLASSES setting.
        combined_permission_classes = \
            action_permissions + self.permission_classes

        return [permission() for permission in combined_permission_classes]

    def __get_action_permissions(self) -> List:
        '''
        Returns the list of permissions specific to the current action.
        '''
        if (self.action == 'create'
                or self.action == 'partial_update'):
            return [IsRegisteredAndConfirmed]
        return []

    def get_throttles(self):
        if (self.action == 'create'
                or self.action == 'partial_update'):
            return [DataUploadThrottle(), DuplicateThrottle()]

        # Call the parent method to use the default throttling setup in the
        # settings.py file.
        return super().get_throttles()

    def get_parsers(self):
        '''
        Override the default parser classes for specific actions.
        '''
        if (self.request.method == 'POST'
                or self.request.method == 'PATCH'):
            # Use JSONParser for the 'create' and 'partial_update' actions to
            # restrict all media types except 'application/json'.
            return [JSONParser()]

        # Call the parent method to use the default parsers setup in the
        # settings.py file.
        return super().get_parsers()

    @handle_errors_decorator
    def list(self, request):
        _, error_response = serialize_params(
            ProductionLocationsSerializer,
            request.GET,
        )

        if error_response:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        record_linkage_enabled = switch_is_active('enable_record_linkage')
        os_model_id = None
        os_search_pipeline_id = None

        if record_linkage_enabled:
            try:
                model_id = Settings.objects.filter(
                    name=Settings.Name.OS_SENTENCE_TRANSFORMER_MODEL_ID,
                ).get()
                os_model_id = model_id.value
            except Settings.DoesNotExist:
                return Response(
                    data={
                        "detail": (
                            "The OpenSearch model id is not set in the "
                            "settings."
                        ),
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            try:
                model_id = Settings.objects.filter(
                    name=Settings.Name.OS_SENTENCE_TRANSFORMER_MODEL_ID,
                ).get()
                search_pipeline_id = Settings.objects.filter(
                    name=Settings.Name.OS_SEARCH_PIPELINE_ID,
                ).get()

                os_search_pipeline_id = search_pipeline_id.value
            except Settings.DoesNotExist:
                return Response(
                    data={
                        "detail": (
                            "The OpenSearch search pipeline id is not set in "
                            "the settings."
                        ),
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        opensearch_service, opensearch_query_director = \
            self.__init_opensearch(
                model_id=os_model_id,
            )
        query_body = opensearch_query_director.build_query(
            request.GET,
        )

        params = {}

        if record_linkage_enabled and os_search_pipeline_id:
            params["search_pipeline"] = os_search_pipeline_id

        response = opensearch_service.search_index(
            OpenSearchIndexNames.PRODUCTION_LOCATIONS_INDEX,
            query_body,
            params,
        )

        if record_linkage_enabled:
            linker = RecordLinker(
                records=response["data"],
            )
            response["data"] = linker.predict(
                name=request.GET.get("name"),
                address=request.GET.get("address"),
                country_code=request.GET.get("country"),
            )

        return Response(response)

    @handle_errors_decorator
    def retrieve(self, _, pk=None):
        query_params = QueryDict("", mutable=True)
        query_params.update({"os_id": pk})

        opensearch_service, opensearch_query_director = \
            self.__init_opensearch()
        query_body = opensearch_query_director.build_query(query_params)
        response = opensearch_service.search_index(
            OpenSearchIndexNames.PRODUCTION_LOCATIONS_INDEX,
            query_body,
        )
        locations = response.get("data", [])

        if len(locations) == 0:
            return Response(
                data={
                    "detail": "The location with the given id was not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(locations[0])

    @transaction.atomic
    def create(self, request):
        if switch_is_active('disable_list_uploading'):
            raise ServiceUnavailableException(
                APIV1CommonErrorMessages.MAINTENANCE_MODE
            )

        if not isinstance(request.data, dict):
            data_type = type(request.data).__name__
            specific_error = APIV1LocationContributionErrorMessages \
                .invalid_data_type_error(data_type)
            return Response(
                {
                    'detail': APIV1CommonErrorMessages.COMMON_REQ_BODY_ERROR,
                    'errors': [{
                        'field': NON_FIELD_ERRORS_KEY,
                        'detail': specific_error
                    }]
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        location_contribution_strategy = LocationContribution()
        moderation_event_creator = ModerationEventCreator(
            location_contribution_strategy
        )
        event_dto = CreateModerationEventDTO(
            contributor=request.user.contributor,
            raw_data=request.data,
            request_type=ModerationEvent.RequestType.CREATE.value
        )
        result = moderation_event_creator.perform_event_creation(event_dto)

        if result.errors:
            return Response(
                result.errors,
                status=result.status_code)

        if result.moderation_event.source == ModerationEvent.Source.SLC:
            send_slc_new_location_confirmation_email(
                result.moderation_event
            )

        return Response(
            {
                'moderation_id': result.moderation_event.uuid,
                'moderation_status': result.moderation_event.status,
                'created_at': result.moderation_event.created_at,
                'cleaned_data': result.moderation_event.cleaned_data,
            },
            status=result.status_code
        )

    @transaction.atomic
    def partial_update(self, request, pk=None):
        if switch_is_active('disable_list_uploading'):
            raise ServiceUnavailableException(
                APIV1CommonErrorMessages.MAINTENANCE_MODE
            )

        if not Facility.objects.filter(id=pk).exists():
            specific_error = APIV1CommonErrorMessages.LOCATION_NOT_FOUND
            return Response(
                {'detail': specific_error},
                status=status.HTTP_404_NOT_FOUND
            )
        if not isinstance(request.data, dict):
            data_type = type(request.data).__name__
            specific_error = APIV1LocationContributionErrorMessages \
                .invalid_data_type_error(data_type)
            return Response(
                {
                    'detail': APIV1CommonErrorMessages.COMMON_REQ_BODY_ERROR,
                    'errors': [{
                        'field': NON_FIELD_ERRORS_KEY,
                        'detail': specific_error
                    }]
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        location_contribution_strategy = LocationContribution()
        moderation_event_creator = ModerationEventCreator(
            location_contribution_strategy
        )
        event_dto = CreateModerationEventDTO(
            contributor=request.user.contributor,
            os=Facility.objects.get(id=pk),
            raw_data=request.data,
            request_type=ModerationEvent.RequestType.UPDATE.value
        )
        result = moderation_event_creator.perform_event_creation(event_dto)

        if result.errors:
            return Response(
                result.errors,
                status=result.status_code)

        if result.moderation_event.source == ModerationEvent.Source.SLC:
            send_slc_additional_info_confirmation_email(
                result.moderation_event
            )

        return Response(
            {
                'os_id': result.os.id,
                'moderation_id': result.moderation_event.uuid,
                'moderation_status': result.moderation_event.status,
                'created_at': result.moderation_event.created_at,
                'cleaned_data': result.moderation_event.cleaned_data,
            },
            status=result.status_code
        )
