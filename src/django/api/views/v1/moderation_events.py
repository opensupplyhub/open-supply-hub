import logging
from datetime import datetime

from django.contrib.gis.geos import Point
from django.db import transaction
from django.http import QueryDict
from django.utils import timezone

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from api.constants import ProcessingAction
from api.extended_fields import create_extendedfields_for_single_item
from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.facility_list_item_temp import FacilityListItemTemp
from api.models.facility.facility_match import FacilityMatch
from api.models.facility.facility_match_temp import FacilityMatchTemp
from api.models.moderation_event import ModerationEvent
from api.models.nonstandard_field import NonstandardField
from api.models.source import Source
from api.os_id import make_os_id
from api.permissions import IsRegisteredAndConfirmed
from api.serializers.v1.moderation_event_update_serializer \
    import ModerationEventUpdateSerializer
from api.serializers.v1.moderation_events_serializer \
    import ModerationEventsSerializer
from api.serializers.v1.opensearch_common_validators.moderation_id_validator \
    import ModerationIdValidator
from api.services.opensearch.search import OpenSearchService
from api.views.v1.index_names import OpenSearchIndexNames
from api.views.v1.opensearch_query_builder.moderation_events_query_builder \
    import ModerationEventsQueryBuilder
from api.views.v1.opensearch_query_builder.opensearch_query_director \
    import OpenSearchQueryDirector
from api.views.v1.utils import (
    handle_errors_decorator,
    handle_path_error,
    serialize_params,
)


log = logging.getLogger(__name__)


