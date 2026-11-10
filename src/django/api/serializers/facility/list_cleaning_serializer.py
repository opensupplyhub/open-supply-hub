from django.utils import timezone
from rest_framework.serializers import ModelSerializer

from ...models.facility.list_cleaning_run import (
    ListCleaningRun,
    ListCleaningSuggestion,
)
from ...services.list_cleaning import (
    group_key,
    seconds_left,
    wants_removal,
    window_open,
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


def _group_order(group):
    """Must-fix flags first, then removals, then corrections, largest
    first. Deliberately not by decision state: the UI shows these as
    tabs, and tabs must not move while the contributor works."""
    S = ListCleaningSuggestion
    kind_rank = {S.ISSUE: 0, S.REMOVAL: 1, S.CORRECTION: 2}
    if group['severity'] == S.INTERNAL_NOTE:
        return (9, -group['count'], group['key'])
    if group['severity'] == S.ADVISORY:
        return (3, -group['count'], group['key'])
    return (kind_rank.get(group['kind'], 3), -group['count'], group['key'])


def _new_group(key, s):
    return {
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
        # Exact repeats the parser dropped at upload: shown, not decidable.
        'fixed': 0,
        'applied': 0,
        'auto': True,
        'rows': [],
        'examples': [],
    }


_DECISION_COUNTERS = {
    ListCleaningSuggestion.PENDING: 'pending',
    ListCleaningSuggestion.ACCEPTED: 'accepted',
    ListCleaningSuggestion.REJECTED: 'rejected',
    ListCleaningSuggestion.EDITED: 'edited',
    ListCleaningSuggestion.REMOVED: 'removed',
}


def _tally(g, s):
    extra = s.extra or {}
    g['count'] += 1
    g['rows'].append(s.row_number)
    if not extra.get('auto'):
        g['auto'] = False
    g['by_row'] += bool(extra.get('by_row'))
    g['fixed'] += bool(extra.get('parser_removed'))
    counter = _DECISION_COUNTERS.get(s.decision)
    if counter:
        g[counter] += 1
    g['applied'] += bool(s.applied or extra.get('removal_applied'))
    if len(g['examples']) < GROUP_EXAMPLES:
        g['examples'].append({
            'row_number': s.row_number,
            'original_value': s.original_value,
            'corrected_value': s.corrected_value,
            'note': s.note,
        })


def serialize_groups(suggestions):
    """
    One entry per error type (kind + code + field) across the whole list,
    with counts per decision and a few example rows, so a contributor
    can act on a pattern instead of scrolling every row.
    """
    groups = {}
    for s in suggestions:
        key = group_key(s)
        if key not in groups:
            groups[key] = _new_group(key, s)
        _tally(groups[key], s)
    return sorted(groups.values(), key=_group_order)


def _row_head(s):
    item = s.facility_list_item
    if item is None:
        return {'row_number': s.row_number, 'item_id': None, 'name': '',
                'address': '', 'country_code': '', 'item_status': '',
                'suggestions': []}
    return {
        'row_number': s.row_number,
        'item_id': item.id,
        'name': item.name,
        'address': item.address,
        'country_code': item.country_code,
        'item_status': item.status,
        'suggestions': [],
    }


def _rows_by_number(suggestions):
    rows = {}
    for s in suggestions:
        row = rows.setdefault(s.row_number, _row_head(s))
        row['suggestions'].append(ListCleaningSuggestionSerializer(s).data)
    return sorted(rows.values(), key=lambda r: r['row_number'])


def _value_pending(s):
    """An accepted or typed value that is not on the row yet. An edit
    over an automatic fix is pending even though the row was already
    touched once."""
    S = ListCleaningSuggestion
    if s.kind == S.REMOVAL:
        return False
    if s.decision == S.EDITED:
        item = s.facility_list_item
        current = (item.raw_json or {}).get(s.field) if item else None
        return not s.applied or current != s.final_value
    return (s.kind == S.CORRECTION and s.decision == S.ACCEPTED
            and not s.applied)


def _change_unapplied(s):
    """The contributor decided something that is not yet on the list."""
    S = ListCleaningSuggestion
    extra = s.extra or {}
    if _value_pending(s):
        return True
    if wants_removal(s) and not extra.get('removal_applied'):
        return True
    return (s.decision in (S.REJECTED, S.PENDING)
            and bool(s.applied or extra.get('removal_applied')))


def _summary(run, suggestions):
    S = ListCleaningSuggestion
    auto = [s for s in suggestions if (s.extra or {}).get('auto')]
    corrections = [s for s in suggestions if s.kind == S.CORRECTION]
    fixes_to_review = [s for s in corrections
                       if not (s.extra or {}).get('auto')]
    must_fix = [s for s in suggestions if s.severity == S.MUST_FIX]
    removed_rows = {s.row_number for s in suggestions if wants_removal(s)}

    def rows_where(seq, predicate):
        return {s.row_number for s in seq
                if predicate(s) and s.row_number not in removed_rows}

    def pending(s):
        return s.decision == S.PENDING

    # The one number the screen leads with: rows that still wait for
    # the contributor. A row counts once however many suggestions it
    # carries; automatic fixes are already decided, and a removed row
    # has nothing left to decide.
    to_review = [s for s in suggestions if not (s.extra or {}).get('auto')]
    recommended = [s for s in to_review if s.severity != S.MUST_FIX]
    pending_flag_rows = rows_where(must_fix, pending)
    # Rows a moderator would still have to remove: flagged and neither
    # fixed nor removed, whether the contributor has not got to them
    # yet or chose to leave them as uploaded.
    unresolved_flag_rows = rows_where(
        must_fix, lambda s: s.decision in (S.PENDING, S.REJECTED))
    file_pass = run.file_pass or {}
    return {
        'rows_total': run.facility_list.source.facilitylistitem_set.count(),
        'rows_to_review': len({s.row_number for s in to_review}),
        'rows_pending_review': len(rows_where(to_review, pending)),
        # of those, rows with a problem that blocks approval versus
        # rows with only recommended fixes or things worth a look
        'rows_blocking_pending': len(pending_flag_rows),
        'rows_flagged_unresolved': len(unresolved_flag_rows),
        'rows_recommended_pending': len(
            rows_where(recommended, pending) - pending_flag_rows),
        'rows_must_fix_pending': len(pending_flag_rows),
        'rows_must_fix': len({s.row_number for s in must_fix}),
        'rows_with_corrections': len({s.row_number for s in corrections}),
        'corrections_total': len(corrections),
        'corrections_pending': len([s for s in corrections if pending(s)]),
        'corrections_accepted': len(
            [s for s in corrections
             if s.decision in (S.ACCEPTED, S.EDITED)]),
        'corrections_rejected': len(
            [s for s in corrections if s.decision == S.REJECTED]),
        'corrections_unapplied': len(
            [s for s in corrections if _value_pending(s)]),
        'must_fix_total': len(must_fix),
        # A flag on a row the contributor removed no longer needs fixing.
        'must_fix_pending': len(
            [s for s in must_fix
             if pending(s) and s.row_number not in removed_rows]),
        'must_fix_resolved': len(
            [s for s in must_fix if s.decision in (S.EDITED, S.REMOVED)]),
        'removals': len([s for s in suggestions if s.kind == S.REMOVAL]),
        'rows_removed': len(removed_rows),
        'auto_fixes': len(auto),
        # Suggested fixes that wait for the contributor (auto ones are
        # already done) and how many of those have been decided.
        'fixes_to_review_total': len(fixes_to_review),
        'fixes_to_review_decided': len(
            [s for s in fixes_to_review if not pending(s)]),
        'auto_rows': len({s.row_number for s in auto}),
        # Everything the contributor has decided that is not yet on the
        # list.
        'changes_unapplied': len(
            [s for s in suggestions if _change_unapplied(s)]),
        # What the submission put on the list (for the note on the list
        # page after the window has closed).
        'changes_applied': len([
            s for s in suggestions
            if s.applied or (s.extra or {}).get('removal_applied')]),
        'internal_notes': len(
            [s for s in suggestions if s.severity == S.INTERNAL_NOTE]),
        # Only header problems are left as whole-file findings: exact
        # duplicates are an automatic group and repeated names an
        # advisory group, so both sit in the chips.
        'list_findings': len(file_pass.get('header_issues') or []),
    }


def serialize_run(run, include_internal=False, only_rows=None):
    """
    The payload the list items page renders: the run, a summary, the
    suggestions grouped by error type, and the suggestions grouped by row.
    internal_note issues are only included for moderators
    (include_internal=True); contributors never see them.

    `only_rows` (a set of row numbers) limits `rows` to those rows and
    marks the payload `rows_partial`, so a decision on one row of a
    long list sends back the summary and groups plus that row, not every
    row again; the client merges it into what it has.
    """
    suggestions = list(
        run.suggestions.select_related('facility_list_item').all())
    if not include_internal:
        suggestions = [
            s for s in suggestions
            if s.severity != ListCleaningSuggestion.INTERNAL_NOTE
        ]
    summary = _summary(run, suggestions)
    row_suggestions = suggestions
    if only_rows is not None:
        row_suggestions = [s for s in suggestions
                           if s.row_number in only_rows]
    return {
        'run': ListCleaningRunSerializer(run).data,
        'window_open': window_open(run),
        'seconds_left': seconds_left(run),
        'server_time': timezone.now().isoformat(),
        'summary': summary,
        'groups': serialize_groups(suggestions),
        'rows': _rows_by_number(row_suggestions),
        'rows_partial': only_rows is not None,
    }
