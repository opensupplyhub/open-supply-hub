import logging
import copy
from typing import Tuple, List, Any, Optional, Dict

from django.contrib.gis.geos import Polygon
from django.http import QueryDict
from django.db import transaction
from django.db.models import Q
from django.utils.cache import patch_cache_control

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from waffle import switch_is_active

from api.views.v1.utils import (
    serialize_params,
    handle_errors_decorator,
)
from api.services.opensearch.search import OpenSearchService
from api.services.candidate_retirement import (
    get_tombstone,
    tombstone_payload,
)
from api.services import candidate_validation
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
from api.serializers.v1.duplicate_override_query_param_serializer \
    import DuplicateOverrideQueryParamSerializer
from api.serializers.v1.ignore_warnings_query_param_serializer \
    import IgnoreWarningsQueryParamSerializer
from api.serializers.v1.candidates_bbox_query_param_serializer \
    import CandidatesBboxQueryParamSerializer
from api.serializers.facility.facility_candidate_details_serializer import (
    NOINDEX_HEADER,
    NOINDEX_VALUE,
    candidate_production_location,
    geometry_geojson,
)
from api.models.moderation_event import ModerationEvent
from api.models.facility.facility import Facility
from api.models.facility.facility_candidate_vote import FacilityCandidateVote
from api.models.partner_field import PartnerField
from api.models.extended_field import ExtendedField
from api.throttles import (
    DataUploadThrottle,
    DuplicateThrottle
)
from api.constants import (
    APIV1CandidateVoteErrorMessages,
    APIV1CommonErrorMessages,
    NON_FIELD_ERRORS_KEY,
    APIV1LocationContributionErrorMessages,
)
from api.exceptions import ServiceUnavailableException
from api.mail import (
    send_slc_new_location_confirmation_email,
    send_slc_additional_info_confirmation_email
)
from api.views.v1.response_mappings.production_locations_response import \
    ProductionLocationsResponseMapping
from api.partner_fields.registry import system_partner_field_registry
from api.serializers.facility.partner_field_helper import (
    apply_schema_defaults,
    get_cached_all_partner_fields,
)

logger = logging.getLogger(__name__)


