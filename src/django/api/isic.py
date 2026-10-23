ISIC4_LEVEL_FIELDS = {
    'section': 'isic_section',
    'division': 'isic_division',
    'group': 'isic_group',
    'class': 'isic_class',
}

# Codes mapped from OS Hub Facility Type / Processing Type through the
# crosswalk (OSDEV-3382), searched only when the caller opts in.
ISIC4_MAPPED_FIELD_BY_FIELD = {
    'isic_section': 'isic_mapped_section',
    'isic_division': 'isic_mapped_division',
    'isic_group': 'isic_mapped_group',
    'isic_class': 'isic_mapped_class',
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
