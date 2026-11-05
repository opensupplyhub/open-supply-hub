import React, { useState } from 'react';
import { arrayOf, bool, func, number, object, string } from 'prop-types';
import Button from '@material-ui/core/Button';
import Checkbox from '@material-ui/core/Checkbox';
import Chip from '@material-ui/core/Chip';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';

import COLOURS from '../util/COLOURS';
import { makeFacilityListCleaningDownloadURL } from '../util/util';

export const RUN_STATUS = Object.freeze({
    PENDING: 'PENDING',
    RUNNING: 'RUNNING',
    COMPLETE: 'COMPLETE',
    FAILED: 'FAILED',
});

export const KIND = Object.freeze({
    CORRECTION: 'CORRECTION',
    ISSUE: 'ISSUE',
    REMOVAL: 'REMOVAL',
});

export const DECISION = Object.freeze({
    PENDING: 'PENDING',
    ACCEPTED: 'ACCEPTED',
    REJECTED: 'REJECTED',
    EDITED: 'EDITED',
    REMOVED: 'REMOVED',
});

// Not a decision: a group action that clears the row-by-row decisions
// of that type so the ordinary group buttons cover every row again.
export const RESET = 'RESET';

export const SEVERITY = Object.freeze({
    MUST_FIX: 'must_fix',
    INTERNAL_NOTE: 'internal_note',
});

export const FIELD_LABELS = Object.freeze({
    country: 'Country',
    name: 'Name',
    address: 'Address',
    sector_product_type: 'Sector / product type',
    facility_type_processing_type: 'Facility type / processing type',
    number_of_workers: 'Number of workers',
    parent_company: 'Parent company',
    row: 'Row',
});

export const CODE_LABELS = Object.freeze({
    whitespace: 'extra spaces removed',
    quotes: 'stray quotes removed',
    filler_text: 'placeholder text removed',
    encoding: 'encoding fixed',
    country_code: 'country converted to its two-letter code',
    separators: 'separators standardised',
    workers_format: 'worker count formatted as a number',
    casing: 'capitalisation fixed',
    country_in_address: 'country name removed from the end of the address',
    name_in_address: 'facility name removed from the address',
    business_name_in_address: 'other business name removed from the address',
    duplicate: 'duplicate of another row',
    empty: 'blank row',
    pii: 'contains personal information',
    missing_country: 'country is missing',
    unknown_country: 'country not recognised',
    missing_name: 'facility name is missing',
    missing_address: 'address is missing',
    too_long: 'value is too long',
    address_po_box: 'address is a PO Box, not a street address',
    address_too_few: 'address has too little detail',
    name_incomplete: 'name looks incomplete',
    repeated_names: 'same name at several addresses',
    empty_row: 'blank row',
});

// What a contributor can do about each must-fix flag, in their words.
const CODE_HELP = Object.freeze({
    pii:
        'OS Hub does not publish personal names, email addresses or phone numbers. Edit the row to remove the personal details, or remove the row.',
    missing_country:
        'Every facility needs a country. Type the country, or remove the row.',
    unknown_country:
        'We could not match this country. Type the country name or its two-letter code, or remove the row.',
    missing_name:
        'Every facility needs a name. Type the facility name, or remove the row.',
    missing_address:
        'Every facility needs an address. Type the address, or remove the row.',
    too_long:
        'Shorten the value to 200 characters or fewer, or remove the row.',
    address_po_box:
        'A PO Box cannot be placed on the map. Type the street address, or remove the row.',
});

export const codeHelp = code => CODE_HELP[(code || '').split('+')[0]] || '';

