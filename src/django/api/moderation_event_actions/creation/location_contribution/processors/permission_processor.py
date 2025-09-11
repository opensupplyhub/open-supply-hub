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

        """
            Enforce per-field contribution permissions on a CreateModerationEventDTO.
            
            If the DTO's raw_data is a dict and contains keys that correspond to PartnerField names, verifies the contributor is allowed to modify those fields. If any unauthorized fields are found, sets event_dto.errors to a validation error payload and event_dto.status_code to HTTP 403 FORBIDDEN, then returns the DTO. If no unauthorized fields are present, delegates processing to the parent processor and returns its result.
            
            Parameters:
                event_dto (CreateModerationEventDTO): DTO representing the moderation event. Expected to contain `raw_data` (a dict of submitted fields) and `contributor` with `partner_fields`.
            
            Returns:
                CreateModerationEventDTO: The same DTO, possibly modified with error details and status_code when unauthorized fields are detected, otherwise the result of the parent processor.
            """
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
        """
        Build a standardized validation error payload for a list of unauthorized field names.
        
        Parameters:
            fields_errors (List[str]): Field names that the contributor is not allowed to modify.
        
        Returns:
            Dict: Validation error dictionary with a top-level 'detail' message and an 'errors' list where each item is a dict containing:
                - 'field': the field name
                - 'detail': the permission error message for that field
        """
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
