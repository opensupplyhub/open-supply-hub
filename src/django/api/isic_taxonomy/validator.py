from dataclasses import dataclass

from api.isic_taxonomy.constants import (
    LABEL_CHAR_PATTERN,
    MAX_FILE_SIZE_BYTES,
    REQUIRED_HEADERS,
    SECTION_CODE_PATTERN,
)
from api.isic_taxonomy.errors import (
    IsicTaxonomyError,
    IsicTaxonomyValidationError,
)
from api.isic_taxonomy.parser import parse_spreadsheet


def validate_file(file_content: bytes, filename: str) -> list[dict[str, str]]:
    '''
    Validate file size and parse spreadsheet rows.

    Returns normalized row dicts when validation succeeds.
    Raises IsicTaxonomyValidationError with all collected errors otherwise.
    '''
    errors: list[IsicTaxonomyError] = []

    if len(file_content) > MAX_FILE_SIZE_BYTES:
        errors.append(IsicTaxonomyError(
            message=(
                f'File exceeds the {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB '
                'size limit.'
            ),
        ))

    if errors:
        raise IsicTaxonomyValidationError(errors)

    rows = parse_spreadsheet(file_content, filename)
    validate_rows(rows)
    return rows


def _padded_code(raw_value: str, width: int) -> str:
    if raw_value.isdigit():
        return raw_value.zfill(width)
    return raw_value


@dataclass
class _ParsedRow:
    section_code: str
    section_label: str
    division_raw: str
    division_label: str
    group_raw: str
    group_label: str
    class_code: str
    class_label: str
    division_code: str
    group_code: str


def _parse_row(row: dict[str, str]) -> _ParsedRow:
    section_code = row.get('section', '').strip().upper()
    section_label = row.get('section_label', '').strip()
    division_raw = row.get('division', '').strip()
    division_label = row.get('division_label', '').strip()
    group_raw = row.get('group', '').strip()
    group_label = row.get('group_label', '').strip()
    class_digits_raw = row.get('4-digits', '').strip()
    class_label = row.get('description', '').strip()

    if not class_digits_raw.isdigit():
        class_code = class_digits_raw
        division_code = _padded_code(division_raw, 2)
        group_code = _padded_code(group_raw, 3)
    else:
        class_code = class_digits_raw.zfill(4)
        division_code = class_code[:2]
        group_code = class_code[:3]

    return _ParsedRow(
        section_code=section_code,
        section_label=section_label,
        division_raw=division_raw,
        division_label=division_label,
        group_raw=group_raw,
        group_label=group_label,
        class_code=class_code,
        class_label=class_label,
        division_code=division_code,
        group_code=group_code,
    )


def _is_empty_row(row: dict[str, str]) -> bool:
    return not any(row.get(header, '').strip() for header in REQUIRED_HEADERS)


def _validate_class_digit_codes(
    row_number: int,
    parsed: _ParsedRow,
    class_digits_raw: str,
    errors: list[IsicTaxonomyError],
) -> None:
    if not class_digits_raw.isdigit():
        errors.append(IsicTaxonomyError(
            row=row_number,
            column='4-digits',
            message='Class code (4-digits) must be numeric.',
        ))
        return

    if parsed.division_raw:
        padded_division = _padded_code(parsed.division_raw, 2)
        if (
            parsed.division_raw.isdigit()
            and padded_division != parsed.division_code
        ):
            errors.append(IsicTaxonomyError(
                row=row_number,
                column='division',
                message=(
                    f'Division "{padded_division}" does not match '
                    f'the first two digits of 4-digits '
                    f'"{parsed.class_code}" (expected '
                    f'"{parsed.division_code}").'
                ),
            ))

    if parsed.group_raw:
        padded_group = _padded_code(parsed.group_raw, 3)
        if parsed.group_raw.isdigit() and padded_group != parsed.group_code:
            errors.append(IsicTaxonomyError(
                row=row_number,
                column='group',
                message=(
                    f'Group "{padded_group}" does not match the '
                    f'first three digits of 4-digits '
                    f'"{parsed.class_code}" (expected "{parsed.group_code}").'
                ),
            ))


def _validate_required_codes(
    row_number: int,
    parsed: _ParsedRow,
    errors: list[IsicTaxonomyError],
) -> None:
    if not parsed.section_code:
        errors.append(IsicTaxonomyError(
            row=row_number,
            column='section',
            message='Section code is required.',
        ))
    elif not SECTION_CODE_PATTERN.match(parsed.section_code):
        errors.append(IsicTaxonomyError(
            row=row_number,
            column='section',
            message=(
                f'Invalid section code "{parsed.section_code}". '
                'Expected a single letter from A through U.'
            ),
        ))

    if not parsed.division_raw.isdigit():
        errors.append(IsicTaxonomyError(
            row=row_number,
            column='division',
            message='Division must be numeric.',
        ))

    if not parsed.group_raw.isdigit():
        errors.append(IsicTaxonomyError(
            row=row_number,
            column='group',
            message='Group must be numeric.',
        ))


def _validate_hierarchy(
    row_number: int,
    parsed: _ParsedRow,
    errors: list[IsicTaxonomyError],
) -> None:
    if not (
        parsed.section_code
        and parsed.division_code
        and parsed.group_code
        and parsed.class_code
    ):
        return

    if not parsed.group_code.startswith(parsed.division_code):
        errors.append(IsicTaxonomyError(
            row=row_number,
            column='4-digits',
            message=(
                f'Group code "{parsed.group_code}" must begin with division '
                f'code "{parsed.division_code}".'
            ),
        ))

    if not parsed.class_code.startswith(parsed.group_code):
        errors.append(IsicTaxonomyError(
            row=row_number,
            column='4-digits',
            message=(
                f'Class code "{parsed.class_code}" must begin with group '
                f'code "{parsed.group_code}".'
            ),
        ))


