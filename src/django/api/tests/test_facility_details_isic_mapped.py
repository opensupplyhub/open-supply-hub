from django.core.cache import caches

from api.models import ExtendedField
from api.models.isic_taxonomy_config import IsicTaxonomyConfig
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase


class FacilityDetailsIsicMappedTest(FacilityAPITestCaseBase):
    '''GET /api/facilities/{os_id}/ returns ISIC values mapped from the
    location's Facility Type and Processing Type (OSDEV-3622).'''

    def setUp(self):
        super().setUp()
        caches['view_cache'].clear()
        self.addCleanup(caches['view_cache'].clear)
        self.config = IsicTaxonomyConfig.load()
        self.config.is_active = True
        self.config.save()

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

    def test_returns_path_by_title_with_its_source(self):
        self._add_processing_type('Final Product Assembly', 'Cut & Sew')

        self.assertEqual(self._mapped(), [{
            'facility_type': 'Final Product Assembly',
            'processing_type': 'Cut & Sew',
            'path': [
                {'level': 'section', 'title': 'Manufacturing'},
                {
                    'level': 'division',
                    'title': 'Manufacture of wearing apparel',
                },
                {
                    'level': 'group',
                    'title': (
                        'Manufacture of wearing apparel, except fur apparel'
                    ),
                },
                {
                    'level': 'class',
                    'title': (
                        'Manufacture of wearing apparel, except fur apparel'
                    ),
                },
            ],
        }])

    def test_never_returns_codes(self):
        self._add_processing_type('Final Product Assembly', 'Cut & Sew')

        for value in self._mapped():
            for step in value['path']:
                self.assertEqual(set(step), {'level', 'title'})

    def test_keeps_the_level_the_crosswalk_supports(self):
        # Sewing maps to section C only; no more specific level is inferred.
        self._add_processing_type('Final Product Assembly', 'Sewing')

        self.assertEqual(
            self._mapped()[0]['path'],
            [{'level': 'section', 'title': 'Manufacturing'}],
        )

    def test_omits_values_that_do_not_map(self):
        self._add_processing_type('Final Product Assembly', 'Tailoring')

        self.assertEqual(self._mapped(), [])

    def test_empty_without_taxonomy_values(self):
        self.assertEqual(self._mapped(), [])

    def test_empty_until_isic_is_enabled(self):
        self._add_processing_type('Final Product Assembly', 'Cut & Sew')
        self.config.is_active = False
        self.config.save()
        caches['view_cache'].clear()

        self.assertEqual(self._mapped(), [])
