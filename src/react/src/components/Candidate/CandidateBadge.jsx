import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import SatelliteIcon from '@material-ui/icons/Satellite';

import {
    CANDIDATE_COPY,
    CANDIDATE_STATES,
    CANDIDATE_STATE_LABELS,
} from '../../util/candidateCopy';
import { candidateBadgeStyles } from './styles';

const STATE_CLASS_KEYS = Object.freeze({
    [CANDIDATE_STATES.UNVERIFIED]: 'stateUnverified',
    [CANDIDATE_STATES.DISPUTED]: 'stateDisputed',
    [CANDIDATE_STATES.CONFIRMED]: 'stateConfirmed',
    [CANDIDATE_STATES.RETIREMENT_PENDING]: 'stateRetirementPending',
});

/**
 * "Satellite-detected candidate" pill. Interim visual (OSDEV-3192).
 */
const CandidateBadgeBase = ({ classes, className }) => (
    <span
        className={`${classes.badge} ${className || ''}`}
        data-testid="candidate-badge"
    >
        <SatelliteIcon className={classes.badgeIcon} />
        {CANDIDATE_COPY.badge}
    </span>
);

CandidateBadgeBase.propTypes = {
    classes: PropTypes.object.isRequired,
    className: PropTypes.string,
};

CandidateBadgeBase.defaultProps = {
    className: null,
};

/**
 * Validation state chip: Unverified / Disputed / Confirmed /
 * Retirement pending.
 */
const CandidateStateChipBase = ({ classes, state, className }) => {
    const stateKey = STATE_CLASS_KEYS[state]
        ? state
        : CANDIDATE_STATES.UNVERIFIED;
    return (
        <span
            className={`${classes.stateChip} ${
                classes[STATE_CLASS_KEYS[stateKey]]
            } ${className || ''}`}
            data-testid="candidate-state-chip"
            data-state={stateKey}
        >
            {CANDIDATE_STATE_LABELS[stateKey]}
        </span>
    );
};

CandidateStateChipBase.propTypes = {
    classes: PropTypes.object.isRequired,
    state: PropTypes.string,
    className: PropTypes.string,
};

CandidateStateChipBase.defaultProps = {
    state: CANDIDATE_STATES.UNVERIFIED,
    className: null,
};

export const CandidateStateChip = withStyles(candidateBadgeStyles)(
    CandidateStateChipBase,
);

export default withStyles(candidateBadgeStyles)(CandidateBadgeBase);
