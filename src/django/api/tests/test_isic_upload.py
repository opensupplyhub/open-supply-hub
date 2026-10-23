import csv

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from api.extended_fields import (
    MAX_ISIC_VALUES,
    create_extendedfields_for_single_item,
    get_isic_extendedfield_value,
)
from api.isic_taxonomy.crosswalk import CROSSWALK_CSV_PATH
from api.isic_taxonomy.isic_lookup import CODE, EXACT, FUZZY, match_isic
from api.isic_taxonomy.revisions import isic_entry
from api.models import ExtendedField
from api.serializers.v1.production_location_post_schema_serializer import (
    ProductionLocationPostSchemaSerializer,
)
from api.models.facility.facility_index import FacilityIndex
from api.tests.facility_api_test_case_base import FacilityAPITestCaseBase
from contricleaner.lib.contri_cleaner import ContriCleaner
from contricleaner.tests.os_id_lookup_mock import OSIDLookupMock
from contricleaner.tests.sector_cache_mock import SectorCacheMock


def isic_4_value(value):
    return get_isic_extendedfield_value(value, ExtendedField.ISIC_4)


def isic_5_value(value):
    return get_isic_extendedfield_value(value, ExtendedField.ISIC_5)


APPAREL = {
    'section': 'C - Manufacturing',
    'division': '14 - Manufacture of wearing apparel',
    'group': '141 - Manufacture of wearing apparel, except fur apparel',
    'class': '1410 - Manufacture of wearing apparel, except fur apparel',
}


class IsicLookupTest(SimpleTestCase):
    def test_matches_a_code_at_every_level(self):
        self.assertEqual(match_isic('1410', '4'), (APPAREL, CODE))
        self.assertEqual(
            match_isic(' 141 ', '4')[0]['group'], APPAREL['group'],
        )
        self.assertEqual(match_isic('14', '4')[0], {
            'section': APPAREL['section'],
            'division': APPAREL['division'],
        })
        self.assertEqual(match_isic('c', '4'), (
            {'section': 'C - Manufacturing'}, CODE,
        ))

    def test_restores_a_leading_zero_excel_dropped(self):
        # "0111" saved as a number in Excel arrives as "111".
        self.assertEqual(match_isic('111', '4')[0]['class'], match_isic(
            '0111', '4')[0]['class'])
        self.assertIsNone(match_isic('2', '4'))

    def test_digits_that_are_a_code_keep_their_own_meaning(self):
        # "141" is the apparel group, even though "0141" (cattle) loses
        # its zero the same way; the contributor's text wins.
        self.assertEqual(match_isic('141', '4')[0]['group'], APPAREL['group'])

    def test_derives_the_section_of_a_division(self):
        self.assertEqual(
            isic_entry('6201', '4')['section'],
            'J - Information and communication',
        )

    def test_matches_an_exact_title_ignoring_case_and_punctuation(self):
        self.assertEqual(
            match_isic(
                'MANUFACTURE OF WEARING APPAREL EXCEPT FUR APPAREL', '4',
            ),
            (APPAREL, EXACT),
        )

    def test_a_title_shared_by_a_group_and_class_resolves_to_the_class(self):
        entry, _ = match_isic(
            'Manufacture of wearing apparel, except fur apparel', '4',
        )
        self.assertEqual(entry['class'], APPAREL['class'])

    def test_matches_a_misspelled_title(self):
        entry, match_type = match_isic('Manufacture of wearing aparel', '4')
        self.assertEqual(match_type, FUZZY)
        self.assertEqual(entry['division'], APPAREL['division'])

    def test_vague_or_unknown_text_matches_nothing(self):
        # A wrong industry is worse than none: fragments and descriptions
        # that only share a word with a title are not guessed.
        for text in (
            'apparel', 'garment factory', 'sewing', '99999', '', None,
        ):
            with self.subTest(text=text):
                self.assertIsNone(match_isic(text, '4'))

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
                            isic_entry(code, '4')[level],
                            f'{code} - {row[f"isic_{level}_title"]}',
                        )