export const styles = Object.freeze({
    panel: Object.freeze({
        padding: '20px',
        margin: '0 0.5rem 20px 0.5rem',
    }),
    heading: Object.freeze({
        fontSize: '1.25rem',
        fontWeight: 700,
        marginBottom: '8px',
    }),
    muted: Object.freeze({
        color: 'rgba(0, 0, 0, 0.6)',
    }),
    statRow: Object.freeze({
        display: 'flex',
        flexWrap: 'wrap',
        gap: '12px',
        margin: '16px 0',
    }),
    stat: Object.freeze({
        flex: '1 1 160px',
        padding: '12px 16px',
        borderRadius: '4px',
        background: '#F5F5F5',
    }),
    statNumber: Object.freeze({
        fontSize: '1.6rem',
        fontWeight: 700,
        lineHeight: 1.2,
    }),
    statLabel: Object.freeze({
        fontSize: '0.8rem',
        color: 'rgba(0, 0, 0, 0.6)',
    }),
    disclaimer: Object.freeze({
        padding: '12px 16px',
        margin: '12px 0',
        borderLeft: `4px solid ${COLOURS.NAVY_BLUE}`,
        background: '#F0F4FF',
        fontSize: '0.9rem',
    }),
    rowCard: Object.freeze({
        border: '1px solid #E0E0E0',
        borderRadius: '4px',
        padding: '12px 16px',
        marginBottom: '12px',
    }),
    rowHeader: Object.freeze({
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'baseline',
        gap: '12px',
        marginBottom: '8px',
    }),
    rowCheckbox: Object.freeze({
        padding: '0 4px 0 0',
        margin: '-4px 0 -4px -8px',
        alignSelf: 'center',
    }),
    bulkBar: Object.freeze({
        position: 'sticky',
        top: 0,
        zIndex: 2,
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        gap: '8px',
        padding: '8px 12px',
        margin: '0 0 12px 0',
        background: '#F5F0FF',
        border: '1px solid #CBB4F5',
        borderRadius: '4px',
    }),
    bulkCount: Object.freeze({
        fontWeight: 700,
        marginRight: '4px',
    }),
    selectAll: Object.freeze({
        display: 'flex',
        alignItems: 'center',
        gap: '2px',
        margin: '0 0 4px -8px',
        fontSize: '0.9rem',
        color: 'rgba(0, 0, 0, 0.7)',
    }),
    rowNumber: Object.freeze({
        fontWeight: 700,
        whiteSpace: 'nowrap',
    }),
    rowIdentity: Object.freeze({
        color: 'rgba(0, 0, 0, 0.7)',
        overflowWrap: 'anywhere',
    }),
    suggestion: Object.freeze({
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        gap: '8px 16px',
        padding: '8px 0',
        borderTop: '1px solid #F0F0F0',
    }),
    tag: Object.freeze({
        display: 'inline-block',
        padding: '2px 8px',
        borderRadius: '10px',
        fontSize: '0.75rem',
        fontWeight: 700,
        whiteSpace: 'nowrap',
    }),
    mustFixTag: Object.freeze({
        background: '#FDECEA',
        color: '#B3261E',
    }),
    internalTag: Object.freeze({
        background: '#EEEEEE',
        color: '#424242',
    }),
    correctionTag: Object.freeze({
        background: '#E8F5E9',
        color: '#1B5E20',
    }),
    removalTag: Object.freeze({
        background: '#FFF3E0',
        color: '#E65100',
    }),
    valueBlock: Object.freeze({
        flex: '1 1 260px',
        minWidth: 0,
    }),
    fieldName: Object.freeze({
        fontSize: '0.8rem',
        color: 'rgba(0, 0, 0, 0.6)',
    }),
    original: Object.freeze({
        textDecoration: 'line-through',
        color: 'rgba(0, 0, 0, 0.5)',
        overflowWrap: 'anywhere',
    }),
    corrected: Object.freeze({
        fontWeight: 600,
        overflowWrap: 'anywhere',
    }),
    arrow: Object.freeze({
        margin: '0 8px',
        color: 'rgba(0, 0, 0, 0.4)',
    }),
    decisionBlock: Object.freeze({
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
        marginLeft: 'auto',
    }),
    decisionText: Object.freeze({
        fontSize: '0.85rem',
        fontWeight: 600,
        marginRight: '8px',
    }),
    footer: Object.freeze({
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        gap: '12px',
        marginTop: '16px',
    }),
    error: Object.freeze({
        color: 'red',
    }),
    findingList: Object.freeze({
        margin: '4px 0 12px 0',
        paddingLeft: '20px',
    }),
});

export const describeCode = code =>
    (code || '')
        .split('+')
        .map(part => CODE_LABELS[part] || part.replace(/_/g, ' '))
        .join(', ');

export const fieldLabel = field => FIELD_LABELS[field] || field;

export const Tag = ({ style, children }) => (
    <span style={{ ...styles.tag, ...style }}>{children}</span>
);

Tag.propTypes = { style: object.isRequired, children: string.isRequired };

export const Stat = ({ value, label }) => (
    <div style={styles.stat}>
        <div style={styles.statNumber}>{value}</div>
        <div style={styles.statLabel}>{label}</div>
    </div>
);

Stat.propTypes = { value: number.isRequired, label: string.isRequired };

const plural = (n, word, words = `${word}s`) =>
    `${n} ${n === 1 ? word : words}`;

const trackerStyles = Object.freeze({
    box: Object.freeze({
        margin: '16px 0',
        padding: '16px 20px',
        borderRadius: '6px',
        background: '#F5F0FF',
        border: '1px solid #E2D1F0',
    }),
    headline: Object.freeze({
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'baseline',
        justifyContent: 'space-between',
        gap: '8px',
        marginBottom: '8px',
    }),
    title: Object.freeze({
        fontSize: '1.15rem',
        fontWeight: 700,
    }),
    percent: Object.freeze({
        fontSize: '1.6rem',
        fontWeight: 800,
        lineHeight: 1,
    }),
    track: Object.freeze({
        height: '12px',
        borderRadius: '6px',
        background: '#E2D9F3',
        overflow: 'hidden',
    }),
    fill: Object.freeze({
        height: '100%',
        borderRadius: '6px',
        transition: 'width .5s ease, background .5s ease',
    }),
    milestones: Object.freeze({
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px 24px',
        margin: '12px 0 0 0',
        padding: 0,
        listStyle: 'none',
    }),
    milestone: Object.freeze({
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        fontSize: '0.95rem',
    }),
    badge: Object.freeze({
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        minWidth: '22px',
        height: '22px',
        padding: '0 6px',
        borderRadius: '11px',
        fontSize: '0.75rem',
        fontWeight: 700,
        color: COLOURS.WHITE,
    }),
    hint: Object.freeze({
        marginTop: '8px',
        fontSize: '0.9rem',
        color: 'rgba(0, 0, 0, 0.65)',
    }),
});

const PURPLE = '#8428FA';
const GREEN = COLOURS.MATERIAL_GREEN;

const Milestone = ({ done, total, label, info }) => {
    const complete = !info && done >= total;
    let badge;
    if (info) {
        badge = (
            <span
                style={{
                    ...trackerStyles.badge,
                    background: COLOURS.DARK_GREY,
                }}
            >
                i
            </span>
        );
    } else if (complete) {
        badge = (
            <span style={{ ...trackerStyles.badge, background: GREEN }}>
                &#10003;
            </span>
        );
    } else {
        badge = (
            <span style={{ ...trackerStyles.badge, background: PURPLE }}>
                {done}/{total}
            </span>
        );
    }
    return (
        <li style={trackerStyles.milestone}>
            {badge}
            <span style={complete ? { color: 'rgba(0, 0, 0, 0.6)' } : null}>
                {label}
            </span>
        </li>
    );
};

