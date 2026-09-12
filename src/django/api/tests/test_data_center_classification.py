from api.extended_fields import create_extendedfield
from api.helpers.data_center import (
    DATA_CENTER_FACILITY_TYPE,
    is_data_center,
)
from api.models.extended_field import ExtendedField
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase


class DataCenterClassificationOnContributionTest(FacilityAPITestCaseBase):
    """
    A contribution whose row-level facility_type value is
    "Data Center" is classified as a data center. No dedicated write path -
    the value flows through the existing facility_type ExtendedField and
    resolves via the taxonomy (OSDEV-2587). These tests verify that.
    """

    fixtures = ["sectors"]

    # facility_type as shaped by ContriCleaner's RowFacilityTypeSerializer
    # (list/API), and by the SLC location_type -> facility_type mapping.
    DATA_CENTER_INPUT = {
        'raw_values': 'Data Center',
        'processed_values': ['Data Center'],
    }
    PRODUCTION_INPUT = {
        'raw_values': 'Final Product Assembly',
        'processed_values': ['Final Product Assembly'],
    }

    def _create_facility_type_field(self, field_value):
        create_extendedfield(
            ExtendedField.FACILITY_TYPE,
            field_value,
            self.list_item,
            self.contributor,
        )
        return ExtendedField.objects.get(
            facility_list_item=self.list_item,
            field_name=ExtendedField.FACILITY_TYPE,
        )

    def test_data_center_facility_type_is_captured_and_resolves(self):
        ef = self._create_facility_type_field(self.DATA_CENTER_INPUT)
        matched_facility_types = [mv[2] for mv in ef.value['matched_values']]
        self.assertIn(DATA_CENTER_FACILITY_TYPE, matched_facility_types)

    def test_contributed_data_center_is_recognized(self):
        ef = self._create_facility_type_field(self.DATA_CENTER_INPUT)
        # After matching, the field is linked to the facility.
        ef.facility = self.facility
        ef.save()
        self.assertTrue(is_data_center(self.facility))

    def test_contributed_production_location_is_not_a_data_center(self):
        ef = self._create_facility_type_field(self.PRODUCTION_INPUT)
        ef.facility = self.facility
        ef.save()
        self.assertFalse(is_data_center(self.facility))
