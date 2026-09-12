"""Build indexed Facility Type and Processing Type queryset annotations."""

import re
from typing import Literal, Self, Sequence, TypeAlias, cast

from django.db.models import BooleanField, IntegerField, QuerySet
from django.db.models.expressions import RawSQL

from api.facility_type_processing_type import get_facility_and_processing_type
from api.services.facility_processing_query import FacilityProcessingResult


TaxonomyMatch: TypeAlias = tuple[
    str | None,
    str | None,
    str | None,
    str | None,
]
Classification: TypeAlias = Literal['taxonomy', 'free_text'] | None
ClassifiedData: TypeAlias = TaxonomyMatch | str | None
ClassifiedValue: TypeAlias = tuple[Classification, ClassifiedData]
SqlParameter: TypeAlias = str | Sequence[str | None]
SqlResult: TypeAlias = tuple[str | None, list[SqlParameter]]


FREE_TEXT_ARRAY_MATCH: str = """
(
    EXISTS (
        SELECT 1 FROM unnest(facility_type) AS elem
        WHERE unaccent(elem) ~* unaccent(%s)
    )
    OR EXISTS (
        SELECT 1 FROM unnest(processing_type) AS elem
        WHERE unaccent(elem) ~* unaccent(%s)
    )
)
"""

# A word-prefix regex over an unnested array cannot use an index, so the
# trigram index on facility_processing_search_text() gathers the candidate
# locations and the regex rechecks only those.
FREE_TEXT_INDEXED_MATCH: str = """
(
    facility_processing_search_text(facility_type, processing_type)
        LIKE '%%' || immutable_unaccent(lower(%s)) || '%%'
    AND {array_match}
)
"""

# Both tiers are scored in one pass over the two arrays.
FREE_TEXT_TERM_SCORE: str = """
(
    SELECT COALESCE(MAX(
        CASE
            WHEN unaccent(elem) ~* unaccent(%s) THEN 2
            WHEN unaccent(elem) ~* unaccent(%s) THEN 1
            ELSE 0
        END
    ), 0)
    FROM unnest(
        COALESCE(facility_type, '{}'::varchar[])
        || COALESCE(processing_type, '{}'::varchar[])
    ) AS elem
)
"""

_LIKE_SPECIAL_CHARACTER_PATTERN: re.Pattern[str] = re.compile(r'([\\%_])')


