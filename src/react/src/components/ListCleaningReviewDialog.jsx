import React, { useEffect, useRef, useState } from 'react';
import { bool, func, number, object, shape } from 'prop-types';
import { connect } from 'react-redux';
import AppBar from '@material-ui/core/AppBar';
import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import Step from '@material-ui/core/Step';
import StepLabel from '@material-ui/core/StepLabel';
import Stepper from '@material-ui/core/Stepper';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';

import {
    fetchFacilityListCleaning,
    resetFacilityListCleaning,
    submitFacilityListCleaningDecisions,
    submitFacilityListCleaningGroupDecisions,
    applyFacilityListCleaning,
    recordFacilityListCleaningEvent,
    beaconFacilityListCleaningEvent,
} from '../actions/facilityListCleaning';

import {
    RESET,
    RUN_STATUS,
    styles as cardStyles,
    ReadinessTracker,
    ListFindings,
    GroupTabs,
    DownloadFixedList,
} from './FacilityListCleaningSuggestions';

import COLOURS from '../util/COLOURS';
import ListCleaningTour from './ListCleaningTour';

const timeOfDay = iso =>
    new Date(iso).toLocaleTimeString(undefined, {
        hour: 'numeric',
        minute: '2-digit',
    });

const countdown = seconds => {
    if (seconds <= 0) return 'Time is up';
    if (seconds < 120) return `Submit within ${seconds} s`;
    return `Submit within ${Math.ceil(seconds / 60)} min`;
};

// The contributor is waiting on this screen, so poll faster than the
// list-page panel does, and stop pretending after a while.
const POLL_INTERVAL_MS = 3000;
const MAX_WAIT_MS = 3 * 60 * 1000;

const STEPS = Object.freeze([
    'Upload file',
    'Automatic checks',
    'Review suggestions',
    'Done',
]);

const STEP = Object.freeze({
    UPLOAD: 0,
    CHECKS: 1,
    REVIEW: 2,
    DONE: 3,
});

const styles = Object.freeze({
    appBar: Object.freeze({
        position: 'relative',
        background: COLOURS.NAVY_BLUE,
    }),
    title: Object.freeze({
        color: COLOURS.WHITE,
        fontSize: '20px',
        fontWeight: 700,
        flex: 1,
    }),
    tourButton: Object.freeze({
        color: COLOURS.WHITE,
        border: '1px solid rgba(255, 255, 255, 0.6)',
    }),
    clock: Object.freeze({
        color: COLOURS.WHITE,
        background: 'rgba(255, 255, 255, 0.16)',
        borderRadius: '14px',
        padding: '4px 12px',
        fontWeight: 700,
        marginRight: '12px',
        whiteSpace: 'nowrap',
    }),
    clockUrgent: Object.freeze({
        background: '#d32f2f',
    }),
    finalNote: Object.freeze({
        flex: '1 1 100%',
        fontSize: '0.85rem',
        color: 'rgba(0, 0, 0, 0.6)',
    }),
    stepper: Object.freeze({
        padding: '16px 0 8px 0',
    }),
    body: Object.freeze({
        maxWidth: '960px',
        margin: '0 auto',
        padding: '0 16px 32px 16px',
    }),
    centred: Object.freeze({
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '16px',
        textAlign: 'center',
        padding: '48px 0',
    }),
    heading: Object.freeze({
        fontSize: '22px',
        fontWeight: 700,
        margin: '16px 0 8px 0',
    }),
    actions: Object.freeze({
        display: 'flex',
        flexWrap: 'wrap',
        gap: '12px',
        alignItems: 'center',
        justifyContent: 'flex-end',
        position: 'sticky',
        bottom: 0,
        background: COLOURS.WHITE,
        borderTop: `1px solid ${COLOURS.GREY}`,
        padding: '12px 0',
        marginTop: '16px',
    }),
    muted: Object.freeze({
        color: COLOURS.DARK_GREY,
        fontSize: '13px',
    }),
    error: Object.freeze({
        color: 'red',
    }),
});

