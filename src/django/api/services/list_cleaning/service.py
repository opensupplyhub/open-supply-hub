"""
Contributor-facing list-cleaning feedback (OSDEV-3726).

start_run      -> create a ListCleaningRun and hand it to the configured
                  runner (Step Functions in deployed environments, local
                  stub rules in development). No-op unless the
                  `enable_list_cleaning_feedback` switch is on.
refresh_run    -> poll an asynchronous runner and ingest its result.
ingest_result  -> turn the pipeline's aggregated {file_pass, records, usage}
                  into ListCleaningSuggestion rows.
record_decisions -> log a contributor's accept / reject / edit per
                  suggestion.
apply_run      -> write accepted corrections onto the PENDING list's items,
                  in place. The uploaded file and each suggestion's
                  original_value keep the original.
"""
import logging

from django.db import transaction
from django.utils import timezone
from waffle import switch_is_active

from api.helpers.helpers import clean
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.list_cleaning_run import (
    ListCleaningRun,
    ListCleaningSuggestion,
)
from django.conf import settings

from .runners import RunFailed, get_runner

log = logging.getLogger(__name__)

SWITCH_NAME = 'enable_list_cleaning_feedback'
ROW_OFFSET = 2  # FacilityListItem.row_index 0 is spreadsheet row 2


def feature_enabled():
    return switch_is_active(SWITCH_NAME)


def build_payload(facility_list):
    """The state machine input: {list_id, rows: [{row, <columns>...}]}."""
    items = (
        FacilityListItem.objects
        .filter(source=facility_list.source)
        .exclude(status=FacilityListItem.ERROR_PARSING)
        .order_by('row_index')
    )
    rows = []
    for item in items:
        row = {'row': item.row_index + ROW_OFFSET}
        for key, value in (item.raw_json or {}).items():
            row[key] = '' if value is None else str(value)
        rows.append(row)
    return {'list_id': str(facility_list.id), 'rows': rows}


def start_run(facility_list, runner_name=None, force=False):
    """
    Start a run for the list. Returns the run, or None when the feature
    switch is off (and `force` is not set).
    """
    if not force and not feature_enabled():
        return None

    runner_name = runner_name or settings.LIST_CLEANING_RUNNER
    run = ListCleaningRun.objects.create(
        facility_list=facility_list, runner=runner_name)
    payload = build_payload(facility_list)
    if not payload['rows']:
        _fail(run, 'The list has no parsed rows to check.')
        return run

    try:
        get_runner(runner_name).start(run, payload)
    except Exception as e:
        log.exception(
            f'[List Cleaning] Run {run.id} for list {facility_list.id} '
            f'failed to start')
        _fail(run, str(e))
    return run


def refresh_run(run):
    """Poll an asynchronous runner; ingest the result when it is ready."""
    if run.status != ListCleaningRun.RUNNING:
        return run
    try:
        result = get_runner(run.runner).fetch_result(run)
    except RunFailed as e:
        _fail(run, str(e))
        return run
    except Exception as e:
        log.exception(f'[List Cleaning] Could not refresh run {run.id}')
        _fail(run, f'Could not read the pipeline result: {e}')
        return run
    if result is not None:
        ingest_result(run, result)
    return run


def _fail(run, error):
    run.status = ListCleaningRun.FAILED
    run.error = error
    run.completed_at = timezone.now()
    run.save(update_fields=['status', 'error', 'completed_at'])


def _corrected_value(change):
    # list_cleaning_01.md emits {field, value, reason}; Cornell's delivered
    # records use {field, original, corrected, reason}. Read both.
    for key in ('value', 'corrected'):
        if key in change:
            return '' if change[key] is None else str(change[key])
    return ''


def _original_value(item, field, change=None):
    if change and change.get('original') is not None:
        return str(change['original'])
    if item is None or not field:
        return ''
    raw = item.raw_json or {}
    if field in raw and raw[field] is not None:
        return str(raw[field])
    if field == 'country':
        return item.country_code or ''
    return str(getattr(item, field, '') or '')


