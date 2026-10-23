from django.core.cache import caches
from django.db import connection
from django.test.utils import CaptureQueriesContext
from waffle.testutils import override_switch

from api.models import ExtendedField
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase


@override_switch('enable_isic_taxonomy', active=True)
class FacilityDetailsIsicMappedTest(FacilityAPITestCaseBase):
    '''GET /api/facilities/{os_id}/ returns ISIC values mapped from the
    location's Facility Type and Processing Type (OSDEV-3622).'''

    def setUp(self):
        super().setUp()
        caches['view_cache'].clear()
        self.addCleanup(caches['view_cache'].clear)

    def _add_processing_type(self, facility_type, processing_type):
        value = {
            'raw_values': processing_type,
            'matched_values': [
                ['PROCESSING_TYPE', 'EXACT', facility_type, processing_type],
            ],
        }
        for field_name in (
            ExtendedField.FACILITY_TYPE,
            ExtendedField.PROCESSING_TYPE,
        ):
            ExtendedField.objects.create(
                contributor=self.contributor,
                facility=self.facility,
                facility_list_item=self.list_item,
                field_name=field_name,
                value=value,
            )

    def _mapped(self):
        response = self.client.get(f'/api/facilities/{self.facility.id}/')
        self.assertEqual(response.status_code, 200)
        return response.json()['properties']['isic_4_mapped']

    def test_returns_path_with_codes_and_its_source(self):
        self._add_processing_type('Final Product Assembly', 'Cut & Sew')

        self.assertEqual(self._mapped(), [{
            'facility_type': 'Final Product Assembly',
            'processing_type': 'Cut & Sew',
            'path': [
                {'level': 'section', 'code': 'C', 'title': 'Manufacturing'},
                {
                    'level': 'division',
                    'code': '14',
                    'title': 'Manufacture of wearing apparel',
                },
                {
                    'level': 'group',
                    'code': '141',
                    'title': (
                        'Manufacture of wearing apparel, except fur apparel'
                    ),
                },
                {
                    'level': 'class',
                    'code': '1410',
                    'title': (
                        'Manufacture of wearing apparel, except fur apparel'
                    ),
                },
            ],
        }])

    def test_keeps_the_level_the_crosswalk_supports(self):
        # Sewing maps to section C only; no more specific level is inferred.
        self._add_processing_type('Final Product Assembly', 'Sewing')

        self.assertEqual(
            self._mapped()[0]['path'],
            [{'level': 'section', 'code': 'C', 'title': 'Manufacturing'}],
        )

    def test_omits_values_that_do_not_map(self):
        self._add_processing_type('Final Product Assembly', 'Tailoring')

        self.assertEqual(self._mapped(), [])

    def test_empty_without_taxonomy_values(self):
        self.assertEqual(self._mapped(), [])

    @override_switch('enable_isic_taxonomy', active=False)
    def test_switch_off_skips_isic_tables(self):
        # migrate runs after the new image is live, so with the switch off
        # the profile must not read the crosswalk.
        self._add_processing_type('Final Product Assembly', 'Cut & Sew')
        caches['view_cache'].clear()

        with CaptureQueriesContext(connection) as queries:
            mapped = self._mapped()

        self.assertEqual(mapped, [])
        self.assertFalse(any(
            'isic_mapped_entries' in q['sql']
            for q in queries
        ))
