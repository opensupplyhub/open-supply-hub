from typing import List

from app.matching.DTOs.facility_list_item_dto import FacilityListItemDict
from app.matching.DTOs.facility_match_dto import FacilityMatchDTO


class ProcessMatch:
    def __init__(self, reader, processor, writer=None):
        self.reader = reader
        self.processor = processor
        self.writer = writer

    def process(self) -> List[FacilityMatchDTO]:
        data = self._read_data()
        processed_data = self._process_data(data)
        return self._write_data(processed_data)

    def _read_data(self) -> FacilityListItemDict:
        return self.reader()

    def _process_data(self, data: FacilityListItemDict) -> List[FacilityMatchDTO]:
        return self.processor(data)

    def _write_data(self, processed_data: List[FacilityMatchDTO]) -> List[FacilityMatchDTO]:
        if self.writer:
            return self.writer(processed_data)
        return []