class FacilityProcessingFilter:
    """
    Build indexed Facility Type and Processing Type filter expressions.

    Values are classified once when the instance is created, then reused for
    match and relevance SQL so both annotations apply identical semantics.
    """

    # Also the shortest term a trigram index can narrow, so no free-text
    # filter falls back to scanning api_facilityindex.
    MIN_FREE_TEXT_LENGTH: int = 3

    def __init__(
        self,
        facility_types: Sequence[str],
        processing_types: Sequence[str],
        exact_processing_types: Sequence[str] | None = None,
    ) -> None:
        """
        Store parsed filters and classify non-exact values once.

        ``exact_processing_types`` is expected to have already been
        intersected with ``processing_types`` by ``FacilityProcessingQuery``.
        """
        self.facility_types = list(facility_types or [])
        self.processing_types = list(processing_types or [])
        self.exact_processing_types = list(exact_processing_types or [])

        exact_identities = {
            value.lower() for value in self.exact_processing_types
        }
        self.legacy_processing_types: list[str] = [
            value
            for value in self.processing_types
            if value.lower() not in exact_identities
        ]

        self._classified_facility_types: list[ClassifiedValue] = (
            self._classify_values(self.facility_types)
        )
        self._classified_processing_types: list[ClassifiedValue] = (
            self._classify_values(self.legacy_processing_types)
        )
        self._free_text_terms: list[str] = [
            cast(str, data)
            for classification, data in (
                self._classified_facility_types
                + self._classified_processing_types
            )
            if classification == 'free_text'
        ]

    @classmethod
    def from_result(cls, parsed: FacilityProcessingResult) -> Self:
        """Create a filter from the query parser's validated result."""
        return cls(
            parsed.facility_types,
            parsed.processing_types,
            parsed.exact_processing_types,
        )

    @classmethod
    def _classify_value(cls, value: str) -> ClassifiedValue:
        """Classify one value as taxonomy, free text, or invalid."""
        trimmed = value.strip()
        if not trimmed:
            return (None, None)

        standard_type: TaxonomyMatch = get_facility_and_processing_type(
            value,
            ['Apparel'],
            allow_fuzzy=len(trimmed) >= cls.MIN_FREE_TEXT_LENGTH,
        )
        if standard_type[0] is not None:
            return ('taxonomy', standard_type)

        if len(trimmed) >= cls.MIN_FREE_TEXT_LENGTH:
            return ('free_text', trimmed)

        return (None, None)

    @classmethod
    def _classify_values(
        cls,
        values: Sequence[str],
    ) -> list[ClassifiedValue]:
        """Classify a sequence while preserving its submitted order."""
        return [cls._classify_value(value) for value in values]

    @staticmethod
    def _word_prefix_pattern(term: str) -> str:
        """Return a PostgreSQL regex matching the start of a word."""
        return rf'\m{re.escape(term)}'

    @classmethod
    def _whole_word_pattern(cls, term: str) -> str:
        """Return a PostgreSQL regex matching one complete word."""
        return rf'{cls._word_prefix_pattern(term)}\M'

    @staticmethod
    def _like_term(term: str) -> str:
        """Escape a term for use inside the trigram containment pattern."""
        return _LIKE_SPECIAL_CHARACTER_PATTERN.sub(r'\\\1', term)

    @classmethod
    def _param_sql_parts(
        cls,
        classified_values: Sequence[ClassifiedValue],
        overlap_field: str,
        taxonomy_slot: int,
    ) -> tuple[list[str], list[SqlParameter]]:
        """Build OR-able indexed predicates for one query parameter."""
        taxonomy_values: list[str | None] = []
        free_text_terms: list[str] = []
        for classification, data in classified_values:
            if classification == 'taxonomy':
                taxonomy_match = cast(TaxonomyMatch, data)
                taxonomy_values.append(taxonomy_match[taxonomy_slot])
            elif classification == 'free_text':
                free_text_terms.append(cast(str, data))

        parts: list[str] = []
        params: list[SqlParameter] = []
        if taxonomy_values:
            parts.append(f'{overlap_field} && %s::varchar[]')
            params.append(taxonomy_values)

        for term in free_text_terms:
            parts.append(
                FREE_TEXT_INDEXED_MATCH.format(
                    array_match=FREE_TEXT_ARRAY_MATCH
                )
            )
            pattern = cls._word_prefix_pattern(term)
            params.extend([cls._like_term(term), pattern, pattern])

        return parts, params

    @classmethod
    def _append_param_clause(
        cls,
        clauses: list[str],
        all_params: list[SqlParameter],
        values: Sequence[str],
        classified_values: Sequence[ClassifiedValue],
        overlap_field: str,
        taxonomy_slot: int,
    ) -> None:
        """
        Append one parameter's OR clause without broadening invalid input.
        """
        if not values:
            return

        parts, params = cls._param_sql_parts(
            classified_values,
            overlap_field,
            taxonomy_slot,
        )
        clauses.append('(' + ' OR '.join(parts) + ')' if parts else '(FALSE)')
        all_params.extend(params)

    def _append_exact_processing_clause(
        self,
        clauses: list[str],
        all_params: list[SqlParameter],
    ) -> None:
        """
        Append case-insensitive exact matching using migration 0233's index.
        """
        if not self.exact_processing_types:
            return

        exact_clause = (
            'lower_varchar_array(processing_type) && %s::text[]'
        )
        if clauses and self.legacy_processing_types:
            clauses[-1] = f'({clauses[-1]} OR {exact_clause})'
        else:
            clauses.append(f'({exact_clause})')
        all_params.append([
            value.lower() for value in self.exact_processing_types
        ])

    def match_sql(self) -> SqlResult:
        """
        Return the indexed boolean SQL expression and its parameters.

        Values within one query parameter are OR'd; Facility Type and
        Processing Type query parameters are AND'd.
        """
        clauses: list[str] = []
        params: list[SqlParameter] = []
        for values, classified, overlap_field, taxonomy_slot in (
            (
                self.facility_types,
                self._classified_facility_types,
                'facility_type',
                2,
            ),
            (
                self.legacy_processing_types,
                self._classified_processing_types,
                'processing_type',
                3,
            ),
        ):
            self._append_param_clause(
                clauses,
                params,
                values,
                classified,
                overlap_field,
                taxonomy_slot,
            )

        self._append_exact_processing_clause(clauses, params)
        if not clauses:
            return None, []

        return ' AND '.join(clauses), params

    def relevance_sql(self) -> SqlResult:
        """Return whole-word/word-prefix relevance SQL and its parameters."""
        score_parts: list[str] = []
        params: list[SqlParameter] = []
        for term in self._free_text_terms:
            score_parts.append(FREE_TEXT_TERM_SCORE)
            params.extend([
                self._whole_word_pattern(term),
                self._word_prefix_pattern(term),
            ])

        if not score_parts:
            return None, []
        if len(score_parts) == 1:
            return score_parts[0], params

        return f"GREATEST({', '.join(score_parts)})", params

    def annotate_match(
        self,
        queryset: QuerySet,
        name: str = '_fp_match',
    ) -> tuple[QuerySet, bool]:
        """Annotate a queryset with the boolean match expression, if any."""
        sql, params = self.match_sql()
        if not sql:
            return queryset, False

        return queryset.annotate(
            **{
                name: RawSQL(
                    sql,
                    params,
                    output_field=BooleanField(),
                )
            }
        ), True

    def annotate_relevance(
        self,
        queryset: QuerySet,
        name: str = '_fp_relevance',
    ) -> tuple[QuerySet, bool]:
        """Annotate a queryset with free-text relevance scoring, if any."""
        sql, params = self.relevance_sql()
        if not sql:
            return queryset, False

        return queryset.annotate(
            **{
                name: RawSQL(
                    sql,
                    params,
                    output_field=IntegerField(),
                )
            }
        ), True
