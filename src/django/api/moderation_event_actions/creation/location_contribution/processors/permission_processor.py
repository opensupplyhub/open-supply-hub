from typing import Dict, Iterable

from rest_framework import status

from api.moderation_event_actions.creation.location_contribution \
    .processors.contribution_processor import ContributionProcessor
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.models.partner_field import PartnerField
from api.constants import APIV1CommonErrorMessages


class PermissionProcessor(ContributionProcessor):

    def process(
            self,
            event_dto: CreateModerationEventDTO
    ) -> CreateModerationEventDTO:

        raw = event_dto.raw_data or {}
        if not raw:
            return super().process(event_dto)

        incoming_keys = set(raw.keys())

        partner_field_names = list(
            PartnerField.objects
            .filter(name__in=incoming_keys)
            .values_list("name", flat=True)
        )

        if not partner_field_names:
            return super().process(event_dto)

        # Permission validation.
        contributor_allowed: set[str] = set(
            event_dto.contributor.partner_fields.values_list("name", flat=True)
        )
        requested_partner_field_names: set[str] = set(partner_field_names)
        unauthorized: set[str] = requested_partner_field_names \
            - contributor_allowed

        if unauthorized:
            event_dto.errors = self.__transform_permission_errors(unauthorized)
            event_dto.status_code = status.HTTP_403_FORBIDDEN
            return event_dto

        return super().process(event_dto)

    @staticmethod
    def __transform_permission_errors(
        fields_errors: Iterable[str]
    ) -> Dict:
        return {
            'detail': APIV1CommonErrorMessages.COMMON_REQ_BODY_ERROR,
            'errors': [
                {
                    'field': field_name,
                    'detail': 'You do not have permission '
                    'to contribute to this field.',
                }
                for field_name in fields_errors
            ],
        }
