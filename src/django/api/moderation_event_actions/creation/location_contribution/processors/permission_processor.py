from typing import Dict, List, Mapping, Tuple, Iterable

from rest_framework import status

from api.moderation_event_actions.creation.location_contribution \
    .processors.contribution_processor import ContributionProcessor
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.models.partner_field import PartnerField
from api.constants import APIV1CommonErrorMessages


class PermissionProcessor(ContributionProcessor):

    TYPE_VALIDATORDS = {
        'int': lambda value: isinstance(value, int)
        and not isinstance(value, bool),
        'float': lambda value: isinstance(value, float)
        and not isinstance(value, bool),
        'string': lambda value: isinstance(value, str),
        'object': lambda value: isinstance(
            value, (dict, list)
        ),
    }

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
                .values_list("name", "type")
        partner_fields: Dict[str, str] = {
            name: ftype
            for name, ftype in partner_fields_qs
        }

        if not partner_fields:
            return super().process(event_dto)

        # Permission validation.
        contributor_allowed: set[str] = set(
            event_dto.contributor.partner_fields.values_list("name", flat=True)
        )
        requested_partner_field_names: set[str] = set(partner_fields.keys())
        unauthorized: set[str] = requested_partner_field_names - contributor_allowed

        if unauthorized:
            event_dto.errors = self.__transform_permission_errors(unauthorized)
            event_dto.status_code = status.HTTP_403_FORBIDDEN
            return event_dto

        # Type validation.
        invalid_type_fields = self.__collect_invalid_type_fields(
            raw,
            partner_fields,
            self.TYPE_VALIDATORDS
        )

        if invalid_type_fields:
            event_dto.errors = self.__transform_type_errors(
                invalid_type_fields
            )
            event_dto.status_code = status \
                .HTTP_422_UNPROCESSABLE_ENTITY

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

    @staticmethod
    def __transform_type_errors(
        invalid_type_fields: List[tuple]
    ) -> Dict:
        return {
            'detail': APIV1CommonErrorMessages.COMMON_REQ_BODY_ERROR,
            'errors': [
                {
                    'field': name,
                    'detail': f'Field {name} must be of type {expected}, '
                    f'but received {type(value).__name__}',
                }
                for name, expected, value in invalid_type_fields
            ],
        }
    
    @staticmethod
    def __collect_invalid_type_fields(
        raw: Mapping[str, object],
        partner_fields: Mapping[str, str],
        validators: Mapping[str, callable],
    ) -> List[Tuple[str, str, object]]:

        invalid_fields = List[Tuple[str, str, object]] = []

        for name, field_type in partner_fields.items():
            value = raw.get(name)

            if value is not None and field_type in validators:
                if not validators[field_type](value):
                    invalid_fields.append(
                        (name, field_type, value)
                    )

        return invalid_fields