def _validate_label_characters(
    row_number: int,
    parsed: _ParsedRow,
    errors: list[IsicTaxonomyError],
) -> None:
    for column, value in (
        ('section_label', parsed.section_label),
        ('division_label', parsed.division_label),
        ('group_label', parsed.group_label),
        ('description', parsed.class_label),
    ):
        if value and not LABEL_CHAR_PATTERN.match(value):
            errors.append(IsicTaxonomyError(
                row=row_number,
                column=column,
                message=(
                    'Contains disallowed characters. Allowed: letters, '
                    'numbers, spaces, and , ; " \' - ( ) . / ’'
                ),
            ))


def _validate_section_label_consistency(
    row_number: int,
    parsed: _ParsedRow,
    section_labels: dict[str, str],
    errors: list[IsicTaxonomyError],
) -> None:
    if not parsed.section_code:
        return

    previous_label = section_labels.get(parsed.section_code)
    if previous_label and previous_label != parsed.section_label:
        errors.append(IsicTaxonomyError(
            row=row_number,
            column='section_label',
            message=(
                f'Section "{parsed.section_code}" has inconsistent '
                f'labels: "{previous_label}" vs "{parsed.section_label}".'
            ),
        ))
    else:
        section_labels[parsed.section_code] = parsed.section_label


def _validate_division_label_consistency(
    row_number: int,
    parsed: _ParsedRow,
    division_labels: dict[tuple[str, str], str],
    errors: list[IsicTaxonomyError],
) -> None:
    if not parsed.section_code or not parsed.division_code:
        return

    division_key = (parsed.section_code, parsed.division_code)
    previous_label = division_labels.get(division_key)
    if previous_label and previous_label != parsed.division_label:
        errors.append(IsicTaxonomyError(
            row=row_number,
            column='division_label',
            message=(
                f'Division "{parsed.division_code}" in section '
                f'"{parsed.section_code}" has inconsistent labels: '
                f'"{previous_label}" vs "{parsed.division_label}".'
            ),
        ))
    else:
        division_labels[division_key] = parsed.division_label


def _validate_group_label_consistency(
    row_number: int,
    parsed: _ParsedRow,
    group_labels: dict[tuple[str, str, str], str],
    errors: list[IsicTaxonomyError],
) -> None:
    if (
        not parsed.section_code
        or not parsed.division_code
        or not parsed.group_code
    ):
        return

    group_key = (
        parsed.section_code,
        parsed.division_code,
        parsed.group_code,
    )
    previous_label = group_labels.get(group_key)
    if previous_label and previous_label != parsed.group_label:
        errors.append(IsicTaxonomyError(
            row=row_number,
            column='group_label',
            message=(
                f'Group "{parsed.group_code}" in division '
                f'"{parsed.division_code}" has inconsistent labels: '
                f'"{previous_label}" vs "{parsed.group_label}".'
            ),
        ))
    else:
        group_labels[group_key] = parsed.group_label


def _validate_label_consistency(
    row_number: int,
    parsed: _ParsedRow,
    section_labels: dict[str, str],
    division_labels: dict[tuple[str, str], str],
    group_labels: dict[tuple[str, str, str], str],
    errors: list[IsicTaxonomyError],
) -> None:
    _validate_section_label_consistency(
        row_number, parsed, section_labels, errors
    )
    _validate_division_label_consistency(
        row_number, parsed, division_labels, errors
    )
    _validate_group_label_consistency(
        row_number, parsed, group_labels, errors
    )


def _validate_duplicate_class_code(
    row_number: int,
    class_code: str,
    seen_class_codes: dict[str, int],
    errors: list[IsicTaxonomyError],
) -> None:
    if not class_code:
        return

    previous_row = seen_class_codes.get(class_code)
    if previous_row is not None:
        errors.append(IsicTaxonomyError(
            row=row_number,
            column='4-digits',
            message=(
                f'Duplicate class code "{class_code}" '
                f'(also on row {previous_row}).'
            ),
        ))
    else:
        seen_class_codes[class_code] = row_number


def validate_rows(rows: list[dict[str, str]]) -> None:
    '''Run stage-1 validation checks and raise if any errors are found.'''
    errors: list[IsicTaxonomyError] = []

    if not rows:
        errors.append(IsicTaxonomyError(
            message='The file must contain at least one class row.',
        ))
        raise IsicTaxonomyValidationError(errors)

    seen_class_codes: dict[str, int] = {}
    section_labels: dict[str, str] = {}
    division_labels: dict[tuple[str, str], str] = {}
    group_labels: dict[tuple[str, str, str], str] = {}

    for row_number, row in enumerate(rows, start=2):
        if _is_empty_row(row):
            errors.append(IsicTaxonomyError(
                row=row_number,
                message='Row is completely empty.',
            ))
            continue

        class_digits_raw = row.get('4-digits', '').strip()
        parsed = _parse_row(row)
        _validate_class_digit_codes(
            row_number,
            parsed,
            class_digits_raw,
            errors,
        )
        _validate_required_codes(row_number, parsed, errors)
        _validate_hierarchy(row_number, parsed, errors)
        _validate_label_characters(row_number, parsed, errors)
        _validate_label_consistency(
            row_number,
            parsed,
            section_labels,
            division_labels,
            group_labels,
            errors,
        )
        _validate_duplicate_class_code(
            row_number,
            parsed.class_code,
            seen_class_codes,
            errors,
        )

    if errors:
        raise IsicTaxonomyValidationError(errors)