Milestone.defaultProps = { done: 0, total: 0, info: false };
Milestone.propTypes = {
    done: number,
    total: number,
    label: string.isRequired,
    info: bool,
};

/*
 * One bar instead of four numbers: how far the list is from being ready
 * for the moderator. Automatic fixes count as done from the start, so
 * the bar never opens at zero, and every decision moves it. "Ready"
 * means every suggestion has an answer, not that the list will be
 * approved.
 */
export const ReadinessTracker = ({ summary, applied }) => {
    const auto = summary.auto_fixes || 0;
    const fixesTotal = summary.fixes_to_review_total || 0;
    const fixesDone = summary.fixes_to_review_decided || 0;
    const flagsTotal = summary.must_fix_total || 0;
    const flagsDone = flagsTotal - (summary.must_fix_pending || 0);
    const total = auto + fixesTotal + flagsTotal;
    const done = auto + fixesDone + flagsDone;
    const percent = total ? Math.round((100 * done) / total) : 100;
    const ready = percent === 100;
    const remaining = total - done;

    let title;
    if (ready && summary.changes_unapplied > 0) {
        title = 'Ready for the moderator: press Apply to finish';
    } else if (ready) {
        title = applied
            ? 'Your changes are applied and the list is ready for the moderator'
            : 'Your list is ready for the moderator';
    } else {
        title = `Your list is ${percent}% ready for the moderator`;
    }

    return (
        <div style={trackerStyles.box} data-tour="intro">
            <div style={trackerStyles.headline}>
                <span style={trackerStyles.title}>{title}</span>
                <span
                    style={{
                        ...trackerStyles.percent,
                        color: ready ? GREEN : PURPLE,
                    }}
                >
                    {percent}%
                </span>
            </div>
            <div
                style={trackerStyles.track}
                role="progressbar"
                aria-valuenow={percent}
                aria-valuemin={0}
                aria-valuemax={100}
            >
                <div
                    style={{
                        ...trackerStyles.fill,
                        width: `${percent}%`,
                        background: ready ? GREEN : PURPLE,
                    }}
                />
            </div>
            <ul style={trackerStyles.milestones}>
                <Milestone
                    done={auto}
                    total={auto}
                    label={`${plural(
                        auto,
                        'formatting fix',
                        'formatting fixes',
                    )} made automatically`}
                />
                <Milestone
                    done={fixesDone}
                    total={fixesTotal}
                    label={`${plural(
                        fixesTotal,
                        'suggested fix',
                        'suggested fixes',
                    )} reviewed`}
                />
                <Milestone
                    done={flagsDone}
                    total={flagsTotal}
                    label={`${plural(
                        flagsTotal,
                        'row',
                    )} needing attention resolved`}
                />
                {summary.list_findings > 0 && (
                    <Milestone
                        info
                        label={`${plural(
                            summary.list_findings,
                            'finding',
                        )} about the whole file to read`}
                    />
                )}
            </ul>
            {!ready && (
                <div style={trackerStyles.hint}>
                    {plural(remaining, 'decision')} to go. Every one you make
                    here makes the list more likely to be approved.
                </div>
            )}
        </div>
    );
};

ReadinessTracker.defaultProps = { applied: false };
ReadinessTracker.propTypes = { summary: object.isRequired, applied: bool };

export const Correction = ({ suggestion, canAct, busy, onDecide }) => {
    const [editing, setEditing] = useState(false);
    const [draft, setDraft] = useState(
        suggestion.decided_value || suggestion.corrected_value,
    );
    const finalValue =
        suggestion.decision === DECISION.EDITED
            ? suggestion.decided_value
            : suggestion.corrected_value;

    const decisionLabel = (() => {
        switch (suggestion.decision) {
            case DECISION.ACCEPTED:
                return suggestion.applied ? 'Applied' : 'Accepted';
            case DECISION.EDITED:
                return suggestion.applied ? 'Applied (edited)' : 'Edited';
            case DECISION.REJECTED:
                return 'Kept original';
            case DECISION.REMOVED:
                return 'Row will be removed';
            default:
                return 'Needs your decision';
        }
    })();

    return (
        <div style={styles.suggestion}>
            <Tag style={styles.correctionTag}>Suggested fix</Tag>
            <div style={styles.valueBlock}>
                <div style={styles.fieldName}>
                    {fieldLabel(suggestion.field)}:{' '}
                    {describeCode(suggestion.code)}
                </div>
                {editing ? (
                    <TextField
                        value={draft}
                        onChange={e => setDraft(e.target.value)}
                        fullWidth
                        margin="dense"
                        autoFocus
                    />
                ) : (
                    <div>
                        <span style={styles.original}>
                            {suggestion.original_value || '(blank)'}
                        </span>
                        <span style={styles.arrow}>&rarr;</span>
                        <span style={styles.corrected}>
                            {finalValue || '(blank)'}
                        </span>
                    </div>
                )}
                {suggestion.note && (
                    <div style={styles.muted}>{suggestion.note}</div>
                )}
            </div>
            <div style={styles.decisionBlock}>
                <span style={styles.decisionText}>{decisionLabel}</span>
                {canAct && editing && (
                    <>
                        <Button
                            size="small"
                            color="primary"
                            disabled={busy || !draft}
                            onClick={() => {
                                setEditing(false);
                                onDecide(DECISION.EDITED, draft);
                            }}
                        >
                            Save
                        </Button>
                        <Button
                            size="small"
                            disabled={busy}
                            onClick={() => setEditing(false)}
                        >
                            Cancel
                        </Button>
                    </>
                )}
                {canAct && !editing && (
                    <>
                        {suggestion.decision !== DECISION.ACCEPTED && (
                            <Button
                                size="small"
                                color="primary"
                                disabled={busy}
                                onClick={() => onDecide(DECISION.ACCEPTED)}
                            >
                                Accept
                            </Button>
                        )}
                        {suggestion.decision !== DECISION.REJECTED && (
                            <Button
                                size="small"
                                disabled={busy}
                                onClick={() => onDecide(DECISION.REJECTED)}
                            >
                                Keep original
                            </Button>
                        )}
                        <Button
                            size="small"
                            disabled={busy}
                            onClick={() => setEditing(true)}
                        >
                            Edit
                        </Button>
                    </>
                )}
            </div>
        </div>
    );
};

