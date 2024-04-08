import unittest
from app.utils.clean import clean


class TestClean(unittest.TestCase):

    def test_clean_column(self):
        input = "first-/test:become,'\nreal"
        output = clean(input)

        self.assertEqual(output, "first test become real")

if __name__ == '__main__':
    unittest.main()
