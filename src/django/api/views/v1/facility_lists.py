import logging
from typing import List

from django.db import transaction

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from api.permissions import IsRegisteredAndConfirmed
from api.constants import APIV1CommonErrorMessages
from api.models.facility.facility_list import FacilityList
from api.services.facility_dissociation_service import (
    deactivate_contributor_source,
)

logger = logging.getLogger(__name__)


class FacilityLists(ViewSet):
    swagger_schema = None

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
        if self.action == 'deactivate':
            return [IsRegisteredAndConfirmed]
        return []

    @action(detail=True, methods=['post'], url_path='deactivate')
    @transaction.atomic
    def deactivate(self, request, pk=None):
        '''
        Deactivate a list the authenticated contributor uploaded, so all of
        its contributions stop being shown as associated with them.

        The contributions are anonymized, not deleted: the list's ``Source`` is
        marked inactive, replacing the contributor name with the contributor
        type across the affected location profiles. Scoping to the caller's
        contributor guarantees a caller can only ever deactivate their own
        list.

        Only an approved (live) list can be deactivated. Deactivation rides on
        ``FacilityList.status = REJECTED``, but a list still awaiting moderator
        approval would have that status silently reverted by a later
        ``approve`` (which fires ``manual_list_reject_revert_trigger`` and
        reactivates the source). Restricting to approved lists keeps the
        deactivation durable.
        '''
        if pk is None or not str(pk).isdecimal():
            return Response(
                {'detail': APIV1CommonErrorMessages.FACILITY_LIST_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND
            )

        facility_list = (
            FacilityList.objects
            .filter(id=pk)
            .select_related('source', 'source__contributor')
            .first()
        )

        # Return the same 404 whether the list is missing or owned by another
        # contributor, so list ownership is not leaked.
        if (facility_list is None
                or facility_list.source is None
                or facility_list.source.contributor_id
                != request.user.contributor.id):
            return Response(
                {'detail': APIV1CommonErrorMessages.FACILITY_LIST_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND
            )

        # A not-yet-approved list can have its REJECTED status reverted by a
        # later approve, so refuse to deactivate anything that is not live.
        if facility_list.status not in (
                FacilityList.APPROVED,
                FacilityList.MATCHED):
            return Response(
                {'detail': APIV1CommonErrorMessages.LIST_NOT_APPROVED},
                status=status.HTTP_400_BAD_REQUEST
            )

        deactivated = deactivate_contributor_source(
            facility_list, request.user
        )

        if not deactivated:
            return Response(
                {'detail': APIV1CommonErrorMessages.LIST_ALREADY_INACTIVE},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                'list_id': facility_list.id,
                'deactivated': True,
            },
            status=status.HTTP_200_OK
        )
