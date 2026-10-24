"""
Resolve contributor ISIC input (OSDEV-3442, OSDEV-3443): a code, an official
title, or text close to a title, checked against one revision's UN structure
(revisions.py). The column a value came in under says the revision: the same
code can mean different things in ISIC 4 and ISIC 5. Results use the shape
ISIC ExtendedFields already store, so search and profiles read them
unchanged. The claim and contribution forms (OSDEV-2974) use it too.
"""

import re
from functools import lru_cache

from thefuzz import fuzz, process

from api.isic_taxonomy.revisions import isic_entry, level_of, titles

# Full-string similarity, stricter than the processing type matcher (85,
# WRatio): a wrong industry is worse than none, and WRatio scores short
# fragments such as "apparel" highly against any title that contains them.
FUZZY_MIN_SCORE = 90

CODE = 'CODE'
EXACT = 'EXACT'
FUZZY = 'FUZZY'

# No ISIC title is near this long; longer text is not worth a fuzzy scan.
MAX_TEXT_LENGTH = 200


def _key(text):
    return re.sub(r'[^a-z0-9]+', ' ', text.lower()).strip()


@lru_cache(maxsize=None)
def _code_by_title(revision):
    # A group and its only class can share a title; the class is the more
    # specific answer, and the structure lists it last.
    return {_key(title): code for code, title in titles(revision).items()}


@lru_cache(maxsize=4096)
def match_isic(text, revision):
    """(entry, CODE | EXACT | FUZZY) for one value, or None."""
    value = (text or '').strip()
    if not value or len(value) > MAX_TEXT_LENGTH:
        return None
    codes = titles(revision)

    code = value.upper()
    if code in codes:
        return isic_entry(code, revision), CODE
    # Excel drops leading zeros from class codes ("0111" -> "111").
    # Restore one only when the digits are not already a code of their
    # own. Shorter numbers are left alone: a stray "2" is not division 02.
    if len(code) == 3 and code.isdigit() and '0' + code in codes:
        return isic_entry('0' + code, revision), CODE

    by_title = _code_by_title(revision)
    key = _key(value)
    if key in by_title:
        return isic_entry(by_title[key], revision), EXACT

    best = process.extractOne(
        key,
        list(by_title),
        scorer=fuzz.token_sort_ratio,
        score_cutoff=FUZZY_MIN_SCORE,
    )
    if best:
        return isic_entry(by_title[best[0]], revision), FUZZY
    return None


CODE_PREFIX = re.compile(r'^\s*([A-Za-z]|\d{1,4})\b')


def full_entry(entry, revision):
    """
    A structured value ({'section': 'C - Manufacturing', 'class': ...}) with
    every level filled in from its most specific code, or None if that code
    is not in the revision.
    """
    for level in ('class', 'group', 'division', 'section'):
        match = CODE_PREFIX.match(str(entry.get(level) or ''))
        if match:
            code = match.group(1).upper()
            return isic_entry(code, revision) if code in titles(revision) \
                else None
    return None


def entries_from_filter_values(values, revision):
    """
    Full entries for "level:code" values, as the search field and the claim
    forms send them, or for entries as the claim API returns them (the
    claimed-details editor sends back what it loaded). None if any value is
    not a code of that level in the revision.
    """
    entries = []
    for value in values or []:
        if isinstance(value, dict):
            entry = full_entry(value, revision)
            if entry is None:
                return None
            entries.append(entry)
            continue
        level, _, code = str(value).partition(':')
        code = code.strip().upper()
        if code not in titles(revision) or level_of(code) != level:
            return None
        entries.append(isic_entry(code, revision))
    return entries


def is_single_level(entry, revision):
    """
    True for a value naming one level with a code of that level, e.g.
    {'class': '1410 - Manufacture of wearing apparel, ...'}, as the
    single-location form sends.
    """
    levels = [level for level in ('section', 'division', 'group', 'class')
              if entry.get(level)]
    if len(levels) != 1:
        return False
    match = CODE_PREFIX.match(str(entry[levels[0]]))
    if match is None:
        return False
    code = match.group(1).upper()
    return code in titles(revision) and level_of(code) == levels[0]
