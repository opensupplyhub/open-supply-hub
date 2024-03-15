import unittest
from app.utils.clean import clean


class TestClean(unittest.TestCase):

    def test_clean_column(self):
        input = 'first-test:become,real'
        output = clean(input)

        self.assertEqual(output, 'firsttest becomereal')
