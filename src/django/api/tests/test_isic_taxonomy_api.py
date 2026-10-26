from django.test import TestCase
from django.urls import reverse
from waffle.testutils import override_switch


class IsicTaxonomyAPITest(TestCase):
    @override_switch('enable_isic_taxonomy', active=True)
    def test_returns_entries_from_both_revisions(self):
        response = self.client.get(reverse('isic_taxonomy'))

        self.assertEqual(response.status_code, 200)
        entries = {entry['id']: entry for entry in response.json()['entries']}
        self.assertEqual(entries['4:13']['codes'], {'4': '13', '5': '13'})
        self.assertEqual(entries['5:1104']['title'], 'Manufacture of malt')
        self.assertEqual(entries['5:1104']['codes'], {'5': '1104'})
        self.assertIn('max-age', response['Cache-Control'])

    @override_switch('enable_isic_taxonomy', active=False)
    def test_switch_off_returns_404(self):
        response = self.client.get(reverse('isic_taxonomy'))

        self.assertEqual(response.status_code, 404)
