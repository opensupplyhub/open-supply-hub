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
    submitFacilityListCleaningGroupDecisions,
    applyFacilityListCleaning,
} from '../actions/facilityListCleaning';

import {
    RUN_STATUS,
    styles as cardStyles,
    Stat,
    ListFindings,
    GroupList,
    DownloadFixedList,
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

const Done = ({ listID, summary, lastApplied, skipped, onContinue }) => (
    <div style={styles.centred}>
        <Typography style={styles.heading}>
            {skipped ? 'No changes applied' : 'Your list has been updated'}
        </Typography>
        {!skipped && lastApplied && (
            <Typography>
                {lastApplied.applied}{' '}
                {lastApplied.applied === 1 ? 'change was' : 'changes were'}{' '}
                applied to your list
                {summary.rows_removed
                    ? `, including ${summary.rows_removed} ${
                          summary.rows_removed === 1 ? 'row' : 'rows'
                      } removed`
                    : ''}
                . The original values are kept with your uploaded file, and a
                moderator will review the list as usual.
            </Typography>
        )}
        {skipped && (
            <Typography>
                Your list was submitted as uploaded. You can still review the
                suggestions on your list page.
            </Typography>
        )}
        {summary.must_fix_pending > 0 && (
            <Typography>
                {summary.must_fix_pending}{' '}
                {summary.must_fix_pending === 1
                    ? 'row still needs'
                    : 'rows still need'}{' '}
                your attention. You can fix or remove them from your list page
                at any time before a moderator reviews the list.
            </Typography>
        )}
        <div style={styles.actions}>
            <DownloadFixedList listID={listID} applied={!skipped} />
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
    decideGroup,
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
                listID={listID}
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
                    A few changes would make your list more likely to be
                    approved
                </Typography>
                <Typography>
                    We checked every row. The findings are grouped by type
                    because the same problem usually repeats through a file:
                    accept or reject a whole group, or open its rows to decide
                    one by one. Rows we could not fix can be corrected or
                    removed right here, with no need to upload again.
                </Typography>
                <div style={cardStyles.statRow}>
                    <Stat
                        value={summary.must_fix_pending}
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
                    are never changed automatically. A moderator will still
                    review the list before anything is published, and applying
                    these changes makes approval more likely.
                </div>
                <ListFindings filePass={run.file_pass || {}} />
                <GroupList
                    groups={data.groups || []}
                    rows={rows}
                    canAct
                    busy={busy}
                    decide={decide}
                    decideGroup={decideGroup}
                />
                <div style={styles.actions}>
                    {(submitError || applyError) && (
                        <Typography style={styles.error}>
                            {(submitError || applyError).join(' ')}
                        </Typography>
                    )}
                    {busy && <CircularProgress size={22} />}
                    <DownloadFixedList
                        listID={listID}
                        applied={!!run.applied_at}
                    />
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
                        disabled={busy || summary.changes_unapplied === 0}
                        onClick={apply}
                    >
                        Apply {summary.changes_unapplied}{' '}
                        {summary.changes_unapplied === 1 ? 'change' : 'changes'}{' '}
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
    decideGroup: (key, decision) =>
        dispatch(
            submitFacilityListCleaningGroupDecisions(listID, [
                { key, decision },
            ]),
        ),
    apply: () => dispatch(applyFacilityListCleaning(listID)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(ListCleaningReviewDialog);