Correction.propTypes = {
    suggestion: object.isRequired,
    canAct: bool.isRequired,
    busy: bool.isRequired,
    onDecide: func.isRequired,
};

export const Issue = ({ suggestion, canAct, busy, onDecide }) => {
    const internal = suggestion.severity === SEVERITY.INTERNAL_NOTE;
    const [editing, setEditing] = useState(false);
    const [draft, setDraft] = useState(
        suggestion.decided_value || suggestion.original_value || '',
    );
    const editable =
        !internal && suggestion.field && suggestion.field !== 'row';

    const decisionLabel = (() => {
        switch (suggestion.decision) {
            case DECISION.EDITED:
                return suggestion.applied ? 'Fixed' : 'Fixed (not yet applied)';
            case DECISION.REMOVED:
                return 'Row will be removed';
            case DECISION.REJECTED:
                return 'Left as uploaded';
            default:
                return internal ? '' : 'Needs your attention';
        }
    })();

    return (
        <div style={styles.suggestion}>
            <Tag style={internal ? styles.internalTag : styles.mustFixTag}>
                {internal ? 'Moderator note' : 'Needs your attention'}
            </Tag>
            <div style={styles.valueBlock}>
                <div style={styles.fieldName}>
                    {fieldLabel(suggestion.field)}:{' '}
                    {describeCode(suggestion.code)}
                </div>
                {editing ? (
                    <TextField
                        value={draft}
                        onChange={e => setDraft(e.target.value)}
                        fullWidth
                        margin="dense"
                        autoFocus
                    />
                ) : (
                    <div>
                        {suggestion.decision === DECISION.EDITED ? (
                            <>
                                <span style={styles.original}>
                                    {suggestion.original_value || '(blank)'}
                                </span>
                                <span style={styles.arrow}>&rarr;</span>
                                <span style={styles.corrected}>
                                    {suggestion.decided_value}
                                </span>
                            </>
                        ) : (
                            <span>
                                {suggestion.original_value || '(blank)'}
                            </span>
                        )}
                    </div>
                )}
                <div style={styles.muted}>{suggestion.note}</div>
                {!internal && codeHelp(suggestion.code) && (
                    <div style={styles.muted}>{codeHelp(suggestion.code)}</div>
                )}
            </div>
            <div style={styles.decisionBlock}>
                <span style={styles.decisionText}>{decisionLabel}</span>
                {canAct && !internal && editing && (
                    <>
                        <Button
                            size="small"
                            color="primary"
                            disabled={busy || !draft}
                            onClick={() => {
                                setEditing(false);
                                onDecide(DECISION.EDITED, draft);
                            }}
                        >
                            Save
                        </Button>
                        <Button
                            size="small"
                            disabled={busy}
                            onClick={() => setEditing(false)}
                        >
                            Cancel
                        </Button>
                    </>
                )}
                {canAct && !internal && !editing && (
                    <>
                        {editable && (
                            <Button
                                size="small"
                                color="primary"
                                disabled={busy}
                                onClick={() => setEditing(true)}
                            >
                                Fix value
                            </Button>
                        )}
                        {suggestion.decision !== DECISION.REMOVED && (
                            <Button
                                size="small"
                                color="secondary"
                                disabled={busy}
                                onClick={() => onDecide(DECISION.REMOVED)}
                            >
                                Remove row
                            </Button>
                        )}
                        {suggestion.decision !== DECISION.REJECTED &&
                            suggestion.decision !== DECISION.PENDING && (
                                <Button
                                    size="small"
                                    disabled={busy}
                                    onClick={() => onDecide(DECISION.REJECTED)}
                                >
                                    Undo
                                </Button>
                            )}
                    </>
                )}
            </div>
        </div>
    );
};

Issue.defaultProps = { canAct: false, busy: false, onDecide: () => {} };

Issue.propTypes = {
    suggestion: object.isRequired,
    canAct: bool,
    busy: bool,
    onDecide: func,
};

export const Removal = ({ suggestion, canAct, busy, onDecide }) => {
    const decisionLabel = (() => {
        switch (suggestion.decision) {
            case DECISION.ACCEPTED:
                return suggestion.applied ? 'Removed' : 'Will be removed';
            case DECISION.REJECTED:
                return 'Kept';
            case DECISION.REMOVED:
                return 'Will be removed';
            default:
                return 'Needs your decision';
        }
    })();
    return (
        <div style={styles.suggestion}>
            <Tag style={styles.removalTag}>Suggested removal</Tag>
            <div style={styles.valueBlock}>
                <div style={styles.fieldName}>
                    {describeCode(suggestion.code)}
                </div>
                <div>{suggestion.note}</div>
            </div>
            <div style={styles.decisionBlock}>
                <span style={styles.decisionText}>{decisionLabel}</span>
                {canAct && suggestion.decision !== DECISION.ACCEPTED && (
                    <Button
                        size="small"
                        color="primary"
                        disabled={busy}
                        onClick={() => onDecide(DECISION.ACCEPTED)}
                    >
                        Remove row
                    </Button>
                )}
                {canAct && suggestion.decision !== DECISION.REJECTED && (
                    <Button
                        size="small"
                        disabled={busy}
                        onClick={() => onDecide(DECISION.REJECTED)}
                    >
                        Keep row
                    </Button>
                )}
            </div>
        </div>
    );
};

