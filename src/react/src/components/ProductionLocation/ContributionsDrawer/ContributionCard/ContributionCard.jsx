import React from 'react';
import {
    object,
    string,
    oneOfType,
    instanceOf,
    bool,
    number,
} from 'prop-types';
import { Link } from 'react-router-dom';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import ScheduleIcon from '@material-ui/icons/Schedule';
import OpenInNewIcon from '@material-ui/icons/OpenInNew';

import { makeProfileRouteLink } from '../../../../util/util';
import formatDisplayDate from '../../utils';
import contributionCardStyles from './styles';

const ContributionCard = ({
    classes,
    value,
    sourceName,
    date,
    promoted,
    contributorId,
}) => (
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
                {sourceName &&
                    (contributorId != null ? (
                        <Link
                            to={makeProfileRouteLink(contributorId)}
                            className={
                                promoted
                                    ? `${classes.contributionSourceLink} ${classes.contributionSourceLinkPromoted}`
                                    : classes.contributionSourceLink
                            }
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            {sourceName}
                            <OpenInNewIcon
                                className={
                                    promoted
                                        ? `${classes.contributionSourceIcon} ${classes.contributionSourceIconPromoted}`
                                        : classes.contributionSourceIcon
                                }
                                aria-hidden
                            />
                        </Link>
                    ) : (
                        <Typography
                            className={
                                promoted
                                    ? `${classes.contributionSource} ${classes.contributionSourcePromoted}`
                                    : classes.contributionSource
                            }
                        >
                            {sourceName}
                        </Typography>
                    ))}
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
    contributorId: oneOfType([string, number]),
};

ContributionCard.defaultProps = {
    sourceName: null,
    date: null,
    promoted: false,
    contributorId: null,
};

export default withStyles(contributionCardStyles)(ContributionCard);
