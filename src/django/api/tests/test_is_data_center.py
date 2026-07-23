from django.test import SimpleTestCase

from api.helpers.data_center import (
    DATA_CENTER_FACILITY_TYPE,
    is_data_center,
    matched_values_include_data_center,
)
from api.models.extended_field import ExtendedField
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase


def facility_type_value(*facility_types):
    """Build a facility_type ExtendedField value with the given facility
    types placed at index 2 of each matched_values entry (the real shape)."""
    return {
        'raw_values': list(facility_types),
        'matched_values': [
            ['FACILITY_TYPE', 'EXACT', ft, None] for ft in facility_types
        ],
    }


class MatchedValuesIncludeDataCenterTest(SimpleTestCase):
    """Pure-logic tests for the matched_values parser (no DB)."""

    def test_data_center_value_returns_true(self):
        value = facility_type_value(DATA_CENTER_FACILITY_TYPE)
        self.assertTrue(matched_values_include_data_center(value))

    def test_production_value_returns_false(self):
        value = facility_type_value('Final Product Assembly')
        self.assertFalse(matched_values_include_data_center(value))

    def test_mixed_value_returns_true(self):
        # A value carrying both a production type and Data Center.
        value = facility_type_value('Office / HQ', DATA_CENTER_FACILITY_TYPE)
        self.assertTrue(matched_values_include_data_center(value))

    def test_empty_or_malformed_values_return_false(self):
        self.assertFalse(matched_values_include_data_center(None))
        self.assertFalse(matched_values_include_data_center('Data Center'))
        self.assertFalse(matched_values_include_data_center({}))
        self.assertFalse(
            matched_values_include_data_center({'matched_values': []})
        )
        self.assertFalse(
            matched_values_include_data_center({'matched_values': [['x']]})
        )


class IsDataCenterTest(FacilityAPITestCaseBase):
    """DB-level tests for the is_data_center helper."""

    def _add_facility_type(self, *facility_types):
        return ExtendedField.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            facility_list_item=self.list_item,
            field_name=ExtendedField.FACILITY_TYPE,
            value=facility_type_value(*facility_types),
        )

    def test_none_returns_false(self):
        self.assertFalse(is_data_center(None))

    def test_facility_without_facility_type_returns_false(self):
        self.assertFalse(is_data_center(self.facility))

    def test_data_center_facility_returns_true(self):
        self._add_facility_type(DATA_CENTER_FACILITY_TYPE)
        self.assertTrue(is_data_center(self.facility))

    def test_production_facility_returns_false(self):
        self._add_facility_type('Final Product Assembly')
        self.assertFalse(is_data_center(self.facility))

    def test_mixed_facility_returns_true(self):
        # Interim rule (OSDEV-3067 AC#3): any Data Center value => True.
        self._add_facility_type('Office / HQ')
        self._add_facility_type(DATA_CENTER_FACILITY_TYPE)
        self.assertTrue(is_data_center(self.facility))
