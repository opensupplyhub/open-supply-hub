/*
 * A small list-cleaning payload in the shape GET /cleaning/ returns:
 * one suggested fix, one automatic fix, one flagged row, one automatic
 * removal and one advisory note, on a six-row list.
 */
const suggestion = (id, rowNumber, overrides) => ({
    id,
    row_number: rowNumber,
    facility_list_item: 100 + rowNumber,
    kind: 'CORRECTION',
    field: '',
    code: '',
    severity: '',
    original_value: '',
    corrected_value: '',
    note: '',
    extra: {},
    decision: 'PENDING',
    decided_value: '',
    decided_at: null,
    applied: false,
    ...overrides,
});

export const SUGGESTIONS = {
    workers: suggestion(1, 2, {
        field: 'number_of_workers',
        code: 'workers_format',
        original_value: '1,200',
        corrected_value: '1200',
        note: 'Formatted as a number.',
    }),
    country: suggestion(2, 2, {
        field: 'country',
        code: 'country_code',
        original_value: 'Viet Nam',
        corrected_value: 'VN',
        decision: 'ACCEPTED',
        extra: { auto: true },
    }),
    poBox: suggestion(3, 3, {
        kind: 'ISSUE',
        field: 'address',
        code: 'address_po_box',
        severity: 'must_fix',
        original_value: 'PO Box 41, Dhaka',
        note: 'The address has no street.',
    }),
    duplicate: suggestion(4, 4, {
        kind: 'REMOVAL',
        field: 'row',
        code: 'duplicate',
        decision: 'ACCEPTED',
        note: 'This row repeats row 2, so it was removed.',
        extra: { auto: true, duplicate_of: 2 },
    }),
    repeated: suggestion(5, 5, {
        kind: 'ISSUE',
        field: 'name',
        code: 'repeated_names',
        severity: 'advisory',
        original_value: 'Same Name Ltd',
        note: 'The same name appears on rows 6 with a different address.',
    }),
};

const group = (s, count, overrides) => ({
    key: `${s.kind}:${s.code}:${s.field}`,
    kind: s.kind,
    code: s.code,
    field: s.field,
    severity: s.severity,
    count,
    pending: s.decision === 'PENDING' ? count : 0,
    accepted: s.decision === 'ACCEPTED' ? count : 0,
    rejected: 0,
    edited: 0,
    removed: 0,
    by_row: 0,
    applied: 0,
    auto: !!s.extra.auto,
    rows: [s.row_number],
    examples: [
        {
            row_number: s.row_number,
            original_value: s.original_value,
            corrected_value: s.corrected_value,
            note: s.note,
        },
    ],
    ...overrides,
});

export const GROUPS = [
    group(SUGGESTIONS.poBox, 1),
    group(SUGGESTIONS.duplicate, 1),
    group(SUGGESTIONS.workers, 1),
    group(SUGGESTIONS.country, 1),
    group(SUGGESTIONS.repeated, 1),
];

const row = (rowNumber, name, address, suggestions) => ({
    row_number: rowNumber,
    item_id: 100 + rowNumber,
    name,
    address,
    country_code: 'VN',
    item_status: 'PARSED',
    suggestions,
});

export const ROWS = [
    row(2, 'Thanh Cong Textile', '36 Tay Thanh Street', [
        SUGGESTIONS.workers,
        SUGGESTIONS.country,
    ]),
    row(3, 'ABC Garments', 'PO Box 41, Dhaka', [SUGGESTIONS.poBox]),
    row(4, 'Thanh Cong Textile', '36 Tay Thanh Street', [
        SUGGESTIONS.duplicate,
    ]),
    row(5, 'Same Name Ltd', 'Industrial Zone 1', [SUGGESTIONS.repeated]),
];

export const SUMMARY = Object.freeze({
    rows_total: 6,
    rows_to_review: 3,
    rows_pending_review: 3,
    rows_blocking_pending: 1,
    rows_flagged_unresolved: 1,
    rows_recommended_pending: 2,
    rows_must_fix_pending: 1,
    rows_must_fix: 1,
    rows_with_corrections: 1,
    corrections_total: 2,
    corrections_pending: 1,
    corrections_accepted: 1,
    corrections_rejected: 0,
    corrections_unapplied: 1,
    must_fix_total: 1,
    must_fix_pending: 1,
    must_fix_resolved: 0,
    removals: 1,
    rows_removed: 0,
    auto_fixes: 2,
    fixes_to_review_total: 1,
    fixes_to_review_decided: 0,
    auto_rows: 2,
    changes_unapplied: 2,
    changes_applied: 0,
    internal_notes: 0,
    list_findings: 0,
});

export const RUN = Object.freeze({
    id: 7,
    status: 'COMPLETE',
    runner: 'stub',
    prompt_version: 'stub',
    file_pass: {},
    usage: {},
    error: '',
    created_at: '2026-11-09T10:00:00Z',
    started_at: '2026-11-09T10:00:00Z',
    completed_at: '2026-11-09T10:00:05Z',
    applied_at: null,
    review_until: '2026-11-09T11:00:00Z',
    submitted_at: null,
    closed_at: null,
    closed_reason: '',
});

export const reviewData = (overrides = {}) => ({
    run: { ...RUN, ...(overrides.run || {}) },
    window_open: true,
    seconds_left: 1800,
    server_time: '2026-11-09T10:30:00Z',
    summary: { ...SUMMARY, ...(overrides.summary || {}) },
    groups: GROUPS,
    rows: ROWS,
    ...Object.fromEntries(
        Object.entries(overrides).filter(
            ([key]) => !['run', 'summary'].includes(key),
        ),
    ),
});

export const cleaningState = (data, extra = {}) => ({
    facilityListCleaning: {
        data,
        fetching: false,
        error: null,
        submitting: false,
        submitError: null,
        applying: false,
        applyError: null,
        lastApplied: null,
        ...extra,
    },
});
