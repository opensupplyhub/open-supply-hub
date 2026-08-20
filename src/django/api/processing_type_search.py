"""
Ranking for the processing type typeahead.

Candidate values come from the api_facility_processing_value table, which
holds every distinct processing type indexed on api_facilityindex together
with the number of locations carrying it, and is kept in step with
api_facilityindex by triggers. Both the Apparel taxonomy labels and
unmatched contributor values live there, so suggestions cover terms that are
not part of the taxonomy yet.

Candidates are filtered in Postgres with a case- and accent-insensitive
substring match and then scored in Python: the tiers are cheap to reason
about, the candidate set for a 3+ character query is small, and keeping the
scoring here means it can be unit tested without a database.
"""

import re

from unidecode import unidecode

from django.db import connection

from api.facility_type_processing_type import (
    ALL_FACILITY_TYPES,
    FACILITY_PROCESSING_TYPES,
)
from api.helpers.helpers import clean

PROCESSING_TYPE_KIND = 'processing_type'

DEFAULT_SUGGESTION_LIMIT = 40
MAX_SUGGESTION_LIMIT = 100

EXACT_MATCH_SCORE = 1000
PREFIX_MATCH_SCORE = 900
WORD_PREFIX_MATCH_SCORE = 800
WORD_PREFIX_POSITION_PENALTY = 10
SUBSTRING_MATCH_SCORE = 500

# Applied when one of the selected facility types is a parent of the value.
# Selected facility types rank suggestions, they never remove them: values
# outside the selection are marked `dim` instead of being dropped.
FACILITY_TYPE_MATCH_BOOST = 250

CANDIDATE_VALUES_SQL = """
    SELECT
        value,
        facility_count
    FROM
        api_facility_processing_value
    WHERE
        kind = %s
        AND unaccent(value) ILIKE unaccent(%s)
"""

TAXONOMY_VALUES_SQL = """
    SELECT
        value,
        facility_count
    FROM
        api_facility_processing_value
    WHERE
        kind = %s
        AND lower(value) = ANY(%s)
"""

TOP_CONTRIBUTOR_VALUES_SQL = """
    SELECT
        value,
        facility_count
    FROM
        api_facility_processing_value
    WHERE
        kind = %s
        AND NOT (lower(value) = ANY(%s))
    ORDER BY
        facility_count DESC,
        value ASC
    LIMIT %s
"""

_WHITESPACE_PATTERN = re.compile(r'\s+')
_WORD_PATTERN = re.compile(r'[a-z0-9]+')
_ILIKE_SPECIAL_CHARACTER_PATTERN = re.compile(r'([\\%_])')


def _normalize(value):
    return _WHITESPACE_PATTERN.sub(' ', unidecode(value)).strip().lower()


def _build_processing_type_parents():
    """
    Map every taxonomy processing type to all of its facility types.

    PROCESSING_TYPES_TO_FACILITY_TYPES keeps only the first parent, which
    loses the second parent of Embroidery and Embellishment.
    """
    parents = {}

    for facility_type_key, processing_types in (
        FACILITY_PROCESSING_TYPES.items()
    ):
        facility_type = ALL_FACILITY_TYPES[facility_type_key]
        for processing_type in processing_types.values():
            facility_types = parents.setdefault(processing_type, [])
            if facility_type not in facility_types:
                facility_types.append(facility_type)

    return {
        processing_type: tuple(facility_types)
        for processing_type, facility_types in parents.items()
    }


PROCESSING_TYPE_PARENTS = _build_processing_type_parents()

# Values keep the casing and punctuation the contributor submitted, so
# "Warehousing Distribution" and "Warehousing / Distribution" both reach the
# facility index. Grouping and taxonomy membership therefore run on the same
# punctuation-insensitive form the rest of the platform matches with.
_TAXONOMY_BY_KEY = {
    clean(processing_type): (processing_type, facility_types)
    for processing_type, facility_types in PROCESSING_TYPE_PARENTS.items()
}

_TAXONOMY_LOWERCASE_VALUES = sorted(
    processing_type.lower() for processing_type in PROCESSING_TYPE_PARENTS
)

_FACILITY_TYPE_BY_KEY = {
    clean(facility_type): facility_type
    for facility_type in ALL_FACILITY_TYPES.values()
}


def _grouping_key(value):
    return clean(value) or _normalize(value)


def get_processing_type_parents(value):
    """Return the facility types a processing type belongs to."""
    if not value:
        return ()

    canonical = _TAXONOMY_BY_KEY.get(_grouping_key(value))

    return canonical[1] if canonical else ()


def resolve_facility_types(facility_types):
    """
    Map requested facility types to their taxonomy labels.

    Accepts the labels used by the filter sidebar as well as the lowercase
    keys stored in ALL_FACILITY_TYPES. Unknown values are ignored.
    """
    resolved = set()

    for facility_type in facility_types or []:
        if not facility_type:
            continue
        label = _FACILITY_TYPE_BY_KEY.get(clean(facility_type))
        if label is not None:
            resolved.add(label)

    return resolved


def _ilike_pattern(query):
    escaped = _ILIKE_SPECIAL_CHARACTER_PATTERN.sub(r'\\\1', query)
    return '%{}%'.format(escaped)


