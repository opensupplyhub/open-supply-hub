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
submit_run     -> the one submission (v3): apply every accepted
                  correction, edit and removal onto the PENDING list's
                  items and close the run. Nothing touches the list
                  before this, not even the automatic fixes.
sweep_run      -> close a run whose review window has lapsed; the list
                  then goes through exactly as uploaded.
record_event   -> one row per moment that matters on the review screen
                  (opened, resumed, left, submitted, lapsed), for the
                  "submit versus click away" numbers in metrics_summary.
build_fixed_csv -> the list as it now stands, removed rows last with a
                  tag saying why.
"""
import csv
import io
import logging
import statistics
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from waffle import switch_is_active

from api.extended_fields import (
    create_extendedfields_for_single_item,
    update_extendedfields_for_list_item,
)
from api.helpers.helpers import clean
from api.models.extended_field import ExtendedField
from api.models.facility.facility import Facility
from api.models.facility.facility_list_item import FacilityListItem
from api.models.facility.list_cleaning_run import (
    ListCleaningEvent,
    ListCleaningRun,
    ListCleaningSuggestion,
)
from django.conf import settings

from api.os_id_lookup import OSIDLookup
from api.sector_cache import SectorCache
from contricleaner.lib.contri_cleaner import ContriCleaner

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


def review_deadline(now=None):
    """When a run created now stops accepting the contributor's changes."""
    return (now or timezone.now()) + timedelta(
        minutes=settings.LIST_CLEANING_REVIEW_MINUTES)


def _lock(run):
    """
    Take the run's row lock and reload it, so concurrent requests on the
    same run (two tabs submitting, two polls ingesting the same result)
    queue here and see what the first one did. Callers run inside a
    transaction.
    """
    list(ListCleaningRun.objects.select_for_update().filter(pk=run.pk))
    run.refresh_from_db()


