from thefuzz import fuzz
import math


class AddressMatcher():
    @staticmethod
    def match(address_a: str, address_b: str) -> float:
        if not address_a or not address_b:
            return 0.0

        return (
            fuzz.token_set_ratio(address_a, address_b)
            + fuzz.token_sort_ratio(address_a, address_b)
        ) / 200.0


class NameMatcher():
    @staticmethod
    def match(name_a: str, name_b: str) -> float:
        if not name_a or not name_b:
            return 0.0

        return (
            fuzz.token_set_ratio(name_a, name_b) +
            fuzz.token_sort_ratio(name_a, name_b)
        ) / 200.0


DISTANCE_TO_CONFIDENCE = {
    0.005: 1,
    0.1: 0.9,
    0.152: 0.7,
    1.0: 0.6,
    5: 0.5,
    30: 0.4,
    100: 0.3,
    200: 0.2,
    500: 0.1,
}


class DistanceMatcher():
    @staticmethod
    def match(distance_in_km: float) -> float:
        """
        Returns a confidence score based on the distance in km
        """

        for threshold, score in DISTANCE_TO_CONFIDENCE.items():
            if distance_in_km <= threshold:
                return score

        return 0


class GeocodedLocationTypMatcher():
    @staticmethod
    def match(location_type_a: str, location_type_b: str) -> float:
        """
        Returns a confidence score based on the location type
        """
        if not location_type_a or not location_type_b:
            return 0.0

        if location_type_a == location_type_b:
            return 1.0

        # If one is ROOFTOP and they don't match, confidence should be lower
        if location_type_a == "ROOFTOP" or location_type_b == "ROOFTOP":
            return 0.5

        return 0.0


TOP_LEVEL_OS_SCORE = 110


class OpenSearchScoreMatcher():
    @staticmethod
    def match(score: float) -> float:
        if score < 0:
            return 0.0

        confidence = math.log(score + 1) / math.log(TOP_LEVEL_OS_SCORE + 1)

        if confidence > 1:
            return 1.0

        return confidence
