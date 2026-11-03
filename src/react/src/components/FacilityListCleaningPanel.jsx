import React, { useEffect, useState } from 'react';
import { bool, func, number, object, shape, string } from 'prop-types';
import { connect } from 'react-redux';
import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import Paper from '@material-ui/core/Paper';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';

import {
    fetchFacilityListCleaning,
    resetFacilityListCleaning,
    submitFacilityListCleaningDecisions,
    applyFacilityListCleaning,
    startFacilityListCleaningRun,
} from '../actions/facilityListCleaning';

import COLOURS from '../util/COLOURS';

const POLL_INTERVAL_MS = 15000;

const RUN_STATUS = Object.freeze({
    PENDING: 'PENDING',
    RUNNING: 'RUNNING',
    COMPLETE: 'COMPLETE',
    FAILED: 'FAILED',
});

const KIND = Object.freeze({
    CORRECTION: 'CORRECTION',
    ISSUE: 'ISSUE',
    REMOVAL: 'REMOVAL',
});

const DECISION = Object.freeze({
    PENDING: 'PENDING',
    ACCEPTED: 'ACCEPTED',
    REJECTED: 'REJECTED',
    EDITED: 'EDITED',
});

const FIELD_LABELS = Object.freeze({
    country: 'Country',
    name: 'Name',
    address: 'Address',
    sector_product_type: 'Sector / product type',
    facility_type_processing_type: 'Facility type / processing type',
    number_of_workers: 'Number of workers',
    parent_company: 'Parent company',
    row: 'Row',
});

const CODE_LABELS = Object.freeze({
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
});