const Checking = ({ timedOut, onContinue }) => (
    <div style={styles.centred}>
        <CircularProgress size={48} />
        <Typography style={styles.heading}>
            {timedOut
                ? 'Still checking your list'
                : 'Checking your list for problems'}
        </Typography>
        <Typography>
            Your file has been uploaded. We are looking for formatting fixes and
            rows that need your attention before a moderator reviews it. This
            usually takes a few minutes.
        </Typography>
        {timedOut && (
            <Typography>
                This is taking longer than usual. You can continue to your list
                now and the suggestions will appear there when they are ready.
            </Typography>
        )}
        <Button
            variant={timedOut ? 'contained' : 'text'}
            color="primary"
            onClick={onContinue}
        >
            {timedOut ? 'Continue to my list' : 'Skip and go to my list'}
        </Button>
    </div>
);

Checking.propTypes = { timedOut: bool.isRequired, onContinue: func.isRequired };

const Unavailable = ({ onContinue }) => (
    <div style={styles.centred}>
        <Typography style={styles.heading}>
            Automatic checks unavailable
        </Typography>
        <Typography>
            We could not check this list automatically. Your list has been
            uploaded and a moderator will review it as usual.
        </Typography>
        <Button variant="contained" color="primary" onClick={onContinue}>
            Go to my list
        </Button>
    </div>
);

Unavailable.propTypes = { onContinue: func.isRequired };

const Clean = ({ onContinue }) => (
    <div style={styles.centred}>
        <Typography style={styles.heading}>Your list looks good</Typography>
        <Typography>
            We found nothing to fix. A moderator will review your list as usual.
        </Typography>
        <Button variant="contained" color="primary" onClick={onContinue}>
            Go to my list
        </Button>
    </div>
);

Clean.propTypes = { onContinue: func.isRequired };

const Done = ({ listID, summary, lastApplied, asUploaded, onContinue }) => (
    <div style={styles.centred}>
        <Typography style={styles.heading}>
            Your list has been submitted
        </Typography>
        {!asUploaded && lastApplied && (
            <Typography>
                {lastApplied.applied}{' '}
                {lastApplied.applied === 1 ? 'change was' : 'changes were'}{' '}
                applied to your list
                {summary.rows_removed
                    ? `, including ${summary.rows_removed} ${
                          summary.rows_removed === 1 ? 'row' : 'rows'
                      } removed`
                    : ''}
                . The original values are kept with your uploaded file.
            </Typography>
        )}
        {asUploaded && (
            <Typography>
                Your list was submitted exactly as uploaded; none of the
                suggested changes were made.
            </Typography>
        )}
        {summary.must_fix_pending > 0 && (
            <Typography>
                {summary.must_fix_pending}{' '}
                {summary.must_fix_pending === 1
                    ? 'flagged row went'
                    : 'flagged rows went'}{' '}
                through as uploaded; the moderator will see them.
            </Typography>
        )}
        <Typography>
            This was your one submission. A moderator will now review the list
            and you will hear by email.
        </Typography>
        <div style={styles.actions}>
            <DownloadFixedList listID={listID} applied={!asUploaded} />
            <Button variant="contained" color="primary" onClick={onContinue}>
                Go to my list
            </Button>
        </div>
    </div>
);

Done.defaultProps = { lastApplied: null };

Done.propTypes = {
    listID: number.isRequired,
    summary: object.isRequired,
    lastApplied: object,
    asUploaded: bool.isRequired,
    onContinue: func.isRequired,
};

