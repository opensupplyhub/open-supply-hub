import csv

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from api.extended_fields import (
    create_extendedfields_for_single_item,
    get_isic_4_extendedfield_value,
)
from api.isic_taxonomy.crosswalk import CROSSWALK_CSV_PATH
from api.isic_taxonomy.isic4_lookup import (
    CODE,
    EXACT,
    FUZZY,
    STRUCTURE_CSV_PATH,
    isic4_entry,
    match_isic4,
)
from api.models import ExtendedField
from api.models.facility.facility_index import FacilityIndex
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase
from contricleaner.lib.contri_cleaner import ContriCleaner
from contricleaner.tests.os_id_lookup_mock import OSIDLookupMock
from contricleaner.tests.sector_cache_mock import SectorCacheMock

APPAREL = {
    'section': 'C - Manufacturing',
    'division': '14 - Manufacture of wearing apparel',
    'group': '141 - Manufacture of wearing apparel, except fur apparel',
    'class': '1410 - Manufacture of wearing apparel, except fur apparel',
}


class Isic4LookupTest(SimpleTestCase):
    def test_structure_is_the_complete_un_list(self):
        with open(STRUCTURE_CSV_PATH, newline='') as file:
            codes = [row['code'] for row in csv.DictReader(file)]
        counts = {
            'section': sum(code.isalpha() for code in codes),
            'division': sum(len(code) == 2 for code in codes),
            'group': sum(len(code) == 3 for code in codes),
            'class': sum(len(code) == 4 for code in codes),
        }
        self.assertEqual(
            counts,
            {'section': 21, 'division': 88, 'group': 238, 'class': 419},
        )

    def test_matches_a_code_at_every_level(self):
        self.assertEqual(match_isic4('1410'), (APPAREL, CODE))
        self.assertEqual(match_isic4(' 141 ')[0]['group'], APPAREL['group'])
        self.assertEqual(match_isic4('14')[0], {
            'section': APPAREL['section'],
            'division': APPAREL['division'],
        })
        self.assertEqual(match_isic4('c'), (
            {'section': 'C - Manufacturing'}, CODE,
        ))

    def test_derives_the_section_of_a_division(self):
        self.assertEqual(
            isic4_entry('6201')['section'],
            'J - Information and communication',
        )

    def test_matches_an_exact_title_ignoring_case_and_punctuation(self):
        self.assertEqual(
            match_isic4('MANUFACTURE OF WEARING APPAREL EXCEPT FUR APPAREL'),
            (APPAREL, EXACT),
        )

    def test_a_title_shared_by_a_group_and_class_resolves_to_the_class(self):
        entry, _ = match_isic4(
            'Manufacture of wearing apparel, except fur apparel'
        )
        self.assertEqual(entry['class'], APPAREL['class'])

    def test_matches_a_misspelled_title(self):
        entry, match_type = match_isic4('Manufacture of wearing aparel')
        self.assertEqual(match_type, FUZZY)
        self.assertEqual(entry['division'], APPAREL['division'])

    def test_vague_or_unknown_text_matches_nothing(self):
        # A wrong industry is worse than none: fragments and descriptions
        # that only share a word with a title are not guessed.
        for text in (
            'apparel', 'garment factory', 'sewing', '99999', '', None,
        ):
            with self.subTest(text=text):
                self.assertIsNone(match_isic4(text))

    def test_every_crosswalk_title_is_the_official_un_title(self):
        # The OSDEV-3414 crosswalk must name UN ISIC Rev 4 categories
        # exactly, or profiles would show titles nobody can look up.
        with open(CROSSWALK_CSV_PATH, newline='') as file:
            rows = list(csv.DictReader(file))
        for row in rows:
            for level in ('section', 'division', 'group', 'class'):
                code = row[f'isic_{level}']
                if code:
                    with self.subTest(code=code):
                        self.assertEqual(
                            isic4_entry(code)[level],
                            f'{code} - {row[f"isic_{level}_title"]}',
                        )


