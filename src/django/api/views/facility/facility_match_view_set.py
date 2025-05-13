from drf_yasg.utils import no_body, swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.exceptions import (
    ValidationError,
)
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from ...constants import (
    MatchResponsibility,
    ProcessingAction,
)
from ...facility_history import create_associate_match_change_reason
from ...extended_fields import update_extendedfields_for_list_item
from ...models.facility.facility import Facility
from ...models.facility.facility_list_item import FacilityListItem
from ...models.facility.facility_match import FacilityMatch
from ...models.source import Source
from ...permissions import IsRegisteredAndConfirmed
from ...serializers import (
    FacilityListItemSerializer,
    FacilityMatchSerializer,
)


class FacilityMatchViewSet(RetrieveModelMixin, GenericViewSet):
    queryset = FacilityMatch.objects.all()
    serializer_class = FacilityMatchSerializer
    permission_classes = (IsRegisteredAndConfirmed,)

    def validate_request(self, request, pk):
        filter = self.queryset.filter(pk=pk)
        matches_contributor = Q(
            facility_list_item__source__contributor__admin_id=request.user.pk)
        has_no_list = Q(facility_list_item__source__facility_list=None)
        allows_contributor = Q(
            facility_list_item__source__facility_list__match_responsibility=(
                MatchResponsibility.CONTRIBUTOR))
        allows_superuser = Q(
            facility_list_item__source__facility_list__match_responsibility=(
                MatchResponsibility.MODERATOR)
        )

        # We only allow retrieving matches to items that the logged in
        # user has submitted that they are allowed to moderate
        contributor_filter = matches_contributor & (
            allows_contributor | has_no_list)

        if not request.user.is_superuser:
            filter = filter.filter(contributor_filter)
        else:
            # For super users we also allow retrieving matches to items that
            # are not moderated by contributors
            filter = filter.filter(contributor_filter | allows_superuser |
                                   has_no_list)

        facility_match = get_object_or_404(filter[:1])
        facility_list_item = facility_match.facility_list_item

        if facility_list_item.status != FacilityListItem.POTENTIAL_MATCH:
            raise ValidationError(
                'facility list item status must be POTENTIAL_MATCH'
            )
        if facility_match.status != FacilityMatch.PENDING:
            raise ValidationError('facility match status must be PENDING')

        return facility_match

    @swagger_auto_schema(responses={200: ''})
    def retrieve(self, request, pk=None):
        self.validate_request(request, pk)
        return super(FacilityMatchViewSet, self).retrieve(request, pk=pk)

    @swagger_auto_schema(request_body=no_body, responses={200: ''})
    @transaction.atomic
    @action(detail=True, methods=['POST'])
    def confirm(self, request, pk=None):
        """
        Confirm a potential match between an existing Facility and a Facility
        List Item from an authenticated Contributor's Facility List.

        Returns an updated Facility List Item with the confirmed match's status
        changed to `CONFIRMED` and the Facility List Item's status changed to
        `CONFIRMED_MATCH`. On confirming a potential match, all other
        potential matches will have their status changed to `REJECTED`.

        ## Sample Response

            {
                "id": 1,
                "matches": [
                    {
                        "id": 1,
                        "status": "CONFIRMED",
                        "confidence": 0.6,
                        "results": {
                            "match_type": "single_gazetteer_match",
                            "code_version": "12asdf",
                            "recall_weight": 1,
                            "automatic_threshold": 0.8,
                            "gazetteer_threshold": 0.5,
                            "no_gazetteer_matches": false
                        }
                        "os_id": "os_id_1",
                        "name": "facility match name 1",
                        "address": "facility match address 1",
                        "location": {
                            "lat": 1,
                            "lng": 1
                        },
                        "is_active": true
                    },
                    {
                        "id": 2,
                        "status": "REJECTED",
                        "confidence": 0.7,
                        "results": {
                            "match_type": "single_gazetteer_match",
                            "code_version": "34asdf",
                            "recall_weight": 1,
                            "automatic_threshold": 0.8,
                            "gazetteer_threshold": 0.5,
                            "no_gazetteer_matches": false
                        }
                        "os_id": "os_id_2",
                        "name": "facility match name 2",
                        "address": "facility match address 2",
                        "location": {
                            "lat": 2,
                            "lng": 2
                        },
                        "is_active": true
                    }
                ],
                "row_index": 1,
                "address": "facility list item address",
                "name": "facility list item name",
                "raw_data": "facility liste item name, facility list item address", # noqa
                "status": "CONFIRMED_MATCH",
                "processing_started_at": null,
                "processing_completed_at": null,
                "country_code": "US",
                "facility_list": 1,
                "country_name": "United States",
                "processing_errors": null,
                "list_statuses": ["CONFIRMED_MATCH"],
                "matched_facility": {
                    "os_id": "os_id_1",
                    "name": "facility match name 1",
                    "address": "facility match address 1",
                    "location": {
                        "lat": 1,
                        "lng": 1
                    },
                    "created_from_id": 12345
                }
            }

        """
        facility_match = self.validate_request(request, pk)
        facility_list_item = facility_match.facility_list_item

        facility_match.status = FacilityMatch.CONFIRMED
        facility_match._change_reason = create_associate_match_change_reason(
            facility_match.facility_list_item,
            facility_match.facility,
        )

        facility_match.save()

        matches_to_reject = FacilityMatch \
            .objects \
            .filter(facility_list_item=facility_list_item) \
            .exclude(pk=facility_match.pk)
        # Call `save` in a loop rather than use `update` to make sure that
        # django-simple-history can log the changes
        for match in matches_to_reject:
            match.status = FacilityMatch.REJECTED
            match.save()

        facility_list_item.status = FacilityListItem.CONFIRMED_MATCH
        facility_list_item.facility = facility_match.facility
        facility_list_item.save()

        update_extendedfields_for_list_item(facility_list_item)

        response_data = FacilityListItemSerializer(facility_list_item).data

        if facility_list_item.source.source_type == Source.LIST:
            response_data['list_statuses'] = (
                facility_list_item
                .source
                .facilitylistitem_set
                .values_list('status', flat=True)
                .distinct())

        return Response(response_data)

    @swagger_auto_schema(request_body=no_body, responses={200: ''})
    @transaction.atomic
    @action(detail=True, methods=['POST'])
    def reject(self, request, pk=None):
        """
        Reject a potential match between an existing Facility and a Facility
        List Item from an authenticated Contributor.

        Returns an updated Facility List Item with the potential match's status
        changed to `REJECTED`.

        If all potential matches have been rejected and the Facility List Item
        has been successfully geocoded, creates a new Facility from the
        Facility List Item.

        ## Sample Response

            {
                "id": 1,
                "matches": [
                    {
                        "id": 1,
                        "status": "PENDING",
                        "confidence": 0.6,
                        "results": {
                            "match_type": "single_gazetteer_match",
                            "code_version": "12asdf",
                            "recall_weight": 1,
                            "automatic_threshold": 0.8,
                            "gazetteer_threshold": 0.5,
                            "no_gazetteer_matches": false
                        }
                        "os_id": "os_id_1",
                        "name": "facility match name 1",
                        "address": "facility match address 1",
                        "location": {
                            "lat": 1,
                            "lng": 1
                        },
                        "is_active": true
                    },
                    {
                        "id": 2,
                        "status": "REJECTED",
                        "confidence": 0.7,
                        "results": {
                            "match_type": "single_gazetteer_match",
                            "code_version": "34asdf",
                            "recall_weight": 1,
                            "automatic_threshold": 0.8,
                            "gazetteer_threshold": 0.5,
                            "no_gazetteer_matches": false
                        }
                        "os_id": "os_id_2",
                        "name": "facility match name 2",
                        "address": "facility match address 2",
                        "location": {
                            "lat": 2,
                            "lng": 2
                        },
                        "is_active": true
                    }
                ]
                "row_index": 1,
                "address": "facility list item address",
                "name": "facility list item name",
                "raw_data": "facility liste item name, facility list item address", # noqa
                "status": "POTENTIAL_MATCH",
                "processing_started_at": null,
                "processing_completed_at": null,
                "country_code": "US",
                "country_name": "United States",
                "matched_facility": null,
                "processing_errors": null,
                "facility_list": 1,
                "list_statuses": ["POTENTIAL_MATCH"],
            }
        """
        facility_match = self.validate_request(request, pk)
        facility_list_item = facility_match.facility_list_item

        facility_match.status = FacilityMatch.REJECTED
        facility_match.save()

        remaining_potential_matches = (
            FacilityMatch
            .objects
            .filter(facility_list_item=facility_list_item)
            .filter(status=FacilityMatch.PENDING)
        )
        # If no potential matches remain:
        #
        # - create a new facility for a list item with a geocoded point
        # - set status to `ERROR_MATCHING` for list item with no point
        if remaining_potential_matches.count() == 0:
            no_location = facility_list_item.geocoded_point is None
            no_geocoding_results = facility_list_item.status == \
                FacilityListItem.GEOCODED_NO_RESULTS

            if (no_location or no_geocoding_results):
                facility_list_item.status = FacilityListItem.ERROR_MATCHING
                timestamp = str(timezone.now())
                facility_list_item.processing_results.append({
                    'action': ProcessingAction.CONFIRM,
                    'started_at': timestamp,
                    'error': True,
                    'message': ('Unable to create a new facility from an '
                                'item with no geocoded location'),
                    'finished_at': timestamp,
                })
            else:
                new_facility = (
                    Facility
                    .objects
                    .create(
                        name=facility_list_item.name,
                        address=facility_list_item.address,
                        country_code=facility_list_item.country_code,
                        location=facility_list_item.geocoded_point,
                        created_from=facility_list_item)
                )
                # also create a new facility match
                match_results = {
                    "match_type": "all_potential_matches_rejected",
                }

                FacilityMatch.objects.create(
                    facility_list_item=facility_list_item,
                    facility=new_facility,
                    confidence=1.0,
                    status=FacilityMatch.CONFIRMED,
                    results=match_results
                )

                facility_list_item.facility = new_facility
                facility_list_item.status = (
                    FacilityListItem.CONFIRMED_MATCH
                )
            facility_list_item.save()

            update_extendedfields_for_list_item(facility_list_item)

        response_data = FacilityListItemSerializer(facility_list_item).data

        if facility_list_item.source.source_type == Source.LIST:
            response_data['list_statuses'] = (
                facility_list_item
                .source
                .facilitylistitem_set
                .values_list('status', flat=True)
                .distinct()
            )
        return Response(response_data)
