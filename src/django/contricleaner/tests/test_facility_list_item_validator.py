from contricleaner.api.facility_list_item_validator import (
    FacilityListItemValidator
)
import unittest


class FacilityListItemValidatorTest(unittest.TestCase):
    def setUp(self):
        self.validator = FacilityListItemValidator()

    def test_validate(self):
        # Add your test case here
        pass

    def test_parser(self):
        listProcessor = ListProcessor(CSVListParser())
        csvList = dict()
        listInfo = listProcessor.handle(csvList)
        listInfo.errors
        listInfo.data
        listInfo.items
        listItemProcessor = ListItemProcessor(CSVListItemParser())
        pass

