import logging
import copy
from typing import Tuple, List, Any, Optional, Dict
from uuid import UUID

from django.http import QueryDict
from django.db import transaction

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.decorators import action
from waffle import switch_is_active

from django.utils import timezone

from api.views.v1.utils import (
    serialize_params,
    handle_errors_decorator,
)
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
from api.serializers.v1.duplicate_override_query_param_serializer \
    import DuplicateOverrideQueryParamSerializer
from api.serializers.v1.ignore_warnings_query_param_serializer \
    import IgnoreWarningsQueryParamSerializer
from api.models.moderation_event import ModerationEvent
from api.models.facility.facility import Facility
from api.models.facility.facility_alias import FacilityAlias
from api.models.identity_record_association import (
    IdentityRecordAssociation,
)
from api.models.partner_field import PartnerField
from api.models.extended_field import ExtendedField
from api.os_id import validate_os_id
from api.serializers.v1.identity_record_registration_serializer \
    import IdentityRecordRegistrationSerializer
from api.throttles import (
    DataUploadThrottle,
    DuplicateThrottle
)
from api.constants import (
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
        authenticated_actions = (
            'create',
            'partial_update',
            # Registering a record against an OS ID, and reading the state
            # of a registration. Restricting this further to an approved
            # registrant is a standing-policy question rather than a pilot
            # one: §2.5 accepts RBA's assertion as submitted for the
            # demonstration, and the general case goes to the leadership
            # brief. Not built here.
            'create_identity_record',
            'retrieve_identity_record',
        )
        if self.action in authenticated_actions:
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
    def retrieve(self, _, pk=None):
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
            return Response(
                data={
                    "detail": "The location with the given id was not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        partner_extended_fields = self.__get_partner_fields(pk)
        locations[0].update(partner_extended_fields)

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

    @staticmethod
    def __os_id_exists_here(os_id):
        """
        Whether this instance knows the identifier, following a merge.

        A superseded OS ID keeps resolving to the surviving location
        through FacilityAlias, so a registration against one is accepted
        and stored as submitted. Resolution follows the alias on read,
        which is the behaviour Section 2.7 promises.
        """
        if Facility.objects.filter(pk=os_id).exists():
            return True
        return FacilityAlias.objects.filter(pk=os_id).exists()

    @staticmethod
    def __identity_record_response(association):
        """
        The Section 3.2 envelope.

        `moderation_id` is the association's own uuid. The pilot path
        creates no ModerationEvent, because there is nothing to moderate:
        the association is Open Supply Hub's own construction. The field
        keeps its name so the envelope mirrors the existing
        production-location submission API, as 3.2 intends.
        """
        return {
            'moderation_id': str(association.uuid),
            # Derived rather than hardcoded. Everything this endpoint
            # creates is live on creation, but the model supports the
            # pending row the general case will need, and a helper that
            # reported APPROVED for one would be lying.
            'moderation_status': (
                'APPROVED' if association.is_live else 'PENDING'
            ),
            'created_at': association.created_at,
            'live_from': association.live_from,
        }

    @action(
        detail=True,
        methods=['POST'],
        url_path='identity-records',
    )
    def create_identity_record(self, request, pk=None):
        """
        Register an external record against an OS ID (FR-07, scope doc 3.2).

        Open Supply Hub stores the association and nothing else (NFR-04).
        Pilot-set registrations return live immediately with no
        verification step, because the association is Open Supply Hub's own
        construction rather than RBA's assertion (2.3, 2.5). The PENDING
        path that issues a verification_url is the general case, gated on
        OQ-01, and is deliberately not built here.

        Note on 422. Section 3.2 lists it for "well formed but not
        resolvable here", which Section 3.4 ties to identifiers issued only
        on a private instance. This instance cannot tell that case apart
        from an identifier that does not exist, by design, so the write
        path returns 404 and the distinction is left to OSDEV-3586, which
        owns the private-instance response. The two need to agree.
        """
        os_id = pk

        if not validate_os_id(os_id, raise_on_invalid=False):
            return Response(
                {
                    'detail': APIV1CommonErrorMessages.COMMON_REQ_BODY_ERROR,
                    'errors': [{
                        'field': 'os_id',
                        'detail': f'{os_id} is not a valid OS ID.',
                    }],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not self.__os_id_exists_here(os_id):
            return Response(
                {
                    'detail': 'Identifier not found on this instance.',
                    'errors': [{
                        'field': 'os_id',
                        'detail': (
                            f'{os_id} is not a production location on this '
                            'instance.'
                        ),
                    }],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = IdentityRecordRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    'detail': APIV1CommonErrorMessages.COMMON_REQ_BODY_ERROR,
                    'errors': [
                        {'field': field, 'detail': ' '.join(map(str, msgs))}
                        for field, msgs in serializer.errors.items()
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        resolver_uri = data['resolver_uri']

        existing = IdentityRecordAssociation.objects.filter(os_id=os_id)

        if existing.filter(
            live_from__isnull=False
        ).exclude(resolver_uri=resolver_uri).exists():
            return Response(
                {
                    'detail': (
                        'This identifier already has a live association '
                        'with a different resolver URI.'
                    ),
                    'errors': [{
                        'field': 'resolver_uri',
                        'detail': (
                            'Withdraw the existing association before '
                            'registering a different resolver for this '
                            'identifier.'
                        ),
                    }],
                },
                status=status.HTTP_409_CONFLICT,
            )

        # An exact repeat. Returning the existing association instead would
        # make this idempotent, which the scope doc does not ask for and
        # which is explicitly out of scope for the pilot, so it is a
        # conflict rather than a quiet success. Catching it here keeps the
        # unique constraint from surfacing as a 500.
        if existing.filter(resolver_uri=resolver_uri).exists():
            return Response(
                {
                    'detail': (
                        'This resolver URI is already registered against '
                        'this identifier.'
                    ),
                    'errors': [{
                        'field': 'resolver_uri',
                        'detail': 'No change was made.',
                    }],
                },
                status=status.HTTP_409_CONFLICT,
            )

        association = IdentityRecordAssociation.objects.create(
            os_id=os_id,
            resolver_uri=resolver_uri,
            record_type=data['record_type'],
            issuer=data['issuer'],
            registrant_reference=data.get('registrant_reference', ''),
            live_from=timezone.now(),
        )

        return Response(
            self.__identity_record_response(association),
            status=status.HTTP_202_ACCEPTED,
        )

    @action(
        detail=True,
        methods=['GET'],
        url_path='identity-records/(?P<moderation_id>[^/.]+)',
    )
    def retrieve_identity_record(
        self, request, pk=None, moderation_id=None
    ):
        """
        Current state of a registration, and once live, the time from
        which it resolves (scope doc 3.2).
        """
        try:
            parsed_id = UUID(str(moderation_id))
        except ValueError:
            # A non-UUID in the path is a miss, not a crash. Filtering on
            # a UUIDField with a malformed value raises rather than
            # returning empty.
            parsed_id = None

        association = None
        if parsed_id is not None:
            association = IdentityRecordAssociation.objects.filter(
                os_id=pk, uuid=parsed_id
            ).first()

        if association is None:
            return Response(
                {
                    'detail': 'Registration not found.',
                    'errors': [{
                        'field': 'moderation_id',
                        'detail': (
                            f'No registration {moderation_id} for {pk}.'
                        ),
                    }],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            self.__identity_record_response(association),
            status=status.HTTP_200_OK,
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
