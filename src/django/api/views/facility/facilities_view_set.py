import json
import traceback
import asyncio
import logging
from api.models.transactions.index_facilities_new import index_facilities_new
from api.models.facility.facility_index import FacilityIndex
from contricleaner.lib.parsers.source_parser_json import SourceParserJSON
from contricleaner.lib.serializers.contri_cleaner_serializer import \
    ContriCleanerSerializer

from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    CreateModelMixin,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import (
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    ValidationError
)
from waffle import switch_is_active, flag_is_active
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models import Extent
from django.core import exceptions as core_exceptions
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import F, Q
from django.shortcuts import redirect
from django.utils import timezone
from drf_yasg.openapi import Schema, TYPE_OBJECT
from drf_yasg.utils import no_body, swagger_auto_schema

from ...models import (
    Contributor,
    Facility,
    FacilityActivityReport,
    FacilityAlias,
    FacilityClaim,
    FacilityClaimReviewNote,
    FacilityListItem,
    FacilityListItemTemp,
    FacilityLocation,
    FacilityMatch,
    ExtendedField,
    Source,
    Version
)
from ...constants import (
    FeatureGroups,
    FacilityCreateQueryParams,
    FacilityMergeQueryParams,
    ProcessingAction,
    UpdateLocationParams,
    ErrorMessages
)
from ...exceptions import BadRequestException
from ...extended_fields import (
    create_extendedfields_for_single_item,
)
from ...facility_history import (
    create_dissociate_match_change_reason,
    create_facility_history_list,
)
from ...geocoding import geocode_address
from ...mail import send_claim_facility_confirmation_email

from ...pagination import FacilitiesGeoJSONPagination
from ...permissions import IsRegisteredAndConfirmed, IsSuperuser
from ...processing import handle_external_match_process_result
from ...sector_product_type_parser import SectorCache
from ...serializers import (
    FacilityIndexSerializer,
    FacilityIndexDetailsSerializer,
    FacilityActivityReportSerializer,
    FacilityClaimSerializer,
    FacilityCreateQueryParamsSerializer,
    FacilityMergeQueryParamsSerializer,
    FacilityQueryParamsSerializer,
    FacilityUpdateLocationParamsSerializer,
)
from ...throttles import DataUploadThrottle

from ..fields.create_nonstandard_fields import create_nonstandard_fields
from ..disabled_pagination_inspector import DisabledPaginationInspector
from api.kafka_producer import produce_message_match_process

from .facility_parameters import (
    facility_parameters,
    facilities_list_parameters,
    facilities_create_parameters,
)

# initialize logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)


