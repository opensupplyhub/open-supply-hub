from typing import List, Dict
from api.geocoding import geocode_address
from operator import itemgetter
from api.services.record_linkage.score import ConfidenceCalculator
import pandas as pd
import numpy as np
import os
import copy

dir_path = os.path.dirname(os.path.realpath(__file__))


class RecordLinker():
    records: List[Dict[str, any]]
    records_index: Dict[str, int]
    records_df: pd.DataFrame

    def __init__(self, records: List[Dict[str, any]]):
        self.records_index = {}
        self.records = copy.deepcopy(records)
        self.__create_records_df()

    def __create_records_df(self) -> pd.DataFrame:
        self.records_df = pd.DataFrame(
            index=np.arange(0, len(self.records)),
            columns=[
                "os_id",
                "name",
                "address",
                "country_code",
                "geocoded_location_type",
                "geocoded_address",
                "score",
                "lat",
                "lng"
            ],
        )

        for index, record in enumerate(self.records):
            geocoded_location_type = None

            if "geocoded_location_type" in record:
                geocoded_location_type = record["geocoded_location_type"]

            self.records_df.loc[index] = [
                record["os_id"],
                record["name"],
                record["address"],
                record["country"]["alpha_2"],
                geocoded_location_type,
                record["geocoded_address"] if "geocoded_address" in record else None,
                record["score"] if "score" in record else None,
                record["coordinates"]["lat"],
                record["coordinates"]["lng"]
            ]
            self.records_index[record["os_id"]] = index
            self.records[index]["confidence_score"] = 0.0

    def __get_geocoding_result(self, address: str, country_code: str) -> Dict[str, any]:
        geocoded_data = geocode_address(
            address=address,
            country_code=country_code,
        )

        if not "full_response" in geocoded_data:
            return None

        if not "results" in geocoded_data["full_response"] or not geocoded_data["full_response"]["results"]:
            return None

        result = geocoded_data["full_response"]["results"][0]

        return {
            "geocoded_address": result["formatted_address"],
            "geocoded_location_type": result["geometry"]["location_type"],
            "lat": geocoded_data["geocoded_point"]["lat"],
            "lng": geocoded_data["geocoded_point"]["lng"],
        }

    def predict(self, name: str, address: str, country_code: str) -> List[Dict[str, any]]:
        geocoding_result = self.__get_geocoding_result(
            address=address,
            country_code=country_code
        )

        record = {
            "os_id": "",
            "name": name,
            "address": address,
            "country_code": country_code,
            "geocoded_location_type": None,
            "lat": None,
            "lng": None
        }

        if geocoding_result:
            record["geocoded_location_type"] = geocoding_result["geocoded_location_type"]
            record["lat"] = geocoding_result["lat"]
            record["lng"] = geocoding_result["lng"]
            record["geocoded_address"] = geocoding_result["geocoded_address"]

        self.records_df = ConfidenceCalculator(self.records_df, record).score()

        for _, row in self.records_df.iterrows():
            os_id = row["os_id"]
            index = self.records_index[os_id]
            self.records[index]["confidence_score"] = round(
                row["confidence_score"], 2)

        return sorted(
            self.records,
            key=itemgetter("confidence_score"),
            reverse=True
        )
