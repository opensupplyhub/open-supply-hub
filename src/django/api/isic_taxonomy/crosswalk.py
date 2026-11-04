"""
The OS Hub to ISIC Rev 4 crosswalk, kept as CSVs next to this module so
changes to it are reviewed like code: one for Facility Type / Processing
Type and one for Sector. Both load into api_isiccrosswalkentry; a row names
either a facility type (and maybe a processing type) or a sector.
"""

import csv
import os
import re

from django.db import transaction

CROSSWALK_CSV_PATH = os.path.join(
    os.path.dirname(__file__), 'data', 'os_hub_to_isic4_crosswalk.csv',
)
SECTOR_CROSSWALK_CSV_PATH = os.path.join(
    os.path.dirname(__file__), 'data', 'os_hub_sector_to_isic4_crosswalk.csv',
)

LEVEL_PATTERNS = {
    'isic_section': re.compile(r'^[A-U]$'),
    'isic_division': re.compile(r'^\d{2}$'),
    'isic_group': re.compile(r'^\d{3}$'),
    'isic_class': re.compile(r'^\d{4}$'),
}

CODE_COLUMNS = tuple(
    column
    for level in LEVEL_PATTERNS
    for column in (level, f'{level}_title')
)
TYPE_KEY_COLUMNS = ('facility_type', 'processing_type')
SECTOR_KEY_COLUMNS = ('sector',)
MODEL_COLUMNS = SECTOR_KEY_COLUMNS + TYPE_KEY_COLUMNS + CODE_COLUMNS


class CrosswalkError(ValueError):
    pass


def _check_row(row, key_columns):
    if not row[key_columns[0]]:
        return f'{key_columns[0]} is empty'
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


def _read_csv(path, key_columns):
    columns = key_columns + CODE_COLUMNS
    with open(path, newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        missing = set(columns) - set(reader.fieldnames or [])
        if missing:
            raise CrosswalkError(
                f'{os.path.basename(path)}: Missing columns: '
                f'{", ".join(sorted(missing))}.'
            )

        rows, seen = [], set()
        for line, raw in enumerate(reader, start=2):
            row = dict.fromkeys(MODEL_COLUMNS, '')
            row.update({col: (raw[col] or '').strip() for col in columns})
            key = tuple(row[col].lower() for col in key_columns)
            problem = (
                _check_row(row, key_columns)
                or (key in seen and 'duplicate row')
            )
            if problem:
                raise CrosswalkError(
                    f'{os.path.basename(path)} line {line}: {problem}.'
                )
            seen.add(key)
            rows.append(row)
    return rows


def load_crosswalk_rows(
    path=CROSSWALK_CSV_PATH,
    sector_path=SECTOR_CROSSWALK_CSV_PATH,
):
    '''sector_path=None loads only the Facility Type / Processing Type rows.'''
    rows = _read_csv(path, TYPE_KEY_COLUMNS)
    if sector_path:
        rows += _read_csv(sector_path, SECTOR_KEY_COLUMNS)
    return rows


def replace_crosswalk_entries(entry_model, rows):
    '''
    entry_model is passed in so migrations can use their historical one;
    columns that model does not have yet are left out.
    '''
    fields = {field.name for field in entry_model._meta.get_fields()}
    with transaction.atomic():
        entry_model.objects.all().delete()
        entry_model.objects.bulk_create(
            entry_model(**{
                column: value
                for column, value in row.items()
                if column in fields
            })
            for row in rows
        )
    return len(rows)


def get_mapped_isic_values(facility_types, processing_types, sectors):
    '''
    The crosswalk rows that apply to a location, for its profile: what each
    came from and its ISIC path (level, code and title). Reads the same SQL
    function as the search index, so profile and search agree. Rows that
    deliberately map to nothing are left out.
    '''
    from api.models import IsicCrosswalkEntry

    entries = IsicCrosswalkEntry.objects.raw(
        'SELECT * FROM isic_mapped_entries('
        '%s::varchar[], %s::varchar[], %s::varchar[]) '
        'ORDER BY sector, facility_type, processing_type',
        [
            list(facility_types or []),
            list(processing_types or []),
            list(sectors or []),
        ],
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
                'sector': entry.sector,
                'facility_type': entry.facility_type,
                'processing_type': entry.processing_type,
                'path': path,
            })
    return values
