import React from 'react';
import {
    object,
    string,
    oneOfType,
    node,
    instanceOf,
    oneOf,
    func,
    number,
} from 'prop-types';
import Typography from '@material-ui/core/Typography';
import Chip from '@material-ui/core/Chip';
import Grid from '@material-ui/core/Grid';
import { withStyles } from '@material-ui/core/styles';
import { Link } from 'react-router-dom';
import ScheduleIcon from '@material-ui/icons/Schedule';
import PersonIcon from '@material-ui/icons/PersonOutline';

import IconComponent from '../../Shared/IconComponent/IconComponent';
import { profileRoute, DATE_FORMATS } from '../../../util/constants';
import { formatDate } from '../../../util/util';
import { getContributionsCount } from '../ContributionsDrawer/utils';
import SourcesButton from './SourcesButton/SourcesButton';
import { STATUS_CLAIMED, STATUS_CROWDSOURCED } from './constants';
import dataPointStyles from './styles';

const DataPoint = ({
    classes,
    label,
    value,
    tooltipText,
    statusLabel,
    contributorName,
    userId,
    date,
    drawerData,
    onOpenDrawer,
}) => {
    const sourcesCount = getContributionsCount(drawerData?.contributions);
    const showSourcesButton = sourcesCount > 0 && onOpenDrawer;
    const statusChipClass =
        statusLabel === STATUS_CLAIMED
            ? classes.claimedChip
            : statusLabel === STATUS_CROWDSOURCED
              ? classes.crowdsourcedChip
              : null;

    const tooltipIcon = tooltipText ? (
        <IconComponent title={tooltipText} className={classes.tooltipIcon} />
    ) : null;

    return (
        <Grid container className={classes.root} data-testid="data-point">
            <Grid item container className={classes.labelColumn}>
                <Grid item className={classes.labelItem}>
                    <Typography
                        className={classes.label}
                        variant="body2"
                        data-testid="data-point-label"
                    >
                        {label}
                    </Typography>
                </Grid>
                <Grid item className={classes.tooltipIconItem}>
                    {tooltipIcon}
                </Grid>
            </Grid>
            <Grid item container className={classes.valueColumn}>
                <Grid item className={classes.valueWithTooltip}>
                    <Typography
                        className={classes.value}
                        variant="body1"
                        data-testid="data-point-value"
                    >
                        {value}
                    </Typography>
                </Grid>
                <Grid item container className={classes.metaRowWrapper}>
                    <Grid item container className={classes.metaRow}>
                        {statusLabel && (
                            <Grid item>
                                <Chip
                                    label={statusLabel}
                                    size="small"
                                    className={`${classes.statusChip} ${
                                        statusChipClass || ''
                                    }`}
                                    data-testid="data-point-status-chip"
                                />
                            </Grid>
                        )}
                        {contributorName && (
                            <Grid item>
                                <span
                                    className={classes.contributor}
                                    data-testid="data-point-contributor"
                                >
                                    <PersonIcon
                                        fontSize="small"
                                        className={classes.personIcon}
                                    />
                                    {userId != null ? (
                                        <Link
                                            to={profileRoute.replace(
                                                ':id',
                                                String(userId),
                                            )}
                                            className={`${classes.contributorName} ${classes.contributorNameLink}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                        >
                                            {contributorName}
                                        </Link>
                                    ) : (
                                        <Typography
                                            variant="body2"
                                            component="span"
                                            className={classes.contributorName}
                                        >
                                            {contributorName}
                                        </Typography>
                                    )}
                                </span>
                            </Grid>
                        )}
                        {date && (
                            <Grid
                                item
                                className={`${classes.dateItem} ${
                                    contributorName
                                        ? classes.metaDotSeparator
                                        : ''
                                }`}
                            >
                                <span
                                    className={classes.dateBlock}
                                    data-testid="data-point-date"
                                >
                                    <ScheduleIcon
                                        fontSize="small"
                                        className={classes.dateIcon}
                                    />
                                    <Typography
                                        variant="body2"
                                        component="span"
                                        className={classes.dateText}
                                    >
                                        {formatDate(date, DATE_FORMATS.LONG)}
                                    </Typography>
                                </span>
                            </Grid>
                        )}
                        {showSourcesButton && (
                            <Grid
                                item
                                className={`${classes.sourcesButtonItem} ${
                                    date || contributorName
                                        ? classes.metaDotSeparator
                                        : ''
                                }`}
                            >
                                <SourcesButton
                                    sourcesCount={sourcesCount}
                                    onOpenDrawer={onOpenDrawer}
                                />
                            </Grid>
                        )}
                    </Grid>
                </Grid>
            </Grid>
        </Grid>
    );
};

DataPoint.propTypes = {
    classes: object.isRequired,
    label: string.isRequired,
    value: oneOfType([string, node]).isRequired,
    tooltipText: oneOfType([string, node]),
    statusLabel: oneOf([STATUS_CLAIMED, STATUS_CROWDSOURCED]),
    contributorName: string,
    userId: oneOfType([string, number]),
    date: oneOfType([string, instanceOf(Date)]),
    drawerData: object,
    onOpenDrawer: func,
};

DataPoint.defaultProps = {
    tooltipText: null,
    statusLabel: null,
    contributorName: null,
    userId: null,
    date: null,
    drawerData: null,
    onOpenDrawer: null,
};

export default withStyles(dataPointStyles)(DataPoint);
