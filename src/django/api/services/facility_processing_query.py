from typing import List, NamedTuple, Protocol

from api.constants import FacilitiesQueryParams


class ParamsProtocol(Protocol):
    """Interface required from Django and DRF query parameter mappings."""

    def getlist(self, key: str) -> List[str]:
        ...


class FacilityProcessingResult(NamedTuple):
    facility_types: list[str]
    processing_types: list[str]
    exact_processing_types: list[str]


class FacilityProcessingQuery:
    """Parse facility and processing type filters from query parameters."""

    def __init__(self, params: ParamsProtocol) -> None:
        self.params = params

    def _nonblank_values(self, key: str) -> list[str]:
        return [
            value
            for value in self.params.getlist(key)
            if value is not None and value.strip()
        ]

    def parse(self) -> FacilityProcessingResult:
        facility_types = self._nonblank_values(
            FacilitiesQueryParams.FACILITY_TYPE
        )
        processing_types = self._nonblank_values(
            FacilitiesQueryParams.PROCESSING_TYPE
        )
        processing_type_identities = {
            value.lower() for value in processing_types
        }
        exact_processing_types = [
            value
            for value in self._nonblank_values(
                FacilitiesQueryParams.PROCESSING_TYPE_EXACT
            )
            if value.lower() in processing_type_identities
        ]

        return FacilityProcessingResult(
            facility_types=facility_types,
            processing_types=processing_types,
            exact_processing_types=exact_processing_types,
        )
