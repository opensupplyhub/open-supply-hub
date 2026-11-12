import React, { useEffect, useState } from 'react';
import {
    arrayOf,
    func,
    number,
    object,
    oneOf,
    oneOfType,
    string,
} from 'prop-types';
import { connect } from 'react-redux';
import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import Confetti from './Confetti';
import {
    pollClaimLiveCheck,
    resetClaimLiveCheck,
    runClaimLiveCheck,
} from '../../actions/claimLiveCheck';
import { claimedFacilitiesRoute, mapRoute } from '../../util/constants';
import {
    CHECKING_PROGRESS_LINES,
    CHECKING_STAY_TEXT,
    CHECK_TIMEOUT_MS,
    CHOOSE_ONE_LABEL,
    CLAIM_LIVE_CHECK_FIXES,
    CLAIM_LIVE_CHECK_STATUSES,
    FIX_THIS_LABEL,
    GO_BACK_BUTTON_TEXT,
    GO_BACK_HELPER_TEXT,
    GO_BACK_NO_CHECKS_HELPER_TEXT,
    LEAVE_BUTTON_TEXT,
    LEAVE_HELPER_TEXT,
    LEFT_FOR_REVIEW_TITLE,
    NOT_PASSED_TITLE,
    PASSED_TITLE,
    POLL_INTERVAL_MS,
    PROGRESS_LINE_INTERVAL_MS,
    UNAVAILABLE_TEXT,
    UNAVAILABLE_TITLE,
} from './constants';
import { claimLiveCheckStyles, SPINNER_SIZE_PX } from './styles';
import { makeFixLink } from './utils';

const { CHECKING, PASSED, NOT_PASSED, UNAVAILABLE } = CLAIM_LIVE_CHECK_STATUSES;

/*
 * Runs the live check of a claim that has just been submitted or
 * edited, and shows how it went (OSDEV-3805).
 *
 * The claim is already saved when this mounts, so nothing here can
 * cost the claimant their submission: a slow, failed or switched-off
 * check ends as "not available", and the claim waits for a person.
 */
