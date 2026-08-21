from django.http import QueryDict
from django.test import SimpleTestCase

from api.facility_processing_query import parse_facility_processing_query


class FacilityProcessingQueryTest(SimpleTestCase):
    def test_removes_blank_values_and_preserves_nonempty_exact_values(self):
        params = QueryDict(
            'facility_type=&facility_type=Office%20%2F%20HQ'
            '&processing_type=%20%20'
            '&processing_type=CAPS'
            '&processing_type_exact='
            '&processing_type_exact=CAPS'
        )

        parsed = parse_facility_processing_query(params)

        self.assertEqual(parsed.facility_types, ['Office / HQ'])
        self.assertEqual(parsed.processing_types, ['CAPS'])
        self.assertEqual(parsed.exact_processing_types, ['CAPS'])

    def test_exact_companion_requires_identical_regular_value(self):
        params = QueryDict(
            'processing_type=CAPS'
            '&processing_type_exact=Caps'
            '&processing_type_exact=orphan'
        )

        parsed = parse_facility_processing_query(params)

        self.assertEqual(parsed.processing_types, ['CAPS'])
        self.assertEqual(parsed.exact_processing_types, [])