class ModerationEvents(ViewSet):
    swagger_schema = None
    permission_classes = [IsRegisteredAndConfirmed]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opensearch_service = OpenSearchService()
        self.moderation_events_query_builder = ModerationEventsQueryBuilder()
        self.opensearch_query_director = OpenSearchQueryDirector(
                self.moderation_events_query_builder
            )

    @handle_errors_decorator
    def list(self, request):
        _, error_response = serialize_params(
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
    def retrieve(self, _,  pk=None):
        if not ModerationIdValidator.is_valid_uuid(pk):
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

    @handle_errors_decorator
    def patch(self, request, pk=None):
        if not (request.user.is_superuser or request.user.is_staff):
            raise PermissionDenied(
                detail="Only the Moderator can perform this action."
            )

        if not ModerationIdValidator.is_valid_uuid(pk):
            return handle_path_error(
                field="moderation_id",
                message="Invalid UUID format.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            event = ModerationEvent.objects.get(uuid=pk)
        except ModerationEvent.DoesNotExist:
            return handle_path_error(
                field="moderation_id",
                message="Moderation event not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = ModerationEventUpdateSerializer(
            event,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {
                "message": 'The request body contains '
                'invalid or missing fields.',
                "error": [serializer.errors]
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @handle_errors_decorator
    def add_production_location(self, request, moderation_id):

        self.__validate_user_permissions(request)

        if not ModerationIdValidator.is_valid_uuid(moderation_id):
            return handle_path_error(
                field="moderation_id",
                message="Invalid UUID format.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            event = ModerationEvent.objects.get(uuid=moderation_id)
        except ModerationEvent.DoesNotExist:
            return handle_path_error(
                field="moderation_id",
                message="Moderation event not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if event.status != ModerationEvent.Status.PENDING:
            return handle_path_error(
                field="status",
                message="Moderation status must be PENDING.",
                status_code=status.HTTP_410_GONE,
            )

        data = event.cleaned_data
        contributor = event.contributor
        header_row_keys = data["raw_json"].keys()

        with transaction.atomic():
            try:
                source = self.__create_source(contributor)
                log.info(f'[Moderation Event] Source created. Id: {source.id}')

                self.__create_nonstandard_fields(header_row_keys, contributor)
                log.info('[Moderation Event] Nonstandard fields created.')

                header_str = ','.join(header_row_keys)
                item = self.__create_facility_list_item(
                    source, data, header_str, FacilityListItem.MATCHED
                )
                log.info(
                    f'[Moderation Event] FacilityListItem created. Id: '
                    f'{item.id}'
                )

                create_extendedfields_for_single_item(item, data["fields"])
                log.info('[Moderation Event] Extended fields created.')

                self.__set_geocoded_location(item, data, event)
                log.info('[Moderation Event] Geocoded location set.')

                facility_id = make_os_id(item.country_code)
                log.info(
                    f'[Moderation Event] Facility ID created: {facility_id}'
                )

                self.__create_new_facility(item, facility_id)
                log.info(
                    f'[Moderation Event] Facility created. Id: {facility_id}'
                )

                self.__update_item_with_facility_id(item, facility_id)
                log.info(
                    '[Moderation Event] FacilityListItem updated with '
                    'facility ID.'
                )

                FacilityListItemTemp.copy(item)
                log.info('[Moderation Event] FacilityListItemTemp created.')

                self.__create_facility_match_temp(item)
                log.info('[Moderation Event] FacilityMatchTemp created.')

                self.__create_facility_match(item)
                log.info('[Moderation Event] FacilityMatch created.')

                self.__update_event(event, item)
                log.info(
                    '[Moderation Event] Status and os_id of Moderation Event '
                    'updated.'
                )

            except Exception as e:
                log.error(f'[Moderation Event] Error: {str(e)}')
                return Response(
                    {
                        "message": "An unexpected error occurred while "
                        "processing the request."
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(
            {"os_id": item.facility_id}, status=status.HTTP_201_CREATED
        )

    @staticmethod
    def __validate_user_permissions(request):
        if not (request.user.is_superuser or request.user.is_staff):
            raise PermissionDenied(
                detail="Only the Moderator can perform this action."
            )

    @staticmethod
    def __create_source(contributor) -> Source:
        return Source.objects.create(
            contributor=contributor,
            source_type=Source.SINGLE,
            is_public=True,
            create=True,
        )

    @staticmethod
    def __create_nonstandard_fields(fields, contributor):
        unique_fields = list(set(fields))

        existing_fields = NonstandardField.objects.filter(
            contributor=contributor
        ).values_list('column_name', flat=True)
        new_fields = filter(lambda f: f not in existing_fields, unique_fields)
        standard_fields = [
            'sector',
            'country',
            'name',
            'address',
            'lat',
            'lng',
        ]
        nonstandard_fields = filter(
            lambda f: f.lower() not in standard_fields, new_fields
        )

        for field in nonstandard_fields:
            (
                NonstandardField.objects.create(
                    contributor=contributor, column_name=field
                )
            )

        log.info(
            f'[Moderation Event] Nonstandard fields: {nonstandard_fields}'
        )

    @staticmethod
    def __set_geocoded_location(item, data, event):
        if event.geocode_result:
            item.geocoded_point = Point(
                event.geocode_result["longitude"],
                event.geocode_result["latitude"],
            )
            item.geocoded_address = event.geocode_result["geocoded_address"]
            item.processing_results.append(
                {
                    'action': ProcessingAction.GEOCODE,
                    'started_at': str(timezone.now()),
                    'error': False,
                    'skipped_geocoder': False,
                    'data': event.geocode_result['full_response'],
                    'finished_at': str(timezone.now()),
                }
            )
        else:
            item.geocoded_point = Point(
                data["fields"]["lng"], data["fields"]["lat"]
            )
            item.processing_results.append(
                {
                    'action': ProcessingAction.GEOCODE,
                    'started_at': str(timezone.now()),
                    'error': False,
                    'skipped_geocoder': True,
                    'finished_at': str(timezone.now()),
                }
            )
        item.save()

    @staticmethod
    def __create_facility_list_item(source, data, header_str, status):
        return FacilityListItem.objects.create(
            source=source,
            row_index=0,
            raw_data=','.join(
                f'"{value}"' for value in data["raw_json"].values()
            ),
            raw_json=data["raw_json"],
            raw_header=header_str,
            name=data["name"],
            clean_name=data["clean_name"],
            address=data["address"],
            clean_address=data["clean_address"],
            country_code=data["country_code"],
            sector=data["sector"],
            status=status,
            processing_results=[
                {
                    'action': ProcessingAction.PARSE,
                    'started_at': str(timezone.now()),
                    'error': False,
                    'finished_at': str(timezone.now()),
                    'is_geocoded': False,
                }
            ],
        )

    @staticmethod
    def __create_new_facility(item, facility_id):
        return Facility.objects.create(
            id=facility_id,
            name=item.name,
            address=item.address,
            country_code=item.country_code,
            location=item.geocoded_point,
            created_from_id=item.id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    @staticmethod
    def __update_item_with_facility_id(item, facility_id):
        item.facility_id = facility_id
        item.processing_results.append(
            {
                'action': ProcessingAction.MATCH,
                'started_at': str(timezone.now()),
                'error': False,
                'finished_at': str(timezone.now()),
            }
        )
        item.save()

    @staticmethod
    def __create_facility_match_temp(item):
        return FacilityMatchTemp.objects.create(
            facility_id=item.facility_id,
            confidence=1.0,
            facility_list_item_id=item.id,
            status=FacilityMatchTemp.AUTOMATIC,
            results={"match_type": "moderation_event"},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    @staticmethod
    def __create_facility_match(item):
        return FacilityMatch.objects.create(
            facility_id=item.facility_id,
            confidence=1.0,
            facility_list_item_id=item.id,
            status=FacilityMatch.AUTOMATIC,
            results={"match_type": "moderation_event"},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    @staticmethod
    def __update_event(event, item):
        event.status = ModerationEvent.Status.APPROVED
        event.os_id = item.facility_id
        event.save()
