"""Tests for make_training_json.eval_overlap. Run: python3 -m unittest test_make_training_json"""
import csv
import os
import tempfile
import unittest

from make_training_json import curate, eval_overlap, only_countries, parse_countries


class EvalOverlapTest(unittest.TestCase):
    """eval_overlap counts selected training pairs that also appear in the evaluation file."""

    def _eval_file(self, ids):
        """Write a small eval_set.csv holding the given match ids; return its path."""
        handle = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="")
        self.addCleanup(os.unlink, handle.name)
        writer = csv.writer(handle)
        writer.writerow(["match_id", "country", "pick_one", "exact_text"])
        for mid in ids:
            writer.writerow([mid, "xx", 0, 0])
        handle.close()
        return handle.name

    def test_no_overlap_is_zero(self):
        """A training selection with no pair in the evaluation file reports 0."""
        selected = [{"match_id": "1"}, {"match_id": "2"}]
        self.assertEqual(eval_overlap(selected, self._eval_file(["3", "4"])), 0)

    def test_counts_each_shared_pair(self):
        """Every training pair that is also an evaluation pair is counted once."""
        selected = [{"match_id": "1"}, {"match_id": "2"}, {"match_id": "3"}]
        self.assertEqual(eval_overlap(selected, self._eval_file(["2", "3", "9"])), 2)


class CurateMixTest(unittest.TestCase):
    """curate takes the requested number of each class, so the match to non-match mix can be changed."""

    def _rows(self):
        """A small pool: 60 matches and 60 non-matches, half of each with a long shared name prefix
        (so they count as hard), all in the training half."""
        rows = []
        for label in (0, 1):
            for i in range(60):
                hard = i % 2 == 0
                name = ("shared prefix long enough " + str(i)) if hard else ("x%d" % i)
                other = ("shared prefix long enough " + str(i) + "b") if hard else ("y%d" % i)
                rows.append({"match_id": "%d-%d" % (label, i), "label": label,
                             "left": {"name": name, "address": "a", "country": "xx"},
                             "right": {"name": other, "address": "a", "country": "xx"},
                             "confidence": float(label), "train": True})
        return rows

    def _counts(self, selected):
        """(matches, non-matches) in a selection."""
        return (sum(r["label"] == 1 for r in selected), sum(r["label"] == 0 for r in selected))

    def test_default_is_equal_classes(self):
        """With only per_class set, both classes get that many pairs."""
        _, selected = curate(self._rows(), 20, 2.0 / 3.0)
        self.assertEqual(self._counts(selected), (20, 20))

    def test_classes_can_differ(self):
        """per_match and per_distinct set each class's size on its own."""
        _, selected = curate(self._rows(), 20, 2.0 / 3.0, per_match=10, per_distinct=40)
        self.assertEqual(self._counts(selected), (10, 40))


class CountryFilterTest(unittest.TestCase):
    """parse_countries and only_countries pick one region's pairs."""

    def test_parse_handles_case_and_spaces(self):
        """Codes are lowercased and trimmed; an empty value means no filter."""
        self.assertEqual(parse_countries("CN, tw ,hk"), {"cn", "tw", "hk"})
        self.assertIsNone(parse_countries(""))
        self.assertIsNone(parse_countries(None))

    def test_only_countries_keeps_the_region(self):
        """Only rows from the listed countries are kept; with no codes every row is kept."""
        rows = [{"country": "in"}, {"country": "pk"}, {"country": "us"}]
        self.assertEqual([r["country"] for r in only_countries(rows, {"in", "pk"})], ["in", "pk"])
        self.assertEqual(len(only_countries(rows, None)), 3)


class HardSelectionTest(unittest.TestCase):
    """The hard-pair share and the way hard pairs are chosen can be changed."""

    def _rows(self):
        """40 matches and 40 non-matches. Half of each class has lookalike names (hard by probe); a further
        quarter has a recorded score that disagrees with the label (hard only by surprise)."""
        rows = []
        for label in (0, 1):
            for i in range(40):
                look = i % 2 == 0
                name = ("shared prefix long enough %d" % i) if look else ("x%d" % i)
                other = name + "b" if look else "y%d" % i
                conf = (1.0 - label) if i % 4 == 1 else float(label)        # i % 4 == 1: disagrees with the label
                rows.append({"match_id": "%d-%d" % (label, i), "label": label,
                             "left": {"name": name, "address": "a", "country": "xx"},
                             "right": {"name": other, "address": "a", "country": "xx"},
                             "confidence": conf, "train": True})
        return rows

    def test_hard_share_changes_the_mix(self):
        """A higher hard share draws more lookalike or disputed pairs into the selection."""
        low = sum(r["probe"] or r["surprise"] for r in curate(self._rows(), 10, 0.0)[1])
        high = sum(r["probe"] or r["surprise"] for r in curate(self._rows(), 10, 1.0)[1])
        self.assertLess(low, high)

    def test_no_surprise_ignores_the_recorded_score(self):
        """With use_surprise off, a pair is hard only if its names are lookalikes, so no surprise-only pair
        counts as hard and the 'hard' pool is smaller."""
        with_s = curate(self._rows(), 10, 1.0)[1]
        without = curate(self._rows(), 10, 1.0, use_surprise=False)[1]
        self.assertTrue(all(r["probe"] for r in without if r["label"] == 1))
        self.assertGreater(sum(not r["probe"] for r in with_s), sum(not r["probe"] for r in without))


if __name__ == "__main__":
    unittest.main()
