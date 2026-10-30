from django.db.models import Q

from api.isic_taxonomy import revisions
from api.isic_taxonomy.constants import LEVELS

# api_facilityindex columns per revision; {level} is section..class. ISIC 4
# also searches the values Open Supply Hub contributes, mapped from each
# location's Facility Type / Processing Type and Sector through the
# crosswalk (OSDEV-3382).
ISIC_COLUMNS = {
    '4': ('isic_{level}', 'isic_mapped_{level}'),
    '5': ('isic5_{level}',),
}


def parse_isic_filter_values(values):
    """
    Parse repeatable params like section:A into (level, code) pairs.
    Invalid entries are ignored.
    """
    parsed = []
    for value in values:
        if not value or ':' not in value:
            continue
        level, code = value.split(':', 1)
        if level in LEVELS and code:
            parsed.append((level, code))
    return parsed


def build_isic_filter(selected):
    """
    Q matching locations classified under any selected category, in the
    revision it was picked in or, through the UN correspondence, in the
    other one. selected = {'4': [(level, code)], '5': [...]}.
    """
    codes = {}
    for revision, pairs in selected.items():
        for level, code in pairs:
            codes.setdefault((revision, level), set()).add(code)
            translated = revisions.translate(
                revisions.classes_under(code, revision), revision,
            )
            target = revisions.other(revision)
            codes.setdefault((target, 'class'), set()).update(translated)

    isic_filter = Q()
    for (revision, level), level_codes in codes.items():
        for column in ISIC_COLUMNS[revision] if level_codes else ():
            isic_filter |= Q(**{
                f'{column.format(level=level)}__overlap': sorted(level_codes),
            })
    return isic_filter or None
