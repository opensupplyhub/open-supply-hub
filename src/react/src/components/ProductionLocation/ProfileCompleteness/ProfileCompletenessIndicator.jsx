import React from 'react';
import { func, number, object, shape } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';

import { PROFILE_COMPLETENESS_LABEL } from './constants';
import { formatLevel } from './utils';
import profileCompletenessStyles from './styles';

/*
The header indicator: one to three filled bars under the claim status,
which stays the most prominent status on the page. Clicking it opens the
breakdown below the header.
*/
const ProfileCompletenessIndicator = ({ classes, score, onClick }) => {
    if (!score?.level) {
        return null;
    }

    const { level, max_level: maxLevel } = score;
    const bars = Array.from({ length: maxLevel }, (_, index) => index + 1);

    return (
        <button
            type="button"
            className={classes.indicator}
            onClick={onClick}
            aria-label={`${PROFILE_COMPLETENESS_LABEL}: ${formatLevel(
                level,
                maxLevel,
            )}. Show how it is calculated.`}
            data-testid="profile-completeness-indicator"
        >
            <span className={classes.bars} aria-hidden="true">
                {bars.map(bar => (
                    <span
                        key={bar}
                        className={[
                            classes.bar,
                            classes[`barHeight${bar}`],
                            bar <= level ? classes.barFilled : '',
                        ]
                            .filter(Boolean)
                            .join(' ')}
                        data-testid={
                            bar <= level
                                ? 'profile-completeness-bar-filled'
                                : 'profile-completeness-bar-empty'
                        }
                    />
                ))}
            </span>
            <span className={classes.indicatorLabel}>
                {PROFILE_COMPLETENESS_LABEL}
            </span>
        </button>
    );
};

ProfileCompletenessIndicator.propTypes = {
    classes: object.isRequired,
    score: shape({
        level: number,
        max_level: number,
    }),
    onClick: func,
};

ProfileCompletenessIndicator.defaultProps = {
    score: null,
    onClick: () => {},
};

export default withStyles(profileCompletenessStyles)(
    ProfileCompletenessIndicator,
);
