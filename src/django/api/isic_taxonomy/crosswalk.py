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


def get_mapped_isic_values(facility_types, processing_types):
    '''
    The crosswalk rows that apply to a location, for its profile: what each
    came from and its ISIC path (level, code and title). Reads the same SQL
    function as the search index, so profile and search agree. Rows that
    deliberately map to nothing are left out.
    '''
    from api.models import IsicCrosswalkEntry

    entries = IsicCrosswalkEntry.objects.raw(
        'SELECT * FROM isic_mapped_entries(%s::varchar[], %s::varchar[]) '
        'ORDER BY facility_type, processing_type',
        [list(facility_types or []), list(processing_types or [])],
    )
    values = []
    for entry in entries:
        path = [
            {
                'level': level.replace('isic_', ''),
                'code': getattr(entry, level),
                'title': getattr(entry, f'{level}_title'),
            }
            for level in LEVEL_PATTERNS
            if getattr(entry, level)
        ]
        if path:
            values.append({
                'facility_type': entry.facility_type,
                'processing_type': entry.processing_type,
                'path': path,
            })
    return values