Removal.propTypes = {
    suggestion: object.isRequired,
    canAct: bool.isRequired,
    busy: bool.isRequired,
    onDecide: func.isRequired,
};

const FINDINGS_PREVIEW = 5;

/*
 * Whole-file findings, kept short: exact duplicates are already handled
 * in the automatic tier, so they get one line; repeated names are a note
 * for the moderator more than a task for the contributor, so they get a
 * count with the detail folded unless the list is short.
 */
export const ListFindings = ({ filePass }) => {
    const [open, setOpen] = useState(false);
    const headerIssues = filePass.header_issues || [];
    const duplicates = filePass.exact_duplicates || [];
    const repeated = filePass.repeated_names || [];
    if (!headerIssues.length && !duplicates.length && !repeated.length) {
        return null;
    }
    const fold = repeated.length > FINDINGS_PREVIEW;
    const shown = fold && !open ? [] : repeated;
    return (
        <div>
            <Typography variant="subheading">
                Findings about the whole file
            </Typography>
            <ul style={styles.findingList}>
                {headerIssues.map(issue => (
                    <li key={`header-${issue.column || issue.note}`}>
                        {issue.note || `Header problem: ${issue.column}`}
                    </li>
                ))}
                {duplicates.length > 0 && (
                    <li>
                        {plural(duplicates.length, 'row')}{' '}
                        {duplicates.length === 1 ? 'is' : 'are'} an exact repeat
                        of an earlier row and{' '}
                        {duplicates.length === 1 ? 'was' : 'were'} removed
                        (listed under automatic fixes).
                    </li>
                )}
                {repeated.length > 0 && (
                    <li>
                        {plural(repeated.length, 'name')}{' '}
                        {repeated.length === 1 ? 'appears' : 'appear'} at more
                        than one address. That can be right (several sites of
                        one company); check the ones that are not.
                        {fold && (
                            <Button size="small" onClick={() => setOpen(!open)}>
                                {open ? 'Hide' : 'Show'} the {repeated.length}
                            </Button>
                        )}
                    </li>
                )}
                {shown.map(group => (
                    <li
                        key={`rep-${group.name}-${group.rows.join('-')}`}
                        style={styles.muted}
                    >
                        &ldquo;{group.name}&rdquo; on rows{' '}
                        {group.rows.join(', ')}.
                    </li>
                ))}
            </ul>
        </div>
    );
};

ListFindings.propTypes = { filePass: object.isRequired };

export const suggestionKey = s => `${s.kind}:${s.code}:${s.field}`;

export const isAuto = s => !!(s.extra && s.extra.auto);

export const visibleRows = (rows, filter) =>
    rows
        .map(row =>
            filter
                ? { ...row, suggestions: row.suggestions.filter(filter) }
                : row,
        )
        .filter(row => row.suggestions.length);

export const SuggestionRows = ({
    rows,
    canAct,
    busy,
    decide,
    filter,
    selected,
    onToggle,
}) =>
    visibleRows(rows, filter).map((row, i) => (
        <div
            key={row.row_number}
            style={styles.rowCard}
            data-tour={i === 0 ? 'rows' : undefined}
        >
            <div style={styles.rowHeader}>
                {canAct && onToggle && (
                    <Checkbox
                        checked={selected.has(row.row_number)}
                        onChange={() => onToggle(row.row_number)}
                        disabled={busy}
                        color="primary"
                        style={styles.rowCheckbox}
                        inputProps={{
                            'aria-label': `Select row ${row.row_number}`,
                        }}
                    />
                )}
                <span style={styles.rowNumber}>Row {row.row_number}</span>
                <span style={styles.rowIdentity}>
                    {row.name}
                    {row.address ? ` — ${row.address}` : ''}
                    {row.country_code ? ` (${row.country_code})` : ''}
                </span>
            </div>
            {row.suggestions.map(suggestion => {
                const onDecide = (decision, value) =>
                    decide([{ id: suggestion.id, decision, value }]);
                if (suggestion.kind === KIND.CORRECTION) {
                    return (
                        <Correction
                            key={suggestion.id}
                            suggestion={suggestion}
                            canAct={canAct}
                            busy={busy}
                            onDecide={onDecide}
                        />
                    );
                }
                if (suggestion.kind === KIND.REMOVAL) {
                    return (
                        <Removal
                            key={suggestion.id}
                            suggestion={suggestion}
                            canAct={canAct}
                            busy={busy}
                            onDecide={onDecide}
                        />
                    );
                }
                return (
                    <Issue
                        key={suggestion.id}
                        suggestion={suggestion}
                        canAct={canAct}
                        busy={busy}
                        onDecide={onDecide}
                    />
                );
            })}
        </div>
    ));

SuggestionRows.defaultProps = {
    filter: null,
    selected: new Set(),
    onToggle: null,
};

SuggestionRows.propTypes = {
    rows: arrayOf(object).isRequired,
    canAct: bool.isRequired,
    busy: bool.isRequired,
    decide: func.isRequired,
    filter: func,
    selected: object,
    onToggle: func,
};

const groupTitle = group => {
    if (group.kind === KIND.REMOVAL) {
        return `Rows to remove: ${describeCode(group.code)}`;
    }
    return `${fieldLabel(group.field)}: ${describeCode(group.code)}`;
};

