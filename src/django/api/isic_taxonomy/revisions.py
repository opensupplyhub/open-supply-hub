"""
ISIC Rev 4 and Rev 5 as published by the UN (data/): each revision's
structure, the class-level correspondence between them, and the list of
titles the search field offers. Codes differ between revisions, so search
works on titles; a category whose level and title are the same in both
revisions is one entry.
"""

import csv
import os
from collections import defaultdict
from functools import lru_cache

from api.isic_taxonomy.constants import REVISIONS

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
STRUCTURE_FILES = {
    '4': 'isic_rev4_structure.csv',
    '5': 'isic_rev5_structure.csv',
}
CORRESPONDENCE_FILE = 'isic4_to_isic5.csv'

LEVEL_BY_LENGTH = {2: 'division', 3: 'group', 4: 'class'}


def _read(name):
    with open(os.path.join(DATA_DIR, name), newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def level_of(code):
    return 'section' if code.isalpha() else LEVEL_BY_LENGTH[len(code)]


def other(revision):
    return '5' if revision == '4' else '4'


@lru_cache(maxsize=None)
def titles(revision):
    """{code: title} in the UN file's order."""
    return {
        row['code']: row['title']
        for row in _read(STRUCTURE_FILES[revision])
    }


@lru_cache(maxsize=None)
def _section_of_division(revision):
    sections, section = {}, None
    for code in titles(revision):
        if code.isalpha():
            section = code
        elif len(code) == 2:
            sections[code] = section
    return sections


def chain(code, revision):
    """Codes from the section down to code, e.g. ['C', '14', '141', '1410']."""
    if code.isalpha():
        return [code]
    section = _section_of_division(revision)[code[:2]]
    return [section] + [code[:n] for n in (2, 3, 4) if n <= len(code)]


@lru_cache(maxsize=None)
def _classes_under(revision):
    under = defaultdict(set)
    for code in titles(revision):
        if level_of(code) == 'class':
            for ancestor in chain(code, revision):
                under[ancestor].add(code)
    return under


def classes_under(code, revision):
    return _classes_under(revision).get(code, set())


@lru_cache(maxsize=None)
def _correspondence():
    pairs = defaultdict(set)
    for row in _read(CORRESPONDENCE_FILE):
        pairs[('4', row['isic4_class'])].add(row['isic5_class'])
        pairs[('5', row['isic5_class'])].add(row['isic4_class'])
    return pairs


def translate(classes, revision):
    """The other revision's classes that the given classes correspond to."""
    pairs = _correspondence()
    return set().union(*(pairs[(revision, c)] for c in classes))


def _repeats_parent(code, revision):
    path = chain(code, revision)
    names = titles(revision)
    return len(path) > 1 and names[path[-2]] == names[code]


@lru_cache(maxsize=None)
def entries():
    """
    One entry per (level, title): {id, title, level, codes: {revision:
    code}, trail}. A category whose title repeats its parent's is left out;
    picking the parent covers it. The id is the first revision's
    "<revision>:<code>".
    """
    merged = {}
    for revision in REVISIONS:
        for code, title in titles(revision).items():
            key = (level_of(code), title)
            merged.setdefault(key, {})[revision] = code

    result = []
    for (level, title), codes in merged.items():
        if all(_repeats_parent(c, r) for r, c in codes.items()):
            continue
        revision, code = next(iter(codes.items()))
        names = titles(revision)
        trail = []
        for ancestor in chain(code, revision)[:-1]:
            if not trail or trail[-1] != names[ancestor]:
                trail.append(names[ancestor])
        result.append({
            'id': f'{revision}:{code}',
            'title': title,
            'level': level,
            'codes': codes,
            'trail': ' › '.join(trail),
        })
    return tuple(result)


@lru_cache(maxsize=None)
def entry_by_code():
    return {
        (revision, code): entry['id']
        for entry in entries()
        for revision, code in entry['codes'].items()
    }


@lru_cache(maxsize=None)
def count_map():
    """
    (revision, code, entry id) rows: which entries a location with that
    code counts toward. A class also counts toward the entries of the other
    revision's classes it corresponds to, and their parents, so a count
    covers values uploaded under either revision.
    """
    ids = entry_by_code()
    rows = set()
    for revision in REVISIONS:
        for code in titles(revision):
            if (revision, code) in ids:
                rows.add((revision, code, ids[(revision, code)]))
            if level_of(code) != 'class':
                continue
            target = other(revision)
            for translated in translate({code}, revision):
                for ancestor in chain(translated, target):
                    if (target, ancestor) in ids:
                        rows.add((revision, code, ids[(target, ancestor)]))
    return tuple(sorted(rows))


def isic_entry(code, revision):
    """{'section': 'C - Manufacturing', ..., 'class': '1410 - ...'}"""
    names = titles(revision)
    return {
        level_of(c): f'{c} - {names[c]}' for c in chain(code, revision)
    }
