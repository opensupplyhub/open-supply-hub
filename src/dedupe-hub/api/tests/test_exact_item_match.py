import unittest

from app.matching.matcher.exact.exact_item_match import ExactItemMatch


class TestExactItemMatch(unittest.TestCase):

    def setUp(self):
        self.item_id = 1
        self.matches = []
        self.started = "2024-04-22 10:57:29.258354"
        self.finished = "2024-04-22 10:57:29.263924"
        self.results = {}
        self.automatic_threshold = 1.0

        self.item_match = ExactItemMatch(
            item_id=self.item_id,
            matches=self.matches,
            started=self.started,
            finished=self.finished,
            results=self.results,
            automatic_threshold=self.automatic_threshold,
        )

    def test_process_no_matches(self):
        self.assertEqual(self.item_match.process(), [])


if __name__ == '__main__':
    unittest.main()
