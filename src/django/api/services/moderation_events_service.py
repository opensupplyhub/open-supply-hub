import logging
from enum import Enum

from rest_framework.exceptions import NotFound, ParseError

from api.constants import (
    LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX,
    APIV1CommonErrorMessages,
    APIV1ModerationEventErrorMessages,
)
from api.exceptions import GoneException, InternalServerErrorException
from api.models.facility.facility import Facility
from api.models.moderation_event import ModerationEvent
from api.os_id import string_matches_os_id_format
from api.serializers.v1.opensearch_common_validators.moderation_id_validator \
    import ModerationIdValidator
from api.views.v1.utils import create_error_detail

log = logging.getLogger(__name__)


class ModerationEventsService:
    class Role(Enum):
        MODERATOR = 'moderator'
        OWNER = 'owner'
        UNKNOWN = 'unknown'

    @staticmethod
    def validate_uuid(value):
        if not ModerationIdValidator.is_valid_uuid(value):
            raise ParseError(
                create_error_detail(
                    field="moderation_id",
                    detail=(
                        APIV1ModerationEventErrorMessages.INVALID_UUID_FORMAT
                    ),
                )
            )

    @staticmethod
    def fetch_moderation_event_by_uuid(uuid):
        try:
            return ModerationEvent.objects.get(uuid=uuid)
        except ModerationEvent.DoesNotExist:
            raise NotFound(
                create_error_detail(
                    field="moderation_id",
                    detail=APIV1ModerationEventErrorMessages.EVENT_NOT_FOUND,
                )
            )

    @staticmethod
    def validate_moderation_status(status):
        if status != ModerationEvent.Status.PENDING:
            raise GoneException(
                detail=APIV1ModerationEventErrorMessages.EVENT_NOT_PENDING
            )

    @staticmethod
    def validate_location_os_id(os_id):
        if not string_matches_os_id_format(os_id):
            raise ParseError(
                create_error_detail(
                    field="os_id",
                    detail=APIV1CommonErrorMessages.LOCATION_ID_NOT_VALID,
                )
            )

        if not Facility.objects.filter(id=os_id).exists():
            raise NotFound(
                create_error_detail(
                    field="os_id",
                    detail=APIV1CommonErrorMessages.LOCATION_NOT_FOUND,
                )
            )

    @staticmethod
    def handle_processing_error(error_message):
        log.error(
            f'{LOCATION_CONTRIBUTION_APPROVAL_LOG_PREFIX} '
            f'Error: {str(error_message)}'
        )
        raise InternalServerErrorException()

    @staticmethod
    def validate_restriction_role(
        request,
        event: ModerationEvent = None
    ):
        if request.user.is_superuser:
            return ModerationEventsService.Role.MODERATOR

        if event:
            if request.user.contributor.id == event.contributor.id:
                return ModerationEventsService.Role.OWNER

        return ModerationEventsService.Role.UNKNOWN
