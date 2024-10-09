from typing import Union

from rest_framework.response import Response

from api.facility_actions.processing_facility import ProcessingFacility


class ProcessingFacilityExecutor:
    '''
    Class defines which interface execute for the processing of a facility.
    It uses the strategy pattern to execute the processing.
    '''

    def __init__(self, strategy: ProcessingFacility) -> None:
        self._strategy = strategy

    def run_processing(self) -> Union[Response, None]:
        result = self._strategy.process_facility()

        return result
