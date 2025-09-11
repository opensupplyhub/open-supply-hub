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
            Validate that the contributor is allowed to modify any partner-specific fields in the event DTO; if not, attach validation errors and set a 403 status, otherwise continue processing via the superclass.
            
            If `event_dto.raw_data` is a dict, the method compares its keys against all PartnerField names. For any keys that correspond to partner fields but are not in the contributor's allowed partner_fields, the method populates `event_dto.errors` with a structured validation payload, sets `event_dto.status_code` to HTTP 403 Forbidden, and returns the DTO immediately. If no unauthorized partner fields are found (or `raw_data` is absent/not a dict), the DTO is passed to `super().process()`.
            
            Parameters:
                event_dto (CreateModerationEventDTO): DTO for the moderation event; may be mutated (errors and status_code) when unauthorized fields are detected.
            
            Returns:
                CreateModerationEventDTO: The original DTO, possibly modified with errors and a 403 status when permission violations are found; otherwise the result of `super().process(event_dto)`.
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
        Build a validation error payload listing fields the contributor is not permitted to modify.
        
        Parameters:
            fields_errors (List[str]): Names of partner fields for which the contributor lacks permission.
        
        Returns:
            Dict: Validation error dictionary with keys:
                - 'detail' (str): General request body error message.
                - 'errors' (List[Dict[str, str]]): One entry per field with 'field' and 'detail' describing the permission error.
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
