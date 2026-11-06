from django.utils import timezone
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
                  'completed_at', 'applied_at', 'review_until',
                  'submitted_at', 'closed_at', 'closed_reason')


GROUP_EXAMPLES = 3


def _group_key(s):
    return f'{s.kind}:{s.code}:{s.field}'


def _group_order(group):
    """Must-fix flags first, then removals, then corrections, largest
    first. Deliberately not by decision state: the UI shows these as
    tabs, and tabs must not move while the contributor works."""
    S = ListCleaningSuggestion
    kind_rank = {S.ISSUE: 0, S.REMOVAL: 1, S.CORRECTION: 2}
    if group['severity'] == S.INTERNAL_NOTE:
        return (9, -group['count'], group['key'])
    return (kind_rank.get(group['kind'], 3), -group['count'], group['key'])


def serialize_groups(suggestions):
    """
    One entry per error type (kind + code + field) across the whole list,
    with counts per decision and a few example rows, so a contributor
    can act on a pattern instead of scrolling every row.
    """
    S = ListCleaningSuggestion
    groups = {}
    for s in suggestions:
        key = _group_key(s)
        g = groups.get(key)
        if g is None:
            g = groups[key] = {
                'key': key,
                'kind': s.kind,
                'code': s.code,
                'field': s.field,
                'severity': s.severity,
                'count': 0,
                'pending': 0,
                'accepted': 0,
                'rejected': 0,
                'edited': 0,
                'removed': 0,
                'by_row': 0,
                'applied': 0,
                'auto': True,
                'rows': [],
                'examples': [],
            }
        g['count'] += 1
        g['rows'].append(s.row_number)
        if not (s.extra or {}).get('auto'):
            g['auto'] = False
        if (s.extra or {}).get('by_row'):
            g['by_row'] += 1
        if s.decision == S.PENDING:
            g['pending'] += 1
        elif s.decision == S.ACCEPTED:
            g['accepted'] += 1
        elif s.decision == S.REJECTED:
            g['rejected'] += 1
        elif s.decision == S.EDITED:
            g['edited'] += 1
        elif s.decision == S.REMOVED:
            g['removed'] += 1
        if s.applied or (s.extra or {}).get('removal_applied'):
            g['applied'] += 1
        if len(g['examples']) < GROUP_EXAMPLES:
            g['examples'].append({
                'row_number': s.row_number,
                'original_value': s.original_value,
                'corrected_value': s.corrected_value,
                'note': s.note,
            })
    return sorted(groups.values(), key=_group_order)


def serialize_run(run, include_internal=False):
    """
    The payload the list items page renders: the run, a summary, the
    suggestions grouped by error type, and the suggestions grouped by row.
    internal_note issues are only included for moderators
    (include_internal=True); contributors never see them.
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

    S = ListCleaningSuggestion
    corrections = [s for s in suggestions if s.kind == S.CORRECTION]
    must_fix = [s for s in suggestions if s.severity == S.MUST_FIX]
    must_fix_rows = {s.row_number for s in must_fix}
    removed_rows = {
        s.row_number for s in suggestions
        if s.decision == S.REMOVED
        or (s.kind == S.REMOVAL and s.decision == S.ACCEPTED)}

    def value_pending(s):
        """An accepted or typed value that is not on the row yet. An edit
        over an automatic fix is pending even though the row was already
        touched once."""
        if s.kind == S.REMOVAL:
            return False
        if s.decision == S.EDITED:
            item = s.facility_list_item
            current = (item.raw_json or {}).get(s.field) if item else None
            return not s.applied or current != s.final_value
        return (s.kind == S.CORRECTION and s.decision == S.ACCEPTED
                and not s.applied)

    # Everything the contributor has decided that is not yet on the list.
    changes_unapplied = len([
        s for s in suggestions
        if value_pending(s)
        or ((s.decision == S.REMOVED
             or (s.kind == S.REMOVAL and s.decision == S.ACCEPTED))
            and not (s.extra or {}).get('removal_applied'))
        or (s.decision in (S.REJECTED, S.PENDING) and (
            s.applied or (s.extra or {}).get('removal_applied')))
    ])
    file_pass = run.file_pass or {}
    pending_flag_rows = {
        s.row_number for s in must_fix
        if s.decision == S.PENDING and s.row_number not in removed_rows}
    summary = {
        'rows_total': run.facility_list.source.facilitylistitem_set.count(),
        # rows a moderator would still have to remove, for the warning
        # before a submission that leaves many of them
        'rows_must_fix_pending': len(pending_flag_rows),
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
            [s for s in corrections if value_pending(s)]),
        'must_fix_total': len(must_fix),
        # A flag on a row the contributor removed no longer needs fixing.
        'must_fix_pending': len(
            [s for s in must_fix if s.decision == S.PENDING
             and s.row_number not in removed_rows]),
        'must_fix_resolved': len(
            [s for s in must_fix if s.decision in (S.EDITED, S.REMOVED)]),
        'removals': len([s for s in suggestions
                         if s.kind == ListCleaningSuggestion.REMOVAL]),
        'rows_removed': len(removed_rows),
        'auto_fixes': len(
            [s for s in suggestions if (s.extra or {}).get('auto')]),
        # Suggested fixes that wait for the contributor (auto ones are
        # already done) and how many of those have been decided: the
        # readiness tracker's middle milestone.
        'fixes_to_review_total': len(
            [s for s in corrections if not (s.extra or {}).get('auto')]),
        'fixes_to_review_decided': len(
            [s for s in corrections if not (s.extra or {}).get('auto')
             and s.decision != S.PENDING]),
        'auto_rows': len(
            {s.row_number for s in suggestions
             if (s.extra or {}).get('auto')}),
        'changes_unapplied': changes_unapplied,
        # What the submission put on the list (for the note on the list
        # page after the window has closed).
        'changes_applied': len([
            s for s in suggestions
            if s.applied or (s.extra or {}).get('removal_applied')]),
        'internal_notes': len(
            [s for s in suggestions
             if s.severity == ListCleaningSuggestion.INTERNAL_NOTE]),
        'list_findings': (
            len(file_pass.get('header_issues') or [])
            + len(file_pass.get('exact_duplicates') or [])
            + len(file_pass.get('repeated_names') or [])
        ),
    }

    from api.services.list_cleaning import seconds_left, window_open
    return {
        'run': ListCleaningRunSerializer(run).data,
        'window_open': window_open(run),
        'seconds_left': seconds_left(run),
        'server_time': timezone.now().isoformat(),
        'summary': summary,
        'groups': serialize_groups(suggestions),
        'rows': sorted(rows.values(), key=lambda r: r['row_number']),
    }
