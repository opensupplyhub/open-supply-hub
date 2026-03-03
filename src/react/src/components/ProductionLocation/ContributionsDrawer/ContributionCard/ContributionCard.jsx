import React from 'react';
import { object, string, oneOfType, instanceOf, bool } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import ScheduleIcon from '@material-ui/icons/Schedule';

import { formatDisplayDate } from '../../utils';
import contributionCardStyles from './styles';

const ContributionCard = ({ classes, value, sourceName, date, promoted }) => (
    <div
        className={
            promoted
                ? `${classes.contributionCard} ${classes.contributionCardPromoted}`
                : classes.contributionCard
        }
    >
        <Typography
            className={
                promoted
                    ? `${classes.contributionValue} ${classes.contributionValuePromoted}`
                    : classes.contributionValue
            }
        >
            {value}
        </Typography>
        <div className={classes.contributionValueContainer}>
            <div className={classes.contributionSourceContainer}>
                {sourceName ? (
                    <Typography
                        className={
                            promoted
                                ? `${classes.contributionSource} ${classes.contributionSourcePromoted}`
                                : classes.contributionSource
                        }
                    >
                        {sourceName}
                    </Typography>
                ) : null}
            </div>
            <div className={classes.contributionMetaContainer}>
                {date ? (
                    <span
                        className={
                            promoted
                                ? `${classes.dateWithIcon} ${classes.dateWithIconPromoted}`
                                : classes.dateWithIcon
                        }
                    >
                        <ScheduleIcon
                            fontSize="small"
                            className={
                                promoted
                                    ? `${classes.dateIcon} ${classes.dateIconPromoted}`
                                    : classes.dateIcon
                            }
                        />
                        {formatDisplayDate(date)}
                    </span>
                ) : null}
            </div>
        </div>
    </div>
);

ContributionCard.propTypes = {
    classes: object.isRequired,
    value: string.isRequired,
    sourceName: string,
    date: oneOfType([string, instanceOf(Date)]),
    promoted: bool,
};

ContributionCard.defaultProps = {
    sourceName: null,
    date: null,
    promoted: false,
};

export default withStyles(contributionCardStyles)(ContributionCard);