const ClaimLiveCheck = ({
    classes,
    claimID,
    history,
    status,
    fixes,
    checksLeft,
    runCheck,
    pollCheck,
    resetCheck,
}) => {
    const [timedOut, setTimedOut] = useState(false);
    const [leftForReview, setLeftForReview] = useState(false);
    const [progressLine, setProgressLine] = useState(0);

    useEffect(() => {
        runCheck(claimID);
        const timeout = setTimeout(() => setTimedOut(true), CHECK_TIMEOUT_MS);
        return () => {
            clearTimeout(timeout);
            resetCheck();
        };
    }, [claimID, runCheck, resetCheck]);

    // A null status is the request that starts the check still being
    // on its way; it is shown as checking too.
    const waiting = !timedOut && (status === null || status === CHECKING);
    const polling = !timedOut && status === CHECKING;

    useEffect(() => {
        if (!polling) {
            return undefined;
        }
        const interval = setInterval(
            () => pollCheck(claimID),
            POLL_INTERVAL_MS,
        );
        return () => clearInterval(interval);
    }, [polling, claimID, pollCheck]);

    useEffect(() => {
        if (!waiting) {
            return undefined;
        }
        const interval = setInterval(
            () =>
                setProgressLine(line =>
                    Math.min(line + 1, CHECKING_PROGRESS_LINES.length - 1),
                ),
            PROGRESS_LINE_INTERVAL_MS,
        );
        return () => clearInterval(interval);
    }, [waiting]);

    const exits = (
        <div className={classes.actions}>
            <Button
                variant="contained"
                className={classes.secondaryButton}
                onClick={() => history.push(claimedFacilitiesRoute)}
            >
                To My Claims
            </Button>
            <Button
                variant="contained"
                className={classes.primaryButton}
                onClick={() => history.push(mapRoute)}
            >
                Search OS Hub
            </Button>
        </div>
    );

    if (waiting) {
        return (
            <div
                className={classes.panel}
                role="status"
                data-testid="claim-live-check-checking"
            >
                <Typography className={classes.progress}>
                    <CircularProgress
                        size={SPINNER_SIZE_PX}
                        className={classes.spinner}
                    />
                    {CHECKING_PROGRESS_LINES[progressLine]}
                </Typography>
                <Typography className={classes.text}>
                    {CHECKING_STAY_TEXT}
                </Typography>
            </div>
        );
    }

    if (leftForReview) {
        return (
            <div className={classes.panelUnavailable} role="status">
                <Typography className={classes.title}>
                    {LEFT_FOR_REVIEW_TITLE}
                </Typography>
                {exits}
            </div>
        );
    }

    if (status === PASSED) {
        return (
            <div className={classes.panelPassed} role="status">
                <Confetti />
                <Typography className={classes.title}>
                    {PASSED_TITLE}
                </Typography>
                {exits}
            </div>
        );
    }

    if (status === NOT_PASSED) {
        const canCheckAgain = checksLeft > 0;
        return (
            <div className={classes.panelNotPassed} role="status">
                <Typography className={classes.title}>
                    {NOT_PASSED_TITLE}
                </Typography>
                <Typography className={classes.label}>
                    {FIX_THIS_LABEL}
                </Typography>
                <ul className={classes.fixes}>
                    {fixes.map(fix => (
                        <li key={fix}>{CLAIM_LIVE_CHECK_FIXES[fix].text}</li>
                    ))}
                </ul>
                <Typography className={classes.label}>
                    {CHOOSE_ONE_LABEL}
                </Typography>
                <div className={classes.choices}>
                    <div className={classes.choice}>
                        <Button
                            variant="contained"
                            className={classes.primaryButton}
                            onClick={() =>
                                history.push(
                                    makeFixLink(
                                        claimID,
                                        fixes[0],
                                        canCheckAgain,
                                    ),
                                )
                            }
                        >
                            {GO_BACK_BUTTON_TEXT}
                        </Button>
                        <span>
                            {canCheckAgain
                                ? GO_BACK_HELPER_TEXT
                                : GO_BACK_NO_CHECKS_HELPER_TEXT}
                        </span>
                    </div>
                    <div className={classes.choice}>
                        <Button
                            variant="contained"
                            className={classes.secondaryButton}
                            onClick={() => setLeftForReview(true)}
                        >
                            {LEAVE_BUTTON_TEXT}
                        </Button>
                        <span>{LEAVE_HELPER_TEXT}</span>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className={classes.panelUnavailable} role="status">
            <Typography className={classes.title}>
                {UNAVAILABLE_TITLE}
            </Typography>
            <Typography className={classes.text}>{UNAVAILABLE_TEXT}</Typography>
            {exits}
        </div>
    );
};

ClaimLiveCheck.defaultProps = {
    status: null,
};

ClaimLiveCheck.propTypes = {
    classes: object.isRequired,
    claimID: oneOfType([number, string]).isRequired,
    history: object.isRequired,
    status: oneOf([CHECKING, PASSED, NOT_PASSED, UNAVAILABLE]),
    fixes: arrayOf(oneOf(Object.keys(CLAIM_LIVE_CHECK_FIXES))).isRequired,
    checksLeft: number.isRequired,
    runCheck: func.isRequired,
    pollCheck: func.isRequired,
    resetCheck: func.isRequired,
};

const mapStateToProps = ({
    claimLiveCheck: { status, fixes, checksLeft },
}) => ({
    status,
    fixes,
    checksLeft,
});

const mapDispatchToProps = dispatch => ({
    runCheck: claimID => dispatch(runClaimLiveCheck(claimID)),
    pollCheck: claimID => dispatch(pollClaimLiveCheck(claimID)),
    resetCheck: () => dispatch(resetClaimLiveCheck()),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(claimLiveCheckStyles)(ClaimLiveCheck));
