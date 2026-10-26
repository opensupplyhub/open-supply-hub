"""Tests for outcomes.py: one test per outcome, per reason, and per edge case.

Run from this folder:  python3 -m unittest test_outcomes -v
Uses made-up uploads. FLOOR and BAR are the production values on main.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from outcomes import OUTCOMES, classify_upload  # noqa: E402

FLOOR, BAR = 0.5, 0.8


def cand(facility, score, exact=False):
    """Build one candidate record the way classify_upload expects it."""
    return {"facility": facility, "score": score, "exact": exact}


def run(cands, true):
    """Classify with production's floor and bar."""
    return classify_upload(cands, true, FLOOR, BAR)


class UploadWithAConfirmedMatch(unittest.TestCase):
    """Uploads whose true facility exists (here, facility "A")."""

    def test_correctly_matched_when_the_true_match_is_alone_above_the_bar(self):
        """One candidate, the true one, above the bar: auto-matched correctly."""
        self.assertEqual(run([cand("A", 0.92)], "A"), ("correctly_matched", "alone_above_bar"))

    def test_correctly_matched_when_it_is_the_only_one_above_the_bar_of_several(self):
        """Several candidates but only the true one is strictly above the bar."""
        self.assertEqual(run([cand("A", 0.91), cand("B", 0.7), cand("C", 0.6)], "A"),
                         ("correctly_matched", "alone_above_bar"))

    def test_correctly_matched_through_the_exact_string_tie_break(self):
        """Two above the bar, but only the true one is an exact string match."""
        got = run([cand("A", 0.9, exact=True), cand("B", 0.88)], "A")
        self.assertEqual(got, ("correctly_matched", "exact_string_tie_break"))

    def test_review_above_bar_when_several_clear_the_bar_with_no_tie_break(self):
        """The case from the example: true match and a sibling both above the bar."""
        self.assertEqual(run([cand("A", 0.92), cand("B", 0.88), cand("C", 0.4)], "A"),
                         ("review_above_bar", "several_above_bar"))

    def test_review_above_bar_when_two_candidates_are_exact_matches(self):
        """Two exact string matches do not break the tie, so it goes to review."""
        got = run([cand("A", 0.9, exact=True), cand("B", 0.9, exact=True)], "A")
        self.assertEqual(got.outcome, "review_above_bar")

    def test_review_below_bar_when_the_true_match_is_in_the_review_range(self):
        """The only candidate scores between the floor and the bar."""
        self.assertEqual(run([cand("A", 0.7)], "A"), ("review_below_bar", "best_below_bar"))

    def test_review_below_bar_when_the_true_match_shares_the_review_range(self):
        """Several candidates, none above the bar, true match among them."""
        self.assertEqual(run([cand("A", 0.7), cand("B", 0.6)], "A").outcome, "review_below_bar")

    def test_duplicate_when_nothing_was_retrieved(self):
        """No candidates at all: a new facility is created though a match existed."""
        self.assertEqual(run([], "A"), ("duplicate", "never_retrieved"))

    def test_duplicate_when_the_true_match_scored_below_the_floor_and_nothing_else_cleared_it(self):
        """The true match was retrieved but scored under the floor: new facility."""
        self.assertEqual(run([cand("A", 0.3)], "A"), ("duplicate", "scored_below_floor"))

    def test_duplicate_when_review_would_not_offer_the_true_match(self):
        """A wrong candidate reaches review but the true match was never retrieved."""
        self.assertEqual(run([cand("B", 0.6)], "A"), ("duplicate", "never_retrieved"))

    def test_duplicate_when_review_has_the_true_match_only_below_the_floor(self):
        """A wrong candidate is in review and the true one scored below the floor."""
        self.assertEqual(run([cand("B", 0.6), cand("A", 0.2)], "A"),
                         ("duplicate", "scored_below_floor"))

    def test_incorrect_match_when_a_wrong_candidate_is_alone_above_the_bar(self):
        """The true match scored lower; a wrong sibling alone cleared the bar."""
        self.assertEqual(run([cand("B", 0.85), cand("A", 0.6)], "A"),
                         ("incorrect_match", "true_match_not_chosen"))

    def test_incorrect_match_when_the_true_match_was_never_retrieved(self):
        """A wrong candidate was the only one retrieved and it cleared the bar."""
        self.assertEqual(run([cand("B", 0.9)], "A"),
                         ("incorrect_match", "true_match_never_retrieved"))

    def test_incorrect_match_when_the_tie_break_picks_the_wrong_one(self):
        """Two above the bar; the only exact string match is the wrong facility."""
        got = run([cand("A", 0.92), cand("B", 0.9, exact=True)], "A")
        self.assertEqual(got, ("incorrect_match", "true_match_not_chosen"))


