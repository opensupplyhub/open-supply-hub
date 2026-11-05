"""
Contributor-facing list-cleaning feedback (OSDEV-3726).

start_run      -> create a ListCleaningRun and hand it to the configured
                  runner (Step Functions in deployed environments, local
                  stub rules in development). No-op unless the
                  `enable_list_cleaning_feedback` switch is on.
refresh_run    -> poll an asynchronous runner and ingest its result.
ingest_result  -> turn the pipeline's aggregated {file_pass, records, usage}
                  into ListCleaningSuggestion rows.
record_decisions -> log a contributor's accept / reject / edit / remove
                  per suggestion, or per error type across the list.
apply_run      -> write accepted corrections and edits onto the PENDING
                  list's items in place, and drop rows the contributor
                  removed. The uploaded file and each suggestion's
                  original_value keep the original.
build_fixed_csv -> the list as it now stands, removed rows last with a
                  tag saying why.
"""
import csv
import io
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
            auto = decision == ListCleaningSuggestion.ACCEPTED
            suggestions.append(ListCleaningSuggestion(
                kind=ListCleaningSuggestion.CORRECTION,
                field=field,
                code=code,
                original_value=_original_value(item, field, change),
                corrected_value=_corrected_value(change),
                note=change.get('note', '') or '',
                decision=decision,
                decided_at=now if auto else None,
                extra={'auto': True} if auto else {},
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
            # Exact duplicates and blank rows are removed automatically:
            # the parser already drops exact duplicates before the
            # pipeline runs, and neither needs judgment. The contributor
            # can still put a row back.
            if reason == 'duplicate' and duplicate_of:
                note = (f'This row repeats row {duplicate_of}, so it was '
                        'removed.')
            else:
                note = 'This row is blank, so it was removed.'
            suggestions.append(ListCleaningSuggestion(
                kind=ListCleaningSuggestion.REMOVAL,
                field='row',
                code=reason,
                note=note,
                decision=ListCleaningSuggestion.ACCEPTED,
                decided_at=now,
                extra={'duplicate_of': duplicate_of, 'auto': True},
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

    # Silent formatting fixes and automatic removals go onto the list
    # straight away, so a contributor who does nothing still gets them.
    auto_ids = {
        s.id for s in run.suggestions.all() if (s.extra or {}).get('auto')}
    if auto_ids:
        apply_run(run, only=auto_ids)

    log.info(
        f'[List Cleaning] Run {run.id} complete: {len(suggestions)} '
        f'suggestions ({len(auto_ids)} applied automatically) for list '
        f'{run.facility_list_id}')
    return run


class DecisionError(ValueError):
    pass


def _apply_decision(suggestion, decision, value, user, now, by_row):
    """
    Validate one decision against one suggestion and set it. `by_row`
    records whether the contributor decided this row on its own; group
    actions leave such rows alone, so fixing two rows and then removing
    "the rest" of that error type does what it says.
    """
    S = ListCleaningSuggestion
    if suggestion.kind == S.ISSUE:
        # A flagged row can be fixed in place (EDITED), dropped (REMOVED)
        # or left as it is (REJECTED). It cannot be "accepted": there is
        # no suggested value to accept.
        if decision == S.ACCEPTED:
            raise DecisionError(
                'A flagged row has no suggested value to accept; edit it, '
                'remove it or leave it as it is.')
        if suggestion.severity == S.INTERNAL_NOTE:
            raise DecisionError('Moderator notes cannot be decided.')
    if decision == S.EDITED:
        if value is None or str(value) == '':
            raise DecisionError('An edited decision needs a value.')
        if suggestion.kind == S.REMOVAL:
            raise DecisionError('A removal cannot be edited.')
        if suggestion.field in ('', 'row'):
            raise DecisionError('This flag is not tied to a single field.')
    if decision == S.REMOVED and suggestion.kind == S.REMOVAL:
        decision = S.ACCEPTED  # same meaning; keep one spelling
    suggestion.decision = decision
    suggestion.decided_value = str(value) if decision == S.EDITED else ''
    suggestion.decided_by = user
    suggestion.decided_at = now
    extra = dict(suggestion.extra or {})
    extra['by_row'] = by_row
    suggestion.extra = extra
    suggestion.save(update_fields=[
        'decision', 'decided_value', 'decided_by', 'decided_at', 'extra'])
    return suggestion


@transaction.atomic
def record_decisions(run, decisions, user):
    """
    decisions: [{'id': <suggestion id>, 'decision': ACCEPTED|REJECTED|
                 EDITED|REMOVED|PENDING, 'value': <text, EDITED only>}]
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
        updated.append(_apply_decision(
            suggestion, decision, entry.get('value', ''), user, now,
            by_row=True))
    return updated


def group_key(suggestion):
    return f'{suggestion.kind}:{suggestion.code}:{suggestion.field}'


@transaction.atomic
def record_group_decisions(run, groups, user):
    """
    groups: [{'key': '<kind>:<code>:<field>', 'decision': ACCEPTED|
              REJECTED|REMOVED|PENDING}
             or {'key': ..., 'reset': True}]
    One decision for every suggestion of that error type, so a contributor
    with thousands of rows can act on a pattern instead of a row. Each
    affected suggestion still gets its own logged decision. Rows the
    contributor already decided one by one keep that decision; a `reset`
    entry puts those rows back to undecided (or back to the automatic
    fix, for an auto-applied type) so the group buttons cover them again.
    """
    allowed = {c for c, _ in ListCleaningSuggestion.DECISION_CHOICES}
    allowed.discard(ListCleaningSuggestion.EDITED)  # values differ per row
    by_key = {}
    for s in run.suggestions.all():
        by_key.setdefault(group_key(s), []).append(s)
    now = timezone.now()
    updated = []
    for entry in groups:
        key = entry.get('key')
        if key not in by_key:
            raise DecisionError(f'Group {key!r} is not part of this run.')
        if entry.get('reset'):
            S = ListCleaningSuggestion
            for suggestion in by_key[key]:
                extra = suggestion.extra or {}
                if not extra.get('by_row'):
                    continue
                back_to = S.ACCEPTED if extra.get('auto') else S.PENDING
                updated.append(_apply_decision(
                    suggestion, back_to, '', user, now, by_row=False))
            continue
        decision = entry.get('decision')
        if decision not in allowed:
            raise DecisionError(
                f'Decision {decision!r} cannot be made for a whole group.')
        for suggestion in by_key[key]:
            if (suggestion.extra or {}).get('by_row'):
                continue
            updated.append(_apply_decision(
                suggestion, decision, '', user, now, by_row=False))
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


REMOVED_STATUSES = (FacilityListItem.DUPLICATE,
                    FacilityListItem.ITEM_REMOVED)


def _wants_removal(s):
    S = ListCleaningSuggestion
    return s.decision == S.REMOVED or (
        s.kind == S.REMOVAL and s.decision == S.ACCEPTED)


def _removal_reason(suggestions):
    """Plain-language reason a row was dropped, for the CSV tag."""
    for s in suggestions:
        if not _wants_removal(s):
            continue
        if s.kind == ListCleaningSuggestion.REMOVAL:
            dup = (s.extra or {}).get('duplicate_of')
            if s.code == 'duplicate' and dup:
                return f'duplicate of row {dup}'
            return s.code.replace('_', ' ')
        field = s.field.replace('_', ' ') if s.field else 'row'
        return f'{s.code.replace("_", " ")} in {field}'
    # The parser drops exact duplicates before the pipeline runs, so a row
    # can be gone without any accepted suggestion; still say why.
    for s in suggestions:
        if s.kind == ListCleaningSuggestion.REMOVAL:
            dup = (s.extra or {}).get('duplicate_of')
            if s.code == 'duplicate' and dup:
                return f'duplicate of row {dup}'
            return s.code.replace('_', ' ')
    return ''


@transaction.atomic
def apply_run(run, only=None):
    """
    Write every accepted or edited correction (and every edited flag) onto
    its list item, undo any previously applied change that has since been
    rejected, and remove or restore rows. Items keep raw_data (the
    original CSV line) and the list keeps its uploaded file, so the
    original upload stays recoverable.

    `only` restricts the pass to those suggestion ids (used for the
    automatic fixes at ingest); the row-removal state of a touched item
    is still worked out from all of that item's suggestions.

    Extended fields (sector, number of workers, parent company ...) were
    created at parse time from the original values; re-deriving them from
    the corrected raw_json is a TODO for the full implementation.
    """
    S = ListCleaningSuggestion
    # One instance per item: several suggestions touch the same row, and
    # saving a second stale instance would overwrite the first's changes.
    items = {
        item.id: item
        for item in FacilityListItem.objects.filter(
            source=run.facility_list.source)
    }
    by_item = {}
    for s in run.suggestions.all():
        if s.facility_list_item_id in items:
            by_item.setdefault(s.facility_list_item_id, []).append(s)
    if only is not None:
        only = set(only)
        by_item = {
            item_id: suggestions
            for item_id, suggestions in by_item.items()
            if any(s.id in only for s in suggestions)
        }

    touched = set()
    applied = 0
    reverted = 0
    now = str(timezone.now())

    def log_entry(item, s, applied_flag):
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
            'applied': applied_flag,
        })
        touched.add(item.id)

    for item_id, suggestions in by_item.items():
        item = items[item_id]

        # 1. Value changes: accepted corrections and edited values.
        for s in suggestions:
            if s.kind == S.REMOVAL or (only is not None and s.id not in only):
                continue
            accepted = s.decision in (S.ACCEPTED, S.EDITED)
            if s.kind == S.ISSUE and s.decision != S.EDITED:
                accepted = False
            if accepted and not s.applied:
                _write_field(item, s.field, s.final_value)
                s.applied = True
                applied += 1
            elif (accepted and s.applied and s.decision == S.EDITED
                  and (item.raw_json or {}).get(s.field) != s.final_value):
                # re-edited after an earlier apply
                _write_field(item, s.field, s.final_value)
                applied += 1
            elif not accepted and s.applied:
                _write_field(item, s.field, s.original_value)
                s.applied = False
                reverted += 1
            else:
                continue
            log_entry(item, s, s.applied)
            s.save(update_fields=['applied'])

        # 2. Row removal, decided per item so several suggestions on one
        #    row cannot fight over its status.
        want = [s for s in suggestions if _wants_removal(s)]
        was = [s for s in suggestions
               if (s.extra or {}).get('removal_applied')]
        if want and not was:
            dup = any(s.kind == S.REMOVAL and s.code == 'duplicate'
                      for s in want)
            item.status = (FacilityListItem.DUPLICATE if dup
                           else FacilityListItem.ITEM_REMOVED)
            for s in want:
                s.extra = {**(s.extra or {}), 'removal_applied': True}
                if s.kind == S.REMOVAL:
                    s.applied = True
                s.save(update_fields=['extra', 'applied'])
                log_entry(item, s, True)
            applied += 1
        elif not want and was:
            item.status = FacilityListItem.PARSED
            for s in was:
                s.extra = {**(s.extra or {}), 'removal_applied': False}
                if s.kind == S.REMOVAL:
                    s.applied = False
                s.save(update_fields=['extra', 'applied'])
                log_entry(item, s, False)
            reverted += 1

    for item_id in touched:
        items[item_id].save()

    if only is None:
        run.applied_at = timezone.now()
        run.save(update_fields=['applied_at'])
    return {'applied': applied, 'reverted': reverted}


REMOVAL_TAG_COLUMN = 'os_hub_cleaning'


UPLOADED_SUFFIX = ' (as uploaded)'


def build_fixed_csv(run):
    """
    The list as it stands after the contributor's changes: the original
    columns in the original order with the current values, each followed
    by the value as it was uploaded, kept rows first in file order, then
    every removed row with a tag saying why it was dropped. Rows the
    parser rejected outright are included untouched with their own tag,
    so nothing from the upload is lost.
    """
    facility_list = run.facility_list
    header = next(csv.reader([facility_list.header or ''])) \
        if facility_list.header else []
    items = list(
        FacilityListItem.objects
        .filter(source=facility_list.source)
        .order_by('row_index'))
    if not header and items:
        header = list((items[0].raw_json or {}).keys())
    by_item = {}
    for s in run.suggestions.all():
        by_item.setdefault(s.facility_list_item_id, []).append(s)

    def cell(item, column):
        raw = item.raw_json or {}
        key = column.strip().lower().replace(' ', '_')
        value = raw.get(column, raw.get(key, ''))
        return '' if value is None else str(value)

    def uploaded(item):
        # raw_data is the row exactly as it came in, in header order.
        values = next(csv.reader([item.raw_data or '']), [])
        return (values + [''] * len(header))[:len(header)]

    def paired(current, original):
        row = []
        for now, then in zip(current, original):
            row += [now, then]
        return row

    kept, dropped = [], []
    for item in items:
        original = uploaded(item)
        if item.status == FacilityListItem.ERROR_PARSING:
            dropped.append(paired(original, original)
                           + ['not read: fix the row and re-upload'])
            continue
        values = paired([cell(item, column) for column in header], original)
        if item.status in REMOVED_STATUSES:
            reason = _removal_reason(by_item.get(item.id, []))
            if not reason and item.status == FacilityListItem.DUPLICATE:
                reason = 'duplicate row'
            dropped.append(values + [f'removed: {reason or "removed"}'])
        else:
            kept.append(values + [''])

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(
        [h for column in header for h in (column, column + UPLOADED_SUFFIX)]
        + [REMOVAL_TAG_COLUMN])
    writer.writerows(kept)
    writer.writerows(dropped)
    return out.getvalue()
