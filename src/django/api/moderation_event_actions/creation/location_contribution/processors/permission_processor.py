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

        partner_field_names = PartnerField.objects \
            .values_list('name', flat=True)

        if event_dto.raw_data:
            # Permission validation
            matching_partner_field_names = [
                key for key in event_dto.raw_data.keys()
                if key in partner_field_names
            ]

            if matching_partner_field_names:
                contributor_partner_field_names = event_dto.contributor \
                    .partner_fields.values_list('name', flat=True)

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

                # Type validation
                partner_fields = {
                    pf.name: pf.type 
                    for pf in PartnerField.objects.filter(
                        name__in=matching_partner_field_names
                    )
                }

                type_validators = {
                    'int': lambda v: self.__safe_convert(v, int),
                    'float': lambda v: self.__safe_convert(v, float),
                    'string': lambda v: self.__safe_convert(v, str),
                    'object': lambda v: isinstance(v, (dict, list)),
                }

                invalid_type_fields = []

                for name, field_type in partner_fields.items():
                    value = event_dto.raw_data.get(name)

                    if value is not None and field_type in type_validators:
                        if not type_validators[field_type](value):
                            invalid_type_fields.append(
                                (name, field_type, value)
                            )

                if invalid_type_fields:
                    validation_errors = self.__transform_type_errors(
                        invalid_type_fields
                    )

                    event_dto.errors = validation_errors
                    event_dto.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

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

    @staticmethod
    def __transform_type_errors(invalid_type_fields: List[tuple]) -> Dict:
        validation_errors = {
            'detail': APIV1CommonErrorMessages.COMMON_REQ_BODY_ERROR,
            'errors': []
        }

        for name, field_type, value in invalid_type_fields:
            validation_errors['errors'].append(
                {
                    'field': name,
                    'detail': f'Field "{name}" must be of type {field_type}, '
                    f'but received {type(value).__name__}'
                }
            )

        return validation_errors

    @staticmethod
    def __safe_convert(value, convert_func):
        try:
            convert_func(value)
            return True
        except (ValueError, TypeError):
            return False
