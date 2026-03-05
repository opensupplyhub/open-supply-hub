import React from 'react';
import {
    object,
    string,
    oneOfType,
    node,
    instanceOf,
    oneOf,
    shape,
    array,
    func,
} from 'prop-types';
import Typography from '@material-ui/core/Typography';
import Chip from '@material-ui/core/Chip';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import { withStyles } from '@material-ui/core/styles';
import ScheduleIcon from '@material-ui/icons/Schedule';
import PersonIcon from '@material-ui/icons/PersonOutline';

import IconComponent from '../../Shared/IconComponent/IconComponent';
import formatDisplayDate from '../utils';
import getSourcesCount from './utils';
import { STATUS_CLAIMED, STATUS_CROWDSOURCED } from './constants';
import dataPointStyles from './styles';

const DataPoint = ({
    classes,
    label,
    value,
    tooltipText,
    statusLabel,
    contributorName,
    date,
    drawerData,
    onOpenDrawer,
    renderDrawer,
}) => {
    const sourcesCount = getSourcesCount(drawerData);
    const showSourcesButton = sourcesCount > 0 && onOpenDrawer && renderDrawer;

    const getStatusChipClass = () => {
        if (statusLabel === STATUS_CLAIMED) return classes.claimedChip;
        if (statusLabel === STATUS_CROWDSOURCED)
            return classes.crowdsourcedChip;
        return null;
    };

    const tooltipIcon = tooltipText ? (
        <IconComponent title={tooltipText} className={classes.tooltipIcon} />
    ) : null;

    return (
        <Grid container className={classes.root}>
            <Grid item container className={classes.labelColumn}>
                <Grid item className={classes.labelItem}>
                    <Typography className={classes.label} variant="body2">
                        {label}
                    </Typography>
                </Grid>
                <Grid item className={classes.tooltipIconItem}>
                    {tooltipIcon}
                </Grid>
            </Grid>
            <Grid item container className={classes.valueColumn}>
                <Grid item className={classes.valueWithTooltip}>
                    <Typography className={classes.value} variant="body1">
                        {value}
                    </Typography>
                </Grid>

                <Grid item container className={classes.metaRowContainer}>
                    {(contributorName || statusLabel) && (
                        <Grid container item className={classes.metaRow}>
                            {statusLabel ? (
                                <Grid item>
                                    <Chip
                                        label={statusLabel}
                                        size="small"
                                        className={`${classes.statusChip} ${
                                            getStatusChipClass() || ''
                                        }`}
                                    />
                                </Grid>
                            ) : null}
                            {contributorName ? (
                                <Grid item>
                                    <span className={classes.contributor}>
                                        <PersonIcon
                                            fontSize="small"
                                            className={classes.personIcon}
                                        />
                                        <Typography
                                            variant="body2"
                                            component="span"
                                            className={classes.contributorName}
                                        >
                                            {contributorName}
                                        </Typography>
                                    </span>
                                </Grid>
                            ) : null}
                        </Grid>
                    )}
                    {(date || showSourcesButton) && (
                        <Grid
                            item
                            container
                            className={classes.metaRowSecondary}
                        >
                            {date ? (
                                <>
                                    <Grid item className={classes.dateItem}>
                                        <span className={classes.dateBlock}>
                                            <ScheduleIcon
                                                fontSize="small"
                                                className={classes.dateIcon}
                                            />
                                            <Typography
                                                variant="body2"
                                                component="span"
                                                className={classes.dateText}
                                            >
                                                {formatDisplayDate(date)}
                                            </Typography>
                                        </span>
                                    </Grid>
                                </>
                            ) : null}
                            {showSourcesButton && (
                                <Grid
                                    item
                                    className={classes.sourcesButtonItem}
                                >
                                    <Button
                                        className={classes.sourcesButton}
                                        onClick={onOpenDrawer}
                                        aria-label={`View ${sourcesCount} sources`}
                                        data-testid="data-point-sources-button"
                                    >
                                        +{sourcesCount} data sources
                                    </Button>
                                </Grid>
                            )}
                        </Grid>
                    )}
                </Grid>
            </Grid>
            {renderDrawer && typeof renderDrawer === 'function'
                ? renderDrawer()
                : null}
        </Grid>
    );
};

DataPoint.propTypes = {
    classes: object.isRequired,
    label: string.isRequired,
    value: oneOfType([string, node]).isRequired,
    tooltipText: string,
    statusLabel: oneOf([STATUS_CLAIMED, STATUS_CROWDSOURCED]),
    contributorName: string,
    date: oneOfType([string, instanceOf(Date)]),
    drawerData: shape({
        promotedContribution: object,
        contributions: array,
        title: string,
        subtitle: oneOfType([string, node]),
    }),
    onOpenDrawer: func,
    renderDrawer: func,
};

DataPoint.defaultProps = {
    tooltipText: null,
    statusLabel: null,
    contributorName: null,
    date: null,
    drawerData: null,
    onOpenDrawer: null,
    renderDrawer: null,
};

export default withStyles(dataPointStyles)(DataPoint);
