from typing import Dict


class FacilityListItemDTO:
    country: str
    name: str
    address: str


FacilityListItemDict = Dict[str, FacilityListItemDTO]
