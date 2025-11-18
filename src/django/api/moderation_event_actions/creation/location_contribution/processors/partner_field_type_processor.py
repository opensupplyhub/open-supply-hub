from typing import Dict, List, Mapping, Optional, Tuple

import jsonschema
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from jsonschema.validators import Draft202012Validator
from rest_framework import status

from api.moderation_event_actions.creation.location_contribution \
    .processors.contribution_processor import ContributionProcessor
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.models.partner_field import PartnerField
from api.constants import APIV1CommonErrorMessages


class PartnerFieldTypeProcessor(ContributionProcessor):

    TYPE_VALIDATORS = {
        'int': lambda value: isinstance(value, int)
        and not isinstance(value, bool),
        'float': lambda value: isinstance(value, float)
        and not isinstance(value, bool),
        'string': lambda value: isinstance(value, str),
        'object': lambda value: isinstance(
            value, (dict, list)
        ),
    }

    FORMAT_CHECKER = jsonschema.FormatChecker()

    def process(
            self,
            event_dto: CreateModerationEventDTO
    ) -> CreateModerationEventDTO:

        raw = event_dto.raw_data or {}
        if not raw:
            return super().process(event_dto)

        incoming_keys = set(raw.keys())

        partner_fields_qs = PartnerField.objects \
            .filter(name__in=incoming_keys) \
            .values("name", "type", "json_schema")
        partner_fields_data: Dict[str, Dict] = {
            field["name"]: {
                "type": field["type"],
                "json_schema": field["json_schema"]
            }
            for field in partner_fields_qs
        }

        if not partner_fields_data:
            return super().process(event_dto)

        validation_errors = self.__validate_partner_fields(
            raw,
            partner_fields_data
        )

        if validation_errors:
            event_dto.errors = self.__transform_validation_errors(
                validation_errors
            )
            event_dto.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            return event_dto

        return super().process(event_dto)

    @staticmethod
    def __validate_partner_fields(
        raw: Mapping[str, object],
        partner_fields_data: Dict[str, Dict]
    ) -> List[Tuple[str, str]]:

        validation_errors: List[Tuple[str, str]] = []

        for field_name, field_info in partner_fields_data.items():
            value = raw.get(field_name)
            if value is None:
                continue

            field_type = field_info.get("type")
            json_schema = field_info.get("json_schema")

            error = PartnerFieldTypeProcessor.__validate_single_field(
                field_name, value, field_type, json_schema
            )
            if error:
                validation_errors.append(error)

        return validation_errors

    @staticmethod
    def __validate_single_field(
        field_name: str,
        value: object,
        field_type: str,
        json_schema: object
    ) -> Optional[Tuple[str, str]]:

        use_json_schema = (
            field_type == PartnerField.OBJECT and json_schema
        )

        if use_json_schema:
            return PartnerFieldTypeProcessor.__validate_with_json_schema(
                field_name, value, json_schema
            )

        return PartnerFieldTypeProcessor.__validate_with_type_validator(
            field_name, value, field_type
        )

    @staticmethod
    def __validate_with_json_schema(
        field_name: str,
        value: object,
        json_schema: object
    ) -> Optional[Tuple[str, str]]:

        try:
            validator = Draft202012Validator(
                schema=json_schema,
                format_checker=PartnerFieldTypeProcessor.FORMAT_CHECKER
            )
            validator.validate(instance=value)
            return None
        except JsonSchemaValidationError as e:
            error_message = PartnerFieldTypeProcessor.__format_json_schema_error(
                e
            )
            return (field_name, error_message)
        except Exception as e:
            return (field_name, f"Schema validation error: {str(e)}")

    @staticmethod
    def __format_json_schema_error(
        error: JsonSchemaValidationError
    ) -> str:

        error_message = error.message
        error_path = PartnerFieldTypeProcessor.__extract_error_path(error)

        if error_path:
            return f"{error_path}: {error_message}"

        return error_message

    @staticmethod
    def __extract_error_path(
        error: JsonSchemaValidationError
    ) -> Optional[str]:

        if hasattr(error, 'absolute_path') and error.absolute_path:
            return ".".join(str(p) for p in error.absolute_path)

        if hasattr(error, 'path') and error.path:
            return ".".join(str(p) for p in error.path)

        return None

    @staticmethod
    def __validate_with_type_validator(
        field_name: str,
        value: object,
        field_type: str
    ) -> Optional[Tuple[str, str]]:

        if field_type not in PartnerFieldTypeProcessor.TYPE_VALIDATORS:
            return None

        validator = PartnerFieldTypeProcessor.TYPE_VALIDATORS[field_type]
        if validator(value):
            return None

        return (
            field_name,
            f'Field {field_name} must be {field_type}, '
            f'not {type(value).__name__}.'
        )

    @staticmethod
    def __transform_validation_errors(
        validation_errors: List[Tuple[str, str]]
    ) -> Dict:
        return {
            'detail': APIV1CommonErrorMessages.COMMON_REQ_BODY_ERROR,
            'errors': [
                {
                    'field': field_name,
                    'detail': error_message,
                }
                for field_name, error_message in validation_errors
            ],
        }