class GenuinelyNewUpload(unittest.TestCase):
    """Uploads with no existing facility (true facility is None)."""

    def test_correctly_new_when_nothing_reaches_the_floor(self):
        """Nothing retrieved: a new facility is created, as it should be."""
        self.assertEqual(run([], None), ("correctly_new", "nothing_reached_floor"))

    def test_correctly_new_when_only_low_scoring_candidates_exist(self):
        """Candidates below the floor are ignored, so a new facility is created."""
        self.assertEqual(run([cand("B", 0.4)], None).outcome, "correctly_new")

    def test_incorrect_match_when_a_new_upload_is_auto_matched(self):
        """No true match exists but a candidate alone cleared the bar."""
        self.assertEqual(run([cand("B", 0.95)], None), ("incorrect_match", "no_true_match_exists"))

    def test_review_is_workload_for_a_new_upload(self):
        """A new upload with candidates in the review range goes to a human."""
        self.assertEqual(run([cand("B", 0.65)], None), ("review_below_bar", "best_below_bar"))

    def test_review_above_bar_for_a_new_upload(self):
        """Several lookalikes above the bar with no tie-break: review, not a merge."""
        self.assertEqual(run([cand("B", 0.9), cand("C", 0.85)], None).outcome, "review_above_bar")


class ProductionEdgeCases(unittest.TestCase):
    """Behaviours copied from GazetteerItemMatch.process()."""

    def test_a_lone_candidate_exactly_at_the_bar_is_accepted(self):
        """With one candidate the test is score >= bar."""
        self.assertEqual(run([cand("A", 0.8)], "A").outcome, "correctly_matched")

    def test_among_several_a_candidate_exactly_at_the_bar_is_not_enough(self):
        """With several candidates one must be STRICTLY above the bar."""
        self.assertEqual(run([cand("A", 0.8), cand("B", 0.7)], "A").outcome, "review_below_bar")

    def test_a_candidate_exactly_at_the_floor_counts_as_a_candidate(self):
        """The floor is inclusive: a score equal to it keeps the candidate."""
        self.assertEqual(run([cand("A", 0.5)], "A").outcome, "review_below_bar")

    def test_each_facility_counts_once_with_its_best_score(self):
        """Two records of one facility (one above the bar) are a single candidate."""
        got = run([cand("A", 0.6), cand("A", 0.9)], "A")
        self.assertEqual(got.outcome, "correctly_matched")

    def test_two_records_of_one_facility_above_the_bar_are_still_one_candidate(self):
        """Counted separately they would look like two high scorers and force a
        review; production collapses them, so the lone facility is auto-matched."""
        got = run([cand("A", 0.9), cand("A", 0.85)], "A")
        self.assertEqual(got, ("correctly_matched", "alone_above_bar"))

    def test_the_exact_flag_survives_collapsing_duplicate_facility_records(self):
        """If any record of a facility is an exact match, the facility is exact."""
        got = run([cand("A", 0.9), cand("A", 0.85, exact=True), cand("B", 0.88)], "A")
        self.assertEqual(got.outcome, "correctly_matched")


class OutcomeList(unittest.TestCase):
    """The six outcomes are a fixed list."""

    def test_there_are_exactly_six_outcomes(self):
        """The vocabulary agreed for the bars."""
        self.assertEqual(len(OUTCOMES), 6)

    def test_every_case_above_returns_one_of_the_six(self):
        """No classification falls outside the fixed list."""
        cases = [([], "A"), ([], None), ([cand("A", 0.9)], "A"), ([cand("B", 0.9)], None),
                 ([cand("A", 0.6)], "A"), ([cand("A", 0.9), cand("B", 0.9)], "A"),
                 ([cand("B", 0.6)], "A"), ([cand("B", 0.9), cand("A", 0.6)], "A")]
        for cands, true in cases:
            self.assertIn(run(cands, true).outcome, OUTCOMES)


if __name__ == "__main__":
    unittest.main()
