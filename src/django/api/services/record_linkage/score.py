import pandas as pd
from geopy.distance import geodesic
from api.services.record_linkage.matchers import (
    NameMatcher,
    AddressMatcher,
    GeocodedLocationTypMatcher,
    DistanceMatcher,
    OpenSeachScoreMatcher
)


class ConfidenceCalculator():
    records_df: pd.DataFrame
    record: dict
    name_confidence: float = 0.28
    address_confidence: float = 0.15
    geocoded_location_type_confidence: float = 0.02
    geocoded_address_confidence: float = 0.05
    distance_confidence: float = 0.1
    score_confidence: float = 0.5

    def __init__(self, records_df: pd.DataFrame, record: dict):
        self.records_df = records_df
        self.record = record

    def __calculate_confidence_weights(self):
        if self.record['geocoded_location_type'] is "ROOFTOP":
            self.name_confidence = 0.18
            self.address_confidence = 0.2
            self.geocoded_location_type_confidence = 0.02
            self.geocoded_address_confidence = 0.05
            self.distance_confidence = 0.15
            self.score_confidence = 0.4
            return


    def __calculate_confidence_scores(self):
        self.records_df["name_confidence"] = self.records_df["name"].apply(
            lambda row_name: NameMatcher.match(
                row_name,
                self.record["name"]
            ),
        )
        self.records_df["address_confidence"] = self.records_df["address"].apply(
            lambda row_address: AddressMatcher.match(
                row_address,
                self.record["address"]
            ),
        )
        self.records_df["geocoded_address_confidence"] = self.records_df["geocoded_address"].apply(
            lambda row_geocoded_address: AddressMatcher.match(
                row_geocoded_address,
                self.record["geocoded_address"]
            )
        )
        self.records_df["geocoded_location_type_confidence"] = self.records_df["geocoded_location_type"].apply(
            lambda row_geocoded_location_type: GeocodedLocationTypMatcher.match(
                row_geocoded_location_type,
                self.record["geocoded_location_type"]
            )
        )
        self.records_df["distance_in_km"] = self.records_df.apply(
            lambda row: geodesic(
                (row["lat"], row["lng"]),
                (self.record["lat"], self.record["lng"])
            ).km,
            axis=1
        )
        self.records_df["distance_confidence"] = self.records_df["distance_in_km"].apply(
            lambda row_distance: DistanceMatcher.match(
                row_distance
            ),
        )
        self.records_df["score_confidence"] = self.records_df["score"].apply(
            lambda row_score: OpenSeachScoreMatcher.match(
                row_score
            ),
        )

    def score(self) -> pd.DataFrame:
        self.__calculate_confidence_scores()
        self.__calculate_confidence_weights()
        self.records_df["confidence_score"] = self.records_df["name_confidence"] * self.name_confidence + \
            self.records_df["address_confidence"] * self.address_confidence + \
            self.records_df["geocoded_location_type_confidence"] * self.geocoded_location_type_confidence + \
            self.records_df["geocoded_address_confidence"] * self.geocoded_address_confidence + \
            self.records_df["distance_confidence"] * self.distance_confidence + \
            self.records_df["score_confidence"] * self.score_confidence

        return self.records_df
