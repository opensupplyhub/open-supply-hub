import React from 'react';
import PropTypes from 'prop-types';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import { withStyles } from '@material-ui/core/styles';

import OpenInNewIcon from '@material-ui/icons/OpenInNew';
import ScheduleIcon from '@material-ui/icons/Schedule';

import formatContributionDate from './utils';
import styles from './styles';

const ContributionCard = ({ classes, value, sourceName, date, linkUrl }) => (
    <div className={classes.contributionCard}>
        <Typography className={classes.contributionValue}>{value}</Typography>
        {sourceName ? (
            <Typography className={classes.contributionSource}>
                {sourceName}
            </Typography>
        ) : null}
        <div className={classes.contributionMeta}>
            {date ? (
                <span className={classes.dateWithIcon}>
                    <ScheduleIcon
                        fontSize="small"
                        className={classes.dateIcon}
                    />
                    {formatContributionDate(date)}
                </span>
            ) : null}
            {linkUrl ? (
                <IconButton
                    className={classes.contributionLink}
                    component="a"
                    href={linkUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label="Open in new tab"
                    size="small"
                >
                    <OpenInNewIcon fontSize="small" />
                </IconButton>
            ) : null}
        </div>
    </div>
);

ContributionCard.propTypes = {
    classes: PropTypes.object.isRequired,
    value: PropTypes.string.isRequired,
    sourceName: PropTypes.string,
    date: PropTypes.oneOfType([PropTypes.string, PropTypes.instanceOf(Date)]),
    linkUrl: PropTypes.string,
};

ContributionCard.defaultProps = {
    sourceName: null,
    date: null,
    linkUrl: null,
};

export default withStyles(styles)(ContributionCard);
