from api.facility_actions.processing_facility import ProcessingFacility


class ProcessingFacilityExecutor:
    '''
    Class to execute the processing of a facility.
    It uses the strategy pattern to execute the processing.
    '''

    def __init__(self, strategy: ProcessingFacility) -> None:
        self._strategy = strategy

    def run_processing(self) -> None:
        result = self._strategy.process_facility()

        return result
