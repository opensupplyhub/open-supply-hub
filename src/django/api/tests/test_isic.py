from django.test import SimpleTestCase

from api.isic import build_isic_filter, parse_isic_filter_values
from api.isic_taxonomy import revisions


class ParseIsicFilterValuesTest(SimpleTestCase):
    def test_parse_isic_filter_values(self):
        self.assertEqual(
            parse_isic_filter_values(['section:C', 'class:0111', 'invalid']),
            [('section', 'C'), ('class', '0111')],
        )


class IsicRevisionsTest(SimpleTestCase):
    def test_structures_are_the_complete_un_lists(self):
        for revision, sizes in (('4', (21, 88, 238, 419)),
                                ('5', (22, 87, 258, 463))):
            with self.subTest(revision=revision):
                levels = [
                    revisions.level_of(code)
                    for code in revisions.titles(revision)
                ]
                self.assertEqual(
                    tuple(levels.count(level) for level in
                          ('section', 'division', 'group', 'class')),
                    sizes,
                )

    def test_every_class_has_a_counterpart_in_the_other_revision(self):
        for revision in revisions.REVISIONS:
            with self.subTest(revision=revision):
                classes = {
                    code for code in revisions.titles(revision)
                    if revisions.level_of(code) == 'class'
                }
                for code in classes:
                    self.assertTrue(revisions.translate({code}, revision))

    def test_a_code_means_what_its_revision_says(self):
        # 1104 is soft drinks in ISIC 4 but malt in ISIC 5.
        self.assertIn('soft drinks', revisions.titles('4')['1104'])
        self.assertIn('malt', revisions.titles('5')['1104'])
        self.assertEqual(revisions.translate({'1104'}, '5'), {'1103'})

    def test_a_title_shared_by_both_revisions_is_one_entry(self):
        [textiles] = [
            entry for entry in revisions.entries()
            if entry['title'] == 'Manufacture of textiles'
        ]
        self.assertEqual(textiles['codes'], {'4': '13', '5': '13'})
        self.assertEqual(textiles['trail'], 'Manufacturing')

    def test_entries_have_unique_ids_and_hide_repeated_titles(self):
        ids = [entry['id'] for entry in revisions.entries()]
        self.assertEqual(len(ids), len(set(ids)))
        # Class 1410 repeats its group's title; picking the group covers it.
        self.assertNotIn(('4', '1410'), revisions.entry_by_code())
        self.assertIn(('4', '141'), revisions.entry_by_code())

    def test_isic_entry_fills_every_level(self):
        self.assertEqual(revisions.isic_entry('1104', '5'), {
            'section': 'C - Manufacturing',
            'division': '11 - Manufacture of beverages',
            'group': '110 - Manufacture of beverages',
            'class': '1104 - Manufacture of malt',
        })


class BuildIsicFilterTest(SimpleTestCase):
    def test_a_selection_also_matches_the_other_revision(self):
        query = str(build_isic_filter({'4': [('class', '1104')], '5': []}))
        self.assertIn("('isic_class__overlap', ['1104'])", query)
        self.assertIn("('isic5_class__overlap', ['1105'])", query)

    def test_nothing_selected_is_no_filter(self):
        self.assertIsNone(build_isic_filter({'4': [], '5': []}))
