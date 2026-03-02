import React from 'react';
import PropTypes from 'prop-types';
import Typography from '@material-ui/core/Typography';
import Tooltip from '@material-ui/core/Tooltip';
import Chip from '@material-ui/core/Chip';
import Button from '@material-ui/core/Button';
import HelpOutlineIcon from '@material-ui/icons/HelpOutline';
// import InfoIcon from '@material-ui/icons/Info';
import Grid from '@material-ui/core/Grid';
import { withStyles } from '@material-ui/core/styles';

import ScheduleIcon from '@material-ui/icons/Schedule';
import PersonIcon from '@material-ui/icons/PersonOutline';

import { formatDataPointDate, getSourcesCount } from './utils';
import dataPointStyles from './styles';

const STATUS_CLAIMED = 'Claimed';
const STATUS_CROWDSOURCED = 'Crowdsourced';

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
        <Tooltip title={tooltipText} placement="top" enterDelay={200}>
            <HelpOutlineIcon
                className={classes.tooltipIcon}
                fontSize="small"
                aria-label={tooltipText}
            />
        </Tooltip>
    ) : null;

    return (
        <Grid container className={classes.root} wrap="nowrap">
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
            <Grid
                item
                container
                className={classes.valueColumn}
                direction="column"
            >
                <Grid item className={classes.valueWithTooltip}>
                    <Typography className={classes.value} variant="body1">
                        {value}
                    </Typography>
                </Grid>
                {(contributorName || statusLabel) && (
                    <Grid
                        container
                        item
                        alignItems="center"
                        wrap="wrap"
                        className={classes.metaRow}
                    >
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
                        alignItems="center"
                        wrap="wrap"
                        className={classes.metaRowSecondary}
                    >
                        {date ? (
                            <Grid item>
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
                                        {formatDataPointDate(date)}
                                    </Typography>
                                </span>
                            </Grid>
                        ) : null}
                        {date && showSourcesButton ? (
                            <Grid item>
                                <span
                                    className={classes.metaSeparator}
                                    aria-hidden="true"
                                >
                                    ·
                                </span>
                            </Grid>
                        ) : null}
                        {showSourcesButton && (
                            <Grid item>
                                <Button
                                    className={classes.sourcesButton}
                                    onClick={onOpenDrawer}
                                    aria-label={`View ${sourcesCount} sources`}
                                    data-testid="data-point-sources-button"
                                >
                                    +{sourcesCount} sources
                                </Button>
                            </Grid>
                        )}
                    </Grid>
                )}
            </Grid>
            {renderDrawer && typeof renderDrawer === 'function'
                ? renderDrawer()
                : null}
        </Grid>
    );
};

DataPoint.propTypes = {
    classes: PropTypes.object.isRequired,
    label: PropTypes.string.isRequired,
    value: PropTypes.oneOfType([PropTypes.string, PropTypes.node]).isRequired,
    tooltipText: PropTypes.string,
    statusLabel: PropTypes.oneOf([STATUS_CLAIMED, STATUS_CROWDSOURCED]),
    contributorName: PropTypes.string,
    date: PropTypes.oneOfType([PropTypes.string, PropTypes.instanceOf(Date)]),
    drawerData: PropTypes.shape({
        promotedContribution: PropTypes.object,
        contributions: PropTypes.array,
        title: PropTypes.string,
        subtitle: PropTypes.string,
    }),
    onOpenDrawer: PropTypes.func,
    renderDrawer: PropTypes.func,
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
export { STATUS_CLAIMED, STATUS_CROWDSOURCED };
