from api.facility_actions.processing_facility import ProcessingFacility


class ProcessingFacilityExecutor:
    def __init__(self, strategy: ProcessingFacility) -> None:
        """
        Usually, the Context accepts a strategy through the constructor, but
        also provides a setter to change it at runtime.
        """

        self._strategy = strategy

    def run_processing(self) -> None:
        """
        The Context delegates some work to the Strategy object instead of
        implementing multiple versions of the algorithm on its own.
        """

        result = self._strategy.process_facility()

        return result
