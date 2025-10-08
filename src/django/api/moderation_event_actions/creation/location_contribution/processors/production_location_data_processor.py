import logging
import copy
from typing import Dict, List, Optional, Any

from rest_framework import status

from api.sector_cache import SectorCache
from api.os_id_lookup import OSIDLookup
from contricleaner.lib.contri_cleaner import ContriCleaner
from contricleaner.lib.exceptions.handler_not_set_error \
    import HandlerNotSetError
from api.exceptions import MissingRequiredFieldsException
from api.moderation_event_actions.creation.location_contribution \
    .processors.contribution_processor import ContributionProcessor
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.constants import (
    APIV1CommonErrorMessages,
    NON_FIELD_ERRORS_KEY
)
from api.models.moderation_event import ModerationEvent
from api.services.production_locations_lookup \
    import (
        fetch_required_fields,
        get_missing_required_fields,
        has_all_required_fields,
        has_some_required_fields,
        is_coordinates_without_all_required_fields,
    )
from api.serializers.v1.production_location_post_schema_serializer \
    import ProductionLocationPostSchemaSerializer
from api.serializers.v1.production_location_patch_schema_serializer \
    import ProductionLocationPatchSchemaSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import ErrorDetail


log = logging.getLogger(__name__)


class ProductionLocationDataProcessor(ContributionProcessor):

    def process(
            self,
            event_dto: CreateModerationEventDTO) -> CreateModerationEventDTO:
        cc_ready_data = self.__extract_data_for_contri_cleaner(
            event_dto.raw_data
        )

        # Handle PATCH request backfill BEFORE ContriCleaner validation.
        if event_dto.request_type == ModerationEvent.RequestType.UPDATE.value:
            try:
                cc_ready_data = self.__validate_and_backfill_patch_data(
                    cc_ready_data, event_dto
                )
            except MissingRequiredFieldsException as e:
                event_dto.errors = e.detail
                event_dto.status_code = e.status_code
                return event_dto

        # Choose serializer per request type (POST vs PATCH).
        serializer = self.__prepare_serializer(
            cc_ready_data,
            event_dto.request_type
        )

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            log.error(
                f'[API V1 Location Upload] Schema Serializer Error: {e}'
            )
            event_dto.errors = {
                'detail': APIV1CommonErrorMessages.COMMON_REQ_BODY_ERROR,
                'errors': self._transform_errors(
                    serializer.errors)}
            event_dto.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

            return event_dto

        mapped_data = self.__map_fields_to_supported_cc_schema(cc_ready_data)

        contri_cleaner = ContriCleaner(
            mapped_data,
            SectorCache(),
            OSIDLookup()
        )
        try:
            cc_processed_data = contri_cleaner.process_data()
        except HandlerNotSetError as err:
            log.error(
                f'[API V1 Location Upload] Internal ContriCleaner Error: {err}'
            )
            event_dto.errors = {
                'detail': APIV1CommonErrorMessages.COMMON_INTERNAL_ERROR
            }
            event_dto.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            return event_dto

        list_level_errors = cc_processed_data.errors
        if list_level_errors:
            transformed_list_level_errors = \
                self.__transform_cc_errors_to_api_v1_format(
                    list_level_errors
                )
            event_dto.errors = transformed_list_level_errors
            event_dto.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

            return event_dto

        processed_location_object = cc_processed_data.rows[0]
        location_object_validation_errors = processed_location_object.errors
        if location_object_validation_errors:
            transformed_location_object_validation_errors = \
                self.__transform_cc_errors_to_api_v1_format(
                    location_object_validation_errors
                )
            event_dto.errors = transformed_location_object_validation_errors
            event_dto.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

            return event_dto

        # Save the cleaned data in case of successful
        # ContriCleaner serialization.
        event_dto.cleaned_data = dict(processed_location_object._asdict())

        return super().process(event_dto)

    @staticmethod
    def __prepare_serializer(cc_ready_data: Dict, request_type: str):
        if request_type == ModerationEvent.RequestType.CREATE.value:
            return ProductionLocationPostSchemaSerializer(data=cc_ready_data)

        # Handle v1 PATCH requests (backfill already happened earlier).
        return ProductionLocationPatchSchemaSerializer(data=cc_ready_data)

    @staticmethod
    def __validate_and_backfill_patch_data(
        cc_ready_data: Dict,
        event_dto: CreateModerationEventDTO
    ) -> Dict:

        '''
        If the client provided no updatable fields, do not backfill here;
        let the PATCH serializer enforce "No fields provided".
        '''
        if not cc_ready_data:
            return cc_ready_data
        # Check original raw_data to decide on backfill strategy.
        raw_data = event_dto.raw_data

        ProductionLocationDataProcessor.__handle_all_required_fields_errors(
            raw_data
        )

        # If all required fields are missing, perform backfill.
        if not has_all_required_fields(raw_data):
            # Create a deep copy to avoid mutating the original data.
            backfilled_data = copy.deepcopy(cc_ready_data)
            default_required_fields = fetch_required_fields(event_dto.os.id)

            # Add the required fields directly
            # (before ContriCleaner processing).
            for field in ('name', 'address', 'country'):
                if (field not in backfilled_data or
                        not backfilled_data.get(field)):
                    backfilled_data[field] = default_required_fields.get(
                        field, ''
                    )

            return backfilled_data

        # Return original data if no backfill is needed.
        return cc_ready_data

    @staticmethod
    def __handle_all_required_fields_errors(raw_data: Dict):
        missing_fields = get_missing_required_fields(raw_data)

        if not missing_fields:
            return

        if is_coordinates_without_all_required_fields(raw_data):
            ProductionLocationDataProcessor. \
                __raise_coordinates_validation_error(missing_fields)

        if has_some_required_fields(raw_data):
            ProductionLocationDataProcessor. \
                __raise_partial_fields_validation_error(
                    raw_data, missing_fields
                )

    @staticmethod
    def __raise_coordinates_validation_error(missing_fields: List[str]):
        raise MissingRequiredFieldsException(
            detail={
                "detail": APIV1CommonErrorMessages.COMMON_REQ_BODY_ERROR,
                "errors": [
                    {
                        "field": field,
                        "detail": (
                            f"Field {field} is required when coordinates "
                            f"are provided."
                        ),
                    }
                    for field in missing_fields
                ]
            }
        )

    @staticmethod
    def __raise_partial_fields_validation_error(
        raw_data: Dict, missing_fields: List[str]
    ):
        required_fields = ('name', 'address', 'country')
        provided_fields = [
            field for field in required_fields if raw_data.get(field)
        ]

        verb = 'is' if len(provided_fields) == 1 else 'are'
        provided_list = ', '.join(provided_fields)

        raise MissingRequiredFieldsException(
            detail={
                "detail": APIV1CommonErrorMessages.COMMON_REQ_BODY_ERROR,
                "errors": [
                    {
                        "field": field,
                        "detail": (
                            f"Field {field} is required when {provided_list} "
                            f"{verb} provided."
                        ),
                    }
                    for field in missing_fields
                ]
            }
        )

    @staticmethod
    def __extract_data_for_contri_cleaner(input_raw_data: Dict) -> Dict:
        copied_raw_data = copy.deepcopy(input_raw_data)
        # Delete the source from the copied raw data to prevent it from being
        # passed to ContriCleaner. The source has been verified and assigned
        # to the appropriate property of the CreateModerationEventDTO
        # within SourceProcessor.
        if 'source' in copied_raw_data:
            del copied_raw_data['source']

        return copied_raw_data

    @staticmethod
    def __map_fields_to_supported_cc_schema(data_to_map: Dict) -> Dict:
        '''
        This method maps input fields to the predefined set of supported
        fields in the ContriCleaner library. It should be a temporary solution
        until some form of serializer versioning is implemented for
        ContriCleaner.
        '''

        mapped_data = {}

        if 'location_type' in data_to_map:
            mapped_data['facility_type'] = data_to_map['location_type']

        if 'coordinates' in data_to_map:
            if 'lat' in data_to_map['coordinates']:
                mapped_data['lat'] = data_to_map['coordinates']['lat']
            if 'lng' in data_to_map['coordinates']:
                mapped_data['lng'] = data_to_map['coordinates']['lng']

        # Add fields that don't require mapping.
        for key, value in data_to_map.items():
            if key not in ['location_type', 'coordinates']:
                mapped_data[key] = value

        return mapped_data

    @staticmethod
    def __transform_cc_errors_to_api_v1_format(cc_errors: List[Dict]) -> Dict:
        # Initialize the new structure.
        transformed_errors = {
            'detail': APIV1CommonErrorMessages.COMMON_REQ_BODY_ERROR,
            'errors': []
        }

        # Iterate through the errors and convert them.
        for cc_error in cc_errors:
            if (cc_error['field'] == 'facility_type'):
                location_type_error = \
                    ProductionLocationDataProcessor\
                    .__substitute_facility_type_in_error_message(cc_error)
                transformed_errors['errors'].append(location_type_error)
            else:
                transformed_errors['errors'].append({
                    'field': cc_error['field'],
                    'detail': cc_error['message']
                })

        return transformed_errors

    @staticmethod
    def __substitute_facility_type_in_error_message(
            facility_type_error: Dict) -> Dict:
        '''
        Replaces occurrences of a facility_type field name in the
        ContriCleaner error message with a new location_type field name to
        support the v1 API schema. It should be a temporary solution until
        some form of serializer versioning is implemented for ContriCleaner.
        '''

        field_mapping_config = {
            'facility_type': 'location_type'
        }
        field_to_replace = facility_type_error['field']

        return {
            'field': field_mapping_config[field_to_replace],
            'detail': facility_type_error['message'].replace(
                field_to_replace,
                field_mapping_config[field_to_replace]
            )
        }

    @staticmethod
    def _transform_errors(serializer_errors: Dict) -> List[Dict]:
        def __append_extracted_error(field: str, error: Any) -> None:
            extracted = ProductionLocationDataProcessor.\
                    __extract_error(field, error)
            if extracted:
                formatted_errors.append(extracted)

        formatted_errors = []

        for field, errors in serializer_errors.items():
            if isinstance(errors, list):
                for err in errors:
                    __append_extracted_error(field, err)
            elif isinstance(errors, dict):
                if NON_FIELD_ERRORS_KEY in errors and len(errors) == 1:
                    __append_extracted_error(
                            field,
                            errors[NON_FIELD_ERRORS_KEY][0])
                else:
                    nested = ProductionLocationDataProcessor.\
                        _transform_errors(errors)
                    formatted_errors.append({"field": field, "errors": nested})

        return formatted_errors

    @staticmethod
    def __extract_error(field: str, error: Any) -> Optional[Dict]:
        if isinstance(error, ErrorDetail):
            return {"field": field, "detail": str(error)}

        if isinstance(error, dict) and "field" in error and "detail" in error:
            err_field = str(error.get("field", ""))
            err_detail = str(error.get("detail", ""))
            return {"field": err_field, "detail": err_detail}

        if isinstance(error, dict) and NON_FIELD_ERRORS_KEY in error:
            return {"field": field,
                    "detail": str(error[NON_FIELD_ERRORS_KEY][0])}

        return None
