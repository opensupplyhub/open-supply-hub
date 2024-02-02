from typing_extensions import TypedDict


class ResultsDTO(TypedDict):
    no_gazetteer_matches: str
    no_geocoded_items: str
    gazetteer_threshold: str
    automatic_threshold: str
    recall_weight: str
    code_version: str
