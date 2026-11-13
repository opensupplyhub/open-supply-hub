import React, { useEffect, useRef, useState } from 'react';
import { bool, func, number, object, shape } from 'prop-types';
import { connect } from 'react-redux';
import AppBar from '@material-ui/core/AppBar';
import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
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
    ReadinessTracker,
    ListFindings,
    GroupTabs,
    DownloadFixedList,
    plural,
} from './FacilityListCleaningSuggestions';

import COLOURS from '../util/COLOURS';
import ListCleaningTour from './ListCleaningTour';

const timeOfDay = iso =>
    new Date(iso).toLocaleTimeString(undefined, {
        hour: 'numeric',
        minute: '2-digit',
    });

// "9:54 AM" today, or "Nov 7, 12:30 AM" if the hour runs past midnight.
const deadlineText = iso => {
    const d = new Date(iso);
    const sameDay = d.toDateString() === new Date().toDateString();
    return d.toLocaleString(undefined, {
        hour: 'numeric',
        minute: '2-digit',
        ...(sameDay ? {} : { month: 'short', day: 'numeric' }),
    });
};

const countdown = seconds => {
    if (seconds <= 0) return 'Time is up';
    if (seconds < 120) return `Submit within ${seconds} s`;
    return `Submit within ${Math.ceil(seconds / 60)} min`;
};

// The contributor is waiting on this screen, so poll faster than the
// list-page panel does, and stop pretending after a while.
const POLL_INTERVAL_MS = 3000;
const MAX_WAIT_MS = 3 * 60 * 1000;

// The upload as four steps, so the review reads as one of them; the
// note under the bar says a human moderator still checks the list after
// the contributor submits.
const STEPS = Object.freeze([
    'Upload file',
    'Automatic checks',
    'Review issues',
    'Submit for manual review',
]);

// Published processing times, linked from the done screen.
const PROCESSING_TIMES_URL =
    'https://info.opensupplyhub.org/resources/data-processing-timelines';

const STEP = Object.freeze({
    UPLOAD: 0,
    CHECKS: 1,
    REVIEW: 2,
    SUBMIT: 3,
});

