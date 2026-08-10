import re

# Matches ISIC display strings like "C - Manufacturing" or
# "0111 - Growing of cereals".
ISIC_DISPLAY_CODE_PATTERN = re.compile(
    r'^\s*([A-Za-z]|\d+)\s*-\s+',
)


def normalize_isic_code(raw_string):
    """
    Extract the leading ISIC code from a stored display string.

    Examples:
        "C - Manufacturing" -> "C"
        "0111 - Growing of cereals (except rice), ..." -> "0111"
        "62 - Computer programming, ..." -> "62"

    Returns None when the input is empty or does not contain a
    recognizable code.
    """
    if raw_string is None:
        return None

    if not isinstance(raw_string, str):
        return None

    value = raw_string.strip()
    if not value:
        return None

    match = ISIC_DISPLAY_CODE_PATTERN.match(value)
    if match:
        code = match.group(1)
        return code.upper() if code.isalpha() else code

    if re.fullmatch(r'[A-Za-z]', value):
        return value.upper()

    if re.fullmatch(r'\d+', value):
        return value

    return None


ISIC4_LEVEL_FIELDS = {
    'section': 'isic_section',
    'division': 'isic_division',
    'group': 'isic_group',
    'class': 'isic_class',
}


def parse_isic4_filter_values(values):
    """
    Parse repeatable isic_4 params like section:A into field/code pairs.
    Invalid entries are ignored.
    """
    parsed = []
    for value in values:
        if not value or ':' not in value:
            continue
        level, code = value.split(':', 1)
        field_name = ISIC4_LEVEL_FIELDS.get(level)
        if field_name and code:
            parsed.append((field_name, code))
    return parsed
