import logging

from rest_framework.exceptions import PermissionDenied, ParseError, NotFound

from api.constants import APIV1CommonErrorMessages
from api.exceptions import GoneException, InternalServerErrorException
from api.models.moderation_event import ModerationEvent
from api.serializers.v1.opensearch_common_validators.moderation_id_validator \
    import ModerationIdValidator
from api.views.v1.utils import create_error_detail

log = logging.getLogger(__name__)


class ModerationEventsService:
    @staticmethod
    def validate_user_permissions(request):
        if not (request.user.is_superuser or request.user.is_staff):
            raise PermissionDenied(
                detail="Only the Moderator can perform this action."
            )

    @staticmethod
    def validate_uuid(value):
        if not ModerationIdValidator.is_valid_uuid(value):
            raise ParseError(
                create_error_detail(
                    field="moderation_id",
                    detail="Invalid UUID format."
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
                    detail=APIV1CommonErrorMessages.MODERATION_EVENT_NOT_FOUND
                )
            )

    @staticmethod
    def validate_moderation_status(status):
        if status != ModerationEvent.Status.PENDING:
            raise GoneException(
                detail="The moderation event should be in PENDING status."
            )

    @staticmethod
    def handle_processing_error(error_message):
        log.error(f'[Moderation Event] Error: {str(error_message)}')
        raise InternalServerErrorException()
