"""Tests for merge_training: the base stays whole, additions follow it, and a pair already present is not added twice."""
import unittest

import merge_training as mt


def ex(name, country="mx"):
    """One training example: a pair of records that share a name, with made-up ids."""
    left = {"id": "l-" + name, "country": country, "name": name, "address": "1 main st"}
    right = {"id": "r-" + name, "country": country, "name": name + " sa", "address": "1 main st"}
    return {"__class__": "tuple", "__value__": [left, right]}


class Merge(unittest.TestCase):
    """Putting two training files together."""

    def test_additions_follow_the_base(self):
        """Every base pair is kept in order, then the added pairs of the same class."""
        base = {"match": [ex("a")], "distinct": [ex("b")]}
        extra = {"match": [ex("c"), ex("d")], "distinct": [ex("e")]}
        merged, skipped = mt.merge(base, extra)
        names = lambda cls: [e["__value__"][0]["name"] for e in merged[cls]]  # noqa: E731
        self.assertEqual((names("match"), names("distinct"), skipped), (["a", "c", "d"], ["b", "e"], 0))

    def test_same_text_is_not_added_twice(self):
        """A pair with the same text as one already in the same class is skipped, even with different ids."""
        base = {"match": [ex("a")], "distinct": []}
        again = ex("a")
        again["__value__"][0]["id"] = "other-id"
        merged, skipped = mt.merge(base, {"match": [again], "distinct": []})
        self.assertEqual((len(merged["match"]), skipped), (1, 1))

    def test_same_pair_in_the_other_class_is_kept(self):
        """The skip is per class: a pair that is a match in one file and a non-match in the other stays in both."""
        merged, skipped = mt.merge({"match": [ex("a")], "distinct": []}, {"match": [], "distinct": [ex("a")]})
        self.assertEqual((len(merged["match"]), len(merged["distinct"]), skipped), (1, 1, 0))

    def test_inputs_are_not_changed(self):
        """Merging leaves the two input dictionaries as they were."""
        base = {"match": [ex("a")], "distinct": []}
        mt.merge(base, {"match": [ex("b")], "distinct": []})
        self.assertEqual(len(base["match"]), 1)


if __name__ == "__main__":
    unittest.main()
