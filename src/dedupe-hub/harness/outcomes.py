#!/usr/bin/env python3
"""What finally happens to one upload. OSDEV-3277.

Given the candidates the search rules retrieved for an upload, their scores, and
the facility the upload truly belongs to (or none, if it is a genuinely new
facility), classify_upload() returns exactly one of six outcomes, so the outcomes
for a set of uploads add up to 100%:

  correctly_matched   auto-matched to the true facility
  correctly_new       a genuinely new upload, and a new facility was created
  review_below_bar    sent to a human; no candidate was confidently above the
                      auto bar (the best was between the floor and the bar)
  review_above_bar    sent to a human; two or more candidates cleared the auto
                      bar and nothing broke the tie
  duplicate           the upload has an existing facility but the system will not
                      link it: nothing reached the floor (a new facility is
                      created), or it went to review WITHOUT the true match on
                      the list, so a human cannot pick it
  incorrect_match     auto-matched to the wrong facility (including an upload
                      that had no true match at all)

A `cause` is returned with each outcome so a bar can show the reasons inside it.

The decision rules copy production's GazetteerItemMatch.process() in dedupe-hub:
  * candidates are only those scoring at or above the candidate floor, keeping
    each facility's best score;
  * none  -> a new facility is created;
  * one   -> auto-match if its score is at or above the auto bar, else review;
  * several -> the ones STRICTLY above the auto bar count: exactly one is
    auto-matched; more than one is auto-matched only if exactly one of the
    candidates is an exact string match, otherwise review; none above the bar is
    review. (Note the quirk: a lone candidate exactly at the bar is accepted, but
    among several one must be strictly above it.)

Pure stdlib. Whether the true match is "on the list" means it is among the
candidates at or above the floor.
"""
from collections import namedtuple

OUTCOMES = ("correctly_matched", "correctly_new", "review_below_bar",
            "review_above_bar", "duplicate", "incorrect_match")

Result = namedtuple("Result", "outcome cause")


def _best_per_facility(candidates):
    """Collapse candidates to one per facility, keeping the best score. A
    facility is exact if any of its records is an exact string match."""
    best = {}
    for c in candidates:
        cur = best.get(c["facility"])
        if cur is None or c["score"] > cur["score"]:
            best[c["facility"]] = {"facility": c["facility"], "score": c["score"],
                                   "exact": bool(c.get("exact"))}
        elif c.get("exact"):
            cur["exact"] = True
    return list(best.values())


def _lead(candidates):
    """How far the best candidate's score is ahead of the next-best (0 if there is only one)."""
    ranked = sorted((c["score"] for c in candidates), reverse=True)
    return ranked[0] - ranked[1] if len(ranked) > 1 else 0.0


def decide(candidates, floor, auto, promote=0.0, hold=0.0):
    """What production does with an upload's candidates, plus two optional margin rules (both off by default).

    promote: when several candidates clear the auto bar, auto-match the top one anyway if it leads the
             next-best by at least this much (production sends those to review unless one is an exact match).
    hold:    when exactly one candidate clears the bar but the next-best is within this much of it,
             send the upload to review instead of auto-matching (production would auto-match it).

    Returns (action, chosen, above_floor, above_bar) where action is
    'new_facility', 'auto_match' or 'review', `chosen` is the facility that is
    auto-matched (else None), and the last two are the candidate lists at or
    above the floor and strictly above the auto bar.
    """
    above_floor = [c for c in _best_per_facility(candidates) if c["score"] >= floor]
    above_bar = [c for c in above_floor if c["score"] > auto]
    if not above_floor:
        return "new_facility", None, above_floor, above_bar
    if len(above_floor) == 1:
        only = above_floor[0]
        if only["score"] >= auto:
            return "auto_match", only["facility"], above_floor, above_bar
        return "review", None, above_floor, above_bar
    ranked = sorted(above_floor, key=lambda c: -c["score"])
    lead = ranked[0]["score"] - ranked[1]["score"]          # how far the best candidate is ahead of the next
    if len(above_bar) == 1:
        if hold and lead < hold:
            return "review", None, above_floor, above_bar
        return "auto_match", above_bar[0]["facility"], above_floor, above_bar
    if len(above_bar) > 1:
        if promote and lead >= promote:
            return "auto_match", ranked[0]["facility"], above_floor, above_bar
        exact = [c for c in above_floor if c["exact"]]
        if len(exact) == 1:
            return "auto_match", exact[0]["facility"], above_floor, above_bar
    return "review", None, above_floor, above_bar


def classify_upload(candidates, true_facility, floor, auto, promote=0.0, hold=0.0):
    """Classify one upload into one of the six outcomes.

    `candidates` is a list of {"facility": id, "score": float, "exact": bool}
    for everything the search rules retrieved (scores below the floor are
    ignored, as production ignores them). `true_facility` is the facility the
    upload truly belongs to, or None for a genuinely new upload. Returns
    Result(outcome, cause).
    """
    action, chosen, above_floor, above_bar = decide(candidates, floor, auto, promote, hold)
    on_list = {c["facility"] for c in above_floor}
    retrieved = {c["facility"] for c in candidates}

    def why_missing():
        """Why a true match is not on the list the system works from."""
        return "scored_below_floor" if true_facility in retrieved else "never_retrieved"

    if action == "auto_match":
        if true_facility is None:
            return Result("incorrect_match", "no_true_match_exists")
        if chosen == true_facility:
            if len(above_bar) == 1 or len(above_floor) == 1:
                cause = "alone_above_bar"
            elif promote and _lead(above_floor) >= promote and not any(c["exact"] for c in above_bar):
                cause = "margin_win"
            else:
                cause = "exact_string_tie_break"
            return Result("correctly_matched", cause)
        if true_facility in on_list:
            return Result("incorrect_match", "true_match_not_chosen")
        return Result("incorrect_match", "true_match_" + why_missing())

    if action == "new_facility":
        if true_facility is None:
            return Result("correctly_new", "nothing_reached_floor")
        return Result("duplicate", why_missing())

    # review
    if true_facility is not None and true_facility not in on_list:
        return Result("duplicate", why_missing())
    if len(above_bar) >= 2:
        return Result("review_above_bar", "several_above_bar")
    return Result("review_below_bar", "best_below_bar")
