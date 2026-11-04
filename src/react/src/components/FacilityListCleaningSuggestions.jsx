import React, { useState } from 'react';
import { arrayOf, bool, func, number, object, string } from 'prop-types';
import Button from '@material-ui/core/Button';
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

export const ListFindings = ({ filePass }) => {
    const headerIssues = filePass.header_issues || [];
    const duplicates = filePass.exact_duplicates || [];
    const repeated = filePass.repeated_names || [];
    if (!headerIssues.length && !duplicates.length && !repeated.length) {
        return null;
    }
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
                {duplicates.map(pair => (
                    <li key={`dup-${pair.remove}`}>
                        Row {pair.remove} repeats row {pair.keep} ({pair.match}{' '}
                        match).
                    </li>
                ))}
                {repeated.map(group => (
                    <li key={`rep-${group.name}-${group.rows.join('-')}`}>
                        &ldquo;{group.name}&rdquo; appears on rows{' '}
                        {group.rows.join(', ')} with different addresses.
                    </li>
                ))}
            </ul>
        </div>
    );
};

ListFindings.propTypes = { filePass: object.isRequired };

export const suggestionKey = s => `${s.kind}:${s.code}:${s.field}`;

export const isAuto = s => !!(s.extra && s.extra.auto);

export const SuggestionRows = ({ rows, canAct, busy, decide, filter }) =>
    rows
        .map(row =>
            filter
                ? { ...row, suggestions: row.suggestions.filter(filter) }
                : row,
        )
        .filter(row => row.suggestions.length)
        .map(row => (
            <div key={row.row_number} style={styles.rowCard}>
                <div style={styles.rowHeader}>
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

SuggestionRows.defaultProps = { filter: null };

SuggestionRows.propTypes = {
    rows: arrayOf(object).isRequired,
    canAct: bool.isRequired,
    busy: bool.isRequired,
    decide: func.isRequired,
    filter: func,
};

const groupTitle = group => {
    if (group.kind === KIND.REMOVAL) {
        return `Rows to remove: ${describeCode(group.code)}`;
    }
    return `${fieldLabel(group.field)}: ${describeCode(group.code)}`;
};

const plural = (n, word, words = `${word}s`) =>
    `${n} ${n === 1 ? word : words}`;

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
    const undecided = group.count - group.rejected;
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
            {canAct && !internal && (
                <div style={chipStyles.headerActions}>
                    {group.kind === KIND.CORRECTION && (
                        <>
                            <Button
                                size="small"
                                variant="outlined"
                                color="primary"
                                disabled={
                                    busy || group.accepted === group.count
                                }
                                onClick={() => onGroup(DECISION.ACCEPTED)}
                            >
                                Accept all {group.count}
                            </Button>
                            <Button
                                size="small"
                                variant="outlined"
                                disabled={
                                    busy || group.rejected === group.count
                                }
                                onClick={() => onGroup(DECISION.REJECTED)}
                            >
                                Keep all originals
                            </Button>
                        </>
                    )}
                    {(isRemoval || isIssue) && (
                        <>
                            <Button
                                size="small"
                                variant="outlined"
                                color={isRemoval ? 'primary' : 'secondary'}
                                disabled={
                                    busy ||
                                    group.removed + group.accepted ===
                                        group.count
                                }
                                onClick={() =>
                                    onGroup(
                                        isRemoval
                                            ? DECISION.ACCEPTED
                                            : DECISION.REMOVED,
                                    )
                                }
                            >
                                Remove {plural(undecided || group.count, 'row')}
                            </Button>
                            <Button
                                size="small"
                                variant="outlined"
                                disabled={
                                    busy || group.rejected === group.count
                                }
                                onClick={() => onGroup(DECISION.REJECTED)}
                            >
                                {isRemoval
                                    ? 'Keep all rows'
                                    : 'Leave all as uploaded'}
                            </Button>
                        </>
                    )}
                    {isIssue && (
                        <span style={styles.muted}>or fix each row below</span>
                    )}
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
        if (key === AUTO || automatic.some(g => g.key === key)) {
            setShowAuto(true);
        }
    };

    return (
        <div>
            {automatic.length > 0 && (
                <div style={autoStyles.box}>
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
            <div style={chipStyles.bar} role="tablist">
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
            <SuggestionRows
                rows={rows}
                canAct={canAct}
                busy={busy}
                decide={decide}
                filter={filter}
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