class ProductionLocations(ViewSet):
    swagger_schema = None

    @staticmethod
    def __init_opensearch() -> Tuple[OpenSearchService,
                                     OpenSearchQueryDirector]:
        opensearch_service = OpenSearchService()
        opensearch_query_builder = ProductionLocationsQueryBuilder()
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
        if self.__is_vote_write():
            # Ticket OSDEV-3245: any authenticated account may vote; the
            # (facility, user) unique constraint is the anti-abuse control.
            return [IsAuthenticated]
        return []

    def __is_vote_write(self):
        return (
            self.action == 'candidate_votes'
            and self.request.method == 'POST'
        )

    def get_throttles(self):
        if (self.action == 'create'
                or self.action == 'partial_update'):
            return [DataUploadThrottle(), DuplicateThrottle()]
        if self.__is_vote_write():
            # Same per-user write rate as the other v1 write actions. No
            # DuplicateThrottle: a repeat vote is idempotent and changing
            # a vote back within its window must not 429.
            return [DataUploadThrottle()]

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

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(
            request, response, *args, **kwargs
        )
        # A rejected submission creates no moderation event, so the entry
        # DuplicateThrottle recorded for it must not block an identical
        # retry (e.g. resubmitting unchanged data after dismissing the
        # duplicate or quality-warning dialog). 429 is excluded: that is
        # the throttle's own rejection, and clearing on it would let every
        # second identical request through.
        if (response.status_code >= status.HTTP_400_BAD_REQUEST
                and response.status_code
                != status.HTTP_429_TOO_MANY_REQUESTS):
            DuplicateThrottle().clear(request, self)
        return response

    @handle_errors_decorator
    def list(self, request):
        _, error_response = serialize_params(
            ProductionLocationsSerializer,
            request.GET,
        )

        if error_response:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        opensearch_service, opensearch_query_director = \
            self.__init_opensearch()
        query_body = opensearch_query_director.build_query(
            request.GET,
            ProductionLocationsResponseMapping.PRODUCTION_LOCATIONS
        )
        response = opensearch_service.search_index(
            OpenSearchIndexNames.PRODUCTION_LOCATIONS_INDEX,
            query_body,
        )
        return Response(response)

    @handle_errors_decorator
    def retrieve(self, request, pk=None):
        '''
        One production location by OS ID, from OpenSearch.

        Candidate production locations (Earth Genome satellite detections,
        OSDEV-3249) have no OpenSearch document, so on a miss the OS ID is
        checked against ``Facility.including_candidates`` and a candidate
        is served from the database with the candidate labeling
        (``is_candidate``, ``source``, ``external_id``, ``confidence``,
        ``polygon``, ``validation`` and ``suggested_matches``; see
        api/serializers/facility/facility_candidate_details_serializer.py).
        Candidates are reachable only this way and through
        ``GET .../candidates/?bbox=``: the ``list`` search, the tiles and
        ``/api/facilities-downloads/`` never include them. A retired
        candidate answers 410, anything else unknown 404, and confirmed
        facilities are untouched by the fallback.
        '''
        query_params = QueryDict("", mutable=True)
        query_params.update({"os_id": pk})

        opensearch_service, opensearch_query_director = \
            self.__init_opensearch()
        query_body = opensearch_query_director.build_query(
            query_params,
            ProductionLocationsResponseMapping.PRODUCTION_LOCATION_BY_OS_ID
        )
        response = opensearch_service.search_index(
            OpenSearchIndexNames.PRODUCTION_LOCATIONS_INDEX,
            query_body,
        )
        locations = response.get("data", [])

        if len(locations) == 0:
            # Candidates are never indexed (OSDEV-3243), so they always
            # miss OpenSearch; one primary-key lookup serves them from
            # the database instead (OSDEV-3249).
            candidate = Facility.including_candidates.filter(
                pk=pk, is_candidate=True
            ).first()
            if candidate is not None:
                return self.__candidate_response(
                    candidate_production_location(candidate, request.user)
                )
            # A retired OS ID (NOT_A_FACILITY tombstone, OSDEV-3246) is
            # not in OpenSearch and is excluded from historical_os_id, so
            # it always lands here. One primary-key lookup on the miss
            # path tells 410 Gone apart from a plain 404.
            tombstone = get_tombstone(pk)
            if tombstone is not None:
                return Response(
                    data=tombstone_payload(tombstone),
                    status=status.HTTP_410_GONE,
                )
            return Response(
                data={
                    "detail": "The location with the given id was not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        partner_extended_fields = self.__get_partner_fields(pk)
        locations[0].update(partner_extended_fields)

        return Response(locations[0])

    @staticmethod
    def __candidate_response(data):
        '''
        A candidate payload carries the caller's own vote, so it must not
        be stored in a shared cache (``Cache-Control: private``), and it
        must not be indexed by search engines (``X-Robots-Tag: noindex``;
        the SPA has no server-rendered head to carry a meta tag).
        '''
        response = Response(data)
        patch_cache_control(response, private=True)
        response[NOINDEX_HEADER] = NOINDEX_VALUE
        return response

    @action(detail=False, methods=['GET'], url_path='candidates')
    def candidates(self, request):
        '''
        Candidate production locations inside a bounding box (OSDEV-3249).

        ``GET /api/v1/production-locations/candidates/?bbox=minLng,minLat,
        maxLng,maxLat[&limit=N]`` is open, read-only and rate limited like
        the other v1 reads. It answers a GeoJSON FeatureCollection of the
        candidates whose detected polygon (or point, when there is no
        polygon) intersects the box, each Feature labeled with
        ``os_id``, ``confidence``, ``source``, the derived validation
        ``state`` and ``tally`` and the pin ``centroid``. ``limit``
        defaults to 200 and is capped at 500; a malformed, inverted,
        out-of-range or oversized (more than 2 degrees on a side) bbox is
        400. Only ``is_candidate`` rows are ever returned, so the
        brand/CSO data contract (confirmed facilities only) is unaffected.
        '''
        params = CandidatesBboxQueryParamSerializer(data=request.query_params)
        if not params.is_valid():
            field, messages = next(iter(params.errors.items()))
            return Response(
                {
                    'detail': APIV1CommonErrorMessages.COMMON_REQ_QUERY_ERROR,
                    'errors': [{'field': field, 'detail': str(messages[0])}],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        envelope = Polygon.from_bbox(params.validated_data['bbox'])
        envelope.srid = 4326
        candidates = list(
            Facility.including_candidates
            .filter(is_candidate=True)
            .filter(
                Q(polygon__intersects=envelope)
                | Q(polygon__isnull=True, location__intersects=envelope)
            )
            .order_by('id')
            .only('id', 'location', 'polygon', 'confidence', 'source')
            [:params.validated_data['limit']]
        )
        vote_tallies = candidate_validation.tallies(
            candidate.id for candidate in candidates
        )
        return self.__candidate_response({
            'type': 'FeatureCollection',
            'features': [
                self.__candidate_feature(
                    candidate, vote_tallies[candidate.id]
                )
                for candidate in candidates
            ],
        })

    @staticmethod
    def __candidate_feature(facility, vote_tally):
        state = candidate_validation.derive_state(vote_tally)
        geometry = (
            facility.polygon if facility.polygon is not None
            else facility.location
        )
        return {
            'type': 'Feature',
            'id': facility.id,
            'geometry': geometry_geojson(geometry),
            'properties': {
                'os_id': facility.id,
                'confidence': facility.confidence,
                'source': facility.source,
                'state': candidate_validation.public_state(state),
                'tally': vote_tally,
                'centroid': {
                    'lat': facility.location.y,
                    'lng': facility.location.x,
                },
            },
        }

    @action(
        detail=True,
        methods=['GET', 'POST'],
        url_path='candidate-votes',
    )
    def candidate_votes(self, request, pk=None):
        '''
        Community existence votes on a candidate (OSDEV-3245).

        GET (open): the live tally, the derived state and, when the
        caller is authenticated, their own vote.
        POST (authenticated) ``{"vote": "confirmed"|"not_a_facility"}``:
        records or changes the caller's vote (201 created / 200 changed)
        and returns the same body. 404 for an unknown OS ID or one that is
        not a candidate, 410 for a retired OS ID, 409 once the candidate
        is confirmed (voting closed). State derivation and the
        consensus-no handling (auto-retire vs. moderation gate) live in
        api/services/candidate_validation.py.
        '''
        facility = Facility.including_candidates.filter(pk=pk).first()
        if facility is None:
            tombstone = get_tombstone(pk)
            if tombstone is not None:
                return Response(
                    data=tombstone_payload(tombstone),
                    status=status.HTTP_410_GONE,
                )
            return Response(
                data={'detail': APIV1CommonErrorMessages.LOCATION_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not facility.is_candidate:
            return Response(
                data={
                    'detail': APIV1CandidateVoteErrorMessages.NOT_A_CANDIDATE
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.method == 'GET':
            vote_tally = candidate_validation.tally(facility)
            state = candidate_validation.derive_state(vote_tally)
            return Response(
                self.__vote_body(
                    facility.id,
                    request.user,
                    vote_tally,
                    candidate_validation.public_state(state),
                )
            )

        vote = request.data.get('vote') if isinstance(
            request.data, dict
        ) else None
        if vote not in FacilityCandidateVote.Vote.values:
            return Response(
                data={
                    'detail': APIV1CommonErrorMessages.COMMON_REQ_BODY_ERROR,
                    'errors': [{
                        'field': 'vote',
                        'detail':
                            APIV1CandidateVoteErrorMessages.INVALID_VOTE,
                    }],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            outcome = candidate_validation.cast_vote(
                facility, request.user, vote
            )
        except candidate_validation.VotingClosedError:
            return Response(
                data={
                    'detail': APIV1CandidateVoteErrorMessages.VOTING_CLOSED
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            self.__vote_body(
                facility.id,
                request.user,
                outcome.tally,
                outcome.reported_state,
                your_vote=outcome.vote,
            ),
            status=(
                status.HTTP_201_CREATED if outcome.created
                else status.HTTP_200_OK
            ),
        )

    @staticmethod
    def __vote_body(os_id, user, vote_tally, state, your_vote=None):
        if your_vote is None and user.is_authenticated:
            your_vote = (
                FacilityCandidateVote.objects
                .filter(facility_id=os_id, user=user)
                .values_list('vote', flat=True)
                .first()
            )
        return {
            'os_id': os_id,
            'your_vote': your_vote,
            'tally': vote_tally,
            'state': state,
        }

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

        check_overrides, error_response = self.__parse_check_overrides(
            request
        )
        if error_response is not None:
            return error_response

        location_contribution_strategy = LocationContribution()
        moderation_event_creator = ModerationEventCreator(
            location_contribution_strategy
        )
        event_dto = CreateModerationEventDTO(
            contributor=request.user.contributor,
            raw_data=request.data,
            request_type=ModerationEvent.RequestType.CREATE.value,
            **check_overrides,
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

        check_overrides, error_response = self.__parse_check_overrides(
            request
        )
        if error_response is not None:
            return error_response

        location_contribution_strategy = LocationContribution()
        moderation_event_creator = ModerationEventCreator(
            location_contribution_strategy
        )
        event_dto = CreateModerationEventDTO(
            contributor=request.user.contributor,
            os=Facility.objects.get(id=pk),
            raw_data=request.data,
            request_type=ModerationEvent.RequestType.UPDATE.value,
            **check_overrides,
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

    @staticmethod
    def __parse_check_overrides(request):
        '''
        Reads the ?duplicate_override and ?ignore_warnings query params
        that let the SLC form resubmit past the DuplicateSubmissionProcessor
        and SubmissionQualityProcessor checks after the contributor has
        confirmed the warning. Shared by create (POST) and partial_update
        (PATCH), since both run the same contribution pipeline. Returns
        (overrides, None) on success, where overrides are keyword args for
        CreateModerationEventDTO, or (None, Response) with the 400 to
        return when either param holds something other than true/false.
        '''
        param_serializers = (
            ('duplicate_override', DuplicateOverrideQueryParamSerializer),
            ('ignore_warnings', IgnoreWarningsQueryParamSerializer),
        )
        overrides = {}
        for field, serializer_class in param_serializers:
            serializer = serializer_class(data=request.query_params)
            if not serializer.is_valid():
                return None, Response(
                    {
                        'detail': (
                            APIV1CommonErrorMessages.COMMON_REQ_QUERY_ERROR
                        ),
                        'errors': [{
                            'field': field,
                            'detail': str(serializer.errors[field][0])
                        }]
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            overrides[field] = serializer.validated_data[field]

        return overrides, None

    def __get_partner_fields(self, pk):
        """
        Checks and returns partner extended fields for a
        production location object by its ID or
        by the provided Facility instance.

        Caches the list of partner field names for one hour.
        Returns a dictionary of the form:
            {
                "field_name_1": value_1,
                "field_name_2": value_2,
                ...
            }
        """
        all_partner_fields = get_cached_all_partner_fields()
        partner_field_names = [
            field.name
            for field in all_partner_fields
            if field.active and field.available_in_api
        ]

        if not partner_field_names:
            return {}

        partner_extended_fields = {}
        partner_field_values = ExtendedField.objects.filter(
            facility__id=pk,
            field_name__in=partner_field_names,
        ).values("field_name", "value")
        json_schemas = {
            field.name: field.json_schema
            for field in all_partner_fields
            if field.json_schema and field.type == PartnerField.OBJECT
        }

        for field in partner_field_values:
            field_value = field.get("value")
            field_name = field.get("field_name")
            value = self.__get_partner_field_value(
                value=field_value,
                schema=json_schemas.get(field_name),
            )

            if value is None:
                continue

            partner_extended_fields[field_name] = value

        facility = (
            Facility.objects.filter(id=pk)
            .only(
                "id",
                "country_code",
                "location",
            )
            .first()
        )

        if not facility:
            logger.warning(f"PL viewset: Facility not found for ID: {pk}")
            return partner_extended_fields

        for provider in system_partner_field_registry.providers:
            field_name = provider._get_field_name()

            if field_name not in partner_field_names:
                continue

            provider_data = provider.fetch_data(facility)

            if provider_data is None:
                continue

            provider_value = provider_data.get("value")

            if not field_name or not isinstance(provider_value, dict):
                continue

            value = self.__get_partner_field_value(
                value=provider_value,
                schema=json_schemas.get(field_name),
            )

            if value is None:
                continue

            partner_extended_fields[field_name] = value

        return partner_extended_fields

    def __get_partner_field_value(
        self,
        value: Any,
        schema: Optional[Dict] = None,
    ) -> Any:
        """
        Get partner field value from the provider value.
        """
        if not isinstance(value, dict):
            return None

        raw_values = value.get("raw_values")

        if isinstance(raw_values, list):
            return raw_values

        if isinstance(raw_values, dict):
            return apply_schema_defaults(
                copy.deepcopy(raw_values),
                schema,
            )

        return value.get("raw_value")
