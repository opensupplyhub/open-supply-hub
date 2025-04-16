import logging

from rest_framework import status

from api.moderation_event_actions.creation.location_contribution \
    .processors.contribution_processor import ContributionProcessor
from api.moderation_event_actions.creation.dtos.create_moderation_event_dto \
    import CreateModerationEventDTO
from api.constants import (
    APIV1LocationContributionErrorMessages,
    APIV1LocationContributionKeys,
    APIV1CommonErrorMessages,
    NON_FIELD_ERRORS_KEY
)
from api.geocoding import geocode_address

log = logging.getLogger(__name__)


class GeocodingProcessor(ContributionProcessor):

    def process(
            self,
            event_dto: CreateModerationEventDTO) -> CreateModerationEventDTO:
        lat = event_dto.cleaned_data['fields'].get(
            APIV1LocationContributionKeys.LAT
        )
        lng = event_dto.cleaned_data['fields'].get(
            APIV1LocationContributionKeys.LNG
        )

        if lat is None or lng is None:
            try:
                geocode_result = geocode_address(
                    event_dto.cleaned_data['address'],
                    event_dto.cleaned_data['country_code']
                )

                if geocode_result['result_count'] > 0:
                    event_dto.geocode_result = geocode_result
                else:
                    event_dto.errors = {
                        'detail': (
                            APIV1CommonErrorMessages.COMMON_REQ_BODY_ERROR
                        ),
                        'errors': [
                            {
                                'field': NON_FIELD_ERRORS_KEY,
                                'detail': (
                                    APIV1LocationContributionErrorMessages
                                    .GEOCODED_NO_RESULTS
                                )
                            }
                        ]
                    }
                    event_dto.status_code = \
                        status.HTTP_422_UNPROCESSABLE_ENTITY

                    return event_dto
            except ValueError as value_err:
                log.error(
                    (f'[API V1 Location Upload] Internal Geocoding Error: '
                     f'{value_err}')
                )
                event_dto.errors = {
                    'detail': APIV1CommonErrorMessages.COMMON_INTERNAL_ERROR
                }
                event_dto.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

                return event_dto

        return event_dto