const groupStatus = group => {
    const parts = [];
    if (group.pending) parts.push(`${group.pending} to review`);
    if (group.accepted) {
        parts.push(
            group.kind === KIND.REMOVAL
                ? `${group.accepted} to remove`
                : `${group.accepted} accepted`,
        );
    }
    if (group.edited) parts.push(`${group.edited} fixed by you`);
    if (group.removed) parts.push(`${plural(group.removed, 'row')} to remove`);
    if (group.rejected) parts.push(`${group.rejected} kept as uploaded`);
    if (group.applied) parts.push(`${group.applied} applied`);
    return parts.join(' · ');
};

const ALL = 'all';

const chipStyles = Object.freeze({
    bar: Object.freeze({
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px',
        padding: '4px 0 12px 0',
        borderBottom: `1px solid ${COLOURS.GREY}`,
        marginBottom: '12px',
    }),
    dot: Object.freeze({
        display: 'inline-block',
        width: '8px',
        height: '8px',
        borderRadius: '50%',
        marginRight: '6px',
    }),
    header: Object.freeze({
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
        padding: '0 0 12px 0',
    }),
    headerActions: Object.freeze({
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px',
        alignItems: 'center',
    }),
});

const groupKindColour = group => {
    if (group.severity === SEVERITY.INTERNAL_NOTE || group.auto) {
        return COLOURS.DARK_GREY;
    }
    if (group.kind === KIND.ISSUE) return '#d32f2f';
    if (group.kind === KIND.REMOVAL) return '#ef6c00';
    return '#2e7d32';
};

const chipLabel = group => (
    <span>
        <span
            style={{ ...chipStyles.dot, background: groupKindColour(group) }}
        />
        {groupTitle(group)} ({group.count})
    </span>
);

/*
 * The group-level actions for the selected error type: act on the
 * pattern once, then look at the rows underneath only if needed.
 */
const GroupHeader = ({ group, canAct, busy, decideGroup }) => {
    const internal = group.severity === SEVERITY.INTERNAL_NOTE;
    const isIssue = group.kind === KIND.ISSUE;
    const isRemoval = group.kind === KIND.REMOVAL;
    const onGroup = decision => decideGroup(group.key, decision);
    // Rows the contributor decided one by one keep that decision; the
    // group buttons act on the others.
    const byRow = group.by_row || 0;
    const rest = group.count - byRow;
    const others = byRow ? `the other ${rest}` : `all ${group.count}`;
    const otherRows = byRow
        ? `the other ${plural(rest, 'row')}`
        : plural(group.count, 'row');
    // Nothing left for the button to do once every row outside the
    // one-by-one set already carries that decision.
    const allAccepted = group.accepted >= rest;
    const allRejected = group.rejected >= rest;
    const allRemoved = group.removed + group.accepted >= rest;
    return (
        <div style={chipStyles.header}>
            <Typography variant="subheading">
                {groupTitle(group)}: {plural(group.count, 'row')}
            </Typography>
            {isIssue && !internal && codeHelp(group.code) && (
                <div>{codeHelp(group.code)}</div>
            )}
            {group.examples[0] && group.examples[0].note && (
                <div style={styles.muted}>{group.examples[0].note}</div>
            )}
            {group.auto && (
                <div style={styles.muted}>
                    Applied automatically. Keep all originals undoes it for
                    every row of this type; use a row&rsquo;s own buttons for
                    one.
                </div>
            )}
            <div style={styles.decisionText}>{groupStatus(group)}</div>
            {canAct && !internal && rest > 0 && (
                <div style={chipStyles.headerActions}>
                    {group.kind === KIND.CORRECTION && (
                        <>
                            <Button
                                size="small"
                                variant="outlined"
                                color="primary"
                                disabled={busy || !rest || allAccepted}
                                onClick={() => onGroup(DECISION.ACCEPTED)}
                            >
                                Accept {others}
                            </Button>
                            <Button
                                size="small"
                                variant="outlined"
                                disabled={busy || !rest || allRejected}
                                onClick={() => onGroup(DECISION.REJECTED)}
                            >
                                Keep {others} originals
                            </Button>
                        </>
                    )}
                    {(isRemoval || isIssue) && (
                        <>
                            <Button
                                size="small"
                                variant="outlined"
                                color={isRemoval ? 'primary' : 'secondary'}
                                disabled={busy || !rest || allRemoved}
                                onClick={() =>
                                    onGroup(
                                        isRemoval
                                            ? DECISION.ACCEPTED
                                            : DECISION.REMOVED,
                                    )
                                }
                            >
                                Remove {otherRows}
                            </Button>
                            <Button
                                size="small"
                                variant="outlined"
                                disabled={busy || !rest || allRejected}
                                onClick={() => onGroup(DECISION.REJECTED)}
                            >
                                {isRemoval
                                    ? `Keep ${otherRows}`
                                    : `Leave ${others} as uploaded`}
                            </Button>
                        </>
                    )}
                    {isIssue && (
                        <span style={styles.muted}>or fix each row below</span>
                    )}
                </div>
            )}
            {byRow > 0 && (
                <div style={styles.muted}>
                    {plural(byRow, 'row')} you decided one by one{' '}
                    {byRow === 1 ? 'keeps' : 'keep'} that decision; use the
                    row&rsquo;s own buttons to change it, or{' '}
                    <ResetLink
                        count={byRow}
                        busy={busy}
                        onClick={() => onGroup(RESET)}
                    />
                </div>
            )}
        </div>
    );
};

GroupHeader.propTypes = {
    group: object.isRequired,
    canAct: bool.isRequired,
    busy: bool.isRequired,
    decideGroup: func.isRequired,
};

const ResetLink = ({ count, busy, onClick }) => (
    <Button
        size="small"
        color="primary"
        disabled={busy}
        onClick={onClick}
        style={{ margin: '-6px 0', textTransform: 'none' }}
    >
        reset {count === 1 ? 'that' : `those ${count}`} and start over
    </Button>
);

