"""Tests for the traffic-test scripts: the decision step and the comparison. Pure Python, no model needed."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # the harness folder
sys.path[:0] = [_ROOT] + [os.path.join(_ROOT, d) for d in sorted(os.listdir(_ROOT))
                          if os.path.isdir(os.path.join(_ROOT, d)) and not d.startswith(("_", "."))]
import csv
import os
import tempfile
import unittest

import traffic_compare as tc  # noqa: E402
import traffic_test as tt  # noqa: E402


def upload(item_id="1", country="mx", name="acme", address="1 main st"):
    """A sampled upload as read_sample() returns it."""
    return {"item_id": item_id, "country": country, "rec": {"name": name, "address": address, "country": country}}


class DecideUpload(unittest.TestCase):
    """What happens to one upload given the scores the search returned."""

    def setUp(self):
        """Two indexed records: facility F1 and a confirmed spelling of F2."""
        self.canonical = {"F1": {"name": "acme", "address": "1 main st", "country": "mx"},
                          "F2_MATCH-9": {"name": "acme sa", "address": "2 side st", "country": "mx"}}
        self.exact = {("mx", "acme", "1 main st"): {"F1"}}

    def test_exact_match_wins_before_scoring(self):
        """An upload identical to one facility is auto-matched without looking at scores."""
        out = tt.decide_upload(upload(), {}, self.canonical, self.exact, 0.5, 0.8)
        self.assertEqual((out["decision"], out["chosen"], out["cause"]), ("auto_match", "F1", "exact_matcher"))

    def test_spelling_record_counts_for_its_facility(self):
        """A confirmed spelling's score is credited to the facility it belongs to."""
        out = tt.decide_upload(upload(name="acme sa", address="2 side st "), {"F2_MATCH-9": 0.9},
                               self.canonical, {}, 0.5, 0.8)
        self.assertEqual((out["decision"], out["chosen"]), ("auto_match", "F2"))

    def test_below_floor_means_new_facility(self):
        """Nothing scoring at the floor means a new facility, and the weak candidate is still written out."""
        out = tt.decide_upload(upload(name="zzz"), {"F1": 0.2}, self.canonical, {}, 0.5, 0.8)
        self.assertEqual(out["decision"], "new_facility")
        self.assertEqual(out["candidates"], "F1:0.2000")

    def test_floor_and_bar_change_the_decision(self):
        """The same score is review at 0.5/0.8 and an auto-match at 0.3/0.6."""
        args = (upload(name="zzz"), {"F1": 0.7}, self.canonical, {})
        self.assertEqual(tt.decide_upload(*args, 0.5, 0.8)["decision"], "review")
        self.assertEqual(tt.decide_upload(*args, 0.3, 0.6)["decision"], "auto_match")


class Compare(unittest.TestCase):
    """Comparing two models' decisions."""

    def rows(self, *specs):
        """Build {item_id: row} from (item_id, decision, chosen) triples, all in one country."""
        return {i: {"item_id": i, "country": "mx", "decision": d, "chosen": c, "candidates": ""} for i, d, c in specs}

    def test_agreement_and_kinds(self):
        """Same facility is agreement; different facility, or auto vs review, is a disagreement with a name."""
        a = self.rows(("1", "auto_match", "F1"), ("2", "auto_match", "F1"), ("3", "review", ""), ("4", "new_facility", ""))
        b = self.rows(("1", "auto_match", "F1"), ("2", "auto_match", "F9"), ("3", "auto_match", "F3"), ("4", "new_facility", ""))
        by_pair, by_country, disagreements = tc.compare(a, b)
        self.assertEqual(disagreements, [("2", "both auto-match, different facility"), ("3", "auto_match vs review")])
        self.assertEqual(by_country["mx"]["n"], 4)
        self.assertEqual(by_country["mx"]["differ"], 2)
        self.assertEqual(by_pair[("review", "auto_match")], 1)

    def test_only_shared_uploads_are_compared(self):
        """An upload only one model scored is left out rather than counted as a disagreement."""
        by_pair, _, disagreements = tc.compare(self.rows(("1", "review", "")), self.rows(("2", "review", "")))
        self.assertEqual((sum(by_pair.values()), disagreements), (0, []))

    def test_top_text(self):
        """A chosen facility is named; otherwise the best candidates are listed with their scores."""
        facilities = {"F1": "acme | 1 main st", "F2": "acme sa | 2 side st"}
        chosen = {"chosen": "F1", "candidates": ""}
        listed = {"chosen": "", "candidates": "F2:0.6100;F1:0.5500"}
        self.assertEqual(tc.top_text(chosen, facilities), "CHOSE F1: acme | 1 main st")
        self.assertEqual(tc.top_text(listed, facilities, k=1), "F2 (0.6100): acme sa | 2 side st")

    def test_pct(self):
        """Percentages print to one decimal, and an empty denominator prints a dash."""
        self.assertEqual((tc.pct(1, 8), tc.pct(0, 0)), ("12.5%", "-"))


class ReadIndex(unittest.TestCase):
    """Reading the index file."""

    def test_spellings_and_exact_lookup(self):
        """Facility rows and spelling rows get dedupe-hub's ids, a nameless row is dropped, and the exact lookup works."""
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "index.csv")
            with open(path, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["kind", "facility_id", "match_id", "country", "name", "address"])
                w.writerow(["facility", "F1", "", "mx", "Acme", "1 Main St"])
                w.writerow(["match", "F1", "7", "mx", "Acme SA", "1 Main St"])
                w.writerow(["facility", "F2", "", "mx", "", "nowhere"])
            canonical, exact = tt.read_index(path)
        self.assertEqual(sorted(canonical), ["F1", "F1_MATCH-7"])
        self.assertEqual(exact[("mx", "acme", "1 main st")], {"F1"})
        self.assertEqual(tt.facility_of("F1_MATCH-7"), "F1")


if __name__ == "__main__":
    unittest.main()