const styles = Object.freeze({
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

const describeCode = code =>
    (code || '')
        .split('+')
        .map(part => CODE_LABELS[part] || part.replace(/_/g, ' '))
        .join(', ');

const fieldLabel = field => FIELD_LABELS[field] || field;

const Tag = ({ style, children }) => (
    <span style={{ ...styles.tag, ...style }}>{children}</span>
);

Tag.propTypes = { style: object.isRequired, children: string.isRequired };

const Stat = ({ value, label }) => (
    <div style={styles.stat}>
        <div style={styles.statNumber}>{value}</div>
        <div style={styles.statLabel}>{label}</div>
    </div>
);

Stat.propTypes = { value: number.isRequired, label: string.isRequired };

const Correction = ({ suggestion, canAct, busy, onDecide }) => {
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

const Issue = ({ suggestion }) => {
    const internal = suggestion.severity === 'internal_note';
    return (
        <div style={styles.suggestion}>
            <Tag style={internal ? styles.internalTag : styles.mustFixTag}>
                {internal ? 'Moderator note' : 'Needs your attention'}
            </Tag>
            <div style={styles.valueBlock}>
                <div style={styles.fieldName}>
                    {fieldLabel(suggestion.field)}:{' '}
                    {suggestion.code.replace(/_/g, ' ')}
                </div>
                <div>{suggestion.note}</div>
            </div>
        </div>
    );
};

Issue.propTypes = { suggestion: object.isRequired };

const Removal = ({ suggestion, canAct, busy, onDecide }) => {
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

const ListFindings = ({ filePass }) => {
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
                        Row {pair.remove} repeats row {pair.keep} (
                        {pair.match} match).
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

const FacilityListCleaningPanel = ({
    isAdminUser,
    canAct,
    data,
    fetching,
    error,
    submitting,
    submitError,
    applying,
    applyError,
    lastApplied,
    fetchCleaning,
    pollCleaning,
    clearCleaning,
    decide,
    apply,
    startRun,
}) => {
    useEffect(() => {
        fetchCleaning();
        return () => clearCleaning();
    }, [fetchCleaning, clearCleaning]);

    const runStatus = data && data.run ? data.run.status : null;
    const isRunning =
        runStatus === RUN_STATUS.RUNNING || runStatus === RUN_STATUS.PENDING;

    useEffect(() => {
        if (!isRunning) {
            return undefined;
        }
        const timer = setInterval(pollCleaning, POLL_INTERVAL_MS);
        return () => clearInterval(timer);
    }, [isRunning, pollCleaning]);

    if (!data && fetching) {
        return null;
    }

    if (error) {
        return null;
    }

    if (!data || !data.run) {
        if (isAdminUser && data && data.enabled !== undefined) {
            return (
                <Paper style={styles.panel}>
                    <Typography style={styles.heading}>
                        Automated checks
                    </Typography>
                    <Typography style={styles.muted}>
                        No automated check has run for this list
                        {data.enabled
                            ? '.'
                            : ' (the enable_list_cleaning_feedback switch is off).'}
                    </Typography>
                    <Button
                        variant="outlined"
                        color="primary"
                        style={{ marginTop: '12px' }}
                        onClick={startRun}
                        disabled={fetching}
                    >
                        Run checks now (moderator)
                    </Button>
                </Paper>
            );
        }
        return null;
    }

    const { run, summary, rows } = data;
    const busy = submitting || applying;

    if (isRunning) {
        return (
            <Paper style={styles.panel}>
                <Typography style={styles.heading}>
                    Automated checks in progress
                </Typography>
                <div
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                    }}
                >
                    <CircularProgress size={22} />
                    <Typography>
                        We are checking your list for problems and formatting
                        fixes you can make before a moderator reviews it. This
                        usually takes a few minutes. This page refreshes on
                        its own.
                    </Typography>
                </div>
            </Paper>
        );
    }

    if (runStatus === RUN_STATUS.FAILED) {
        return (
            <Paper style={styles.panel}>
                <Typography style={styles.heading}>
                    Automated checks unavailable
                </Typography>
                <Typography>
                    We could not check this list automatically. A moderator
                    will review it as usual.
                </Typography>
                {isAdminUser && (
                    <Typography style={styles.muted}>
                        Error: {run.error}
                    </Typography>
                )}
                {isAdminUser && (
                    <Button
                        variant="outlined"
                        color="primary"
                        style={{ marginTop: '12px' }}
                        onClick={startRun}
                    >
                        Retry (moderator)
                    </Button>
                )}
            </Paper>
        );
    }

    const nothingFound =
        !rows.length && !summary.list_findings && !summary.removals;

    return (
        <Paper style={styles.panel}>
            <Typography style={styles.heading}>
                Automated checks on your list
            </Typography>
            {nothingFound ? (
                <Typography>
                    We found nothing to fix. Your list will be reviewed by a
                    moderator as usual.
                </Typography>
            ) : (
                <>
                    <div style={styles.statRow}>
                        <Stat
                            value={summary.rows_must_fix}
                            label="rows that need your attention"
                        />
                        <Stat
                            value={summary.corrections_total}
                            label={`suggested fixes (${summary.corrections_pending} to review)`}
                        />
                        <Stat
                            value={summary.removals}
                            label="rows suggested for removal"
                        />
                        <Stat
                            value={summary.list_findings}
                            label="findings about the whole file"
                        />
                        {isAdminUser && (
                            <Stat
                                value={summary.internal_notes}
                                label="moderator notes (not shown to contributor)"
                            />
                        )}
                    </div>
                    <div style={styles.disclaimer}>
                        These are automated suggestions, not decisions. You
                        are responsible for the data you submit: accept a fix
                        only if it is correct for that facility, and fix rows
                        that need your attention in your file. Facility names
                        and addresses are never changed automatically. A
                        moderator will still review the list before anything
                        is published.
                    </div>
                    <ListFindings filePass={run.file_pass || {}} />
                    {rows.map(row => (
                        <div key={row.row_number} style={styles.rowCard}>
                            <div style={styles.rowHeader}>
                                <span style={styles.rowNumber}>
                                    Row {row.row_number}
                                </span>
                                <span style={styles.rowIdentity}>
                                    {row.name}
                                    {row.address ? ` — ${row.address}` : ''}
                                    {row.country_code
                                        ? ` (${row.country_code})`
                                        : ''}
                                </span>
                            </div>
                            {row.suggestions.map(suggestion => {
                                const onDecide = (decision, value) =>
                                    decide([
                                        { id: suggestion.id, decision, value },
                                    ]);
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
                                    />
                                );
                            })}
                        </div>
                    ))}
                    <div style={styles.footer}>
                        {canAct && (
                            <Button
                                variant="contained"
                                color="primary"
                                disabled={
                                    busy || summary.corrections_unapplied === 0
                                }
                                onClick={apply}
                            >
                                Apply {summary.corrections_unapplied} accepted{' '}
                                {summary.corrections_unapplied === 1
                                    ? 'fix'
                                    : 'fixes'}{' '}
                                to my list
                            </Button>
                        )}
                        {busy && <CircularProgress size={22} />}
                        {run.applied_at && (
                            <Typography style={styles.muted}>
                                Last applied{' '}
                                {new Date(run.applied_at).toLocaleString()}
                                {lastApplied
                                    ? ` (${lastApplied.applied} applied, ${lastApplied.reverted} reverted)`
                                    : ''}
                            </Typography>
                        )}
                        {(submitError || applyError) && (
                            <Typography style={styles.error}>
                                {(submitError || applyError).join(' ')}
                            </Typography>
                        )}
                        {isAdminUser && (
                            <Typography style={styles.muted}>
                                Run {run.id}: {run.runner}, prompt{' '}
                                {run.prompt_version || 'n/a'}
                            </Typography>
                        )}
                    </div>
                </>
            )}
        </Paper>
    );
};

FacilityListCleaningPanel.defaultProps = {
    data: null,
    error: null,
    submitError: null,
    applyError: null,
    lastApplied: null,
};

FacilityListCleaningPanel.propTypes = {
    isAdminUser: bool.isRequired,
    canAct: bool.isRequired,
    data: shape({
        enabled: bool,
        run: object,
        summary: object,
    }),
    fetching: bool.isRequired,
    error: object,
    submitting: bool.isRequired,
    submitError: object,
    applying: bool.isRequired,
    applyError: object,
    lastApplied: object,
    fetchCleaning: func.isRequired,
    pollCleaning: func.isRequired,
    clearCleaning: func.isRequired,
    decide: func.isRequired,
    apply: func.isRequired,
    startRun: func.isRequired,
};

const mapStateToProps = ({
    facilityListCleaning: {
        data,
        fetching,
        error,
        submitting,
        submitError,
        applying,
        applyError,
        lastApplied,
    },
}) => ({
    data,
    fetching,
    error,
    submitting,
    submitError,
    applying,
    applyError,
    lastApplied,
});

const mapDispatchToProps = (dispatch, { listID }) => ({
    fetchCleaning: () => dispatch(fetchFacilityListCleaning(listID)),
    pollCleaning: () =>
        dispatch(fetchFacilityListCleaning(listID, { silent: true })),
    clearCleaning: () => dispatch(resetFacilityListCleaning()),
    decide: decisions =>
        dispatch(submitFacilityListCleaningDecisions(listID, decisions)),
    apply: () => dispatch(applyFacilityListCleaning(listID)),
    startRun: () => dispatch(startFacilityListCleaningRun(listID)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(FacilityListCleaningPanel);
