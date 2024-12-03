import logging
import copy
from typing import Dict, List

from rest_framework import status

from api.sector_cache import SectorCache
from contricleaner.lib.contri_cleaner import ContriCleaner
from contricleaner.lib.exceptions.handler_not_set_error \
    import HandlerNotSetError
from api.moderation_event_actions.creation.location_contribution \
    .processors.contribution_processor import ContributionProcessor
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.constants import APIV1CommonErrorMessages


# Initialize logger.
log = logging.getLogger(__name__)


class ProductionLocationDataProcessor(ContributionProcessor):

    def process(
            self,
            event_dto: CreateModerationEventDTO) -> CreateModerationEventDTO:
        cc_ready_data = self.__extract_data_for_contri_cleaner(
            event_dto.raw_data
        )
        mapped_data = self.__map_fields_to_supported_cc_schema(cc_ready_data)

        contri_cleaner = ContriCleaner(mapped_data, SectorCache())
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
                self.__trasform_cc_errors_to_api_v1_format(
                    list_level_errors
                )
            event_dto.errors = transformed_list_level_errors
            event_dto.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

            return event_dto

        processed_location_object = cc_processed_data.rows[0]
        location_object_validation_errors = processed_location_object.errors
        if location_object_validation_errors:
            transformed_location_object_validation_errors = \
                self.__trasform_cc_errors_to_api_v1_format(
                    location_object_validation_errors
                )
            event_dto.errors = transformed_location_object_validation_errors
            event_dto.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

            return event_dto

        # Save the cleaned data in case of successful ContriCleaner
        # serialization.
        event_dto.cleaned_data = dict(processed_location_object._asdict())

        return super().process(event_dto)

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
    def __trasform_cc_errors_to_api_v1_format(cc_errors: List[Dict]) -> Dict:
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