class IsicExtendedFieldValueTest(SimpleTestCase):
    def test_list_text_resolves_codes_and_titles_separated_by_pipes(self):
        self.assertEqual(
            isic_4_value(
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

    def test_commas_split_codes_but_never_titles(self):
        # Titles contain commas, so only "|" separates values; commas
        # still split a run of bare codes.
        value = isic_4_value(
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
                    isic_4_value(text), {'raw_value': []},
                )

    def test_structured_values_are_unchanged(self):
        # The v1 API (and RBA) send objects; those keep working as before.
        self.assertEqual(
            isic_4_value([{'class': '1410 - Apparel'}]),
            {'raw_value': [{'class': '1410 - Apparel'}]},
        )

    def test_one_cell_resolves_at_most_the_v1_limit(self):
        value = isic_4_value(','.join(['1410'] * 10000))

        self.assertEqual(len(value['raw_value']), MAX_ISIC_VALUES)

    def test_blank_pieces_do_not_count_toward_the_limit(self):
        value = isic_4_value(',' * 40 + '1410')

        self.assertEqual(value['raw_value'], [APPAREL])

    def test_stored_entries_are_copies_of_the_cached_match(self):
        first = isic_4_value('1410')['raw_value'][0]
        first['class'] = 'changed'

        self.assertEqual(match_isic('1410', '4')[0], APPAREL)

    def test_very_long_text_is_not_scanned(self):
        self.assertIsNone(match_isic('apparel ' * 100, '4'))

    def test_titles_separated_by_commas_are_not_split(self):
        # Splitting on commas would cut titles like "Manufacture of wearing
        # apparel, except fur apparel" into fragments.
        self.assertEqual(
            isic_4_value('Weaving of textiles, Finishing of textiles'),
            {'raw_value': []},
        )

    def test_each_column_reads_its_own_revision(self):
        # 1104 is soft drinks in ISIC 4 but malt in ISIC 5.
        self.assertIn(
            'soft drinks', isic_4_value('1104')['raw_value'][0]['class'],
        )
        self.assertEqual(
            isic_5_value('1104')['raw_value'][0]['class'],
            '1104 - Manufacture of malt',
        )
        self.assertEqual(
            isic_5_value('Manufacture of malt')['matched_values'],
            [['Manufacture of malt', EXACT]],
        )

    def test_isic_5_objects_are_stored_with_every_level(self):
        self.assertEqual(
            isic_5_value([{'class': '1104 - Manufacture of malt'}]),
            {'raw_value': [isic_entry('1104', '5')]},
        )
        self.assertEqual(
            isic_5_value([{'class': '9999 - Not a class'}]),
            {'raw_value': []},
        )

    def test_text_that_matches_nothing_stores_nothing(self):
        self.assertEqual(
            isic_4_value('garment factory'),
            {'raw_value': []},
        )


class IsicListUploadTest(FacilityAPITestCaseBase):
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
            b'"1410|Weaving of textiles|garment factory"\n',
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

    def test_a_csv_isic_5_column_reaches_search(self):
        uploaded = SimpleUploadedFile(
            'list.csv',
            b'country,name,address,sector,isic_4,isic_5\n'
            b'US,Brewery,1 Main St,Food,1104,1104\n',
        )
        row = ContriCleaner(
            uploaded, SectorCacheMock(), OSIDLookupMock()
        ).process_data().rows[0]

        create_extendedfields_for_single_item(self.list_item, row.fields)
        ExtendedField.objects.filter(
            facility_list_item=self.list_item,
        ).update(facility=self.facility)
        # update() skips the trigger; save one row to reindex.
        ExtendedField.objects.filter(facility=self.facility).first().save()

        index = FacilityIndex.objects.get(id=self.facility.id)
        self.assertEqual(index.isic_class, ['1104'])
        self.assertEqual(index.isic5_class, ['1104'])
        # ISIC 5 1104 is malt: an ISIC 4 search for malt (1103) finds it.
        response = self.client.get(
            '/api/facilities/', {'isic_4': 'class:1103'},
        )
        self.assertEqual(
            [feature['id'] for feature in response.json()['features']],
            [self.facility.id],
        )


class Isic5V1SchemaTest(SimpleTestCase):
    def _errors(self, isic_5):
        serializer = ProductionLocationPostSchemaSerializer(data={
            'name': 'Mill', 'address': '1 Main St', 'country': 'US',
            'isic_5': isic_5,
        })
        serializer.is_valid()
        return serializer.errors.get('isic_5')

    def test_accepts_isic_5_objects(self):
        self.assertIsNone(self._errors([{'class': '1104 - Malt'}]))

    def test_rejects_codes_isic_5_does_not_have(self):
        self.assertIsNotNone(self._errors([{'class': '9999 - Nothing'}]))
