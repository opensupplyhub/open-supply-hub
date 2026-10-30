"""Tests for augment_training.py. Run: python3 -m unittest test_augment_training"""
import random
import unittest

from augment_training import as_example, parse_add, sample_pairs


def row(mid, country, label, train=True):
    """A minimal labeled-pair row the way make_training_json.load_pairs returns it."""
    return {"match_id": mid, "country": country, "label": label, "train": train,
            "left": {"name": "a" + mid, "address": "x", "country": country},
            "right": {"name": "b" + mid, "address": "x", "country": country}}


class ParseAddTest(unittest.TestCase):
    """parse_add reads the country:count arguments."""

    def test_reads_codes_and_counts(self):
        """Codes are lowercased and mapped to their per-class count."""
        self.assertEqual(parse_add(["CN:10", "us:5"]), {"cn": 10, "us": 5})

    def test_rejects_a_missing_count(self):
        """An argument without a number is an error, not a silent zero."""
        with self.assertRaises(ValueError):
            parse_add(["cn"])


class SamplePairsTest(unittest.TestCase):
    """sample_pairs draws balanced pairs for one country from the training half only."""

    def _rows(self):
        """20 training-half matches and 20 non-matches for 'cn', 20 of each for 'us', and some evaluation-half cn rows."""
        rows = []
        for c in ("cn", "us"):
            for label in (0, 1):
                rows += [row(f"{c}{label}-{i}", c, label) for i in range(20)]
        rows += [row(f"ev-{i}", "cn", i % 2, train=False) for i in range(10)]
        return rows

    def test_returns_the_requested_number_of_each_class(self):
        """N matches and N non-matches come back, all from the right country and label."""
        m, n = sample_pairs(self._rows(), "cn", 5, random.Random(0))
        self.assertEqual((len(m), len(n)), (5, 5))
        self.assertTrue(all(r["country"] == "cn" and r["label"] == 1 for r in m))
        self.assertTrue(all(r["country"] == "cn" and r["label"] == 0 for r in n))

    def test_only_training_half_pairs_are_used(self):
        """Evaluation-half rows are never drawn, however many are asked for."""
        m, n = sample_pairs(self._rows(), "cn", 20, random.Random(1))
        self.assertTrue(all(r["train"] for r in m + n))

    def test_same_seed_same_pairs_different_seed_different_pairs(self):
        """The draw is repeatable for a seed and changes with it."""
        a = [r["match_id"] for r in sample_pairs(self._rows(), "us", 5, random.Random(0))[0]]
        b = [r["match_id"] for r in sample_pairs(self._rows(), "us", 5, random.Random(0))[0]]
        c = [r["match_id"] for r in sample_pairs(self._rows(), "us", 5, random.Random(7))[0]]
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_too_few_pairs_is_an_error(self):
        """Asking for more pairs than the country has says so."""
        with self.assertRaises(ValueError):
            sample_pairs(self._rows(), "cn", 21, random.Random(0))


class AsExampleTest(unittest.TestCase):
    """as_example matches dedupe's training-file format."""

    def test_is_a_tuple_of_the_two_records(self):
        """The example is a __class__ tuple holding the left and right records."""
        ex = as_example(row("1", "cn", 1))
        self.assertEqual(ex["__class__"], "tuple")
        self.assertEqual(len(ex["__value__"]), 2)


if __name__ == "__main__":
    unittest.main()