def _match_score(normalized_value, normalized_query):
    """
    Score a value against a query, or return None when it does not match.

    A match on a later word scores lower than one on an earlier word, so for
    the query "dyeing" the value "Knit Dyeing" ranks above "Cut Trim Dyeing".
    """
    if normalized_value == normalized_query:
        return EXACT_MATCH_SCORE

    if normalized_value.startswith(normalized_query):
        return PREFIX_MATCH_SCORE

    words = _WORD_PATTERN.findall(normalized_value)
    for position, word in enumerate(words):
        if position and word.startswith(normalized_query):
            return (
                WORD_PREFIX_MATCH_SCORE
                - WORD_PREFIX_POSITION_PENALTY * position
            )

    if normalized_query in normalized_value:
        return SUBSTRING_MATCH_SCORE

    return None


def _fetch_matching_values(normalized_query):
    with connection.cursor() as cursor:
        cursor.execute(
            CANDIDATE_VALUES_SQL,
            [PROCESSING_TYPE_KIND, _ilike_pattern(normalized_query)],
        )
        return cursor.fetchall()


def _fetch_top_values_by_count(limit):
    """
    Fetch the candidates for an empty query.

    Every taxonomy value is fetched, not just the most common ones: a
    selected facility type can promote any of its children, and a value that
    reaches the results with a count taken from the fetch rather than from
    the view would report zero locations.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            TAXONOMY_VALUES_SQL,
            [PROCESSING_TYPE_KIND, _TAXONOMY_LOWERCASE_VALUES],
        )
        candidates = cursor.fetchall()

        cursor.execute(
            TOP_CONTRIBUTOR_VALUES_SQL,
            [PROCESSING_TYPE_KIND, _TAXONOMY_LOWERCASE_VALUES, limit],
        )
        return [*candidates, *cursor.fetchall()]


def _taxonomy_candidates():
    """
    Taxonomy labels are always suggestible, even with no locations indexed
    under them yet, so they are offered alongside the view rows.
    """
    return [
        (processing_type, 0)
        for processing_type in PROCESSING_TYPE_PARENTS
    ]


def _group_candidates(candidates, normalized_query):
    """
    Dedupe only identical stored values.

    Taxonomy labels are appended as synthetic zero-count candidates. When a
    stored value is identical to one of those labels, retain the stored count
    rather than adding it twice. Casing and punctuation variants remain
    independently selectable rows with their own counts.
    """
    grouped = {}

    for value, count in candidates:
        if not value or not _grouping_key(value):
            continue

        score = (
            0 if normalized_query is None
            else _match_score(_normalize(value), normalized_query)
        )
        if score is None:
            continue

        group = grouped.get(value)
        if group is None:
            grouped[value] = {
                'value': value,
                'count': count,
                'score': score,
            }
            continue

        group['count'] = max(group['count'], count)
        group['score'] = max(group['score'], score)

    return grouped


def _build_row(key, group, selected_facility_types):
    canonical = _TAXONOMY_BY_KEY.get(_grouping_key(key))
    facility_types = canonical[1] if canonical else ()

    matches_selection = any(
        facility_type in selected_facility_types
        for facility_type in facility_types
    )
    score = group['score']
    if matches_selection:
        score += FACILITY_TYPE_MATCH_BOOST

    return {
        'value': group['value'],
        # Concrete variants remain independently selectable, so display the
        # stored value rather than giving every variant the same taxonomy
        # label and making distinct counts look like duplicate rows.
        'label': group['value'],
        'count': group['count'],
        'in_taxonomy': canonical is not None,
        'facility_types': list(facility_types),
        'dim': bool(selected_facility_types) and not matches_selection,
        'score': score,
    }


def search_processing_types(
    query='',
    facility_types=None,
    limit=DEFAULT_SUGGESTION_LIMIT,
):
    """
    Rank processing type suggestions for a typeahead query.

    An empty query returns the most common values with taxonomy terms
    first. Selected facility types boost the values they are parents of and
    dim the rest; nothing is filtered out.

    `value` is a concrete, case-sensitive indexed value suitable for exact
    filtering. `label` displays that same concrete value so independently
    selectable casing and punctuation variants remain distinguishable.
    """
    limit = min(max(int(limit), 0), MAX_SUGGESTION_LIMIT)
    if limit == 0:
        return []

    normalized_query = _normalize(query) if query else ''
    selected_facility_types = resolve_facility_types(facility_types)
    is_empty_query = not normalized_query

    if is_empty_query:
        candidates = _fetch_top_values_by_count(limit)
    else:
        candidates = _fetch_matching_values(normalized_query)

    candidates = [*candidates, *_taxonomy_candidates()]
    grouped = _group_candidates(
        candidates,
        None if is_empty_query else normalized_query,
    )

    rows = [
        _build_row(key, group, selected_facility_types)
        for key, group in grouped.items()
    ]

    if is_empty_query:
        rows.sort(key=lambda row: (
            -row['score'],
            not row['in_taxonomy'],
            -row['count'],
            row['value'],
        ))
    else:
        rows.sort(key=lambda row: (
            -row['score'],
            -row['count'],
            row['value'],
        ))

    return [
        {field: value for field, value in row.items() if field != 'score'}
        for row in rows[:limit]
    ]
