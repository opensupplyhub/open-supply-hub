import pandas as pd


class ConfidenceCalculator():
    records_df: pd.DataFrame
    record: dict

    def __init__(self, records_df: pd.DataFrame, record: dict):
        self.records_df = records_df
        self.record = record

    def score(self) -> pd.DataFrame:
        self.records_df["confidence_score"] = self.records_df["name_confidence"] * 0.28 + \
            self.records_df["address_confidence"] * 0.15 + \
            self.records_df["geocoded_location_type_confidence"] * 0.02 + \
            self.records_df["geocoded_address_confidence"] * 0.05 + \
            self.records_df["distance_confidence"] * 0.1 + \
            self.records_df["score_confidence"] * 0.5

        return self.records_df
