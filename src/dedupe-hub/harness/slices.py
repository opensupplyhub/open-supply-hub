#!/usr/bin/env python3
"""Named evaluation slices for OSDEV-3277.

The ticket requires the slices, and the regression tolerance, to be named BEFORE
the comparison is run, and the same list is reused by OSDEV-3619 (shadow run)
and OSDEV-3620 (features). This file is that list: edit it, commit it, and put
the same list on the ticket.

A slice is a named subset of the labeled pairs. Country slices partition the
data. The lookalike slice cuts across all of them, and the ticket judges it on
error count at the shipped operating point (AC#3), not on AC#2's three
conditions, so slice_report.py prints its absolute error counts.

Country codes are lowercase ISO alpha-2, as in the `item_country` column.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_training_json import prefix_len  # noqa: E402

PROBE_PREFIX = 12   # same definition evaluate.py uses for the lookalike probe

# PROPOSAL, NOT A DECISION. These are the five countries already measured on
# this ticket (about 45% of upload volume). Add or remove entries here once the
# per-country label counts are known; slice_report.py prints every country with
# enough pairs, named or not, so the counts are visible before you choose.
COUNTRY_SLICES = {
    "Korea": "kr",
    "China": "cn",
    "Mexico": "mx",
    "Bangladesh": "bd",
    "Vietnam": "vn",
    # "India": "in",
}

LOOKALIKE = "Lookalike (siblings)"


def is_lookalike(row):
    """Long shared name prefix but not identical: the Unit A vs Unit B class."""
    return (prefix_len(row["name_l"], row["name_r"]) >= PROBE_PREFIX
            and row["name_l"] != row["name_r"])


def assign(rows, min_n=0):
    """Return an ordered {slice name: [rows]}.

    Order: ALL, the named countries, the lookalike class, then every other
    country with at least `min_n` rows, largest first. Rows without a country
    value are grouped under "(no country)".
    """
    out = {"ALL": list(rows)}

    by_country = {}
    for r in rows:
        by_country.setdefault(r.get("country") or "", []).append(r)

    named_codes = set()
    for label, code in COUNTRY_SLICES.items():
        named_codes.add(code)
        out[f"{label} ({code})"] = by_country.get(code, [])

    out[LOOKALIKE] = [r for r in rows if is_lookalike(r)]

    others = sorted(
        ((c, rs) for c, rs in by_country.items()
         if c not in named_codes and len(rs) >= min_n),
        key=lambda kv: -len(kv[1]))
    for code, rs in others:
        out[code.upper() if code else "(no country)"] = rs
    return out
