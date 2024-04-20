from api.facility_actions.processing_facility import ProcessingFacility

from rest_framework.response import Response


class ProcessingFacilityExecutor:
    '''
    Class defines which interface execute for the processing of a facility.
    It uses the strategy pattern to execute the processing.
    '''

    def __init__(self, strategy: ProcessingFacility) -> None:
        self._strategy = strategy

    def run_processing(self) -> Response:
        result = self._strategy.process_facility()

        return result