// Warn before a submission that leaves many rows a human moderator would
// have to remove: more than this many, or more than this share of the
// list. A submission as uploaded always gets a warning while anything is
// still flagged.
const REMOVABLE_ROWS_WARN_COUNT = 25;
const REMOVABLE_ROWS_WARN_SHARE = 0.15;

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
    next: Object.freeze({
        textAlign: 'left',
        maxWidth: '560px',
        padding: '12px 20px',
        borderRadius: '6px',
        background: '#F0F4FF',
    }),
    nextTitle: Object.freeze({
        fontWeight: 700,
        marginBottom: '4px',
    }),
    introList: Object.freeze({
        margin: '8px 0',
        padding: '0 0 0 20px',
    }),
    doneList: Object.freeze({
        textAlign: 'left',
        maxWidth: '560px',
        margin: 0,
        padding: '0 0 0 20px',
    }),
    warnTitle: Object.freeze({
        fontSize: '1.2rem',
        fontWeight: 700,
        marginBottom: '8px',
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
        padding: '0 16px',
    }),
    content: Object.freeze({
        // No padding of its own: the sticky footer should meet the
        // bottom edge, and the body supplies the side gutters.
        padding: 0,
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
            Your file has been uploaded. We are checking every row for issues
            that need your review before a human moderator sees it. This usually
            takes a few minutes.
        </Typography>
        {timedOut && (
            <Typography>
                This is taking longer than usual. You can continue to your list
                now and the issues will appear there when they are ready.
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
            uploaded and a human moderator will review it as usual.
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
            We found nothing to fix, so your list has gone straight to a human
            moderator as uploaded.
        </Typography>
        <Button variant="contained" color="primary" onClick={onContinue}>
            Go to my list
        </Button>
        <WhatHappensNext />
    </div>
);

Clean.propTypes = { onContinue: func.isRequired };

const WhatHappensNext = () => (
    <div style={styles.next}>
        <Typography style={styles.nextTitle}>What happens next</Typography>
        <Typography>
            A member of our moderation team will review your list manually
            before it is published on OS Hub. See our{' '}
            <a
                href={PROCESSING_TIMES_URL}
                target="_blank"
                rel="noopener noreferrer"
            >
                standard processing times
            </a>
            .
        </Typography>
        <Typography>
            We&rsquo;ll email you at the address registered to this account when
            your list is approved, or sooner if anything needs to change.
        </Typography>
    </div>
);

const Done = ({ listID, summary, lastApplied, asUploaded, onContinue }) => {
    const flagged = summary.rows_flagged_unresolved || 0;
    const removedNote = summary.rows_removed
        ? `, including ${plural(summary.rows_removed, 'row')} removed`
        : '';
    return (
        <div style={styles.centred}>
            <Typography style={styles.heading}>
                Your list has been submitted for review
            </Typography>
            <ul style={styles.doneList}>
                {!asUploaded && lastApplied && (
                    <li>
                        {lastApplied.applied}{' '}
                        {lastApplied.applied === 1 ? 'fix was' : 'fixes were'}{' '}
                        applied to your list{removedNote}. Your original values
                        are still in the file you uploaded.
                    </li>
                )}
                {asUploaded && (
                    <li>
                        It went exactly as uploaded; none of the fixes were
                        applied.
                    </li>
                )}
                {flagged > 0 && (
                    <li>
                        {flagged}{' '}
                        {flagged === 1
                            ? 'row still has a required fix'
                            : 'rows still have required fixes'}{' '}
                        and went through as uploaded. The moderator will decide
                        on {flagged === 1 ? 'it' : 'them'}, and may ask you for
                        a corrected upload.
                    </li>
                )}
                <li>
                    No further changes can be made here. To see the status of
                    your list, go to your list page.
                </li>
            </ul>
            <WhatHappensNext />
            <div style={styles.actions}>
                <DownloadFixedList listID={listID} applied={!asUploaded} />
                <Button
                    variant="contained"
                    color="primary"
                    onClick={onContinue}
                >
                    Go to my list
                </Button>
            </div>
        </div>
    );
};

Done.defaultProps = { lastApplied: null };

Done.propTypes = {
    listID: number.isRequired,
    summary: object.isRequired,
    lastApplied: object,
    asUploaded: bool.isRequired,
    onContinue: func.isRequired,
};

const closedText = (run, summary) => {
    const applied = summary?.changes_applied;
    if (run.closed_reason !== 'submitted') {
        const how = applied
            ? ` with the ${plural(applied, 'change')} you had decided by then`
            : ' exactly as uploaded';
        return `The hour for changes ended at ${timeOfDay(
            run.closed_at,
        )}, so the list went to a human moderator${how}.`;
    }
    const how = applied ? ` with ${plural(applied, 'change')}` : ' as uploaded';
    return `You submitted it at ${timeOfDay(
        run.submitted_at,
    )}${how}. No further changes are possible.`;
};

// Reopened after the window closed: nothing to decide any more.
const Closed = ({ run, summary, onContinue }) => (
    <div style={styles.centred}>
        <Typography style={styles.heading}>
            {run.closed_reason === 'submitted'
                ? 'This list has already been submitted'
                : 'The review window has closed'}
        </Typography>
        <Typography>{closedText(run, summary)}</Typography>
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

// Warn before a submission a human moderator is unlikely to approve as
// it stands: many flagged rows left, or nothing changed at all.
const SubmitWarning = ({ warn, summary, busy, onClose, onConfirm }) => (
    <Dialog
        open={!!warn}
        onClose={onClose}
        aria-labelledby="list-cleaning-submit-warning"
    >
        <DialogContent>
            {warn?.asUploaded ? (
                <>
                    <Typography
                        id="list-cleaning-submit-warning"
                        style={styles.warnTitle}
                    >
                        We may not be able to approve your list
                    </Typography>
                    <Typography>
                        If you continue without making the required changes, we
                        may not be able to approve your list and publish your
                        data to OS Hub.
                    </Typography>
                </>
            ) : (
                <>
                    <Typography
                        id="list-cleaning-submit-warning"
                        style={styles.warnTitle}
                    >
                        {summary.rows_flagged_unresolved === 1
                            ? '1 row still has a required fix'
                            : `${summary.rows_flagged_unresolved} rows still have required fixes`}
                    </Typography>
                    <Typography>
                        That is{' '}
                        {Math.round(
                            (100 * summary.rows_flagged_unresolved) /
                                Math.max(1, summary.rows_total),
                        )}
                        % of your list: personal information, PO Box addresses,
                        missing or unreadable details. Without these fixes, the
                        moderator won&rsquo;t be able to approve those rows, and
                        lists with this many are much less likely to be approved
                        as a whole. Fixing or removing them here first takes a
                        minute per type.
                    </Typography>
                </>
            )}
        </DialogContent>
        <DialogActions>
            <Button disabled={busy} onClick={onConfirm}>
                Continue anyway
            </Button>
            <Button variant="contained" color="primary" onClick={onClose}>
                Go back and fix
            </Button>
        </DialogActions>
    </Dialog>
);

SubmitWarning.defaultProps = { warn: null };
SubmitWarning.propTypes = {
    warn: shape({ asUploaded: bool }),
    summary: object.isRequired,
    busy: bool.isRequired,
    onClose: func.isRequired,
    onConfirm: func.isRequired,
};

// The review itself: intro, tracker, chips and rows, the footer with
// the one submission, and the walkthrough.
const ReviewStep = ({ review }) => {
    const {
        listID,
        run,
        summary,
        data,
        rows,
        busy,
        decide,
        decideGroup,
        showAuto,
        setShowAuto,
        submitError,
        applyError,
        leave,
        trySubmit,
        doSubmit,
        warn,
        setWarn,
        tour,
        dismissTour,
    } = review;
    const submitLabel = `Apply ${plural(
        summary.changes_unapplied || 0,
        'change',
    )} and submit`;
    return (
        <>
            <Typography style={styles.muted}>
                After you submit, a human moderator from our team reviews your
                list before it is published.
            </Typography>
            <Typography style={styles.heading}>
                A few issues in your list need your review
            </Typography>
            <Typography>
                We ran automated checks on every row of your list and found some
                issues that need your review before you submit.
            </Typography>
            <ul style={styles.introList}>
                <li>
                    Formatting issues that didn&rsquo;t need your input were
                    fixed automatically. You can undo any of those fixes.
                </li>
                <li>
                    Required fixes must be made before we can approve your list.
                </li>
                <li>
                    Recommended fixes improve your data but won&rsquo;t stop
                    approval.
                </li>
                <li>
                    Accept a fix only if it is correct for that facility. We
                    never change facility names or addresses automatically.
                </li>
            </ul>
            <Typography>
                Nothing changes on your list until you press Apply. You can
                submit once, by {timeOfDay(run.review_until)}.
            </Typography>
            <ReadinessTracker
                summary={summary}
                applied={!!run.applied_at}
                showingAuto={showAuto}
                onViewFixes={() => setShowAuto(s => !s)}
            />
            <ListFindings filePass={run.file_pass || {}} />
            <GroupTabs
                groups={data.groups || []}
                rows={rows}
                canAct
                busy={busy}
                decide={decide}
                decideGroup={decideGroup}
                showAuto={showAuto}
                onShowAuto={setShowAuto}
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
                        onClick={() => trySubmit(true)}
                    >
                        Continue with no changes
                    </Button>
                )}
                <Button
                    variant="contained"
                    color="primary"
                    disabled={busy}
                    onClick={() => trySubmit(summary.changes_unapplied === 0)}
                >
                    {submitLabel}
                </Button>
                <span style={styles.finalNote}>
                    This is your one submission. You can come back and review
                    until {deadlineText(run.review_until)}; after that, the list
                    goes to a human moderator with whatever you have decided by
                    then.
                </span>
            </div>
            {tour && <ListCleaningTour onDone={dismissTour} />}
            <SubmitWarning
                warn={warn}
                summary={summary}
                busy={busy}
                onClose={() => setWarn(null)}
                onConfirm={() => {
                    const choice = warn;
                    setWarn(null);
                    doSubmit(choice.asUploaded);
                }}
            />
        </>
    );
};

ReviewStep.propTypes = { review: object.isRequired };

/*
 * The review window as this browser sees it: a deadline set from the
 * server's count, a once-a-second clock while the window is open, and
 * one more fetch when it runs out so the server can close the run and
 * the screen follow.
 */
const useReviewClock = (data, finished, fetchRef) => {
    const [deadline, setDeadline] = useState(null);
    const [now, setNow] = useState(Date.now());
    useEffect(() => {
        if (data?.run?.status === RUN_STATUS.COMPLETE) {
            setDeadline(Date.now() + (data.seconds_left || 0) * 1000);
        }
    }, [data]);
    const windowOpen = !!data?.window_open;
    useEffect(() => {
        if (!windowOpen || finished) return undefined;
        const timer = setInterval(() => {
            setNow(Date.now());
            if (deadline && Date.now() >= deadline) fetchRef.current();
        }, 1000);
        return () => clearInterval(timer);
    }, [windowOpen, finished, deadline, fetchRef]);
    const secondsLeft = deadline
        ? Math.max(0, Math.round((deadline - now) / 1000))
        : 0;
    return { windowOpen, secondsLeft };
};

/*
 * Metrics: one "opened"/"resumed" per visit, "left" when they go
 * without submitting by closing the tab (the button records its own).
 */
const useReviewEvents = ({ listID, resumed, reviewing, openedAt, data }) => {
    const [reported, setReported] = useState(false);
    useEffect(() => {
        if (!reviewing) setReported(false);
    }, [reviewing]);
    const secondsAtOpen = data?.seconds_left ?? null;
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
    const [warn, setWarn] = useState(null); // { asUploaded } while shown
    const [showAuto, setShowAuto] = useState(false);
    // The walkthrough: null until the data is in, then open the first time
    // this user reaches the review (see dismissTour below).
    const [tour, setTour] = useState(null);

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
        setTour(null);
        fetchRef.current();
        return () => clearRef.current();
    }, [open, listID]);

    const run = data?.run;
    const runStatus = run?.status ?? null;
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

    // The Done screen waits for the server: a failed submission keeps
    // the review on screen with its error and the buttons to retry.
    const asUploadedRef = useRef(false);
    useEffect(() => {
        if (lastApplied) {
            setFinished(
                f => f || (asUploadedRef.current ? 'uploaded' : 'submitted'),
            );
        }
    }, [lastApplied]);

    const { windowOpen, secondsLeft } = useReviewClock(
        data,
        finished,
        fetchRef,
    );

    const reviewing = windowOpen && !finished && !!data?.summary;
    useReviewEvents({ listID, resumed, reviewing, openedAt, data });
    const doSubmit = asUploaded => {
        asUploadedRef.current = asUploaded;
        apply(asUploaded ? { asUploaded: true } : undefined);
    };
    // A list that still has many rows a human moderator would remove is
    // much less likely to be approved as a whole: say so before it goes.
    // Submitting as uploaded while anything is flagged gets a warning
    // whatever the count.
    const trySubmit = asUploaded => {
        const current = data ? data.summary : null;
        const pendingRows = current ? current.rows_flagged_unresolved || 0 : 0;
        const total = current ? current.rows_total || 0 : 0;
        const risky =
            pendingRows > REMOVABLE_ROWS_WARN_COUNT ||
            (total > 0 && pendingRows / total > REMOVABLE_ROWS_WARN_SHARE);
        if (risky || (asUploaded && pendingRows > 0)) {
            setWarn({ asUploaded });
            return;
        }
        doSubmit(asUploaded);
    };
    const leave = () => {
        recordFacilityListCleaningEvent(listID, 'left', {
            via: 'button',
            seconds_open: openedAt
                ? Math.round((Date.now() - openedAt) / 1000)
                : null,
        });
        onContinue();
    };

    // The walkthrough opens by itself the first time this user reaches
    // the review. Closing it is recorded against the user (a
    // tour_dismissed event), so later reviews start without it and the
    // header button brings it back.
    const tourSeen = !!data?.tour_seen;
    const hasSummary = !!data?.summary;
    useEffect(() => {
        if (tour === null && hasSummary) setTour(!tourSeen);
    }, [tour, hasSummary, tourSeen]);
    const tourRecorded = useRef(false);
    const dismissTour = how => {
        setTour(false);
        if (tourSeen || tourRecorded.current) return;
        tourRecorded.current = true;
        recordFacilityListCleaningEvent(listID, 'tour_dismissed', {
            how: typeof how === 'string' ? how : 'closed',
        });
    };
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
        activeStep = STEP.SUBMIT;
        content = (
            <Done
                listID={listID}
                summary={summary}
                lastApplied={lastApplied}
                asUploaded={finished === 'uploaded'}
                onContinue={onContinue}
            />
        );
    } else if (nothingFound) {
        activeStep = STEP.SUBMIT;
        content = <Clean onContinue={onContinue} />;
    } else if (!windowOpen) {
        activeStep = STEP.SUBMIT;
        content = (
            <Closed run={run} summary={summary} onContinue={onContinue} />
        );
    } else {
        activeStep = STEP.REVIEW;
        content = (
            <ReviewStep
                review={{
                    listID,
                    run,
                    summary,
                    data,
                    rows,
                    busy,
                    decide,
                    decideGroup,
                    showAuto,
                    setShowAuto,
                    submitError,
                    applyError,
                    leave,
                    trySubmit,
                    doSubmit,
                    warn,
                    setWarn,
                    tour,
                    dismissTour,
                }}
            />
        );
    }

    return (
        <Dialog fullScreen open={open} aria-labelledby="list-cleaning-review">
            <AppBar style={styles.appBar}>
                <Toolbar>
                    <Typography id="list-cleaning-review" style={styles.title}>
                        Review your list before it goes to a human moderator
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
            <DialogContent style={styles.content}>
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
    // decision: it clears that type's row-by-row decisions. With
    // `everyRow`, the row-by-row decisions are cleared first so the
    // decision covers every row of the type.
    decideGroup: (keys, decision, everyRow = false) =>
        dispatch(
            submitFacilityListCleaningGroupDecisions(
                listID,
                [keys].flat().reduce((acc, key) => {
                    if (decision === RESET) {
                        return acc.concat({ key, reset: true });
                    }
                    if (everyRow) acc.push({ key, reset: true });
                    return acc.concat({ key, decision });
                }, []),
            ),
        ),
    apply: (options = {}) =>
        dispatch(applyFacilityListCleaning(listID, options)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(ListCleaningReviewDialog);
