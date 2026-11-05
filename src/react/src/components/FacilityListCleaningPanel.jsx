import React, { useEffect } from 'react';
import { bool, func, number, object, shape } from 'prop-types';
import { connect } from 'react-redux';
import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';

import {
    fetchFacilityListCleaning,
    resetFacilityListCleaning,
    submitFacilityListCleaningDecisions,
    submitFacilityListCleaningGroupDecisions,
    applyFacilityListCleaning,
    startFacilityListCleaningRun,
} from '../actions/facilityListCleaning';

import {
    RESET,
    RUN_STATUS,
    styles,
    Stat,
    ListFindings,
    GroupTabs,
    DownloadFixedList,
} from './FacilityListCleaningSuggestions';

const POLL_INTERVAL_MS = 15000;

const FacilityListCleaningPanel = ({
    listID,
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
    decideGroup,
    apply,
    onApplied,
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
                        usually takes a few minutes. This page refreshes on its
                        own.
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
                    We could not check this list automatically. A moderator will
                    review it as usual.
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
                            value={summary.must_fix_pending}
                            label="rows that need your attention"
                        />
                        <Stat
                            value={summary.corrections_total}
                            label={`suggested fixes (${summary.corrections_pending} to review)`}
                        />
                        <Stat
                            value={summary.auto_fixes}
                            label="fixes made automatically"
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
                        These are automated suggestions, not decisions. You are
                        responsible for the data you submit: accept a fix only
                        if it is correct for that facility. Rows we could not
                        fix can be corrected or removed here, with no need to
                        upload again. Facility names and addresses are never
                        changed automatically. A moderator will still review the
                        list before anything is published, and applying these
                        changes makes approval more likely.
                    </div>
                    <ListFindings filePass={run.file_pass || {}} />
                    <GroupTabs
                        groups={data.groups || []}
                        rows={rows}
                        canAct={canAct}
                        busy={busy}
                        decide={decide}
                        decideGroup={decideGroup}
                    />
                    <div style={styles.footer}>
                        {canAct && (
                            <Button
                                variant="contained"
                                color="primary"
                                disabled={
                                    busy || summary.changes_unapplied === 0
                                }
                                onClick={() =>
                                    apply().then(() => onApplied && onApplied())
                                }
                            >
                                Apply {summary.changes_unapplied}{' '}
                                {summary.changes_unapplied === 1
                                    ? 'change'
                                    : 'changes'}{' '}
                                to my list
                            </Button>
                        )}
                        <DownloadFixedList
                            listID={listID}
                            applied={!!run.applied_at}
                        />
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
    onApplied: null,
    data: null,
    error: null,
    submitError: null,
    applyError: null,
    lastApplied: null,
};

FacilityListCleaningPanel.propTypes = {
    listID: number.isRequired,
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
    decideGroup: func.isRequired,
    apply: func.isRequired,
    onApplied: func,
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
    // One key or a list of keys; one request either way. RESET is not a
    // decision: it clears that type's row-by-row decisions.
    decideGroup: (keys, decision) =>
        dispatch(
            submitFacilityListCleaningGroupDecisions(
                listID,
                []
                    .concat(keys)
                    .map(key =>
                        decision === RESET
                            ? { key, reset: true }
                            : { key, decision },
                    ),
            ),
        ),
    apply: () => dispatch(applyFacilityListCleaning(listID)),
    startRun: () => dispatch(startFacilityListCleaningRun(listID)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(FacilityListCleaningPanel);
