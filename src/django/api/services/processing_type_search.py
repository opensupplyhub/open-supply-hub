"""
Ranking for the processing type typeahead.

Candidate values come from the api_facility_processing_value table, which
holds one row per PostgreSQL lower-case processing type identity together
with the number of locations carrying any casing variant. Both the Apparel
taxonomy labels and unmatched contributor values are suggested, including
terms that are not part of the taxonomy yet.
"""

import re
from collections.abc import Iterable
from typing import TypedDict

from unidecode import unidecode

from django.db.models import BooleanField, F, Func, TextField, Value
from django.db.models.functions import Collate, Lower

from api.facility_type_processing_type import (
    ALL_FACILITY_TYPES,
    FACILITY_PROCESSING_TYPES,
)
from api.helpers.helpers import clean
from api.models.facility.facility_processing_value import (
    FacilityProcessingValue,
)

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

_WHITESPACE_PATTERN = re.compile(r'\s+')
_WORD_PATTERN = re.compile(r'[a-z0-9]+')
_LIKE_SPECIAL_CHARACTER_PATTERN = re.compile(r'([\\%_])')


class ImmutableUnaccent(Func):
    function = 'immutable_unaccent'
    output_field = TextField()


class Like(Func):
    arity = 2
    arg_joiner = ' LIKE '
    template = '%(expressions)s'
    output_field = BooleanField()


class CandidateGroup(TypedDict):
    value: str
    count: int
    score: int


class ScoredSuggestion(TypedDict):
    value: str
    label: str
    count: int
    in_taxonomy: bool
    facility_types: list[str]
    dim: bool
    score: int


class ProcessingTypeSuggestion(TypedDict):
    value: str
    label: str
    count: int
    in_taxonomy: bool
    facility_types: list[str]
    dim: bool


CandidateRow = tuple[str, str, int]


def _normalize(value: str) -> str:
    return _WHITESPACE_PATTERN.sub(' ', unidecode(value)).strip().lower()


def _build_processing_type_parents() -> dict[str, tuple[str, ...]]:
    """
    Map every taxonomy processing type to all of its facility types.

    PROCESSING_TYPES_TO_FACILITY_TYPES keeps only the first parent, which
    loses the second parent of Embroidery and Embellishment.
    """
    parents: dict[str, list[str]] = {}

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

# Taxonomy membership is deliberately case-only. Punctuation, accents, and
# whitespace remain separate identities.
_TAXONOMY_BY_KEY = {
    processing_type.lower(): (processing_type, facility_types)
    for processing_type, facility_types in PROCESSING_TYPE_PARENTS.items()
}

_TAXONOMY_VALUES = sorted(PROCESSING_TYPE_PARENTS)

_FACILITY_TYPE_BY_KEY = {
    clean(facility_type): facility_type
    for facility_type in ALL_FACILITY_TYPES.values()
}


def _like_pattern(query: str) -> str:
    escaped = _LIKE_SPECIAL_CHARACTER_PATTERN.sub(r'\\\1', query)
    return '%{}%'.format(escaped)


def _match_score(
    normalized_value: str,
    normalized_query: str,
) -> int | None:
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


