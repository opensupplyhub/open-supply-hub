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
        if not any(row.get(header, '').strip() for header in REQUIRED_HEADERS):
            errors.append(IsicTaxonomyError(
                row=row_number,
                message='Row is completely empty.',
            ))
            continue

        section_code = row.get('section', '').strip().upper()
        section_label = row.get('section_label', '').strip()
        division_raw = row.get('division', '').strip()
        division_label = row.get('division_label', '').strip()
        group_raw = row.get('group', '').strip()
        group_label = row.get('group_label', '').strip()
        class_digits_raw = row.get('4-digits', '').strip()
        class_label = row.get('description', '').strip()

        if not class_digits_raw.isdigit():
            errors.append(IsicTaxonomyError(
                row=row_number,
                column='4-digits',
                message='Class code (4-digits) must be numeric.',
            ))
            class_code = class_digits_raw
            division_code = _padded_code(division_raw, 2)
            group_code = _padded_code(group_raw, 3)
        else:
            class_code = class_digits_raw.zfill(4)
            division_code = class_code[:2]
            group_code = class_code[:3]

            if division_raw:
                padded_division = _padded_code(division_raw, 2)
                if (
                    division_raw.isdigit()
                    and padded_division != division_code
                ):
                    errors.append(IsicTaxonomyError(
                        row=row_number,
                        column='division',
                        message=(
                            f'Division "{padded_division}" does not match '
                            f'the first two digits of 4-digits '
                            f'"{class_code}" (expected "{division_code}").'
                        ),
                    ))

            if group_raw:
                padded_group = _padded_code(group_raw, 3)
                if group_raw.isdigit() and padded_group != group_code:
                    errors.append(IsicTaxonomyError(
                        row=row_number,
                        column='group',
                        message=(
                            f'Group "{padded_group}" does not match the '
                            f'first three digits of 4-digits '
                            f'"{class_code}" (expected "{group_code}").'
                        ),
                    ))

        if not section_code:
            errors.append(IsicTaxonomyError(
                row=row_number,
                column='section',
                message='Section code is required.',
            ))
        elif not SECTION_CODE_PATTERN.match(section_code):
            errors.append(IsicTaxonomyError(
                row=row_number,
                column='section',
                message=(
                    f'Invalid section code "{section_code}". '
                    'Expected a single letter from A through U.'
                ),
            ))

        if not division_raw.isdigit():
            errors.append(IsicTaxonomyError(
                row=row_number,
                column='division',
                message='Division must be numeric.',
            ))

        if not group_raw.isdigit():
            errors.append(IsicTaxonomyError(
                row=row_number,
                column='group',
                message='Group must be numeric.',
            ))

        if section_code and division_code and group_code and class_code:
            if not group_code.startswith(division_code):
                errors.append(IsicTaxonomyError(
                    row=row_number,
                    column='4-digits',
                    message=(
                        f'Group code "{group_code}" must begin with division '
                        f'code "{division_code}".'
                    ),
                ))

            if not class_code.startswith(group_code):
                errors.append(IsicTaxonomyError(
                    row=row_number,
                    column='4-digits',
                    message=(
                        f'Class code "{class_code}" must begin with group '
                        f'code "{group_code}".'
                    ),
                ))

        for column, value in (
            ('section_label', section_label),
            ('division_label', division_label),
            ('group_label', group_label),
            ('description', class_label),
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

        if section_code:
            previous_label = section_labels.get(section_code)
            if previous_label and previous_label != section_label:
                errors.append(IsicTaxonomyError(
                    row=row_number,
                    column='section_label',
                    message=(
                        f'Section "{section_code}" has inconsistent labels: '
                        f'"{previous_label}" vs "{section_label}".'
                    ),
                ))
            else:
                section_labels[section_code] = section_label

        if section_code and division_code:
            division_key = (section_code, division_code)
            previous_label = division_labels.get(division_key)
            if previous_label and previous_label != division_label:
                errors.append(IsicTaxonomyError(
                    row=row_number,
                    column='division_label',
                    message=(
                        f'Division "{division_code}" in section '
                        f'"{section_code}" has inconsistent labels: '
                        f'"{previous_label}" vs "{division_label}".'
                    ),
                ))
            else:
                division_labels[division_key] = division_label

        if section_code and division_code and group_code:
            group_key = (section_code, division_code, group_code)
            previous_label = group_labels.get(group_key)
            if previous_label and previous_label != group_label:
                errors.append(IsicTaxonomyError(
                    row=row_number,
                    column='group_label',
                    message=(
                        f'Group "{group_code}" in division "{division_code}" '
                        f'has inconsistent labels: "{previous_label}" vs '
                        f'"{group_label}".'
                    ),
                ))
            else:
                group_labels[group_key] = group_label

        if class_code:
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

    if errors:
        raise IsicTaxonomyValidationError(errors)
