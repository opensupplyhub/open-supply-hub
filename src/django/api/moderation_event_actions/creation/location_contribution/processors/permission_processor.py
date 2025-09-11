from typing import Dict, List

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
            event_dto: CreateModerationEventDTO) -> CreateModerationEventDTO:

        partner_fields = PartnerField.objects.all()
        partner_field_names = [field.name for field in partner_fields]

        if event_dto.raw_data and isinstance(event_dto.raw_data, dict):
            matching_partner_field_names = [
                key for key in event_dto.raw_data.keys()
                if key in partner_field_names
            ]

            if matching_partner_field_names:
                contributor_partner_fields = event_dto.contributor \
                    .partner_fields.all()
                contributor_partner_field_names = [
                    field.name for field in contributor_partner_fields
                ]

                unauthorized_partner_fields = [
                    name for name in matching_partner_field_names
                    if name not in contributor_partner_field_names
                ]

                if unauthorized_partner_fields:
                    validation_errors = self.__transform_fields_errors(
                        unauthorized_partner_fields
                    )
                    event_dto.errors = validation_errors
                    event_dto.status_code = status.HTTP_403_FORBIDDEN

                    return event_dto

        return super().process(event_dto)

    @staticmethod
    def __transform_fields_errors(fields_errors: List[str]) -> Dict:
        validation_errors = {
            'detail': APIV1CommonErrorMessages.COMMON_REQ_BODY_ERROR,
            'errors': []
        }

        for field_name in fields_errors:
            validation_errors['errors'].append(
                {
                    'field': field_name,
                    'detail': 'You do not have permission '
                    'to contribute to this field.'
                }
            )

        return validation_errors