def start_run(facility_list, runner_name=None, force=False):
    """
    Start a run for the list. Returns the run, or None when the feature
    switch is off (and `force` is not set).
    """
    if not force and not feature_enabled():
        return None

    runner_name = runner_name or settings.LIST_CLEANING_RUNNER
    run = ListCleaningRun.objects.create(
        facility_list=facility_list,
        runner=runner_name,
        review_until=review_deadline())
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
    suggestions the run already had, so a re-ingest is idempotent, but
    never a run that has already completed: two polls can fetch the same
    result, and the second must not wipe decisions made since the first.
    """
    _lock(run)
    if run.status not in (ListCleaningRun.PENDING, ListCleaningRun.RUNNING):
        log.info(f'[List Cleaning] Run {run.id} is {run.status}; '
                 'ignoring a repeated result')
        return run
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

    # v3: nothing goes onto the list until the contributor submits, the
    # automatic fixes included. They are pre-accepted, so a submission
    # that touches nothing else still carries them; a lapsed window
    # sends the list exactly as uploaded.
    auto = len([s for s in suggestions if (s.extra or {}).get('auto')])
    log.info(
        f'[List Cleaning] Run {run.id} complete: {len(suggestions)} '
        f'suggestions ({auto} pre-accepted) for list '
        f'{run.facility_list_id}; review open until {run.review_until}')
    return run


# ---- the review window ------------------------------------------------

def window_open(run):
    return (run.closed_at is None and run.review_until is not None
            and timezone.now() < run.review_until)


def seconds_left(run):
    if not window_open(run):
        return 0
    return max(0, int((run.review_until - timezone.now()).total_seconds()))


def record_event(run, kind, user=None, meta=None):
    return ListCleaningEvent.objects.create(
        run=run, kind=kind, user=user, meta=meta or {})


def _close(run, reason, now):
    run.closed_at = now
    run.closed_reason = reason
    run.save(update_fields=['closed_at', 'closed_reason'])


def sweep_run(run):
    """Close the run if its window has lapsed. Safe to call any time."""
    if run is None or run.closed_at is not None or run.review_until is None:
        return run
    now = timezone.now()
    if now < run.review_until:
        return run
    _close(run, ListCleaningRun.LAPSED, now)
    record_event(run, ListCleaningEvent.LAPSED, meta={
        'opened': run.events.filter(
            kind__in=(ListCleaningEvent.OPENED,
                      ListCleaningEvent.RESUMED)).exists(),
    })
    log.info(f'[List Cleaning] Run {run.id} lapsed; list '
             f'{run.facility_list_id} goes through as uploaded')
    return run


def sweep_lapsed():
    """Close every run whose window has passed (for a scheduler)."""
    closed = 0
    for run in ListCleaningRun.objects.filter(
            closed_at__isnull=True, review_until__lt=timezone.now()):
        sweep_run(run)
        closed += 1
    return closed


def _ensure_open(run):
    _lock(run)
    sweep_run(run)
    if run.closed_at is not None:
        if run.closed_reason == ListCleaningRun.SUBMITTED:
            raise DecisionError(
                'This list has already been submitted; no further '
                'changes are possible.')
        raise DecisionError(
            'The review window for this list has closed; it went '
            'through as uploaded.')
    if run.review_until is None:
        raise DecisionError('This run has no review window.')


@transaction.atomic
def submit_run(run, user, as_uploaded=False):
    """
    The contributor's one submission. Applies every accepted or edited
    suggestion (automatic fixes included) unless `as_uploaded`, then
    closes the run so nothing on the list changes again.
    """
    _ensure_open(run)
    now = timezone.now()
    if as_uploaded:
        counts = {'applied': 0, 'reverted': 0}
    else:
        counts = apply_run(run)
    run.submitted_at = now
    run.save(update_fields=['submitted_at'])
    _close(run, ListCleaningRun.SUBMITTED, now)
    record_event(run, ListCleaningEvent.SUBMITTED, user=user, meta={
        'as_uploaded': as_uploaded,
        'applied': counts['applied'],
        'rows_removed': run.facility_list.source.facilitylistitem_set
        .filter(status__in=REMOVED_STATUSES).count(),
        'seconds_after_upload': int(
            (now - run.created_at).total_seconds()),
        **change_breakdown(run, as_uploaded),
    })
    log.info(f'[List Cleaning] Run {run.id} submitted '
             f'({"as uploaded" if as_uploaded else counts})')
    return counts


def change_breakdown(run, as_uploaded=False):
    """
    How much the contributor changed, split into what went on by itself
    (the pre-accepted automatic fixes) and what took a person: fixes
    they accepted, values they typed, rows they removed, and the flags
    they resolved or left. Everything is zero for a submission as
    uploaded, since nothing went on.
    """
    S = ListCleaningSuggestion
    suggestions = list(run.suggestions.exclude(severity=S.INTERNAL_NOTE))
    auto = [s for s in suggestions if (s.extra or {}).get('auto')]
    fixes = [s for s in suggestions
             if s.kind == S.CORRECTION and not (s.extra or {}).get('auto')]
    flags = [s for s in suggestions if s.severity == S.MUST_FIX]
    removed_rows = {s.row_number for s in suggestions
                    if s.decision == S.REMOVED}
    flags_resolved = [
        s for s in flags
        if s.decision == S.EDITED or s.row_number in removed_rows]
    out = {
        'auto_offered': len(auto),
        'auto_turned_off': len(
            [s for s in auto if s.decision == S.REJECTED]),
        'fixes_offered': len(fixes),
        'fixes_accepted': len(
            [s for s in fixes if s.decision == S.ACCEPTED]),
        'fixes_kept_original': len(
            [s for s in fixes if s.decision == S.REJECTED]),
        'values_typed': len(
            [s for s in suggestions if s.decision == S.EDITED]),
        'rows_removed_by_review': len(removed_rows),
        'flags_offered': len(flags),
        'flags_resolved': len(flags_resolved),
        'flags_left_as_uploaded': len(flags) - len(flags_resolved),
        'row_decisions': len(
            [s for s in suggestions if (s.extra or {}).get('by_row')
             and s.decision != S.PENDING]),
    }
    if as_uploaded:
        out['auto_applied'] = 0
        out['reviewed_changes'] = 0
    else:
        out['auto_applied'] = len(
            [s for s in auto if s.decision == S.ACCEPTED])
        # changes that took a person: accepted fixes, typed values and
        # rows removed, counted once each
        out['reviewed_changes'] = (
            out['fixes_accepted'] + out['values_typed']
            + out['rows_removed_by_review'])
    return out


BREAKDOWN_TOTALS = (
    'auto_offered', 'auto_applied', 'auto_turned_off',
    'fixes_offered', 'fixes_accepted', 'fixes_kept_original',
    'values_typed', 'rows_removed_by_review',
    'flags_offered', 'flags_resolved', 'flags_left_as_uploaded',
    'reviewed_changes',
)


def metrics_summary():
    """
    Submit versus click away, across every closed run. Counts runs, not
    events: a contributor who opens, leaves, resumes and submits is one
    "submitted" run that was also "left once".
    """
    E = ListCleaningEvent
    runs = ListCleaningRun.objects.filter(
        status=ListCleaningRun.COMPLETE).prefetch_related('events')
    out = {
        'runs_complete': 0,
        'runs_open': 0,
        'review_opened': 0,
        'submitted_with_changes': 0,
        'submitted_as_uploaded': 0,
        'lapsed_after_opening': 0,
        'lapsed_never_opened': 0,
        'left_at_least_once': 0,
        'resumed_at_least_once': 0,
        'median_minutes_to_submit': None,
        'median_changes_applied': None,
        'median_auto_applied': None,
        'median_reviewed_changes': None,
        'totals': dict.fromkeys(BREAKDOWN_TOTALS, 0),
    }
    minutes, applied, auto_applied, reviewed = [], [], [], []
    for run in runs:
        out['runs_complete'] += 1
        kinds = [e.kind for e in run.events.all()]
        opened = E.OPENED in kinds or E.RESUMED in kinds
        if opened:
            out['review_opened'] += 1
        if E.LEFT in kinds:
            out['left_at_least_once'] += 1
        if E.RESUMED in kinds:
            out['resumed_at_least_once'] += 1
        if run.closed_at is None:
            out['runs_open'] += 1
            continue
        if run.closed_reason == ListCleaningRun.LAPSED:
            key = ('lapsed_after_opening' if opened
                   else 'lapsed_never_opened')
            out[key] += 1
            continue
        submitted = next(
            (e for e in run.events.all() if e.kind == E.SUBMITTED), None)
        meta = submitted.meta if submitted else {}
        if meta.get('as_uploaded'):
            out['submitted_as_uploaded'] += 1
        else:
            out['submitted_with_changes'] += 1
            applied.append(meta.get('applied', 0))
            auto_applied.append(meta.get('auto_applied', 0))
            reviewed.append(meta.get('reviewed_changes', 0))
        for key in BREAKDOWN_TOTALS:
            out['totals'][key] += meta.get(key, 0)
        if 'seconds_after_upload' in meta:
            minutes.append(meta['seconds_after_upload'] / 60)
    if minutes:
        out['median_minutes_to_submit'] = round(statistics.median(minutes), 1)
    if applied:
        out['median_changes_applied'] = statistics.median(applied)
        out['median_auto_applied'] = statistics.median(auto_applied)
        out['median_reviewed_changes'] = statistics.median(reviewed)
    decided = (out['submitted_with_changes'] + out['submitted_as_uploaded']
               + out['lapsed_after_opening'] + out['lapsed_never_opened'])
    out['submit_rate'] = (
        round((out['submitted_with_changes']
               + out['submitted_as_uploaded']) / decided, 3)
        if decided else None)
    return out


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
    _ensure_open(run)
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
    _ensure_open(run)
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
    # Every other field lives only in raw_json until the item is
    # re-parsed.


REMOVED_STATUSES = (FacilityListItem.DUPLICATE,
                    FacilityListItem.ITEM_REMOVED)


def _rederive_items(items):
    """
    Bring what parse derived from the uploaded row into line with the
    corrected one: sector, the cleaned name and address, and the
    ExtendedField rows (worker count, parent company, product, facility
    and processing types, ids) the facility page reads. A row that is
    now removed loses its extended fields; a row that is back gets them
    again. Rows already matched keep their facility link, and the
    facility is touched so the search index picks the change up.
    """
    sector_cache = SectorCache()
    os_id_lookup = OSIDLookup()
    now = timezone.now()
    for item in items:
        if item.status in REMOVED_STATUSES:
            ExtendedField.objects.filter(facility_list_item=item).delete()
        else:
            _rederive_item(item, sector_cache, os_id_lookup)
        if item.facility_id:
            Facility.objects.filter(pk=item.facility_id).update(
                updated_at=now)


def _rederive_item(item, sector_cache, os_id_lookup):
    processed = ContriCleaner(
        dict(item.raw_json or {}), sector_cache, os_id_lookup
    ).process_data()
    row = processed.rows[0] if processed.rows else None
    if processed.errors or row is None or row.errors:
        # The corrected row no longer parses; keep what parse derived
        # rather than leave the item with nothing. The moderator sees
        # the corrected raw values either way.
        log.warning(
            f'[List Cleaning] Item {item.id} could not be re-parsed after '
            f'apply: {processed.errors or (row and row.errors)}')
        return
    item.sector = row.sector
    item.clean_name = row.clean_name
    item.clean_address = row.clean_address
    item.save(update_fields=['sector', 'clean_name', 'clean_address'])
    ExtendedField.objects.filter(facility_list_item=item).delete()
    create_extendedfields_for_single_item(item, row.fields)
    if item.facility_id:
        update_extendedfields_for_list_item(item)


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
    created at parse time from the uploaded values, so every touched row
    is re-derived from its corrected raw_json afterwards (see
    `_rederive_item`); a removed row loses them.
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
    if touched:
        _rederive_items([items[item_id] for item_id in touched])

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
