import React, { useEffect, useRef, useState } from 'react';
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
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import ClaimLiveCheckWaiting from './ClaimLiveCheckWaiting';
import Confetti from './Confetti';
import {
    giveUpClaimLiveCheck,
    pollClaimLiveCheck,
    resetClaimLiveCheck,
    runClaimLiveCheck,
} from '../../actions/claimLiveCheck';
import {
    claimedFacilitiesRoute,
    mapRoute,
    HEADER_HEIGHT,
} from '../../util/constants';
import {
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
    PANEL_SCROLL_MARGIN_PX,
    PASSED_TITLE,
    POLL_INTERVAL_MS,
    RESULT_HOLD_MS,
    UNAVAILABLE_EMAIL_TEXT,
    UNAVAILABLE_TEXT,
    UNAVAILABLE_TITLE,
} from './constants';
import { claimLiveCheckStyles } from './styles';
import {
    getContributorCount,
    makeFixLink,
    prefersReducedMotion,
} from './utils';

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
    locationName,
    contributorCount,
    runCheck,
    pollCheck,
    giveUpCheck,
    resetCheck,
    onNotStarted,
}) => {
    const [timedOut, setTimedOut] = useState(false);
    // Whether a review was really started for this check. Until then
    // nothing may be promised about it.
    const [started, setStarted] = useState(false);
    const [leftForReview, setLeftForReview] = useState(false);
    const [resultShown, setResultShown] = useState(false);
    const panelRef = useRef(null);

    useEffect(() => {
        runCheck(claimID);
        const timeout = setTimeout(() => setTimedOut(true), CHECK_TIMEOUT_MS);
        return () => {
            clearTimeout(timeout);
            resetCheck();
        };
    }, [claimID, runCheck, resetCheck]);

    useEffect(() => {
        if (status === CHECKING || status === PASSED || status === NOT_PASSED) {
            setStarted(true);
        }
    }, [status]);

    // The check could not be started: it is switched off on the server,
    // not set up, or the request failed. Nothing is being reviewed
    // right now, so the claimant must not be told about a check or an
    // email. The caller shows its usual "submitted" outcome instead.
    const notStarted = !started && (status === UNAVAILABLE || timedOut);
    useEffect(() => {
        if (notStarted && onNotStarted) {
            onNotStarted();
        }
    }, [notStarted, onNotStarted]);

    // The page has given up on a check that is still running.
    const gaveUp = timedOut && status === CHECKING;
    useEffect(() => {
        if (gaveUp) {
            giveUpCheck(claimID);
        }
    }, [gaveUp, claimID, giveUpCheck]);

    // A null status is the request that starts the check still being
    // on its way; it is shown as checking too.
    // An answer is held back for a moment so the claimant sees the bar
    // fill and the last step tick before the result replaces them.
    const hasAnswer = status === PASSED || status === NOT_PASSED;
    const waiting =
        !timedOut &&
        (status === null || status === CHECKING || (hasAnswer && !resultShown));
    const polling = !timedOut && status === CHECKING;

    // The panel replaces a long form, and the page can be scrolled so
    // that its headline sits under the site's fixed top menu. Bring it
    // into view just below the menu when it appears and whenever what
    // it shows changes.
    useEffect(() => {
        const panel = panelRef.current;
        if (!panel || typeof window.scrollTo !== 'function') {
            return;
        }
        const top =
            panel.getBoundingClientRect().top +
            (window.pageYOffset || 0) -
            HEADER_HEIGHT -
            PANEL_SCROLL_MARGIN_PX;
        window.scrollTo(0, Math.max(0, top));
    }, [waiting, leftForReview]);

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
        if (!hasAnswer) {
            setResultShown(false);
            return undefined;
        }
        if (prefersReducedMotion()) {
            setResultShown(true);
            return undefined;
        }
        const hold = setTimeout(() => setResultShown(true), RESULT_HOLD_MS);
        return () => clearTimeout(hold);
    }, [hasAnswer]);

    if (notStarted && onNotStarted) {
        return null;
    }

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
            <div ref={panelRef}>
                <ClaimLiveCheckWaiting
                    done={hasAnswer}
                    locationName={locationName}
                    contributorCount={contributorCount}
                />
            </div>
        );
    }

    if (leftForReview) {
        return (
            <div
                className={classes.panelUnavailable}
                ref={panelRef}
                role="status"
            >
                <Typography component="h2" className={classes.title}>
                    {LEFT_FOR_REVIEW_TITLE}
                </Typography>
                {exits}
            </div>
        );
    }

    if (status === PASSED) {
        return (
            <div className={classes.panelPassed} ref={panelRef} role="status">
                <Confetti />
                <Typography component="h2" className={classes.title}>
                    {PASSED_TITLE}
                </Typography>
                {exits}
            </div>
        );
    }

    if (status === NOT_PASSED) {
        const canCheckAgain = checksLeft > 0;
        return (
            <div
                className={classes.panelNotPassed}
                ref={panelRef}
                role="status"
            >
                <Typography component="h2" className={classes.title}>
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
        <div className={classes.panelUnavailable} ref={panelRef} role="status">
            <Typography component="h2" className={classes.title}>
                {UNAVAILABLE_TITLE}
            </Typography>
            <Typography className={classes.text}>{UNAVAILABLE_TEXT}</Typography>
            <Typography className={classes.text}>
                {UNAVAILABLE_EMAIL_TEXT}
            </Typography>
            {exits}
        </div>
    );
};

ClaimLiveCheck.defaultProps = {
    status: null,
    onNotStarted: null,
    locationName: '',
    contributorCount: null,
};

ClaimLiveCheck.propTypes = {
    classes: object.isRequired,
    claimID: oneOfType([number, string]).isRequired,
    history: object.isRequired,
    status: oneOf([CHECKING, PASSED, NOT_PASSED, UNAVAILABLE]),
    fixes: arrayOf(oneOf(Object.keys(CLAIM_LIVE_CHECK_FIXES))).isRequired,
    checksLeft: number.isRequired,
    locationName: string,
    contributorCount: number,
    runCheck: func.isRequired,
    pollCheck: func.isRequired,
    giveUpCheck: func.isRequired,
    onNotStarted: func,
    resetCheck: func.isRequired,
};

// The fact about the location uses what the claim form (or the pending
// claim edit page) already loaded for it. Nothing is fetched here.
const mapStateToProps = ({
    claimLiveCheck: { status, fixes, checksLeft },
    contributeProductionLocation: {
        singleProductionLocation: { data: location },
    },
}) => ({
    status,
    fixes,
    checksLeft,
    locationName: location?.name || '',
    contributorCount: getContributorCount(location),
});

const mapDispatchToProps = dispatch => ({
    runCheck: claimID => dispatch(runClaimLiveCheck(claimID)),
    pollCheck: claimID => dispatch(pollClaimLiveCheck(claimID)),
    giveUpCheck: claimID => dispatch(giveUpClaimLiveCheck(claimID)),
    resetCheck: () => dispatch(resetClaimLiveCheck()),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(claimLiveCheckStyles)(ClaimLiveCheck));