class Isic4ExtendedFieldValueTest(SimpleTestCase):
    def test_list_text_resolves_codes_and_titles_separated_by_pipes(self):
        self.assertEqual(
            get_isic_4_extendedfield_value(
                '1410|Weaving of textiles|garment factory'
            ),
            {
                'raw_value': [
                    APPAREL,
                    {
                        'section': 'C - Manufacturing',
                        'division': '13 - Manufacture of textiles',
                        'group': (
                            '131 - Spinning, weaving and finishing of '
                            'textiles'
                        ),
                        'class': '1312 - Weaving of textiles',
                    },
                ],
                'matched_values': [
                    ['1410', CODE],
                    ['Weaving of textiles', EXACT],
                ],
            },
        )

    def test_comma_separated_values_split_but_titles_keep_their_commas(self):
        # The list cleaner splits other multi-value columns on commas too,
        # and adds a space after each comma, so contributors send both.
        value = get_isic_4_extendedfield_value(
            '1410, 1312|Manufacture of wearing apparel, except fur apparel'
        )
        self.assertEqual(
            [entry.get('class') for entry in value['raw_value']],
            [
                APPAREL['class'],
                '1312 - Weaving of textiles',
                APPAREL['class'],
            ],
        )
        self.assertEqual(
            [matched[0] for matched in value['matched_values']],
            [
                '1410',
                '1312',
                'Manufacture of wearing apparel, except fur apparel',
            ],
        )

    def test_spreadsheet_noise_matches_nothing(self):
        # What moderators find in list cells: placeholders and formulas.
        for text in ('nan', 'NAN', 'N/A', '=VLOOKUP(A2,B:C,2,0)', '#REF!'):
            with self.subTest(text=text):
                self.assertEqual(
                    get_isic_4_extendedfield_value(text), {'raw_value': []},
                )

    def test_structured_values_are_unchanged(self):
        # The v1 API (and RBA) send objects; those keep working as before.
        self.assertEqual(
            get_isic_4_extendedfield_value([{'class': '1410 - Apparel'}]),
            {'raw_value': [{'class': '1410 - Apparel'}]},
        )

    def test_text_that_matches_nothing_stores_nothing(self):
        self.assertEqual(
            get_isic_4_extendedfield_value('garment factory'),
            {'raw_value': []},
        )


class Isic4ListUploadTest(FacilityAPITestCaseBase):
    def test_a_csv_isic_column_reaches_search(self):
        """
        OSDEV-3442 AC: an ISIC column in an uploaded list ends up on the
        facility. Follows the list pipeline: ContriCleaner parses the file,
        ProcessingFacilityList hands each row's fields to
        create_extendedfields_for_single_item, and the facility's
        ExtendedFields drive the search index.
        """
        uploaded = SimpleUploadedFile(
            'list.csv',
            b'country,name,address,sector,isic_4\n'
            b'US,Mill,1 Main St,Apparel,'
            b'"1410, Weaving of textiles|garment factory"\n',
        )
        row = ContriCleaner(
            uploaded, SectorCacheMock(), OSIDLookupMock()
        ).process_data().rows[0]

        create_extendedfields_for_single_item(self.list_item, row.fields)

        field = ExtendedField.objects.get(
            facility_list_item=self.list_item,
            field_name=ExtendedField.ISIC_4,
        )
        self.assertEqual(
            field.value['matched_values'],
            [['1410', CODE], ['Weaving of textiles', EXACT]],
        )

        # Matching the item to a facility links its ExtendedFields; this
        # stands in for that step, which fires the indexing trigger.
        field.facility = self.facility
        field.save()

        index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertEqual(sorted(index.isic_class), ['1312', '1410'])
        response = self.client.get(
            '/api/facilities/', {'isic_4': 'class:1312'},
        )
        self.assertEqual(
            [feature['id'] for feature in response.json()['features']],
            [self.facility.id],
        )
