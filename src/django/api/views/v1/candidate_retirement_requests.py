from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from api.constants import APIV1CandidateVoteErrorMessages
from api.models.facility.facility_candidate_retirement_request import (
    FacilityCandidateRetirementRequest,
)
from api.permissions import IsSuperuser
from api.services import candidate_validation


class CandidateRetirementRequests(ViewSet):
    '''
    The moderator side of the pilot's candidate retirement gate
    (OSDEV-3245). Moderators only (same ``IsSuperuser`` permission as the
    moderation-events actions).

    GET  /api/v1/candidate-retirement-requests/
        Open requests, oldest first: ``[{id, os_id, tally, created_at,
        updated_at}]``. A request is open exactly as long as its row
        exists (see the model docstring).
    POST /api/v1/candidate-retirement-requests/{id}/approve/
        Retires the candidate with the live tally through
        ``retire_candidate`` (hard delete + NOT_A_FACILITY tombstone) and
        answers 200 ``{os_id, state: "retired", tally}``. 404 when the
        request is not (or no longer) open.

    There is deliberately no reject action yet: a request dissolves on
    its own when later votes break the consensus, and whether moderators
    should be able to veto a standing consensus is a Product call.
    '''
    swagger_schema = None
    permission_classes = [IsSuperuser]

    def list(self, request):
        rows = (
            FacilityCandidateRetirementRequest.objects
            .order_by('created_at')
            .values('id', 'facility_id', 'tally', 'created_at', 'updated_at')
        )
        return Response([
            {
                'id': row['id'],
                'os_id': row['facility_id'],
                'tally': row['tally'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
            }
            for row in rows
        ])

    @action(detail=True, methods=['POST'])
    def approve(self, request, pk=None):
        retirement_request = (
            FacilityCandidateRetirementRequest.objects
            .filter(pk=pk)
            .first()
        )
        if retirement_request is None:
            raise NotFound(
                detail=APIV1CandidateVoteErrorMessages.REQUEST_NOT_FOUND
            )

        tombstone = candidate_validation.approve_retirement(
            retirement_request, request.user
        )
        return Response(
            {
                'os_id': tombstone.os_id,
                'state': candidate_validation.RETIRED,
                'tally': tombstone.retirement_tally,
            },
            status=status.HTTP_200_OK,
        )
