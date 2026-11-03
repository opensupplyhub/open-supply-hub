from rest_framework.serializers import ModelSerializer

from ...models.facility.list_cleaning_run import (
    ListCleaningRun,
    ListCleaningSuggestion,
)


class ListCleaningSuggestionSerializer(ModelSerializer):
    class Meta:
        model = ListCleaningSuggestion
        fields = ('id', 'row_number', 'facility_list_item', 'kind', 'field',
                  'code', 'severity', 'original_value', 'corrected_value',
                  'note', 'extra', 'decision', 'decided_value', 'decided_at',
                  'applied')


class ListCleaningRunSerializer(ModelSerializer):
    class Meta:
        model = ListCleaningRun
        fields = ('id', 'status', 'runner', 'prompt_version', 'file_pass',
                  'usage', 'error', 'created_at', 'started_at',
                  'completed_at', 'applied_at')


def serialize_run(run, include_internal=False):
    """
    The payload the list items page renders: the run, a summary, and the
    suggestions grouped by row. internal_note issues are only included for
    moderators (include_internal=True); contributors never see them.
    """
    suggestions = list(
        run.suggestions.select_related('facility_list_item').all())
    if not include_internal:
        suggestions = [
            s for s in suggestions
            if s.severity != ListCleaningSuggestion.INTERNAL_NOTE
        ]

    rows = {}
    for s in suggestions:
        row = rows.get(s.row_number)
        if row is None:
            item = s.facility_list_item
            row = {
                'row_number': s.row_number,
                'item_id': item.id if item else None,
                'name': item.name if item else '',
                'address': item.address if item else '',
                'country_code': item.country_code if item else '',
                'item_status': item.status if item else '',
                'suggestions': [],
            }
            rows[s.row_number] = row
        row['suggestions'].append(ListCleaningSuggestionSerializer(s).data)

    corrections = [s for s in suggestions
                   if s.kind == ListCleaningSuggestion.CORRECTION]
    must_fix_rows = {s.row_number for s in suggestions
                     if s.severity == ListCleaningSuggestion.MUST_FIX}
    file_pass = run.file_pass or {}
    summary = {
        'rows_must_fix': len(must_fix_rows),
        'rows_with_corrections': len({s.row_number for s in corrections}),
        'corrections_total': len(corrections),
        'corrections_pending': len(
            [s for s in corrections
             if s.decision == ListCleaningSuggestion.PENDING]),
        'corrections_accepted': len(
            [s for s in corrections
             if s.decision in (ListCleaningSuggestion.ACCEPTED,
                               ListCleaningSuggestion.EDITED)]),
        'corrections_rejected': len(
            [s for s in corrections
             if s.decision == ListCleaningSuggestion.REJECTED]),
        'corrections_unapplied': len(
            [s for s in corrections
             if s.decision in (ListCleaningSuggestion.ACCEPTED,
                               ListCleaningSuggestion.EDITED)
             and not s.applied]),
        'removals': len([s for s in suggestions
                         if s.kind == ListCleaningSuggestion.REMOVAL]),
        'internal_notes': len(
            [s for s in suggestions
             if s.severity == ListCleaningSuggestion.INTERNAL_NOTE]),
        'list_findings': (
            len(file_pass.get('header_issues') or [])
            + len(file_pass.get('exact_duplicates') or [])
            + len(file_pass.get('repeated_names') or [])
        ),
    }

    return {
        'run': ListCleaningRunSerializer(run).data,
        'summary': summary,
        'rows': sorted(rows.values(), key=lambda r: r['row_number']),
    }
