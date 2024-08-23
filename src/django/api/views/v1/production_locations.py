import logging
from django.http import QueryDict
from django.utils import timezone
from django.db import transaction
from waffle import flag_is_active
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.exceptions import (
    PermissionDenied,
    APIException
)
from api.facility_actions.processing_facility_api import ProcessingFacilityAPI
from api.facility_actions.processing_facility_executor import (
    ProcessingFacilityExecutor
)
from api.views.v1.utils import (
    serialize_params,
    handle_errors_decorator
)
from ...permissions import IsRegisteredAndConfirmed, IsSuperuser
from api.services.search import OpenSearchService
from api.views.v1.opensearch_query_builder.opensearch_query_builder \
    import OpenSearchQueryBuilder
from api.views.v1.opensearch_query_builder.opensearch_query_director \
    import OpenSearchQueryDirector
from api.serializers.v1.production_locations_serializer \
    import ProductionLocationsSerializer
from api.views.v1.index_names import OpenSearchIndexNames

from ...sector_product_type_parser import SectorCache
from ...constants import (
    FeatureGroups,
    FacilityCreateQueryParams
)

from contricleaner.lib.contri_cleaner import ContriCleaner
from contricleaner.lib.exceptions.handler_not_set_error \
    import HandlerNotSetError

from ...serializers import (
    FacilityCreateQueryParamsSerializer,
)

# Initialize logger.
log = logging.getLogger(__name__)


class ProductionLocations(ViewSet):
    # swagger_schema = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opensearch_service = OpenSearchService()
        self.opensearch_query_builder = OpenSearchQueryBuilder()
        self.opensearch_query_director = OpenSearchQueryDirector(
                self.opensearch_query_builder
            )

    @handle_errors_decorator
    def list(self, request):
        params, error_response = serialize_params(
            ProductionLocationsSerializer,
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
            OpenSearchIndexNames.PRODUCTION_LOCATIONS_INDEX,
            query_body
        )
        return Response(response)

    @handle_errors_decorator
    def retrieve(self, request,  pk=None):
        query_params = QueryDict('', mutable=True)
        query_params.update({'os_id': pk})
        query_body = self.opensearch_query_director. \
            build_query(query_params)
        response = self.opensearch_service.search_index(
            OpenSearchIndexNames.PRODUCTION_LOCATIONS_INDEX,
            query_body
        )
        return Response(response)

    @transaction.non_atomic_requests
    def create(self, request):
        if not IsRegisteredAndConfirmed().has_permission(request, self):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if not flag_is_active(request._request,
                              FeatureGroups.CAN_SUBMIT_FACILITY):
            raise PermissionDenied()

        log.info(f'[API Upload] Uploading data: {request.data}')

        parsing_started = str(timezone.now())
        log.info('[API Upload] Started CC Parse process!')

        params_serializer = FacilityCreateQueryParamsSerializer(
            data=request.query_params)
        params_serializer.is_valid(raise_exception=True)
        should_create = params_serializer.validated_data[
            FacilityCreateQueryParams.CREATE]
        public_submission = params_serializer.validated_data[
            FacilityCreateQueryParams.PUBLIC]
        private_allowed = flag_is_active(
            request._request, FeatureGroups.CAN_SUBMIT_PRIVATE_FACILITY)
        if not public_submission and not private_allowed:
            raise PermissionDenied('Cannot submit a private facility')

        contri_cleaner = ContriCleaner(request.data, SectorCache())
        try:
            contri_cleaner_processed_data = contri_cleaner.process_data()
        except HandlerNotSetError as err:
            log.error(f'[API Upload] Internal ContriCleaner Error: {err}')
            raise APIException('Internal System Error. '
                               'Please contact support.')

        processing_input = {
            'request': request,
            'contri_cleaner_processed_data': contri_cleaner_processed_data,
            'public_submission': public_submission,
            'should_create': should_create,
            'parsing_started': parsing_started,
        }

        processing_facility_executor = ProcessingFacilityExecutor(
            ProcessingFacilityAPI(processing_input)
        )

        return processing_facility_executor.run_processing()