ResetLink.propTypes = {
    count: number.isRequired,
    busy: bool.isRequired,
    onClick: func.isRequired,
};

/*
 * The Needs-you tab's own actions: every suggested fix at once, or
 * everything left as uploaded. Flags have no value to accept, so Accept
 * all only covers the corrections; rows decided one by one are left
 * alone, as with any group action.
 */
const AllHeader = ({ groups, canAct, busy, decideGroup }) => {
    const corrections = groups.filter(g => g.kind === KIND.CORRECTION);
    const fixes = corrections.reduce(
        (n, g) => n + g.count - (g.by_row || 0),
        0,
    );
    const everything = groups.reduce(
        (n, g) => n + g.count - (g.by_row || 0),
        0,
    );
    const byRow = groups.reduce((n, g) => n + (g.by_row || 0), 0);
    const flagged = groups.length - corrections.length;
    if (!canAct || !groups.length) return null;
    return (
        <div style={chipStyles.header}>
            <div style={chipStyles.headerActions}>
                <Button
                    size="small"
                    variant="outlined"
                    color="primary"
                    disabled={busy || !fixes}
                    onClick={() =>
                        decideGroup(
                            corrections.map(g => g.key),
                            DECISION.ACCEPTED,
                        )
                    }
                >
                    Accept {byRow ? 'the other' : 'all'}{' '}
                    {plural(fixes, 'suggested fix', 'suggested fixes')}
                </Button>
                <Button
                    size="small"
                    variant="outlined"
                    disabled={busy || !everything}
                    onClick={() =>
                        decideGroup(
                            groups.map(g => g.key),
                            DECISION.REJECTED,
                        )
                    }
                >
                    Keep {byRow ? 'the rest' : 'everything'} as uploaded
                </Button>
                <span style={styles.muted}>
                    {flagged > 0 &&
                        'Flagged rows have nothing to accept: fix or remove them by type or by row. '}
                    Or pick a type above.
                </span>
            </div>
            {byRow > 0 && (
                <div style={styles.muted}>
                    {plural(byRow, 'row')} you decided one by one{' '}
                    {byRow === 1 ? 'keeps' : 'keep'} that decision, or{' '}
                    <ResetLink
                        count={byRow}
                        busy={busy}
                        onClick={() =>
                            decideGroup(
                                groups.filter(g => g.by_row).map(g => g.key),
                                RESET,
                            )
                        }
                    />
                </div>
            )}
        </div>
    );
};

AllHeader.propTypes = {
    groups: arrayOf(object).isRequired,
    canAct: bool.isRequired,
    busy: bool.isRequired,
    decideGroup: func.isRequired,
};

const AUTO = 'auto';

const autoStyles = Object.freeze({
    box: Object.freeze({
        border: `1px solid ${COLOURS.GREY}`,
        borderRadius: '4px',
        background: COLOURS.LIGHT_GREY,
        padding: '10px 14px',
        margin: '4px 0 16px 0',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
    }),
    head: Object.freeze({
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '8px',
    }),
    bar: Object.freeze({
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px',
    }),
});

const chipProps = (key, active) => ({
    clickable: true,
    color: active === key ? 'primary' : 'default',
    variant: active === key ? 'default' : 'outlined',
    role: 'tab',
    'aria-selected': active === key,
});

/*
 * Actions on the rows the contributor ticked. They touch only the
 * suggestions shown on the current tab, go out as one request, and
 * count as row-by-row decisions so a later group action leaves them be.
 */
const BulkBar = ({ rows, selected, busy, decide, onClear }) => {
    const picked = rows.filter(r => selected.has(r.row_number));
    const suggestions = picked.reduce(
        (acc, r) =>
            acc.concat(
                r.suggestions.filter(
                    s => s.severity !== SEVERITY.INTERNAL_NOTE,
                ),
            ),
        [],
    );
    const fixes = suggestions.filter(s => s.kind === KIND.CORRECTION);
    if (!picked.length) return null;
    const send = (list, decision) => {
        decide(list.map(s => ({ id: s.id, decision })));
        onClear();
    };
    return (
        <div style={styles.bulkBar} data-tour="bulk">
            <span style={styles.bulkCount}>
                {plural(picked.length, 'row')} selected:
            </span>
            {fixes.length > 0 && (
                <Button
                    size="small"
                    variant="outlined"
                    color="primary"
                    disabled={busy}
                    onClick={() => send(fixes, DECISION.ACCEPTED)}
                >
                    Accept{' '}
                    {plural(fixes.length, 'suggested fix', 'suggested fixes')}
                </Button>
            )}
            <Button
                size="small"
                variant="outlined"
                disabled={busy}
                onClick={() => send(suggestions, DECISION.REJECTED)}
            >
                Keep as uploaded
            </Button>
            <Button
                size="small"
                variant="outlined"
                color="secondary"
                disabled={busy}
                onClick={() => send(suggestions, DECISION.REMOVED)}
            >
                Remove {plural(picked.length, 'row')}
            </Button>
            <Button size="small" disabled={busy} onClick={onClear}>
                Clear selection
            </Button>
        </div>
    );
};

BulkBar.propTypes = {
    rows: arrayOf(object).isRequired,
    selected: object.isRequired,
    busy: bool.isRequired,
    decide: func.isRequired,
    onClear: func.isRequired,
};

/*
 * Two tiers of chips. The top bar is what needs the contributor: flags,
 * removals and fixes with judgment in them, one chip per error type plus
 * "Needs you". Below it, folded by default, the fixes made automatically
 * at ingest, which they can open to inspect and undo by type. Lists run
 * to thousands of rows; the errors do not come in thousands of kinds.
 */