class ProcessingTypeSearch:
    """Rank processing type suggestions for the filter typeahead."""

    def __init__(
        self,
        query: str = '',
        facility_types: Iterable[str] | None = None,
        limit: int = DEFAULT_SUGGESTION_LIMIT,
    ) -> None:
        self._limit = min(max(int(limit), 0), MAX_SUGGESTION_LIMIT)
        self._normalized_query = _normalize(query) if query else ''
        self._selected_facility_types = self._resolve_facility_types(
            facility_types,
        )
        self._is_empty_query = not self._normalized_query

    def build_suggestions(self) -> list[ProcessingTypeSuggestion]:
        """
        Return ranked suggestions for the current query.

        An empty query balances positive-count taxonomy and contributor
        values. Selected facility types boost matching rows and dim the
        rest; nothing is filtered out for a typed query.
        """
        if self._limit == 0:
            return []

        if self._is_empty_query:
            candidates = self._fetch_top_values_by_count()
        else:
            candidates = self._fetch_matching_values()

        grouped = self._group_candidates(
            [*candidates, *self._taxonomy_candidates()],
        )
        rows = [
            self._build_row(key, group)
            for key, group in grouped.items()
        ]

        if self._is_empty_query:
            rows.sort(key=lambda row: (
                -row['score'],
                not row['in_taxonomy'],
                -row['count'],
                row['value'],
            ))
            rows = self._select_empty_query_rows(rows)
        else:
            rows.sort(key=lambda row: (
                -row['score'],
                -row['count'],
                row['value'],
            ))

        return [
            {
                field: value
                for field, value in row.items()
                if field != 'score'
            }
            for row in rows[:self._limit]
        ]

    def _fetch_matching_values(self) -> list[CandidateRow]:
        """Fetch values whose unaccented form contains the query."""
        return list(
            FacilityProcessingValue.objects.filter(
                kind=PROCESSING_TYPE_KIND,
            )
            .alias(
                matches=Like(
                    ImmutableUnaccent(Lower(F('value'))),
                    ImmutableUnaccent(
                        Lower(Value(_like_pattern(self._normalized_query))),
                    ),
                ),
            )
            .filter(matches=True)
            .values_list('identity', 'value', 'facility_count')
        )

    def _fetch_top_values_by_count(self) -> list[CandidateRow]:
        """
        Fetch candidates for an empty query.

        Every taxonomy value is fetched, not just the most common ones: a
        selected facility type can promote any of its children.
        """
        taxonomy_identities = [
            value.lower() for value in _TAXONOMY_VALUES
        ]
        queryset = FacilityProcessingValue.objects.filter(
            kind=PROCESSING_TYPE_KIND,
        )
        taxonomy_rows = queryset.filter(
            identity__in=taxonomy_identities,
        ).values_list('identity', 'value', 'facility_count')
        contributor_rows = (
            queryset.exclude(identity__in=taxonomy_identities)
            .order_by('-facility_count', Collate('value', 'C'))
            .values_list('identity', 'value', 'facility_count')
            [:self._limit]
        )
        return [*taxonomy_rows, *contributor_rows]

    @staticmethod
    def _taxonomy_candidates() -> list[CandidateRow]:
        """
        Supply taxonomy labels even when no locations are indexed under them.

        Empty-query ranking drops those zero-count rows later.
        """
        return [
            (processing_type.lower(), processing_type, 0)
            for processing_type in PROCESSING_TYPE_PARENTS
        ]

    def _group_candidates(
        self,
        candidates: Iterable[CandidateRow],
    ) -> dict[str, CandidateGroup]:
        """Dedupe candidates by their PostgreSQL lower-case identity."""
        grouped: dict[str, CandidateGroup] = {}
        normalized_query = (
            None if self._is_empty_query else self._normalized_query
        )

        for identity, value, count in candidates:
            if not value or not identity:
                continue

            score = (
                0 if normalized_query is None
                else _match_score(_normalize(value), normalized_query)
            )
            if score is None:
                continue

            group = grouped.get(identity)
            if group is None:
                grouped[identity] = {
                    'value': value,
                    'count': count,
                    'score': score,
                }
                continue

            group['count'] = max(group['count'], count)
            group['score'] = max(group['score'], score)

        return grouped

    def _build_row(
        self,
        key: str,
        group: CandidateGroup,
    ) -> ScoredSuggestion:
        """Attach taxonomy metadata, facility-type boost, and dim flag."""
        canonical = _TAXONOMY_BY_KEY.get(key)
        facility_types = canonical[1] if canonical else ()
        value = canonical[0] if canonical else group['value']
        matches_selection = any(
            facility_type in self._selected_facility_types
            for facility_type in facility_types
        )
        score = group['score']
        if matches_selection:
            score += FACILITY_TYPE_MATCH_BOOST

        return {
            'value': value,
            'label': value,
            'count': group['count'],
            'in_taxonomy': canonical is not None,
            'facility_types': list(facility_types),
            'dim': (
                bool(self._selected_facility_types) and not matches_selection
            ),
            'score': score,
        }

    def _select_empty_query_rows(
        self,
        rows: list[ScoredSuggestion],
    ) -> list[ScoredSuggestion]:
        """Apply the empty-query taxonomy/contributor quota."""
        positive_count_rows = [row for row in rows if row['count'] > 0]
        taxonomy_rows = [
            row for row in positive_count_rows if row['in_taxonomy']
        ]
        contributor_rows = [
            row for row in positive_count_rows if not row['in_taxonomy']
        ]

        taxonomy_quota = (self._limit + 1) // 2
        contributor_quota = self._limit // 2
        selected = [
            *taxonomy_rows[:taxonomy_quota],
            *contributor_rows[:contributor_quota],
        ]

        if len(selected) < self._limit:
            selected.extend([
                *taxonomy_rows[taxonomy_quota:],
                *contributor_rows[contributor_quota:],
            ][:self._limit - len(selected)])

        selected_row_ids = {id(row) for row in selected}
        return [
            row for row in positive_count_rows
            if id(row) in selected_row_ids
        ][:self._limit]

    @staticmethod
    def _resolve_facility_types(
        facility_types: Iterable[str] | None,
    ) -> set[str]:
        """Map requested facility types to their taxonomy labels."""
        resolved = set()
        for facility_type in facility_types or []:
            if not facility_type:
                continue
            label = _FACILITY_TYPE_BY_KEY.get(clean(facility_type))
            if label is not None:
                resolved.add(label)
        return resolved
