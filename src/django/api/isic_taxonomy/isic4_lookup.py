"""
Resolve contributor ISIC Rev 4 input (OSDEV-3442, OSDEV-3443): a code, an
official title, or text close to a title, checked against the UN ISIC Rev 4
structure in data/isic_rev4_structure.csv. Results use the shape isic_4
ExtendedFields already store, so search and profiles read them unchanged.
"""

import csv
import os
import re
from functools import lru_cache

from thefuzz import fuzz, process

STRUCTURE_CSV_PATH = os.path.join(
    os.path.dirname(__file__), 'data', 'isic_rev4_structure.csv',
)

# Full-string similarity, stricter than the processing type matcher (85,
# WRatio): a wrong industry is worse than none, and WRatio scores short
# fragments such as "apparel" highly against any title that contains them.
FUZZY_MIN_SCORE = 90

CODE = 'CODE'
EXACT = 'EXACT'
FUZZY = 'FUZZY'

LEVEL_BY_LENGTH = {2: 'division', 3: 'group', 4: 'class'}

# No ISIC title is near this long; longer text is not worth a fuzzy scan.
MAX_TEXT_LENGTH = 200


def _key(text):
    return re.sub(r'[^a-z0-9]+', ' ', text.lower()).strip()


@lru_cache(maxsize=1)
def _structure():
    with open(STRUCTURE_CSV_PATH, newline='', encoding='utf-8') as file:
        rows = list(csv.DictReader(file))

    titles, section_of, code_by_title = {}, {}, {}
    section = None
    for row in rows:
        code, title = row['code'], row['title']
        titles[code] = title
        if code.isalpha():
            section = code
        else:
            section_of[code[:2]] = section
        # A group and its only class can share a title; the class is the
        # more specific answer, and the structure lists it last.
        code_by_title[_key(title)] = code
    return titles, section_of, code_by_title, list(code_by_title)


def isic4_entry(code):
    """{'section': 'C - Manufacturing', ..., 'class': '1410 - ...'}"""
    titles, section_of, _, _ = _structure()
    section = code if code.isalpha() else section_of[code[:2]]
    entry = {'section': f'{section} - {titles[section]}'}
    for length, level in LEVEL_BY_LENGTH.items():
        if not code.isalpha() and len(code) >= length:
            entry[level] = f'{code[:length]} - {titles[code[:length]]}'
    return entry


@lru_cache(maxsize=4096)
def match_isic4(text):
    """(entry, CODE | EXACT | FUZZY) for one value, or None."""
    value = (text or '').strip()
    if not value or len(value) > MAX_TEXT_LENGTH:
        return None
    titles, _, code_by_title, title_keys = _structure()

    code = value.upper()
    if code in titles:
        return isic4_entry(code), CODE
    # Excel drops leading zeros from class codes ("0111" -> "111").
    # Restore one only when the digits are not already a code of their
    # own. Shorter numbers are left alone: a stray "2" is not division 02.
    if len(code) == 3 and code.isdigit() and '0' + code in titles:
        return isic4_entry('0' + code), CODE

    key = _key(value)
    if key in code_by_title:
        return isic4_entry(code_by_title[key]), EXACT

    best = process.extractOne(
        key,
        title_keys,
        scorer=fuzz.token_sort_ratio,
        score_cutoff=FUZZY_MIN_SCORE,
    )
    if best:
        return isic4_entry(code_by_title[best[0]]), FUZZY
    return None
