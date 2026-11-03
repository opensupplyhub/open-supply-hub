import React, { useEffect, useState } from 'react';
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
    applyFacilityListCleaning,
} from '../actions/facilityListCleaning';

import {
    RUN_STATUS,
    styles as cardStyles,
    Stat,
    ListFindings,
    SuggestionRows,
} from './FacilityListCleaningSuggestions';

import COLOURS from '../util/COLOURS';

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

const Done = ({ summary, lastApplied, skipped, onContinue }) => (
    <div style={styles.centred}>
        <Typography style={styles.heading}>
            {skipped ? 'No fixes applied' : 'Fixes applied to your list'}
        </Typography>
        {!skipped && lastApplied && (
            <Typography>
                {lastApplied.applied}{' '}
                {lastApplied.applied === 1 ? 'fix was' : 'fixes were'} applied
                to your list. The original values are kept with your file.
            </Typography>
        )}
        {skipped && (
            <Typography>
                Your list was submitted as uploaded. You can still review the
                suggestions on your list page.
            </Typography>
        )}
        {summary.rows_must_fix > 0 && (
            <Typography>
                {summary.rows_must_fix}{' '}
                {summary.rows_must_fix === 1
                    ? 'row still needs'
                    : 'rows still need'}{' '}
                your attention. Fix those in your file and upload it again, or
                wait for the moderator to get in touch.
            </Typography>
        )}
        <Button variant="contained" color="primary" onClick={onContinue}>
            Go to my list
        </Button>
    </div>
);

Done.defaultProps = { lastApplied: null };

Done.propTypes = {
    summary: object.isRequired,
    lastApplied: object,
    skipped: bool.isRequired,
    onContinue: func.isRequired,
};

const ListCleaningReviewDialog = ({
    listID,
    open,
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
    apply,
}) => {
    const [openedAt, setOpenedAt] = useState(null);
    const [timedOut, setTimedOut] = useState(false);
    const [finished, setFinished] = useState(null); // 'applied' | 'skipped'

    useEffect(() => {
        if (!open || !listID) {
            return undefined;
        }
        setOpenedAt(Date.now());
        setTimedOut(false);
        setFinished(null);
        fetchCleaning();
        return () => clearCleaning();
    }, [open, listID, fetchCleaning, clearCleaning]);

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
            fetchCleaning();
        }, POLL_INTERVAL_MS);
        return () => clearInterval(timer);
    }, [waiting, openedAt, fetchCleaning]);

    useEffect(() => {
        if (lastApplied) {
            setFinished('applied');
        }
    }, [lastApplied]);

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
                summary={summary}
                lastApplied={lastApplied}
                skipped={finished === 'skipped'}
                onContinue={onContinue}
            />
        );
    } else if (nothingFound) {
        activeStep = STEP.DONE;
        content = <Clean onContinue={onContinue} />;
    } else {
        activeStep = STEP.REVIEW;
        content = (
            <>
                <Typography style={styles.heading}>
                    We found some things to check before your list goes to a
                    moderator
                </Typography>
                <div style={cardStyles.statRow}>
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
                </div>
                <div style={cardStyles.disclaimer}>
                    These are automated suggestions, not decisions. You are
                    responsible for the data you submit: accept a fix only if it
                    is correct for that facility. Facility names and addresses
                    are never changed automatically. Rows that need your
                    attention cannot be fixed here; correct them in your file
                    and upload it again. A moderator will still review the list
                    before anything is published.
                </div>
                <ListFindings filePass={run.file_pass || {}} />
                <SuggestionRows
                    rows={rows}
                    canAct
                    busy={busy}
                    decide={decide}
                />
                <div style={styles.actions}>
                    {(submitError || applyError) && (
                        <Typography style={styles.error}>
                            {(submitError || applyError).join(' ')}
                        </Typography>
                    )}
                    {busy && <CircularProgress size={22} />}
                    <Button
                        color="primary"
                        disabled={busy}
                        onClick={() => setFinished('skipped')}
                    >
                        Continue without applying
                    </Button>
                    <Button
                        variant="contained"
                        color="primary"
                        disabled={busy || summary.corrections_unapplied === 0}
                        onClick={apply}
                    >
                        Apply {summary.corrections_unapplied} accepted{' '}
                        {summary.corrections_unapplied === 1 ? 'fix' : 'fixes'}{' '}
                        and continue
                    </Button>
                </div>
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
    data: null,
    submitError: null,
    applyError: null,
    lastApplied: null,
};

ListCleaningReviewDialog.propTypes = {
    listID: number,
    open: bool.isRequired,
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
    apply: () => dispatch(applyFacilityListCleaning(listID)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(ListCleaningReviewDialog);