def _default_decision(field, code):
    if field in ListCleaningSuggestion.PROTECTED_FIELDS:
        return ListCleaningSuggestion.PENDING
    codes = [c.strip() for c in (code or '').split('+') if c.strip()]
    if codes and all(c in ListCleaningSuggestion.SILENT_CORRECTION_CODES
                     for c in codes):
        return ListCleaningSuggestion.ACCEPTED
    return ListCleaningSuggestion.PENDING


@transaction.atomic
def ingest_result(run, result):
    """
    Store the aggregated pipeline output against the run. Replaces any
    suggestions the run already had, so a re-ingest is idempotent.
    """
    now = timezone.now()
    items_by_row = {
        item.row_index + ROW_OFFSET: item
        for item in FacilityListItem.objects.filter(
            source=run.facility_list.source)
    }
    run.suggestions.all().delete()

    suggestions = []
    for record in result.get('records') or []:
        row_number = record.get('row')
        item = items_by_row.get(row_number)
        common = {'run': run, 'facility_list_item': item,
                  'row_number': row_number}

        for change in record.get('changes') or []:
            field = change.get('field', '')
            code = change.get('reason', '')
            decision = _default_decision(field, code)
            suggestions.append(ListCleaningSuggestion(
                kind=ListCleaningSuggestion.CORRECTION,
                field=field,
                code=code,
                original_value=_original_value(item, field, change),
                corrected_value=_corrected_value(change),
                note=change.get('note', '') or '',
                decision=decision,
                decided_at=(now if decision != ListCleaningSuggestion.PENDING
                            else None),
                **common,
            ))

        for issue in record.get('issues') or []:
            field = issue.get('field', '') or ''
            suggestions.append(ListCleaningSuggestion(
                kind=ListCleaningSuggestion.ISSUE,
                field=field,
                code=issue.get('code', ''),
                severity=issue.get('severity', ''),
                original_value=_original_value(item, field),
                note=issue.get('note', '') or '',
                **common,
            ))

        if record.get('status') == 'removed':
            reason = record.get('removed_reason', '') or ''
            duplicate_of = record.get('duplicate_of')
            if reason == 'duplicate' and duplicate_of:
                note = (f'This row repeats row {duplicate_of}, so it would '
                        'be removed.')
            else:
                note = 'This row is blank, so it would be removed.'
            suggestions.append(ListCleaningSuggestion(
                kind=ListCleaningSuggestion.REMOVAL,
                field='row',
                code=reason,
                note=note,
                extra={'duplicate_of': duplicate_of},
                **common,
            ))

    ListCleaningSuggestion.objects.bulk_create(suggestions)

    run.file_pass = result.get('file_pass') or {}
    run.usage = result.get('usage') or {}
    run.prompt_version = str(result.get('prompt_version') or '')
    run.status = ListCleaningRun.COMPLETE
    run.error = ''
    run.completed_at = now
    run.save()
    log.info(
        f'[List Cleaning] Run {run.id} complete: {len(suggestions)} '
        f'suggestions for list {run.facility_list_id}')
    return run


class DecisionError(ValueError):
    pass


