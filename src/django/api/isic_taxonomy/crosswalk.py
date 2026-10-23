"""
The OS Hub Facility Type / Processing Type to ISIC Rev 4 crosswalk, kept as
a CSV next to this module so changes to it are reviewed like code.
"""

import csv
import os
import re

from django.db import transaction

CROSSWALK_CSV_PATH = os.path.join(
    os.path.dirname(__file__), 'data', 'os_hub_to_isic4_crosswalk.csv',
)

LEVEL_PATTERNS = {
    'isic_section': re.compile(r'^[A-U]$'),
    'isic_division': re.compile(r'^\d{2}$'),
    'isic_group': re.compile(r'^\d{3}$'),
    'isic_class': re.compile(r'^\d{4}$'),
}

MODEL_COLUMNS = ('facility_type', 'processing_type') + tuple(
    column
    for level in LEVEL_PATTERNS
    for column in (level, f'{level}_title')
)


class CrosswalkError(ValueError):
    pass


def _check_row(row):
    if not row['facility_type']:
        return 'facility_type is empty'
    codes = [row[level] for level in LEVEL_PATTERNS]
    for (level, pattern), code in zip(LEVEL_PATTERNS.items(), codes):
        if code and not pattern.match(code):
            return f'{level} "{code}" is not an ISIC Rev 4 code'
        # Profiles show titles, never codes, so every code needs a title.
        if bool(code) != bool(row[f'{level}_title']):
            return f'{level} and {level}_title must both be set or empty'
    # Levels run from the section down without gaps, and a group or class
    # extends the code above it (a division does not contain its section
    # letter).
    depth = sum(1 for code in codes if code)
    if not all(codes[:depth]):
        return 'ISIC levels must run from the section down without gaps'
    _, division, group, isic_class = codes
    for parent, child in ((division, group), (group, isic_class)):
        if child and not child.startswith(parent):
            return f'{child} is not under {parent}'
    return None


def load_crosswalk_rows(path=CROSSWALK_CSV_PATH):
    with open(path, newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        missing = set(MODEL_COLUMNS) - set(reader.fieldnames or [])
        if missing:
            raise CrosswalkError(
                f'Missing columns: {", ".join(sorted(missing))}.'
            )

        rows, seen = [], set()
        for line, raw in enumerate(reader, start=2):
            row = {col: (raw[col] or '').strip() for col in MODEL_COLUMNS}
            key = (
                row['facility_type'].lower(),
                row['processing_type'].lower(),
            )
            problem = _check_row(row) or (key in seen and 'duplicate row')
            if problem:
                raise CrosswalkError(f'Line {line}: {problem}.')
            seen.add(key)
            rows.append(row)
    return rows


def replace_crosswalk_entries(entry_model, rows):
    '''entry_model is passed in so migrations can use their historical one.'''
    with transaction.atomic():
        entry_model.objects.all().delete()
        entry_model.objects.bulk_create(entry_model(**row) for row in rows)
    return len(rows)
