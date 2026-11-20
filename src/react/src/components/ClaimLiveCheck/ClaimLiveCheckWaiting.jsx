import React, { useEffect, useMemo, useState } from 'react';
import { bool, number, object, string } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import {
    CHECKING_BAR_LABEL,
    CHECKING_LEAVE_TEXT,
    CHECKING_STAY_TEXT,
    CHECKING_STEPS,
    CHECKING_TITLE,
    FACT_INTERVAL_MS,
    WAITING_TICK_MS,
} from './constants';
import { waitingStyles } from './styles';
import {
    getCheckingFacts,
    getCheckingProgress,
    getCheckingStepStates,
    STEP_STATES,
} from './utils';

const STEP_STATE_LABELS = Object.freeze({
    [STEP_STATES.DONE]: 'Done',
    [STEP_STATES.NOW]: 'In progress',
    [STEP_STATES.WAITING]: 'Not started',
});

// Nothing in here is a live region: the bar, the steps and the facts
// change too often and would flood a screen reader.
const ClaimLiveCheckWaiting = ({
    classes,
    done,
    locationName,
    contributorCount,
}) => {
    const [elapsedMs, setElapsedMs] = useState(0);

    useEffect(() => {
        if (done) {
            return undefined;
        }
        const startedAt = Date.now();
        const interval = setInterval(
            () => setElapsedMs(Date.now() - startedAt),
            WAITING_TICK_MS,
        );
        return () => clearInterval(interval);
    }, [done]);

    const facts = useMemo(
        () => getCheckingFacts(locationName, contributorCount),
        [locationName, contributorCount],
    );

    const progress = getCheckingProgress(elapsedMs, done);
    const stepStates = getCheckingStepStates(elapsedMs, done);
    const fact = facts[Math.floor(elapsedMs / FACT_INTERVAL_MS) % facts.length];

    return (
        <div className={classes.panel} data-testid="claim-live-check-checking">
            <Typography component="h2" className={classes.title}>
                {CHECKING_TITLE}
            </Typography>
            <Typography className={classes.text}>
                {CHECKING_STAY_TEXT}
            </Typography>
            <div
                className={classes.bar}
                role="progressbar"
                aria-label={CHECKING_BAR_LABEL}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={progress}
            >
                <div
                    className={classes.barFill}
                    style={{ width: `${progress}%` }}
                />
            </div>
            <ul className={classes.steps}>
                {CHECKING_STEPS.map((step, index) => {
                    const state = stepStates[index];
                    const dotClass = {
                        [STEP_STATES.DONE]: classes.dotDone,
                        [STEP_STATES.NOW]: classes.dotNow,
                        [STEP_STATES.WAITING]: classes.dot,
                    }[state];
                    return (
                        <li
                            key={step.label}
                            className={
                                state === STEP_STATES.WAITING
                                    ? classes.step
                                    : classes.stepActive
                            }
                            data-step-state={state}
                        >
                            <span className={dotClass} aria-hidden="true">
                                {state === STEP_STATES.DONE ? '✓' : ''}
                            </span>
                            <span>
                                {step.label}
                                <span className={classes.visuallyHidden}>
                                    {` (${STEP_STATE_LABELS[state]})`}
                                </span>
                            </span>
                        </li>
                    );
                })}
            </ul>
            <div
                className={classes.fact}
                aria-live="off"
                data-testid="claim-live-check-fact"
            >
                <span className={classes.factLabel}>{fact.label}</span>
                <span>{fact.text}</span>
            </div>
            <Typography className={classes.leaveText}>
                {CHECKING_LEAVE_TEXT}
            </Typography>
        </div>
    );
};

ClaimLiveCheckWaiting.defaultProps = {
    done: false,
    locationName: '',
    contributorCount: null,
};

ClaimLiveCheckWaiting.propTypes = {
    classes: object.isRequired,
    done: bool,
    locationName: string,
    contributorCount: number,
};

export default withStyles(waitingStyles)(ClaimLiveCheckWaiting);