class FacilitiesViewSet(ListModelMixin,
                        RetrieveModelMixin,
                        DestroyModelMixin,
                        CreateModelMixin,
                        GenericViewSet):

    queryset = FacilityIndex.objects.all()
    serializer_class = FacilityIndexSerializer
    pagination_class = FacilitiesGeoJSONPagination

    def get_throttles(self):
        if self.request.method == 'POST':
            return [DataUploadThrottle()]

        return super().get_throttles()

    @swagger_auto_schema(manual_parameters=facilities_list_parameters)
    def list(self, request):
        """
        Returns a list of facilities in GeoJSON format for a given query.
        (Maximum of 50 facilities per page if the detail parameter is fale or
        not specified, 10 if the detail parameter is true.)

        ### Sample Response
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "id": "OS_ID_1",
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [1, 1]
                        },
                        "properties": {
                            "name": "facility_name_1",
                            "address" "facility address_1",
                            "country_code": "US",
                            "country_name": "United States",
                            "os_id": "OS_ID_1",
                        }
                    },
                    {
                        "id": "OS_ID_2",
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [2, 2]
                        },
                        "properties": {
                            "name": "facility_name_2",
                            "address" "facility address_2",
                            "country_code": "US",
                            "country_name": "United States",
                            "os_id": "OS_ID_2"
                        }
                    }
                ]
            }

        ### Sample Response - parameter 'detail' equal 'true'
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "id": "OS_ID_1",
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [1, 1]
                        },
                        "properties": {
                            "name": "facility_name_1",
                            "address" "facility address_1",
                            "country_code": "US",
                            "country_name": "United States",
                            "os_id": "OS_ID_1",
                            "contributors": [
                                {
                                    "id": 1,
                                    "name": "contributor_list_name",
                                    "is_verified": false,
                                    "contributor_name": "contributor_name",
                                    "list_name": "list_name"
                                }
                            ],
                            "has_approved_claim": false,
                            "is_closed": null,
                            "contributor_fields": [],
                            "extended_fields": {
                                "field_name": [
                                    {
                                        "value": "field_value",
                                        "field_name": "field_name",
                                        "contributor_id": 1,
                                        "contributor_name": "contributor_name",
                                        "updated_at": "0000-00-00T00:00:00"
                                    }
                                ]
                            }
                            "sector": [
                                {
                                    "updated_at": "0000-00-00T00:00:00",
                                    "contributor_id": 1,
                                    "contributor_name": "contributor_name",
                                    "values": [
                                        "sector_value"
                                    ],
                                    "is_from_claim": false
                                }
                            ]
                        }
                    }
                ]
            }
        """
        params = FacilityQueryParamsSerializer(data=request.query_params)

        if not params.is_valid():
            raise ValidationError(params.errors)

        queryset = (
                FacilityIndex
                .objects
                .filter_by_query_params(request.query_params)
            )
        sort_by = params.validated_data['sort_by']
        order_list = []
        if (sort_by is not None) and (sort_by == 'name'):
            order_list = ['name']
        else:
            order_list = ['-contributors_count', 'name']

        queryset = queryset.extra(order_by=order_list)

        page_queryset = self.paginate_queryset(queryset)

        extent = queryset.aggregate(Extent('location'))['location__extent']

        context = {'request': request}

        if page_queryset is not None:
            should_serialize_details = params.validated_data['detail']
            should_serialize_number_of_public_contributors = \
                params.validated_data["number_of_public_contributors"]
            exclude_fields = []

            if not should_serialize_details:
                exclude_fields.extend([
                    'contributor_fields',
                    'extended_fields',
                    'contributors',
                    'sector'])
            if not should_serialize_number_of_public_contributors:
                exclude_fields.extend(['number_of_public_contributors'])

            serializer = FacilityIndexSerializer(page_queryset, many=True,
                                                 context=context,
                                                 exclude_fields=exclude_fields)
            response = self.get_paginated_response(serializer.data)
            response.data['extent'] = extent
            return response

        response_data = FacilityIndexSerializer(queryset, many=True,
                                                context=context).data
        response_data['extent'] = extent
        return Response(response_data)

    @swagger_auto_schema(manual_parameters=facility_parameters)
    def retrieve(self, request, pk=None):
        """
        Returns the facility specified by a given OS ID in GeoJSON format.

        ### Sample Response
            {
                "id": "OSHUB_ID",
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [1, 1]
                },
                "properties": {
                    "name": "facility_name",
                    "address" "facility address",
                    "country_code": "US",
                    "country_name": "United States",
                    "os_id": "OSHUB_ID",
                    "other_names": [],
                    "other_addresses": [],
                    "contributors": [
                        {
                            "id": 1,
                            "name": "Brand A (2019 Q1 List)",
                            "is_verified": true
                        }
                    ]
                }
            }
        """
        try:
            queryset = FacilityIndex.objects.get(pk=pk)
            context = {'request': request}
            response_data = FacilityIndexDetailsSerializer(
                queryset, context=context).data
            return Response(response_data)
        except FacilityIndex.DoesNotExist as exc:
            # If the facility is not found but an alias is available,
            # redirect to the alias
            aliases = FacilityAlias.objects.filter(os_id=pk)
            if len(aliases) == 0:
                raise NotFound() from exc
            os_id = aliases.first().facility.id

            return redirect('/api/facilities/' + os_id)

    @swagger_auto_schema(request_body=Schema(
        'data',
        type=TYPE_OBJECT,
        description='The country, name, address and sector(s) of the '
                    'facility. See the sample request body above.',
    ), manual_parameters=facilities_create_parameters, responses={201: ''})
    @transaction.non_atomic_requests
    def create(self, request):
        """
        Matches submitted facility details to the full list of facilities.
        By default, creates a new facility if there is no match, or associates
        the authenticated contributor with the facility if there is a confident
        match.

        **NOTE** The form below lists the return status code as 201. When
        POSTing data with `create=false` the return status will be 200, not 201.

        ## Sample Request Body

            {
                "sector_product_type": "Apparel"
                "country": "China",
                "name": "Nantong Jackbeanie Headwear & Garment Co. Ltd.",
                "address": "No.808,the third industry park,Guoyuan Town,Nantong 226500."

            }

        ## Sample Responses

        ### Automatic Match

            {
              "matches": [
                {
                  "id": "CN2019303BQ3FZP",
                  "type": "Feature",
                  "geometry": {
                    "type": "Point",
                    "coordinates": [
                      120.596047,
                      32.172013
                    ]
                  },
                  "properties": {
                    "sector": [
                      {
                        "updated_at": "2022-01-27T17:36:54.597482Z",
                        "contributor_id": 4,
                        "contributor_name": "Researcher A",
                        "values": [
                          "Apparel"
                        ]
                      }
                    ],
                    "name": "Nantong Jackbeanie Headwear Garment Co. Ltd.",
                    "address": "No. 808, The Third Industry Park, Guoyuan Town, Rugao City Nantong",
                    "country_code": "CN",
                    "os_id": "CN2019303BQ3FZP",
                    "other_names": [],
                    "other_addresses": [],
                    "contributors": [
                      {
                        "id": 4,
                        "name": "Researcher A (Summer 2019 Affiliate List)",
                        "is_verified": false
                      },
                      {
                        "id": 12,
                        "name": "Brand B",
                        "is_verified": false
                      }

                    ],
                    "country_name": "China",
                    "claim_info": null,
                    "other_locations": [],
                  },
                  "confidence": 0.8153
                }
              ],
              "item_id": 964,
              "geocoded_geometry": {
                "type": "Point",
                "coordinates": [
                  120.596047,
                  32.172013
                ]
              },
              "geocoded_address": "Guoyuanzhen, Rugao, Nantong, Jiangsu, China",
              "status": "MATCHED",
              "os_id": "CN2019303BQ3FZP"
            }

        ### Potential Match

            {
              "matches": [
                {
                  "id": "CN2019303BQ3FZP",
                  "type": "Feature",
                  "geometry": {
                    "type": "Point",
                    "coordinates": [
                      120.596047,
                      32.172013
                    ]
                  },
                  "properties": {
                    "name": "Nantong Jackbeanie Headwear Garment Co. Ltd.",
                    "address": "No. 808, The Third Industry Park, Guoyuan Town, Rugao City Nantong",
                    "sector": [
                      {
                        "updated_at": "2022-01-27T17:36:54.597482Z",
                        "contributor_id": 4,
                        "contributor_name": "Researcher A",
                        "values": [
                          "Apparel"
                        ]
                      }
                    ],
                    "country_code": "CN",
                    "os_id": "CN2019303BQ3FZP",
                    "other_names": [],
                    "other_addresses": [],
                    "contributors": [
                      {
                        "id": 4,
                        "name": "Researcher A (Summer 2019 Affiliate List)",
                        "is_verified": false
                      }
                    ],
                    "country_name": "China",
                    "claim_info": null,
                    "other_locations": []
                  },
                  "confidence": 0.7686,
                  "confirm_match_url": "/api/facility-matches/135005/confirm/",
                  "reject_match_url": "/api/facility-matches/135005/reject/"
                }
              ],
              "item_id": 959,
              "geocoded_geometry": {
                "type": "Point",
                "coordinates": [
                  120.596047,
                  32.172013
                ]
              },
              "geocoded_address": "Guoyuanzhen, Rugao, Nantong, Jiangsu, China",
              "status": "POTENTIAL_MATCH"
            }


        ### Potential Text Only Match

            {
              "matches": [
                {
                  "id": "CN2019303BQ3FZP",
                  "type": "Feature",
                  "geometry": {
                    "type": "Point",
                    "coordinates": [
                      120.596047,
                      32.172013
                    ]
                  },
                  "properties": {
                    "name": "Nantong Jackbeanie Headwear Garment Co. Ltd.",
                    "address": "No. 808, The Third Industry Park, Guoyuan Town, Rugao City Nantong",
                    "country_code": "CN",
                    "sector": [
                      {
                        "updated_at": "2022-01-27T17:36:54.597482Z",
                        "contributor_id": 4,
                        "contributor_name": "Researcher A",
                        "values": [
                          "Apparel"
                        ]
                      }
                    ],
                    "os_id": "CN2019303BQ3FZP",
                    "other_names": [],
                    "other_addresses": [],
                    "contributors": [
                      {
                        "id": 4,
                        "name": "Researcher A (Summer 2019 Affiliate List)",
                        "is_verified": false
                      }
                    ],
                    "country_name": "China",
                    "claim_info": null,
                    "other_locations": []
                  },
                  "confidence": 0,
                  "confirm_match_url": "/api/facility-matches/135005/confirm/",
                  "reject_match_url": "/api/facility-matches/135005/reject/"
                  "text_only_match": true
                }
              ],
              "item_id": 959,
              "geocoded_geometry": {
                "type": "Point",
                "coordinates": [
                  120.596047,
                  32.172013
                ]
              },
              "geocoded_address": "Guoyuanzhen, Rugao, Nantong, Jiangsu, China",
              "status": "POTENTIAL_MATCH"
            }


        ### New Facility

            {
              "matches": [],
              "item_id": 954,
              "geocoded_geometry": {
                "type": "Point",
                "coordinates": [
                  119.2221539,
                  33.79772
                ]
              },
              "geocoded_address": "30, 32 Yanhuang Ave, Lianshui Xian, Huaian Shi, Jiangsu Sheng, China, 223402",
              "status": "NEW_FACILITY"
            }

        ### No Match

            {
              "matches": [],
              "item_id": 965,
              "geocoded_geometry": null,
              "geocoded_address": null,
              "status": "ERROR_MATCHING"
            }

        ### Geocoder Returned No Results

            {
              "matches": [],
              "item_id": 965,
              "geocoded_geometry": null,
              "geocoded_address": null,
              "status": "GEOCODED_NO_RESULTS",
              "message": "The address you submitted can not be geocoded."
            }
        """  # noqa
        # Adding the @permission_classes decorator was not working so we
        # explicitly invoke our custom permission class.
        if not IsRegisteredAndConfirmed().has_permission(request, self):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if not flag_is_active(request._request,
                              FeatureGroups.CAN_SUBMIT_FACILITY):
            raise PermissionDenied()

        log.info(f'[API Upload] Uploading data: {request.data}')
        log.info('[API Upload] Started CC Parse process!')
        split_pattern = r', |,|\|'
        contri_cleaner = ContriCleanerSerializer(
            SourceParserJSON(request.data), SectorCache(), split_pattern
        )
        rows = contri_cleaner.get_validated_rows()
        row = rows[0]
        if row.errors:
            log.error(f'[API Upload] CC Parsing Errors: {row.errors}')
            return Response({
                "message": "The provided data could not be parsed",
                "errors": row.errors
            }, status=status.HTTP_400_BAD_REQUEST)

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

        parse_started = str(timezone.now())

        source = Source.objects.create(
            contributor=request.user.contributor,
            source_type=Source.SINGLE,
            is_public=public_submission,
            create=should_create
        )

        create_nonstandard_fields(
            list(row.fields.keys()),
            request.user.contributor
        )

        item = FacilityListItem.objects.create(
            source=source,
            row_index=0,
            raw_data=json.dumps(request.data),
            raw_json=row.raw_json,
            raw_header='',
            status=FacilityListItem.PARSED,
            name=row.name,
            clean_name=row.clean_name,
            address=row.address,
            clean_address=row.clean_address,
            country_code=row.country_code,
            sector=row.sector,
            processing_results=[{
                'action': ProcessingAction.PARSE,
                'started_at': parse_started,
                'error': False,
                'finished_at': str(timezone.now()),
                'is_geocoded': False,
            }]
        )

        log.info(f'[API Upload] Source created. Id: {source.id}')
        log.info(f'[API Upload] Source is public: {source.is_public}')
        log.info(f'[API Upload] Source should create: {source.create}')
        log.info(f'[API Upload] FacilityListItem created. Id: {item.id}')

        result = {
            'matches': [],
            'item_id': item.id,
            'geocoded_geometry': None,
            'geocoded_address': None,
            'status': item.status,
        }

        try:
            create_extendedfields_for_single_item(item, row.fields)
        except (core_exceptions.ValidationError, ValueError) as exc:
            error_message = ''

            if isinstance(exc, ValueError):
                error_message = str(exc)
            else:
                error_message = exc.message

            item.status = FacilityListItem.ERROR_PARSING
            item.processing_results.append({
                'action': ProcessingAction.PARSE,
                'started_at': parse_started,
                'error': True,
                'message': error_message,
                'trace': traceback.format_exc(),
                'finished_at': str(timezone.now()),
            })
            item.save()
            result['status'] = item.status
            result['message'] = error_message
            log.error(
                '[API Upload] Creation of ExtendedField error: '
                f'{error_message}'
            )
            log.info(f'[API Upload] FacilityListItem Id: {item.id}')
            return Response(result,
                            status=status.HTTP_400_BAD_REQUEST)

        geocode_started = str(timezone.now())
        log.info(
            '[API Upload] Started Geocode process. '
            f'FacilityListItem Id: {item.id}.'
        )
        log.info(
            f'[API Upload] Address: {row.address}, '
            f'Country Code: {row.country_code}'
        )
        try:
            geocode_result = geocode_address(row.address, row.country_code)
            if geocode_result['result_count'] > 0:
                item.status = FacilityListItem.GEOCODED
                item.geocoded_point = Point(
                    geocode_result["geocoded_point"]["lng"],
                    geocode_result["geocoded_point"]["lat"]
                )
                item.geocoded_address = geocode_result["geocoded_address"]

                result['geocoded_geometry'] = {
                    'type': 'Point',
                    'coordinates': [
                        geocode_result["geocoded_point"]["lng"],
                        geocode_result["geocoded_point"]["lat"],
                    ]
                }
                result['geocoded_address'] = item.geocoded_address
            else:
                item.status = FacilityListItem.GEOCODED_NO_RESULTS
                result['status'] = item.status
                result['message'] = ErrorMessages.GEOCODED_NO_RESULTS

            item.processing_results.append({
                'action': ProcessingAction.GEOCODE,
                'started_at': geocode_started,
                'error': False,
                'skipped_geocoder': False,
                'data': geocode_result['full_response'],
                'finished_at': str(timezone.now()),
            })

            item.save()
            # [A/B Test] OSHUB-507
            FacilityListItemTemp.copy(item)
        except Exception as exc:
            item.status = FacilityListItem.ERROR_GEOCODING
            item.processing_results.append({
                'action': ProcessingAction.GEOCODE,
                'started_at': geocode_started,
                'error': True,
                'message': str(exc),
                'trace': traceback.format_exc(),
                'finished_at': str(timezone.now()),
            })
            item.save()
            result['status'] = item.status
            log.error(f'[API Upload] Geocode Error: {str(exc)}')
            log.info(f'[API Upload] FacilityListItem Id: {item.id}')
            log.info(f'[API Upload] Address: {row.address}, '
                     f'Country Code: {row.country_code}')
            return Response(result,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if item.status == FacilityListItem.GEOCODED:
            log.info('[API Upload] Trying to start Match process!')
            log.info(f'[API Upload] FacilityListItem Id: {item.id}')
            log.info(f'[API Upload] Source Id: {item.id}')
            # Handle and produce message to Kafka with source_id data
            timer = 0
            timeout = 25
            fli_temp = None
            while True:
                if timer > timeout:
                    break
                fli_temp = FacilityListItemTemp.objects.get(
                    source=source.id
                )
                if fli_temp.status == FacilityListItemTemp.GEOCODED:
                    log.info('[API Upload] Started Match process!')
                    log.info(f'[API Upload] FacilityListItem Id: {item.id}')
                    log.info(
                        f'[API Upload] FacilityListItemTemp Id: {fli_temp.id}'
                    )
                    log.info(f'[API Upload] Source Id: {item.id}')
                    asyncio.run(produce_message_match_process(source.id))
                    break
                asyncio.sleep(1)
                timer = timer + 1

            # Handle results of "match" process from Dedupe Hub
            result = handle_external_match_process_result(
                fli_temp.id,
                result,
                request,
                should_create
            )

        errors_status = [FacilityListItem.ERROR_MATCHING,
                         FacilityListItem.GEOCODED_NO_RESULTS]

        log.info(f'[API Upload] Result data: {result}')
        log.info(f'[API Upload] FacilityListItem Id: {item.id}')
        log.info(f'[API Upload] Source Id: {item.id}')

        if (should_create
                and result['status'] not in errors_status):
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_200_OK)

    @swagger_auto_schema(auto_schema=None)
    @transaction.atomic
    def destroy(self, request, pk=None):
        if request.user.is_anonymous:
            raise NotAuthenticated()
        if not request.user.is_superuser:
            raise PermissionDenied()

        try:
            facility = Facility.objects.get(pk=pk)
        except Facility.DoesNotExist as exc:
            raise NotFound() from exc

        if facility.get_approved_claim() is not None:
            raise BadRequestException(
                'Facilities with approved claims cannot be deleted'
            )

        def delete_facility_match(match):
            match.changeReason = 'Deleted {}'.format(facility.id)
            match.delete()

        def delete_facility_list_item(item):
            item.status = FacilityListItem.DELETED
            item.processing_results.append({
                'action': ProcessingAction.DELETE_FACILITY,
                'started_at': now,
                'error': False,
                'finished_at': now,
                'deleted_os_id': facility.id,
            })
            item.facility = None
            item.save()

        def delete_facility_claim_review_notes(claim):
            notes = FacilityClaimReviewNote. \
                objects. \
                filter(claim=claim)
            for note in notes:
                note._change_reason = f'Deleted {facility.id}'
                note.delete()

        now = str(timezone.now())
        created_by_contributor = facility.created_from.source.contributor

        list_items = (
            FacilityListItem
            .objects
            .filter(facility=facility)
            .filter(
                Q(source__create=False) |
                Q(id=facility.created_from.id) |
                Q(source__contributor=created_by_contributor)
            )
        )
        for list_item in list_items:
            delete_facility_list_item(list_item)

        for match in facility.get_created_from_matches():
            delete_facility_match(match)

        other_matches = facility.get_other_matches()
        if other_matches.count() > 0:
            try:
                best_match = max(
                    other_matches.filter(
                        status__in=(FacilityMatch.AUTOMATIC,
                                    FacilityMatch.CONFIRMED)
                    ).exclude(
                        facility_list_item__geocoded_point__isnull=True
                    ).exclude(**{
                        "facility_list_item__source__contributor":
                            created_by_contributor}),
                    key=lambda m: m.confidence)
            except ValueError:
                # Raised when there are no AUTOMATIC or CONFIRMED matches
                best_match = None
            if best_match:
                for match in other_matches.filter(**{
                    "facility_list_item__source__contributor":
                    created_by_contributor
                }):
                    delete_facility_match(match)
                    delete_facility_list_item(match.facility_list_item)

                best_item = best_match.facility_list_item

                promoted_facility = (
                    Facility
                    .objects
                    .create(
                        name=best_item.name,
                        address=best_item.address,
                        country_code=best_item.country_code,
                        location=best_item.geocoded_point,
                        created_from=best_item,
                    )
                )

                (
                    FacilityAlias
                    .objects
                    .create(
                        os_id=facility.id,
                        facility=promoted_facility,
                        reason=FacilityAlias.DELETE
                    )
                )

                best_match.facility = promoted_facility
                best_match._change_reason = (
                    'Deleted {} and promoted {}'.format(
                        facility.id,
                        promoted_facility.id
                    )
                )
                best_match.save()

                best_item.facility = promoted_facility
                best_item.processing_results.append({
                    'action': ProcessingAction.PROMOTE_MATCH,
                    'started_at': now,
                    'error': False,
                    'finished_at': now,
                    'promoted_os_id': promoted_facility.id,
                })
                best_item.save()

                for other_match in other_matches:
                    if other_match.id != best_match.id:
                        other_match.facility = promoted_facility
                        other_match._change_reason = (
                            f'Deleted {facility.id} and'
                            f'promoted {promoted_facility.id}'
                        )
                        other_match.save()

                        other_item = other_match.facility_list_item
                        other_item.facility = promoted_facility
                        other_item.processing_results.append({
                            'action': ProcessingAction.PROMOTE_MATCH,
                            'started_at': now,
                            'error': False,
                            'finished_at': now,
                            'promoted_os_id': promoted_facility.id,
                        })
                        other_item.save()

                for alias in FacilityAlias.objects.filter(facility=facility):
                    os_id = alias.os_id
                    alias._change_reason = 'Deleted {} and promoted {}'.format(
                        facility.id,
                        promoted_facility.id)
                    alias.delete()
                    FacilityAlias.objects.create(
                        facility=promoted_facility,
                        os_id=os_id,
                        reason=FacilityAlias.DELETE)
            else:
                for other_match in other_matches:
                    delete_facility_match(other_match)
                    delete_facility_list_item(other_match.facility_list_item)

        claims = FacilityClaim.objects.filter(facility=facility)

        for claim in claims:
            delete_facility_claim_review_notes(claim)
            claim._change_reason = f'Deleted {facility.id}'
            claim.delete()

        for alias in FacilityAlias.objects.filter(facility=facility):
            alias._change_reason = f'Deleted {facility.id}'
            alias.delete()

        facility.delete()

        try:
            tile_version = Version.objects.get(name='tile_version')
            tile_version.version = F('version') + 1
            tile_version.save()
        except Version.DoesNotExist:
            pass

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(paginator_inspectors=[DisabledPaginationInspector],
                         responses={200: ''})
    @action(detail=False, methods=['get'])
    def count(self, _):
        """
        Returns a count of total Facilities available in Open Supply Hub.

        ### Sample Response
            { "count": 100000 }
        """
        return Response({
            "count": Facility.objects.count()
        })

    @swagger_auto_schema(auto_schema=None, methods=['POST'])
    @action(detail=True, methods=['POST'],
            permission_classes=(IsRegisteredAndConfirmed,))
    @transaction.atomic
    def claim(self, request, pk=None):
        if not switch_is_active('claim_a_facility'):
            raise NotFound()

        try:
            facility = Facility.objects.get(pk=pk)
            contributor = request.user.contributor

            contact_person = request.data.get('contact_person')
            job_title = request.data.get('job_title')
            email = request.data.get('email')
            phone_number = request.data.get('phone_number')
            company_name = request.data.get('company_name')
            parent_company = request.data.get('parent_company')
            website = request.data.get('website')
            facility_description = request.data.get('facility_description')
            verification_method = request.data.get('verification_method')
            preferred_contact_method = request \
                .data \
                .get('preferred_contact_method') or ''
            linkedin_profile = request.data.get('linkedin_profile', '')

            try:
                validate_email(email)
            except core_exceptions.ValidationError as exc:
                raise ValidationError(
                    'Valid email is required'
                ) from exc

            if not company_name:
                raise ValidationError('Company name is required')

            if parent_company:
                try:
                    parent_company_contributor = (
                        Contributor
                        .objects
                        .get(pk=parent_company)
                    )
                    parent_company_name = parent_company_contributor.name
                except ValueError:
                    parent_company_name = parent_company
                    parent_company_contributor = None
            else:
                parent_company_name = None
                parent_company_contributor = None

            user_has_pending_claims = (
                FacilityClaim
                .objects
                .filter(status=FacilityClaim.PENDING)
                .filter(facility=facility)
                .filter(contributor=contributor)
                .count() > 0
            )

            if user_has_pending_claims:
                raise BadRequestException(
                    'User already has a pending claim on this facility'
                )

            facility_claim = (
                FacilityClaim
                .objects
                .create(
                    facility=facility,
                    contributor=contributor,
                    contact_person=contact_person,
                    job_title=job_title,
                    email=email,
                    phone_number=phone_number,
                    company_name=company_name,
                    parent_company=parent_company_contributor,
                    parent_company_name=parent_company_name,
                    website=website,
                    facility_description=facility_description,
                    verification_method=verification_method,
                    preferred_contact_method=preferred_contact_method,
                    linkedin_profile=linkedin_profile
                )
            )
            send_claim_facility_confirmation_email(request, facility_claim)

            approved = (
                FacilityClaim
                .objects
                .filter(status=FacilityClaim.APPROVED)
                .filter(contributor=contributor)
                .values_list('facility__id', flat=True)
            )
            pending = (
                FacilityClaim
                .objects
                .filter(status=FacilityClaim.PENDING)
                .filter(contributor=contributor)
                .values_list('facility__id', flat=True)
            )
            return Response({
                'pending': pending,
                'approved': approved,
            })
        except Facility.DoesNotExist as exc:
            raise NotFound() from exc
        except Contributor.DoesNotExist as exc:
            raise NotFound() from exc

    @swagger_auto_schema(auto_schema=None, methods=['GET'])
    @action(detail=False, methods=['GET'],
            permission_classes=(IsRegisteredAndConfirmed,))
    @transaction.atomic
    def claimed(self, request):
        """
        Returns a list of facility claims made by the authenticated user that
        have been approved.
         ### Sample Response
            [
                {
                    "id": 1,
                    "created_at": "2019-06-10T17:28:17.155025Z",
                    "updated_at": "2019-06-10T17:28:17.155042Z",
                    "contributor_id": 1,
                    "os_id": "US2019161ABC123",
                    "contributor_name": "A Contributor",
                    "facility_name": "Clothing, Inc.",
                    "facility_address": "1234 Main St",
                    "facility_country": "United States",
                    "status": "APPROVED"
                }
            ]
        """

        if not switch_is_active('claim_a_facility'):
            raise NotFound()
        try:
            claims = FacilityClaim.objects.filter(
                contributor=request.user.contributor,
                status=FacilityClaim.APPROVED)
        except Contributor.DoesNotExist as exc:
            raise NotFound(
                'The current User does not have an associated Contributor'
            ) from exc
        return Response(FacilityClaimSerializer(claims, many=True).data)

    @swagger_auto_schema(auto_schema=None, methods=['POST'])
    @action(detail=False, methods=['POST'],
            permission_classes=(IsSuperuser,))
    @transaction.atomic
    def merge(self, request):
        params = FacilityMergeQueryParamsSerializer(data=request.query_params)

        if not params.is_valid():
            raise ValidationError(params.errors)
        target_id = request.query_params.get(FacilityMergeQueryParams.TARGET,
                                             None)
        merge_id = request.query_params.get(FacilityMergeQueryParams.MERGE,
                                            None)
        if target_id == merge_id:
            raise ValidationError({
                FacilityMergeQueryParams.TARGET: [
                    f'Cannot be the same as {FacilityMergeQueryParams.MERGE}.'
                ],
                FacilityMergeQueryParams.MERGE: [
                    f'Cannot be the same as {FacilityMergeQueryParams.TARGET}.'
                ]
            })

        target = Facility.objects.get(id=target_id)
        merge = Facility.objects.get(id=merge_id)

        inactive_match_statuses = (FacilityMatch.PENDING,
                                   FacilityMatch.REJECTED)
        now = str(timezone.now())
        for merge_match in merge.facilitymatch_set.all():
            merge_match.facility = target
            if merge_match.status not in inactive_match_statuses:
                merge_match.status = FacilityMatch.MERGED
            merge_match._change_reason = f'Merged {merge.id} into {target.id}'
            merge_match.save()

            if merge_match.status not in inactive_match_statuses:
                merge_item = merge_match.facility_list_item
                merge_item.facility = target
                merge_item.processing_results.append({
                    'action': ProcessingAction.MERGE_FACILITY,
                    'started_at': now,
                    'error': False,
                    'finished_at': now,
                    'merged_os_id': merge.id,
                })
                merge_item.save()

        # Submitting facilities through the API with create=false will create a
        # FacilityListItem record but not a FacilityMatch. This loop handles
        # updating any items that still reference the merge facility.
        unmatched_items = FacilityListItem.objects.filter(facility=merge)
        for unmatched_item in unmatched_items:
            unmatched_item.facility = target
            unmatched_item.processing_results.append({
                'action': ProcessingAction.MERGE_FACILITY,
                'started_at': now,
                'error': False,
                'finished_at': now,
                'merged_os_id': merge.id,
            })
            unmatched_item.save()

        target_has_approved_claim = FacilityClaim.objects.filter(
            facility=target, status=FacilityClaim.APPROVED).exists()
        merge_claims = FacilityClaim.objects.filter(facility=merge)
        for claim in merge_claims:
            claim.facility = target
            should_change_status = (
                claim.status in (FacilityClaim.APPROVED, FacilityClaim.PENDING)
                and target_has_approved_claim)
            if should_change_status:
                claim.status = (
                    FacilityClaim.REVOKED
                    if claim.status == FacilityClaim.APPROVED
                    else FacilityClaim.DENIED)
                claim.status_change_by = request.user
                claim.status_change_date = timezone.now()
                change_reason_template = (
                    f'Merging {merge.id} into {target.id} '
                    'which already has an approved claim'
                )
                claim.status_change_reason = change_reason_template
                claim._change_reason = change_reason_template
            else:
                claim._change_reason = \
                    f'Merging {merge.id} into {target.id}'
            claim.save()

        for field in ExtendedField.objects.filter(facility=merge):
            field.facility = target
            field.save()

        for alias in FacilityAlias.objects.filter(facility=merge):
            os_id = alias.os_id
            alias._change_reason = 'Merging {} into {}'.format(
                merge.id,
                target.id)
            alias.delete()
            FacilityAlias.objects.create(
                facility=target,
                os_id=os_id,
                reason=FacilityAlias.MERGE)

        FacilityAlias.objects.create(
            os_id=merge.id,
            facility=target,
            reason=FacilityAlias.MERGE)
        # any change to this message will also need to
        # be made in the `facility_history.py` module's
        # `create_facility_history_dictionary` function
        merge._change_reason = 'Merged with {}'.format(target.id)

        FacilityIndex.objects.get(id=merge.id).delete()
        merge.delete()

        target.refresh_from_db()
        context = {'request': request}
        facility_index = FacilityIndex.objects.get(id=target.id)
        response_data = FacilityIndexDetailsSerializer(
            facility_index, context=context).data
        return Response(response_data)

    @swagger_auto_schema(auto_schema=None, methods=['GET', 'POST'])
    @action(detail=True, methods=['GET', 'POST'],
            permission_classes=(IsSuperuser,))
    @transaction.atomic
    def split(self, request, pk=None):
        try:
            if request.method == 'GET':
                facility = Facility.objects.get(pk=pk)
                context = {'request': request}
                facility_index = FacilityIndex.objects.get(id=facility.id)
                facility_data = FacilityIndexDetailsSerializer(
                    facility_index, context=context).data

                facility_data['properties']['matches'] = [
                    {
                        'name': m.facility_list_item.name,
                        'address': m.facility_list_item.address,
                        'country_code': m.facility_list_item.country_code,
                        'list_id':
                        m.facility_list_item.source.facility_list.id
                        if m.facility_list_item.source.facility_list else None,
                        'list_name':
                        m.facility_list_item.source.facility_list.name
                        if m.facility_list_item.source.facility_list else None,
                        'list_description':
                        m.facility_list_item.source.facility_list.description
                        if m.facility_list_item.source.facility_list else None,
                        'list_contributor_name':
                        m.facility_list_item.source.contributor.name
                        if m.facility_list_item.source.contributor else None,
                        'list_contributor_id':
                        m.facility_list_item.source.contributor.id
                        if m.facility_list_item.source.contributor else None,
                        'match_id': m.id,
                        'is_geocoded':
                        m.facility_list_item.geocoded_point is not None,
                        'status': m.status,
                        'is_active': m.is_active,
                        'confidence': m.confidence,
                        'facility_created_by_item':
                        Facility.objects.filter(
                            created_from=m.facility_list_item.id)[0].id
                        if Facility.objects.filter(
                            created_from=m.facility_list_item.id).exists()
                        else None,
                        'transferred_from':
                        [r for r
                            in m.facility_list_item.processing_results
                            if r.get('action', '')
                            == ProcessingAction.MOVE_FACILITY]
                            [0]['previous_facility_os_id']
                            if len(
                                [r for r
                                    in m.facility_list_item.processing_results
                                    if r.get('action', '')
                                    == ProcessingAction.MOVE_FACILITY]) > 0
                            else None,
                    }
                    for m
                    in facility.get_other_matches()
                ]

                return Response(facility_data)

            match_id = request.data.get('match_id')

            if match_id is None:
                raise BadRequestException('Missing required param match_id')

            match_for_new_facility = FacilityMatch \
                .objects \
                .get(pk=match_id)

            old_facility = match_for_new_facility.facility

            list_item_for_match = match_for_new_facility.facility_list_item

            if list_item_for_match.geocoded_point is None:
                raise ValidationError('The match can not be split because '
                                      'it does not have a location.')

            facility_qs = Facility.objects.filter(
                created_from=list_item_for_match)
            if facility_qs.exists():
                # `Facility.created_by` must be unique. If the item was
                # previously used to create a facility, we must related it to
                # that existing facility rather than creating a new facility
                new_facility = facility_qs[0]
            else:
                new_facility = Facility \
                    .objects \
                    .create(
                        name=list_item_for_match.name,
                        address=list_item_for_match.address,
                        country_code=list_item_for_match.country_code,
                        location=list_item_for_match.geocoded_point,
                        created_from=list_item_for_match)

            match_for_new_facility.facility = new_facility
            match_for_new_facility.confidence = 1.0
            match_for_new_facility.status = FacilityMatch.CONFIRMED
            match_for_new_facility.results = {
                'match_type': 'split_by_administator',
                'split_from_os_id': match_for_new_facility.facility.id,
            }

            match_for_new_facility.save()

            now = str(timezone.now())

            list_item_for_match.facility = new_facility
            list_item_for_match.processing_results.append({
                'action': ProcessingAction.SPLIT_FACILITY,
                'started_at': now,
                'error': False,
                'finished_at': now,
                'previous_facility_os_id': old_facility.id,
            })

            list_item_for_match.save()

            fields = ExtendedField.objects.filter(
                facility_list_item=list_item_for_match)
            for field in fields:
                field.facility = new_facility
                field.save()

            index_facilities_new([new_facility.id, old_facility.id])

            return Response({
                'match_id': match_for_new_facility.id,
                'new_os_id': new_facility.id,
            })
        except FacilityListItem.DoesNotExist as exc:
            raise NotFound() from exc
        except FacilityMatch.DoesNotExist as exc:
            raise NotFound() from exc
        except Facility.DoesNotExist as exc:
            raise NotFound() from exc

    @swagger_auto_schema(auto_schema=None, methods=['POST'])
    @action(detail=True, methods=['POST'],
            permission_classes=(IsSuperuser,))
    @transaction.atomic
    def move(self, request, pk=None):
        try:
            match_id = request.data.get('match_id')

            if match_id is None:
                raise BadRequestException('Missing required param match_id')

            match = FacilityMatch.objects.get(pk=match_id)
            old_facility = match.facility
            list_item_for_match = match.facility_list_item

            new_facility = Facility.objects.get(pk=pk)

            match.facility = new_facility
            match.confidence = 1.0
            match.status = FacilityMatch.CONFIRMED
            match.results = {
                'match_type': 'moved_by_administator',
                'move_to_os_id': match.facility.id,
            }

            match.save()

            now = str(timezone.now())

            list_item_for_match.facility = new_facility
            list_item_for_match.processing_results.append({
                'action': ProcessingAction.MOVE_FACILITY,
                'started_at': now,
                'error': False,
                'finished_at': now,
                'previous_facility_os_id': old_facility.id,
            })

            list_item_for_match.save()

            fields = ExtendedField.objects.filter(
                facility_list_item=list_item_for_match)
            for field in fields:
                field.facility = new_facility
                field.save()

            return Response({
                'match_id': match.id,
                'new_os_id': new_facility.id,
            })

        except FacilityListItem.DoesNotExist as exc:
            raise NotFound() from exc
        except FacilityMatch.DoesNotExist as exc:
            raise NotFound() from exc
        except Facility.DoesNotExist as exc:
            raise NotFound() from exc

    @swagger_auto_schema(auto_schema=None, methods=['POST'])
    @action(detail=True, methods=['POST'],
            permission_classes=(IsSuperuser,))
    @transaction.atomic
    def promote(self, request, pk=None):
        match_id = request.data.get('match_id')

        if match_id is None:
            raise BadRequestException('Missing required param match_id')

        try:
            facility = Facility.objects.get(pk=pk)
            match = FacilityMatch.objects.get(pk=match_id)

            matched_statuses = [
                FacilityListItem.MATCHED,
                FacilityListItem.CONFIRMED_MATCH,
            ]

            if match.facility_list_item.status not in matched_statuses:
                raise BadRequestException('Incorrect list item status')

            if match.facility.id != facility.id:
                raise BadRequestException('Match is not to facility')

            if facility.created_from.id == match.facility_list_item.id:
                raise BadRequestException('Facility is created from item.')

            previous_created_from_id = facility.created_from.id

            item = match.facility_list_item.id
            if match.facility_list_item.source.facility_list:
                list = match.facility_list_item.source.facility_list.id
                new_desc = f'item {item} in list {list}'
            else:
                new_desc = f'item {item}'

            item = previous_created_from_id
            if facility.created_from.source.facility_list:
                list = facility.created_from.source.facility_list.id
                previous_desc = f'item {item} in list {list}'
            else:
                previous_desc = f'item {item}'

            reason = f'Promoted {new_desc} over {previous_desc}'

            facility.name = match.facility_list_item.name
            facility.address = match.facility_list_item.address
            facility.country_code = match.facility_list_item.country_code
            facility.location = match.facility_list_item.geocoded_point
            facility.created_from = match.facility_list_item
            facility._change_reason = reason
            facility.save()

            now = str(timezone.now())

            match.facility_list_item.processing_results.append({
                'action': ProcessingAction.PROMOTE_MATCH,
                'started_at': now,
                'error': False,
                'finished_at': now,
                'previous_created_from_id': previous_created_from_id,
            })

            match.facility_list_item.save()

            facility.refresh_from_db()
            context = {'request': request}
            facility_index = FacilityIndex.objects.get(id=facility.id)
            facility_data = FacilityIndexDetailsSerializer(
                facility_index, context=context).data

            facility_data['properties']['matches'] = [
                {
                    'name': m.facility_list_item.name,
                    'address': m.facility_list_item.address,
                    'country_code': m.facility_list_item.country_code,
                    'list_id': m.facility_list_item.source.facility_list.id
                    if m.facility_list_item.source.facility_list else None,
                    'list_name':
                    m.facility_list_item.source.facility_list.name
                    if m.facility_list_item.source.facility_list else None,
                    'list_description':
                    m.facility_list_item.source.facility_list.description
                    if m.facility_list_item.source.facility_list else None,
                    'list_contributor_name':
                    m.facility_list_item.source.contributor.name
                    if m.facility_list_item.source.contributor else None,
                    'list_contributor_id':
                    m.facility_list_item.source.contributor.id
                    if m.facility_list_item.source.contributor else None,
                    'match_id': m.id,
                }
                for m
                in facility.get_other_matches()
            ]

            return Response(facility_data)
        except FacilityListItem.DoesNotExist as exc:
            raise NotFound() from exc
        except FacilityMatch.DoesNotExist as exc:
            raise NotFound() from exc
        except Facility.DoesNotExist as exc:
            raise NotFound() from exc

    @swagger_auto_schema(auto_schema=None, methods=['POST'])
    @action(detail=True, methods=['POST'],
            permission_classes=(IsSuperuser,),
            url_path='update-location')
    @transaction.atomic
    def update_location(self, request, pk=None):
        try:
            facility = Facility.objects.get(pk=pk)
        except Facility.DoesNotExist as exc:
            raise NotFound() from exc

        params = FacilityUpdateLocationParamsSerializer(data=request.data)
        if not params.is_valid():
            raise ValidationError(params.errors)

        facility_location = FacilityLocation(
            facility=facility,
            location=Point(
                float(request.data[UpdateLocationParams.LNG]),
                float(request.data[UpdateLocationParams.LAT])
            ),
            notes=request.data.get('notes', ''),
            created_by=request.user,
        )
        contributor_id = request.data.get(
            UpdateLocationParams.CONTRIBUTOR_ID, None)

        if contributor_id is not None:
            facility_location.contributor = \
                Contributor.objects.get(id=contributor_id)
        facility_location.save()

        facility.location = facility_location.location
        # any change to this message will also need to
        # be made in the `facility_history.py` module's
        # `create_facility_history_dictionary` function
        facility._change_reason = \
            f'Submitted a new FacilityLocation ({facility_location.id})'
        facility.save()

        context = {'request': request}
        facility_index = FacilityIndex.objects.get(id=facility.id)
        facility_data = FacilityIndexDetailsSerializer(
            facility_index, context=context).data
        return Response(facility_data)

    @swagger_auto_schema(responses={200: ''})
    @action(detail=True, methods=['GET'],
            permission_classes=(IsRegisteredAndConfirmed,),
            url_path='history')
    def get_facility_history(self, request, pk=None):
        """
        Returns the history of changes to a facility as a list of dictionaries
        describing the changes.

        ### Sample Response
            [
                {
                    "updated_at": "2019-09-12T02:43:19Z",
                    "action": "DELETE",
                    "detail": "Deleted facility"
                },
                {
                    "updated_at": "2019-09-05T13:15:30Z",
                    "action": "UPDATE",
                    "changes": {
                        "location": {
                            "old": {
                                "type": "Point",
                                "coordinates": [125.6, 10.1]
                            },
                            "new": {
                                "type": "Point",
                                "coordinates": [125.62, 10.14]
                            }
                        }
                    },
                    "detail": "FacilityLocation was changed"
                },
                {
                    "updated_at": "2019-09-02T21:04:30Z",
                    "action": "MERGE",
                    "detail": "Merged with US2019123AG4RD"
                },
                {
                    "updated_at": "2019-09-01T21:04:30Z",
                    "action": "CREATE",
                    "detail": "Facility was created"
                }
            ]
        """
        if not flag_is_active(request._request,
                              FeatureGroups.CAN_GET_FACILITY_HISTORY):
            raise PermissionDenied()

        historical_facility_queryset = Facility.history.filter(id=pk)

        if historical_facility_queryset.count() == 0:
            raise NotFound()

        facility_history = create_facility_history_list(
            historical_facility_queryset,
            pk,
            user=request.user
        )

        return Response(facility_history)

    @swagger_auto_schema(request_body=no_body,
                         responses={200: FacilityIndexDetailsSerializer})
    @action(detail=True, methods=['POST'],
            permission_classes=(IsRegisteredAndConfirmed,),
            url_path='dissociate')
    @transaction.atomic
    def dissociate(self, request, pk=None):
        """
        Deactivate any matches to the facility submitted by the authenticated
        contributor

        Returns the facility details with an updated contributor list.

        ### Sample response
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "id": "OS_ID_1",
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [1, 1]
                        },
                        "properties": {
                            "name": "facility_name_1",
                            "address" "facility address_1",
                            "country_code": "US",
                            "country_name": "United States",
                            "os_id": "OS_ID_1",
                            "contributors": [
                                {
                                    "id": 1,
                                    "name": "Brand A (2019 Q1 List)",
                                    "is_verified": false
                                }
                            ]
                        }
                    },
                    {
                        "id": "OS_ID_2",
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [2, 2]
                        },
                        "properties": {
                            "name": "facility_name_2",
                            "address" "facility address_2",
                            "country_code": "US",
                            "country_name": "United States",
                            "os_id": "OS_ID_2"
                            "contributors": [
                                {
                                    "id": 1,
                                    "name": "Brand A (2019 Q1 List)",
                                    "is_verified": false
                                },
                                {
                                    "id": 2,
                                    "name": "An MSI",
                                    "is_verified": false
                                }
                            ]
                        }
                    }
                ]
            }

        """
        try:
            facility = Facility.objects.get(pk=pk)
        except Facility.DoesNotExist as exc:
            raise NotFound(f'Facility with OS ID {pk} not found') from exc

        contributor = request.user.contributor
        matches = FacilityMatch.objects.filter(
            facility=facility,
            facility_list_item__source__contributor=contributor)

        # Call `save` in a loop rather than use `update` to make sure that
        # django-simple-history can log the changes
        if matches.count() > 0:
            for match in matches:
                if match.is_active:
                    match.is_active = False
                    match._change_reason = \
                        create_dissociate_match_change_reason(
                            match.facility_list_item,
                            facility)
                    match.save()

        context = {'request': request}
        facility_index = FacilityIndex.objects.get(id=facility.id)
        facility_data = FacilityIndexDetailsSerializer(
            facility_index, context=context).data
        return Response(facility_data)

    @swagger_auto_schema(request_body=Schema(
        'data',
        type=TYPE_OBJECT,
        description='The closure state of the facility. Must be OPEN or '
                    'CLOSED. See the sample request body above.',
    ), responses={200: FacilityActivityReportSerializer})
    @action(detail=True, methods=['POST'],
            permission_classes=(IsRegisteredAndConfirmed,),
            url_path='report')
    @transaction.atomic
    def report(self, request, pk=None):
        """
        Report that a facility has been closed or opened.

        ## Sample Request Body

            {
                "closure_state": "CLOSED",
                "reason_for_report": "This facility was closed."
            }
        """
        try:
            facility = Facility.objects.get(pk=pk)
        except Facility.DoesNotExist as exc:
            raise NotFound(
                'Facility with OS ID {} not found'.format(pk)
            ) from exc

        try:
            contributor = request.user.contributor
        except Contributor.DoesNotExist as exc:
            raise ValidationError(
                'Contributor not found for requesting user.'
                ) from exc

        facility_activity_report = FacilityActivityReport.objects.create(
            facility=facility,
            reported_by_user=request.user,
            reported_by_contributor=contributor,
            closure_state=request.data.get('closure_state'),
            reason_for_report=request.data.get('reason_for_report'))

        try:
            facility_activity_report.full_clean()
        except core_exceptions.ValidationError as exc:
            raise BadRequestException(
                'Closure state must be CLOSED or OPEN.'
            ) from exc

        facility_activity_report.save()

        serializer = FacilityActivityReportSerializer(facility_activity_report)
        return Response(serializer.data)

    @swagger_auto_schema(auto_schema=None, methods=['POST'])
    @action(detail=True, methods=['POST'],
            permission_classes=(IsSuperuser,))
    @transaction.atomic
    def link(self, request, pk=None):
        try:
            new_os_id = request.data.get('new_os_id')
            if new_os_id is None:
                raise BadRequestException('Missing required param new_os_id')
            if not Facility.objects.filter(pk=new_os_id).exists():
                raise BadRequestException('Invalid param new_os_id')

            source_facility = Facility.objects.get(pk=pk)
            source_facility.new_os_id = new_os_id

            source_facility.save()

            context = {'request': request}
            facility_index = FacilityIndex.objects.get(
                id=source_facility.id)
            facility_data = FacilityIndexDetailsSerializer(
                facility_index, context=context).data
            return Response(facility_data)

        except Facility.DoesNotExist as exc:
            raise NotFound() from exc
