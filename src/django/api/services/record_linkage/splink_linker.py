from splink import Linker, DuckDBAPI
from typing import List, Dict, Optional
from api.geocoding import geocode_address
import pandas as pd
import numpy as np
import json
import os
import copy

dir_path = os.path.dirname(os.path.realpath(__file__))


class SplinkLinker():
    linker: Linker
    records: List[Dict[str, any]]
    records_index: Dict[str, int]
    records_df: pd.DataFrame

    def __init__(self, records: List[Dict[str, any]]):
        self.records_index = {}
        self.records = copy.deepcopy(records)

        self.__create_records_df()
        self.__init_linker()

    def __init_linker(self):
        with open(f"{dir_path}/record_linkage_model_beta.json", "r") as f:
            settings = json.load(f)
        self.linker = Linker(
            self.records_df,
            settings=settings,
            db_api=DuckDBAPI(),
        )

    def __create_records_df(self) -> pd.DataFrame:
        self.records_df = pd.DataFrame(
            index=np.arange(0, len(self.records)),
            columns=[
                "os_id",
                "name",
                "address",
                "country_code",
                "geocoded_location_type",
                "lat",
                "lng"
            ],
        )

        for index, record in enumerate(self.records):
            geocoded_location_type = None

            if "geocoded_location_type" in record:
                geocoded_location_type = record["geocoded_location_type"]

            country_code = record.get("country", {}).get("alpha_2", None)
            lat = record.get("coordinates", {}).get("lat", None)
            lng = record.get("coordinates", {}).get("lng", None)

            if not all([country_code, lat, lng]):
                raise ValueError(
                    f"Missing required fields in record at index {index}"
                )

            self.records_df.loc[index] = [
                record["os_id"],
                record["name"],
                record["address"],
                country_code,
                geocoded_location_type,
                lat,
                lng
            ]
            self.records_index[record["os_id"]] = index
            self.records[index]["confidence_score"] = 0.0

    def __get_geocoding_result(
        self,
        address: str,
        country_code: str,
    ) -> Optional[Dict[str, any]]:
        geocoded_data = geocode_address(
            address=address,
            country_code=country_code,
        )

        if "full_response" not in geocoded_data:
            return None

        if (
            "results" not in geocoded_data["full_response"]
            or not geocoded_data["full_response"]["results"]
        ):
            return None

        result = geocoded_data["full_response"]["results"][0]

        return {
            "geocoded_address": result["formatted_address"],
            "geocoded_location_type": result["geometry"]["location_type"],
            "lat": geocoded_data["geocoded_point"]["lat"],
            "lng": geocoded_data["geocoded_point"]["lng"],
        }

    def predict(
        self,
        name: str,
        address: str,
        country_code: str,
    ) -> List[Dict[str, any]]:
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
            "lng": None,
            "confidence_score": 0.0,
        }

        if geocoding_result:
            record["geocoded_location_type"] = geocoding_result[
                "geocoded_location_type"
            ]
            record["lat"] = geocoding_result["lat"]
            record["lng"] = geocoding_result["lng"]

        matching_df = self.linker.inference.find_matches_to_new_records(
            [record],
            blocking_rules=[],
        ).as_pandas_dataframe()

        if not matching_df.empty and (
            "match_probability" in matching_df.columns
        ):
            matching_df = matching_df.rename(
                columns={"match_probability": "confidence_score"}
            )

        if not matching_df.empty:
            matching_df = matching_df.sort_values(
                "confidence_score",
                ascending=False,
            )

        if matching_df.empty:
            return self.records

        required_columns = ["os_id_l", "confidence_score"]
        if not all(col in matching_df.columns for col in required_columns):
            raise ValueError(
                "Matching DataFrame missing required "
                f"columns: {required_columns}"
            )

        for _, row in matching_df.iterrows():
            os_id = row["os_id_l"]
            if os_id not in self.records_index:
                continue
            index = self.records_index[os_id]
            self.records[index]["confidence_score"] = round(
                row["confidence_score"], 2
            )

        return self.records