export const GroupTabs = ({
    groups,
    rows,
    canAct,
    busy,
    decide,
    decideGroup,
}) => {
    const [selected, setSelected] = useState(ALL);
    const [showAuto, setShowAuto] = useState(false);
    const [picked, setPicked] = useState(new Set());
    const attention = groups.filter(g => !g.auto);
    const automatic = groups.filter(g => g.auto);
    const current = groups.find(g => g.key === selected);
    let active = ALL;
    if (current) {
        active = selected;
    } else if (selected === AUTO) {
        active = AUTO;
    }
    const autoFixes = automatic.reduce((n, g) => n + g.count, 0);
    const autoRows = new Set(
        automatic.reduce((acc, g) => acc.concat(g.rows), []),
    ).size;
    const attentionRows = new Set(
        attention.reduce((acc, g) => acc.concat(g.rows), []),
    ).size;

    const filter = (() => {
        if (current) return s => suggestionKey(s) === current.key;
        if (active === AUTO) return isAuto;
        return s => !isAuto(s);
    })();

    const select = key => {
        setSelected(key);
        setPicked(new Set());
        if (key === AUTO || automatic.some(g => g.key === key)) {
            setShowAuto(true);
        }
    };
    const shown = visibleRows(rows, filter);
    const toggle = rowNumber => {
        const next = new Set(picked);
        if (next.has(rowNumber)) next.delete(rowNumber);
        else next.add(rowNumber);
        setPicked(next);
    };
    const allPicked =
        shown.length > 0 && shown.every(r => picked.has(r.row_number));

    return (
        <div>
            {automatic.length > 0 && (
                <div style={autoStyles.box} data-tour="automatic">
                    <div style={autoStyles.head}>
                        <span>
                            <b>{plural(autoFixes, 'fix', 'fixes')}</b> made
                            automatically on {plural(autoRows, 'row')}:
                            formatting that needs no judgment, already applied.
                            You can undo any of them by type.
                        </span>
                        <Button
                            size="small"
                            onClick={() => {
                                setShowAuto(!showAuto);
                                if (
                                    showAuto &&
                                    (active === AUTO ||
                                        (current && current.auto))
                                ) {
                                    setSelected(ALL);
                                }
                            }}
                        >
                            {showAuto
                                ? 'Hide automatic fixes'
                                : 'Show automatic fixes'}
                        </Button>
                    </div>
                    {showAuto && (
                        <div style={autoStyles.bar} role="tablist">
                            <Chip
                                label={`All automatic (${plural(
                                    autoRows,
                                    'row',
                                )})`}
                                onClick={() => select(AUTO)}
                                {...chipProps(AUTO, active)}
                            />
                            {automatic.map(group => (
                                <Chip
                                    key={group.key}
                                    label={chipLabel(group)}
                                    onClick={() => select(group.key)}
                                    {...chipProps(group.key, active)}
                                />
                            ))}
                        </div>
                    )}
                </div>
            )}
            <div style={chipStyles.bar} role="tablist" data-tour="chips">
                <Chip
                    label={`Needs you (${plural(attentionRows, 'row')})`}
                    onClick={() => select(ALL)}
                    {...chipProps(ALL, active)}
                />
                {attention.map(group => (
                    <Chip
                        key={group.key}
                        label={chipLabel(group)}
                        onClick={() => select(group.key)}
                        {...chipProps(group.key, active)}
                    />
                ))}
                {!attention.length && (
                    <span style={styles.muted}>
                        Nothing needs your decision.
                    </span>
                )}
            </div>
            {current && (
                <GroupHeader
                    group={current}
                    canAct={canAct}
                    busy={busy}
                    decideGroup={decideGroup}
                />
            )}
            {active === ALL && (
                <AllHeader
                    groups={attention}
                    canAct={canAct}
                    busy={busy}
                    decideGroup={decideGroup}
                />
            )}
            {canAct && shown.length > 1 && (
                <label
                    style={styles.selectAll}
                    htmlFor="list-cleaning-select-all"
                >
                    <Checkbox
                        checked={allPicked}
                        indeterminate={!allPicked && picked.size > 0}
                        onChange={() =>
                            setPicked(
                                allPicked
                                    ? new Set()
                                    : new Set(shown.map(r => r.row_number)),
                            )
                        }
                        disabled={busy}
                        color="primary"
                        id="list-cleaning-select-all"
                        inputProps={{ 'aria-label': 'Select all rows shown' }}
                    />
                    Select all {plural(shown.length, 'row')} on this tab
                </label>
            )}
            {canAct && (
                <BulkBar
                    rows={shown}
                    selected={picked}
                    busy={busy}
                    decide={decide}
                    onClear={() => setPicked(new Set())}
                />
            )}
            <SuggestionRows
                rows={rows}
                canAct={canAct}
                busy={busy}
                decide={decide}
                filter={filter}
                selected={picked}
                onToggle={canAct ? toggle : null}
            />
        </div>
    );
};

GroupTabs.propTypes = {
    groups: arrayOf(object).isRequired,
    rows: arrayOf(object).isRequired,
    canAct: bool.isRequired,
    busy: bool.isRequired,
    decide: func.isRequired,
    decideGroup: func.isRequired,
};

export const DownloadFixedList = ({ listID, applied }) => (
    <Button
        size="small"
        variant="outlined"
        color="primary"
        href={makeFacilityListCleaningDownloadURL(listID)}
        download
        title={
            applied
                ? 'Download your list with the applied changes, removed rows last'
                : 'Apply your changes first; the download reflects the list as it stands'
        }
    >
        Download {applied ? 'fixed' : 'current'} list (CSV)
    </Button>
);

DownloadFixedList.propTypes = {
    listID: number.isRequired,
    applied: bool.isRequired,
};
