import operator
import os
import logging
from functools import reduce
from waffle import switch_is_active

from oar.settings import (
    MAX_UPLOADED_FILE_SIZE_IN_BYTES,
    DEBUG
)
from rest_framework.decorators import action
from rest_framework.exceptions import (
    NotFound,
    ValidationError
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.core.files.uploadedfile import (
    InMemoryUploadedFile,
    TemporaryUploadedFile
)
from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone

from ...aws_batch import submit_jobs, submit_parse_job
from api.constants import (
    FacilityListItemsQueryParams,
    ProcessingAction,
    APIErrorMessages,
)
from api.exceptions import ServiceUnavailableException
from ...facility_history import create_dissociate_match_change_reason
from ...mail import send_facility_list_rejection_email
from ...models.contributor.contributor import Contributor
from ...models.facility.facility_list import FacilityList
from ...models.facility.facility_list_item import FacilityListItem
from ...models.facility.facility_match import FacilityMatch
from ...models.source import Source
from ...models.user import User
from ...permissions import (
    IsRegisteredAndConfirmed,
    IsSuperuser
)
from ...serializers import (
    FacilityListSerializer,
    FacilityListItemSerializer,
    FacilityListItemsQueryParamsSerializer,
)

log = logging.getLogger(__name__)


class FacilityListViewSet(ModelViewSet):
    """
    Upload and update facility lists for an authenticated Contributor.
    """
    queryset = FacilityList.objects.all()
    serializer_class = FacilityListSerializer
    permission_classes = [IsRegisteredAndConfirmed]
    http_method_names = ['get', 'post', 'head', 'options', 'trace']
    swagger_schema = None

    @transaction.atomic
    def create(self, request):
        """
        Upload a new Facility List.

        ## Request Body

        *Required*

        `file` (`file`): CSV file to upload.

        *Optional*

        `name` (`string`): Name of the uploaded file.

        `description` (`string`): Description of the uploaded file.

        `replaces` (`number`): An optional ID for an existing list to replace
                   with the new list

        ### Sample Response

            {
                "id": 1,
                "name": "list name",
                "description": "list description",
                "file_name": "list-1.csv",
                "is_active": true,
                "is_public": true
            }
        """
        if switch_is_active('disable_list_uploading'):
            raise ServiceUnavailableException(
                APIErrorMessages.MAINTENANCE_MODE
            )
        if 'file' not in request.data:
            raise ValidationError('No file specified.')
        uploaded_file = request.data['file']
        if type(uploaded_file) not in (
                InMemoryUploadedFile, TemporaryUploadedFile):
            raise ValidationError('File not submitted properly.')
        if uploaded_file.size > MAX_UPLOADED_FILE_SIZE_IN_BYTES:
            mb = MAX_UPLOADED_FILE_SIZE_IN_BYTES / (1024*1024)
            raise ValidationError(
                'Uploaded file exceeds the maximum size of {:.1f}MB.'.format(
                    mb))

        try:
            contributor = request.user.contributor
        except Contributor.DoesNotExist as exc:
            raise ValidationError(
                'User contributor cannot be None'
            ) from exc

        if 'name' in request.data:
            name = request.data['name']
        else:
            name = os.path.splitext(uploaded_file.name)[0]

        if '|' in name:
            raise ValidationError('Name cannot contain the "|" character.')

        if 'description' in request.data:
            description = request.data['description']
        else:
            description = None

        if description is not None and '|' in description:
            raise ValidationError(
                'Description cannot contain the "|" character.'
            )

        replaces = None
        if 'replaces' in request.data:
            try:
                replaces = int(request.data['replaces'])
            except ValueError as exc:
                raise ValidationError(
                    '"replaces" must be an integer ID.'
                ) from exc
            old_list_qs = FacilityList.objects.filter(
                source__contributor=contributor, pk=replaces)
            if old_list_qs.count() == 0:
                raise ValidationError(
                    f'{replaces} is not a valid FacilityList ID.'
                )
            replaces = old_list_qs[0]
            if FacilityList.objects.filter(replaces=replaces).count() > 0:
                raise ValidationError(
                    f'FacilityList {replaces.pk} has already been replaced.'
                )

        new_list = FacilityList.objects.create(
            name=name,
            description=description,
            file_name=uploaded_file.name,
            file=uploaded_file,
            replaces=replaces,
            match_responsibility=contributor.match_responsibility)
        log.info(f'[List Upload] FacilityList created. ID {new_list.id}.')
        log.info(
            '[List Upload] File saved: name=%s bucket=%s storage=%s',
            uploaded_file.name,
            # getattr(settings, "AWS_STORAGE_BUCKET_NAME", None),
            # getattr(settings, "DEFAULT_FILE_STORAGE", None),
        )

        source = Source.objects.create(
            contributor=contributor,
            source_type=Source.LIST,
            facility_list=new_list)
        log.info(f'[List Upload] Source created. ID {source.id}.')

        if not DEBUG:
            submit_parse_job(new_list)

        serializer = self.get_serializer(new_list)
        return Response(serializer.data)

    def list(self, request):
        """
        Returns Facility Lists for an authenticated Contributor.

        ## Sample Response
            [
                {
                    "id":16,
                    "name":"11",
                    "description":"list 11",
                    "file_name":"11.csv",
                    "is_active":true,
                    "is_public":true
                },
                {
                    "id":15,
                    "name":"old list 11",
                    "description":"old list 11",
                    "file_name":"11.csv",
                    "is_active":false,
                    "is_public":true
                }
            ]
        """
        try:
            facility_lists = (
                FacilityList
                .objects
                .select_related('replaced_by')
                .filter(source__contributor=request.user.contributor)
                .order_by('-created_at')
            )
        except User.contributor.RelatedObjectDoesNotExist as exc:
            raise ValidationError('User contributor cannot be None') from exc

        return Response(
            self.serializer_class(facility_lists, many=True).data
        )

    def retrieve(self, request, pk):
        """
        Returns data describing a single Facility List.

        ## Sample Response
            {
                "id": 16,
                "name": "list 11",
                "description": "list 11 description",
                "file_name": "11.csv",
                "is_active": true,
                "is_public": true,
                "item_count": 100,
                "item_url": "/api/facility-lists/16/items/"
            }
        """
        try:
            if request.user.is_superuser:
                facility_lists = FacilityList.objects.all()
            else:
                facility_lists = FacilityList.objects.filter(
                    source__contributor=request.user.contributor)

            facility_lists = facility_lists.select_related('replaced_by')

            facility_list = facility_lists.get(pk=pk)
            response_data = self.serializer_class(facility_list).data

            return Response(response_data)
        except FacilityList.DoesNotExist as exc:
            raise NotFound() from exc

    @action(detail=True, methods=['POST'],
            permission_classes=(IsSuperuser,),
            url_path='approve')
    def approve(self, request, pk=None):
        """
        Approve a facility list and trigger batch processing.

        ## Sample Request Body

            {
                "status_change_reason": "The facility data was confirmed."
            }
        """
        try:
            facility_list = self.queryset.get(id=pk)
        except FacilityList.DoesNotExist as exc:
            raise NotFound() from exc

        facility_list.status_change_reason = request.data.get('reason', '')
        facility_list.status_change_by = request.user
        facility_list.status = FacilityList.APPROVED
        facility_list.save()

        if not DEBUG:
            submit_jobs(facility_list)

        return Response(
            self.serializer_class(facility_list).data
        )

    @action(detail=True, methods=['POST'],
            permission_classes=(IsSuperuser,),
            url_path='reject')
    def reject(self, request, pk=None):
        """
        Reject a facility list and send a rejection email.

        ## Sample Request Body

            {
                "status_change_reason": "The CSV is formatted incorrectly."
            }
        """
        try:
            facility_list = self.queryset.select_related('source').get(id=pk)
        except FacilityList.DoesNotExist as exc:
            raise NotFound() from exc

        facility_list.status_change_reason = request.data.get('reason', '')
        facility_list.status_change_by = request.user
        facility_list.status = FacilityList.REJECTED
        facility_list.save()

        source = facility_list.source
        source.is_active = False
        source.save()

        send_facility_list_rejection_email(request, facility_list)

        return Response(self.serializer_class(facility_list).data)

    @action(detail=True, methods=['get'])
    def items(self, request, pk):
        """
        Returns data about a single page of Facility List Items.

        ## Sample Response
            {
                "count": 25,
                "next": "/api/facility-lists/16/items/?page=2&pageSize=20",
                "previous": null,
                "results": [
                    "id": 1,
                    "matches": [],
                    "country_name": "United States",
                    "processing_errors": null,
                    "matched_facility": null,
                    "row_index": 1,
                    "raw_data": "List item 1, List item address 1",
                    "status": "GEOCODED",
                    "processing_started_at": null,
                    "processing_completed_at": null,
                    "name": "List item 1",
                    "address": "List item address 1",
                    "country_code": "US",
                    "facility_list": 16
                ],
                ...
            }
        """

        special_case_q_statements = {
            FacilityListItem.NEW_FACILITY: Q(
                Q(status__in=('MATCHED', 'CONFIRMED_MATCH')) &
                Q(facility__created_from_id=F('id')) &
                ~Q(facilitymatch__is_active=False)),
            FacilityListItem.MATCHED: Q(
                Q(status='MATCHED') &
                ~Q(facility__created_from_id=F('id')) &
                ~Q(facilitymatch__is_active=False)),
            FacilityListItem.CONFIRMED_MATCH: Q(
                Q(status='CONFIRMED_MATCH') &
                ~Q(facility__created_from_id=F('id')) &
                ~Q(facilitymatch__is_active=False)),
            FacilityListItem.REMOVED: Q(
                Q(facilitymatch__is_active=False) |
                Q(status=FacilityListItem.ITEM_REMOVED)),
        }

        def make_q_from_status(status):
            if status in special_case_q_statements:
                return (special_case_q_statements[status])
            else:
                return Q(status=status)

        params = FacilityListItemsQueryParamsSerializer(
            data=request.query_params
        )
        if not params.is_valid():
            raise ValidationError(params.errors)

        search = request.query_params.get(
            FacilityListItemsQueryParams.SEARCH)
        status = request.query_params.getlist(
            FacilityListItemsQueryParams.STATUS)

        if search is not None:
            search = search.strip()

        try:
            if request.user.is_superuser:
                facility_lists = FacilityList.objects.all()
            else:
                facility_lists = FacilityList.objects.filter(
                    source__contributor=request.user.contributor)

            facility_list = facility_lists.get(pk=pk)
        except FacilityList.DoesNotExist as exc:
            raise NotFound() from exc

        queryset = (
            FacilityListItem
            .objects
            .filter(source=facility_list.source)
        )
        if search is not None and len(search) > 0:
            queryset = queryset.filter(
                Q(facility__name__icontains=search) |
                Q(facility__address__icontains=search) |
                Q(name__icontains=search) |
                Q(address__icontains=search))
        if status is not None and len(status) > 0:
            q_statements = [make_q_from_status(s) for s in status]
            queryset = queryset.filter(reduce(operator.or_, q_statements))

        queryset = queryset.order_by('row_index')

        page_queryset = self.paginate_queryset(queryset)
        if page_queryset is not None:
            serializer = FacilityListItemSerializer(page_queryset,
                                                    many=True)
            return self.get_paginated_response(serializer.data)

        serializer = FacilityListItemSerializer(queryset, many=True)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['post'],
            url_path='remove')
    def remove_item(self, request, pk=None):
        try:
            facility_list = FacilityList.objects.get(pk=pk)
            is_users_facility = request.user.has_contributor and \
                request.user.contributor == facility_list.source.contributor

            if not is_users_facility and not request.user.is_superuser:
                raise FacilityList.DoesNotExist

            facility_list_item = (
                FacilityListItem
                .objects
                .filter(source=facility_list.source)
                .get(pk=request.data.get('list_item_id'))
            )
            matches_to_deactivate = (
                FacilityMatch
                .objects
                .filter(facility_list_item=facility_list_item)
            )
            if len(matches_to_deactivate) == 0:
                now = str(timezone.now())
                facility_list_item.processing_results.append({
                    'action': ProcessingAction.ITEM_REMOVED,
                    'started_at': now,
                    'error': False,
                    'finished_at': now,
                })
                facility_list_item.status = FacilityListItem.ITEM_REMOVED
                facility_list_item.save()

            else:
                # Call `save` in a loop rather than use `update` to make sure
                # that django-simple-history can log the changes
                for item in matches_to_deactivate:
                    item.is_active = False
                    reason = create_dissociate_match_change_reason(
                        facility_list_item,
                        item.facility,
                    )

                    item._change_reason = reason
                    item.save()

            facility_list_item.refresh_from_db()

            response_data = FacilityListItemSerializer(facility_list_item).data

            response_data['list_statuses'] = (facility_list
                                              .source
                                              .facilitylistitem_set
                                              .values_list('status', flat=True)
                                              .distinct())

            return Response(response_data)
        except FacilityList.DoesNotExist as exc:
            raise NotFound() from exc
        except FacilityListItem.DoesNotExist as exc:
            raise NotFound() from exc
        except FacilityMatch.DoesNotExist as exc:
            raise NotFound() from exc
