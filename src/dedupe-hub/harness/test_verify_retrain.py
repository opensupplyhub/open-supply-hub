"""Tests for verify_retrain.cross_country_rows. Run from the harness folder: python3 -m unittest discover -p 'test_verify_retrain.py'"""
import unittest

import csv
import os
import tempfile

from verify_retrain import CANON_PREFIX, MESSY_PREFIX, cross_country_rows, read_extra_pairs


def pair(mid, left_country, right_country):
    """A minimal evaluation row: an upload from left_country and its facility in right_country."""
    return {"match_id": mid,
            "left": {"name": "a", "address": "b", "country": left_country},
            "right": {"name": "a", "address": "b", "country": right_country}}


class CrossCountryRowsTest(unittest.TestCase):
    """cross_country_rows counts candidates from a country other than the upload's."""

    def setUp(self):
        """Three uploads from 'eg'; the facility of pair 2 is in 'dz', the others in 'eg'."""
        self.rows = [pair("1", "eg", "eg"), pair("2", "eg", "dz"), pair("3", "eg", "eg")]

    def test_counts_other_country_candidates_and_their_scores(self):
        """Upload 1 was offered facility 2 (in dz) at 0.9 and facility 3 (in eg) at 0.6: one cross-country candidate."""
        found = {MESSY_PREFIX + "1": {CANON_PREFIX + "2": 0.9, CANON_PREFIX + "3": 0.6}}
        row = cross_country_rows(self.rows, found)[0]
        self.assertEqual(row, ("1", 1, 1, 1, "0.900000", 1))

    def test_an_upload_with_only_same_country_candidates_has_none(self):
        """Candidates from the upload's own country are not counted as cross-country."""
        found = {MESSY_PREFIX + "1": {CANON_PREFIX + "3": 0.7}}
        row = cross_country_rows(self.rows, found)[0]
        self.assertEqual(row[1:4], (0, 0, 0))
        self.assertEqual(row[4], "")

    def test_the_floor_and_bar_are_applied_to_the_cross_country_score(self):
        """A 0.55 cross-country candidate is at the 0.5 floor but not above the 0.8 bar."""
        found = {MESSY_PREFIX + "1": {CANON_PREFIX + "2": 0.55}}
        row = cross_country_rows(self.rows, found)[0]
        self.assertEqual(row[1:4], (1, 1, 0))

    def test_an_upload_with_no_candidates_gets_a_row_of_zeros(self):
        """Uploads the search returned nothing for still appear, with zero counts."""
        row = cross_country_rows(self.rows, {})[2]
        self.assertEqual(row, ("3", 0, 0, 0, "", 0))


class ReadExtraPairsTest(unittest.TestCase):
    """read_extra_pairs loads the pairs to score after training."""

    def _csv(self, rows):
        """Write a small extra-pairs CSV and return its path."""
        h = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="")
        self.addCleanup(os.unlink, h.name)
        w = csv.writer(h)
        w.writerow(["row", "label", "country_left", "name_left", "address_left", "country_right", "name_right", "address_right"])
        w.writerows(rows)
        h.close()
        return h.name

    def test_reads_rows_and_cleans_them(self):
        """Each readable row comes back with its row number, label and cleaned records."""
        path = self._csv([["1", "match", "LK", "Acme Ltd", "12 Main St", "LK", "ACME LTD.", "12 Main Street"]])
        got = read_extra_pairs(path)
        self.assertEqual(len(got), 1)
        self.assertEqual((got[0]["row"], got[0]["label"]), ("1", "match"))
        self.assertEqual(got[0]["left"]["country"], "lk")

    def test_an_unscoreable_pair_is_skipped(self):
        """A pair with an empty name cannot be scored and is left out rather than crashing the run."""
        path = self._csv([["1", "match", "lk", "", "x", "lk", "y", "z"], ["2", "match", "lk", "a", "b", "lk", "a", "b"]])
        self.assertEqual([r["row"] for r in read_extra_pairs(path)], ["2"])


if __name__ == "__main__":
    unittest.main()
