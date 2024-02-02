from api.facility_type_processing_type import (
    ALIAS_MATCH,
    ALL_FACILITY_TYPES,
    ALL_PROCESSING_TYPES,
    ASSEMBLY,
    EXACT_MATCH,
    FACILITY_TYPE,
    FUZZY_MATCH,
    PROCESSING_TYPE,
    PROCESSING_TYPES_TO_FACILITY_TYPES,
    RAW_MATERIAL_PROCESSING_OR_PRODUCTION,
    SKIPPED_MATCHING,
    WET_ROLLER_PRINTING,
    get_facility_and_processing_type,
)

from django.test import TestCase


class FacilityAndProcessingTypeTest(TestCase):
    def setUp(self):
        self.sector = ["Apparel"]
        self.nonapparel_sector = ["Health"]

    def test_exact_processing_type_match(self):
        processing_type_input = "assembly"
        expected_output = (
            PROCESSING_TYPE,
            EXACT_MATCH,
            PROCESSING_TYPES_TO_FACILITY_TYPES[ALL_PROCESSING_TYPES[ASSEMBLY]],
            ALL_PROCESSING_TYPES[ASSEMBLY],
        )
        output = get_facility_and_processing_type(
            processing_type_input, self.sector
        )
        self.assertEqual(output, expected_output)

    def test_exact_facility_type_match(self):
        facility_type_input = "raw material processing or production"
        facility_type_value = ALL_FACILITY_TYPES[facility_type_input]
        expected_output = (
            FACILITY_TYPE,
            EXACT_MATCH,
            facility_type_value,
            facility_type_value,
        )
        output = get_facility_and_processing_type(
            facility_type_input, self.sector
        )
        self.assertEqual(output, expected_output)

    def test_alias_processing_type_match(self):
        processing_type_input = "wet printing"
        expected_output = (
            PROCESSING_TYPE,
            ALIAS_MATCH,
            PROCESSING_TYPES_TO_FACILITY_TYPES[
                ALL_PROCESSING_TYPES[WET_ROLLER_PRINTING]
            ],
            ALL_PROCESSING_TYPES[WET_ROLLER_PRINTING],
        )
        output = get_facility_and_processing_type(
            processing_type_input, self.sector
        )
        self.assertEqual(output, expected_output)

    def test_fuzzy_processing_type_match(self):
        processing_type_input = "asembley"
        expected_output = (
            PROCESSING_TYPE,
            FUZZY_MATCH,
            PROCESSING_TYPES_TO_FACILITY_TYPES[ALL_PROCESSING_TYPES[ASSEMBLY]],
            ALL_PROCESSING_TYPES[ASSEMBLY],
        )
        output = get_facility_and_processing_type(
            processing_type_input, self.sector
        )
        self.assertEqual(output, expected_output)

    def test_fuzzy_facility_type_match(self):
        facility_type_input = "raw mater process"
        facility_type_value = ALL_FACILITY_TYPES[
            RAW_MATERIAL_PROCESSING_OR_PRODUCTION
        ]
        expected_output = (
            FACILITY_TYPE,
            FUZZY_MATCH,
            facility_type_value,
            facility_type_value,
        )
        output = get_facility_and_processing_type(
            facility_type_input, self.sector
        )
        self.assertEqual(output, expected_output)

    def test_processing_type_sector_nonapparel(self):
        processing_type_input = "assembly"
        expected_output = (
            PROCESSING_TYPE,
            SKIPPED_MATCHING,
            None,
            processing_type_input,
        )
        output = get_facility_and_processing_type(
            processing_type_input, self.nonapparel_sector
        )
        self.assertEqual(output, expected_output)

    def test_exact_facility_type_match_sector_nonapparel(self):
        facility_type_input = "raw material processing or production"
        expected_output = (
            PROCESSING_TYPE,
            SKIPPED_MATCHING,
            None,
            facility_type_input,
        )
        output = get_facility_and_processing_type(
            facility_type_input, self.nonapparel_sector
        )
        self.assertEqual(output, expected_output)