// Reopened after the window closed: nothing to decide any more.
const Closed = ({ run, summary, onContinue }) => (
    <div style={styles.centred}>
        <Typography style={styles.heading}>
            {run.closed_reason === 'submitted'
                ? 'This list has already been submitted'
                : 'The review window has closed'}
        </Typography>
        <Typography>
            {run.closed_reason === 'submitted'
                ? `You submitted it at ${timeOfDay(run.submitted_at)}${
                      summary && summary.changes_applied
                          ? ` with ${summary.changes_applied} ${
                                summary.changes_applied === 1
                                    ? 'change'
                                    : 'changes'
                            }`
                          : ' as uploaded'
                  }. No further changes are possible.`
                : `The hour for changes ended at ${timeOfDay(
                      run.closed_at,
                  )}, so the list went to the moderator exactly as uploaded.`}
        </Typography>
        <Button variant="contained" color="primary" onClick={onContinue}>
            Go to my list
        </Button>
    </div>
);

Closed.defaultProps = { summary: null };
Closed.propTypes = {
    run: object.isRequired,
    summary: object,
    onContinue: func.isRequired,
};

const ListCleaningReviewDialog = ({
    listID,
    open,
    resumed,
    onContinue,
    data,
    submitting,
    submitError,
    applying,
    applyError,
    lastApplied,
    fetchCleaning,
    clearCleaning,
    decide,
    decideGroup,
    apply,
}) => {
    const [openedAt, setOpenedAt] = useState(null);
    const [timedOut, setTimedOut] = useState(false);
    const [finished, setFinished] = useState(null); // 'submitted' | 'uploaded'
    const [confirmUploaded, setConfirmUploaded] = useState(false);
    // The deadline as this browser sees it, from the server's count.
    const [deadline, setDeadline] = useState(null);
    const [now, setNow] = useState(Date.now());
    const [reported, setReported] = useState(false);

    // The connected dispatchers are rebuilt whenever a parent passes a
    // new prop identity; keep the latest in refs so the effects below
    // run once per open, not once per parent render.
    const fetchRef = useRef(fetchCleaning);
    fetchRef.current = fetchCleaning;
    const clearRef = useRef(clearCleaning);
    clearRef.current = clearCleaning;
    useEffect(() => {
        if (!open || !listID) {
            return undefined;
        }
        setOpenedAt(Date.now());
        setTimedOut(false);
        setFinished(null);
        setReported(false);
        fetchRef.current();
        return () => clearRef.current();
    }, [open, listID]);

    const run = data && data.run;
    const runStatus = run ? run.status : null;
    const waiting =
        open &&
        !!listID &&
        (!run ||
            runStatus === RUN_STATUS.PENDING ||
            runStatus === RUN_STATUS.RUNNING);

    useEffect(() => {
        if (!waiting) {
            return undefined;
        }
        const timer = setInterval(() => {
            if (openedAt && Date.now() - openedAt > MAX_WAIT_MS) {
                setTimedOut(true);
            }
            fetchRef.current();
        }, POLL_INTERVAL_MS);
        return () => clearInterval(timer);
    }, [waiting, openedAt]);

    useEffect(() => {
        if (lastApplied) {
            setFinished(f => f || 'submitted');
        }
    }, [lastApplied]);

    useEffect(() => {
        if (data && data.run && data.run.status === RUN_STATUS.COMPLETE) {
            setDeadline(Date.now() + (data.seconds_left || 0) * 1000);
        }
    }, [data]);

    // A once-a-second clock while the window is open; when it runs out,
    // one more fetch lets the server close the run and the screen follow.
    const windowOpen = !!(data && data.window_open);
    useEffect(() => {
        if (!windowOpen || finished) return undefined;
        const timer = setInterval(() => {
            setNow(Date.now());
            if (deadline && Date.now() >= deadline) fetchRef.current();
        }, 1000);
        return () => clearInterval(timer);
    }, [windowOpen, finished, deadline]);
    const secondsLeft = deadline
        ? Math.max(0, Math.round((deadline - now) / 1000))
        : 0;

    // Metrics: one "opened"/"resumed" per visit, "left" when they go
    // without submitting (button or closing the tab).
    const reviewing = windowOpen && !finished && !!data && !!data.summary;
    const secondsAtOpen = data ? data.seconds_left : null;
    useEffect(() => {
        if (!reviewing || reported) return;
        setReported(true);
        recordFacilityListCleaningEvent(
            listID,
            resumed ? 'resumed' : 'opened',
            { seconds_left: secondsAtOpen },
        );
    }, [reviewing, reported, listID, resumed, secondsAtOpen]);
    useEffect(() => {
        if (!reviewing) return undefined;
        const onHide = () =>
            beaconFacilityListCleaningEvent(listID, 'left', {
                via: 'unload',
                seconds_open: openedAt
                    ? Math.round((Date.now() - openedAt) / 1000)
                    : null,
            });
        window.addEventListener('pagehide', onHide);
        return () => window.removeEventListener('pagehide', onHide);
    }, [reviewing, listID, openedAt]);
    const leave = () => {
        recordFacilityListCleaningEvent(listID, 'left', {
            via: 'button',
            seconds_open: openedAt
                ? Math.round((Date.now() - openedAt) / 1000)
                : null,
        });
        onContinue();
    };

    // Prototype: the walkthrough opens with every review so demos need no
    // reset. Production would remember dismissal per user.
    const [tour, setTour] = useState(true);
    const busy = submitting || applying;
    const summary = data ? data.summary : null;
    const rows = data ? data.rows : [];
    const nothingFound =
        summary && !rows.length && !summary.list_findings && !summary.removals;

    let activeStep = STEP.CHECKS;
    let content;
    if (waiting) {
        content = <Checking timedOut={timedOut} onContinue={onContinue} />;
    } else if (runStatus === RUN_STATUS.FAILED || !data || !run) {
        content = <Unavailable onContinue={onContinue} />;
    } else if (finished) {
        activeStep = STEP.DONE;
        content = (
            <Done
                listID={listID}
                summary={summary}
                lastApplied={lastApplied}
                asUploaded={finished === 'uploaded'}
                onContinue={onContinue}
            />
        );
    } else if (!windowOpen) {
        activeStep = STEP.DONE;
        content = (
            <Closed run={run} summary={summary} onContinue={onContinue} />
        );
    } else if (nothingFound) {
        activeStep = STEP.DONE;
        content = <Clean onContinue={onContinue} />;
    } else {
        activeStep = STEP.REVIEW;
        content = (
            <>
                <Typography style={styles.heading}>
                    A few changes would make your list more likely to be
                    approved
                </Typography>
                <Typography>
                    We checked every row. Formatting that needs no judgment is
                    ticked already and will go on when you submit; you can turn
                    any of it off. What is left is grouped by type because the
                    same problem usually repeats through a file. Pick a type to
                    see its rows and accept, keep or remove them all at once, or
                    decide row by row. Nothing changes on your list until you
                    press Submit, and you can submit once: by{' '}
                    {timeOfDay(run.review_until)} at the latest, or the list
                    goes to the moderator exactly as uploaded.
                </Typography>
                <ReadinessTracker
                    summary={summary}
                    applied={!!run.applied_at}
                />
                <div style={cardStyles.disclaimer}>
                    These are automated suggestions, not decisions. You are
                    responsible for the data you submit: accept a fix only if it
                    is correct for that facility. Facility names and addresses
                    are never changed automatically. A moderator will still
                    review the list before anything is published, and applying
                    these changes makes approval more likely.
                </div>
                <ListFindings filePass={run.file_pass || {}} />
                <GroupTabs
                    groups={data.groups || []}
                    rows={rows}
                    canAct
                    busy={busy}
                    decide={decide}
                    decideGroup={decideGroup}
                />
                <div style={styles.actions} data-tour="apply">
                    {(submitError || applyError) && (
                        <Typography style={styles.error}>
                            {(submitError || applyError).join(' ')}
                        </Typography>
                    )}
                    {busy && <CircularProgress size={22} />}
                    <DownloadFixedList listID={listID} applied={false} />
                    <Button color="primary" disabled={busy} onClick={leave}>
                        Decide later
                    </Button>
                    {summary.changes_unapplied > 0 && (
                        <Button
                            color="primary"
                            disabled={busy}
                            onClick={() => {
                                if (!confirmUploaded) {
                                    setConfirmUploaded(true);
                                    return;
                                }
                                setFinished('uploaded');
                                apply({ asUploaded: true });
                            }}
                        >
                            {confirmUploaded
                                ? 'Yes, submit without any changes'
                                : 'Submit as uploaded instead'}
                        </Button>
                    )}
                    <Button
                        variant="contained"
                        color="primary"
                        disabled={busy}
                        onClick={() => {
                            if (summary.changes_unapplied === 0) {
                                setFinished('uploaded');
                                apply({ asUploaded: true });
                            } else {
                                apply();
                            }
                        }}
                    >
                        {summary.changes_unapplied > 0
                            ? `Submit list with ${summary.changes_unapplied} ${
                                  summary.changes_unapplied === 1
                                      ? 'change'
                                      : 'changes'
                              }`
                            : 'Submit list as uploaded'}
                    </Button>
                    <span style={styles.finalNote}>
                        One submission only: after it nothing on the list
                        changes. Decide later keeps the hour running.
                    </span>
                </div>
                {tour && <ListCleaningTour onDone={() => setTour(false)} />}
            </>
        );
    }

    return (
        <Dialog fullScreen open={open} aria-labelledby="list-cleaning-review">
            <AppBar style={styles.appBar}>
                <Toolbar>
                    <Typography id="list-cleaning-review" style={styles.title}>
                        Review your list before it goes to a moderator
                    </Typography>
                    {activeStep === STEP.REVIEW && (
                        <span
                            style={{
                                ...styles.clock,
                                ...(secondsLeft < 300
                                    ? styles.clockUrgent
                                    : {}),
                            }}
                            data-tour="clock"
                        >
                            {countdown(secondsLeft)}
                        </span>
                    )}
                    {activeStep === STEP.REVIEW && !tour && (
                        <Button
                            size="small"
                            style={styles.tourButton}
                            onClick={() => setTour(true)}
                        >
                            Show me around
                        </Button>
                    )}
                </Toolbar>
            </AppBar>
            <DialogContent>
                <div style={styles.body}>
                    <Stepper activeStep={activeStep} style={styles.stepper}>
                        {STEPS.map(label => (
                            <Step key={label}>
                                <StepLabel>{label}</StepLabel>
                            </Step>
                        ))}
                    </Stepper>
                    {content}
                </div>
            </DialogContent>
        </Dialog>
    );
};

ListCleaningReviewDialog.defaultProps = {
    listID: null,
    resumed: false,
    data: null,
    submitError: null,
    applyError: null,
    lastApplied: null,
};

ListCleaningReviewDialog.propTypes = {
    listID: number,
    open: bool.isRequired,
    resumed: bool,
    onContinue: func.isRequired,
    data: shape({
        run: object,
        summary: object,
    }),
    submitting: bool.isRequired,
    submitError: object,
    applying: bool.isRequired,
    applyError: object,
    lastApplied: object,
    fetchCleaning: func.isRequired,
    clearCleaning: func.isRequired,
    decide: func.isRequired,
    decideGroup: func.isRequired,
    apply: func.isRequired,
};

const mapStateToProps = ({
    facilityListCleaning: {
        data,
        submitting,
        submitError,
        applying,
        applyError,
        lastApplied,
    },
}) => ({
    data,
    submitting,
    submitError,
    applying,
    applyError,
    lastApplied,
});

const mapDispatchToProps = (dispatch, { listID }) => ({
    fetchCleaning: () =>
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
    apply: (options = {}) =>
        dispatch(applyFacilityListCleaning(listID, options)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(ListCleaningReviewDialog);