@transaction.atomic
def record_decisions(run, decisions, user):
    """
    decisions: [{'id': <suggestion id>, 'decision': ACCEPTED|REJECTED|
                 EDITED|PENDING, 'value': <text, EDITED only>}]
    Each entry is one logged decision on one row and one code.
    """
    allowed = {c for c, _ in ListCleaningSuggestion.DECISION_CHOICES}
    by_id = {s.id: s for s in run.suggestions.all()}
    now = timezone.now()
    updated = []
    for entry in decisions:
        try:
            suggestion = by_id[int(entry.get('id'))]
        except (KeyError, TypeError, ValueError):
            raise DecisionError(
                f'Suggestion {entry.get("id")!r} is not part of this run.')
        decision = entry.get('decision')
        if decision not in allowed:
            raise DecisionError(f'Unknown decision {decision!r}.')
        if suggestion.kind == ListCleaningSuggestion.ISSUE:
            raise DecisionError(
                'Issues are flags, not suggestions; fix the row instead.')
        value = entry.get('value', '')
        if decision == ListCleaningSuggestion.EDITED:
            if value is None or str(value) == '':
                raise DecisionError('An edited decision needs a value.')
            if suggestion.kind != ListCleaningSuggestion.CORRECTION:
                raise DecisionError('Only corrections can be edited.')
        suggestion.decision = decision
        suggestion.decided_value = (
            str(value) if decision == ListCleaningSuggestion.EDITED else '')
        suggestion.decided_by = user
        suggestion.decided_at = now
        suggestion.save(update_fields=[
            'decision', 'decided_value', 'decided_by', 'decided_at'])
        updated.append(suggestion)
    return updated


def _write_field(item, field, value):
    raw = dict(item.raw_json or {})
    raw[field] = value
    item.raw_json = raw
    if field == 'country' and len(value) == 2:
        item.country_code = value.upper()
    elif field == 'name':
        item.name = value[:200]
        item.clean_name = clean(value)[:200]
    elif field == 'address':
        item.address = value[:200]
        item.clean_address = clean(value)[:200]
    elif field == 'sector_product_type' and not value:
        pass


@transaction.atomic
def apply_run(run):
    """
    Write every accepted or edited correction onto its list item, undo any
    previously applied correction that has since been rejected, and act on
    accepted removals. Items keep raw_data (the original CSV line) and the
    list keeps its uploaded file, so the original upload stays recoverable.

    Extended fields (sector, number of workers, parent company ...) were
    created at parse time from the original values; re-deriving them from
    the corrected raw_json is a TODO for the full implementation.
    """
    # One instance per item: several suggestions touch the same row, and
    # saving a second stale instance would overwrite the first's changes.
    items = {
        item.id: item
        for item in FacilityListItem.objects.filter(
            source=run.facility_list.source)
    }
    touched = set()
    applied = 0
    reverted = 0
    now = str(timezone.now())

    for s in run.suggestions.all():
        item = items.get(s.facility_list_item_id)
        if item is None:
            continue
        accepted = s.decision in (ListCleaningSuggestion.ACCEPTED,
                                  ListCleaningSuggestion.EDITED)

        if s.kind == ListCleaningSuggestion.CORRECTION:
            if accepted and not s.applied:
                _write_field(item, s.field, s.final_value)
                s.applied = True
                applied += 1
            elif accepted and s.applied and (
                    s.decision == ListCleaningSuggestion.EDITED):
                _write_field(item, s.field, s.final_value)
                applied += 1
            elif not accepted and s.applied:
                _write_field(item, s.field, s.original_value)
                s.applied = False
                reverted += 1
            else:
                continue
        elif s.kind == ListCleaningSuggestion.REMOVAL:
            if accepted and not s.applied:
                item.status = (FacilityListItem.DUPLICATE
                               if s.code == 'duplicate'
                               else FacilityListItem.ITEM_REMOVED)
                s.applied = True
                applied += 1
            elif not accepted and s.applied:
                item.status = FacilityListItem.PARSED
                s.applied = False
                reverted += 1
            else:
                continue
        else:
            continue

        # Same shape as the other processing_results entries: the item
        # serializer reads `error` from every entry.
        item.processing_results.append({
            'action': 'list_cleaning',
            'error': False,
            'started_at': now,
            'finished_at': now,
            'run_id': run.id,
            'suggestion_id': s.id,
            'code': s.code,
            'decision': s.decision,
            'applied': s.applied,
        })
        touched.add(item.id)
        s.save(update_fields=['applied'])

    for item_id in touched:
        items[item_id].save()

    run.applied_at = timezone.now()
    run.save(update_fields=['applied_at'])
    return {'applied': applied, 'reverted': reverted}
