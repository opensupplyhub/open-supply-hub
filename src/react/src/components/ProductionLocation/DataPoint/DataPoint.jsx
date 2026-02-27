import React from 'react';
import PropTypes from 'prop-types';
import Typography from '@material-ui/core/Typography';
import Tooltip from '@material-ui/core/Tooltip';
import Chip from '@material-ui/core/Chip';
import Button from '@material-ui/core/Button';
import Icon from '@material-ui/core/Icon';
import InfoIcon from '@material-ui/icons/Info';
import Grid from '@material-ui/core/Grid';
import { withStyles } from '@material-ui/core/styles';

import ScheduleIcon from '@material-ui/icons/Schedule';
import PersonIcon from '@material-ui/icons/Person';

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
            <Icon
                className={classes.tooltipIcon}
                fontSize="small"
                aria-label={tooltipText}
            >
                <InfoIcon />
            </Icon>
        </Tooltip>
    ) : null;

    return (
        <Grid
            container
            className={classes.root}
            spacing={3}
            wrap="nowrap"
            role="group"
        >
            <Grid item className={classes.labelColumn}>
                <Typography className={classes.label} variant="body2">
                    {label}
                </Typography>
            </Grid>
            <Grid item className={classes.tooltipIconColumn}>
                {tooltipIcon}
            </Grid>
            <Grid
                item
                container
                className={classes.valueColumn}
                zeroMinWidth
                direction="column"
                spacing={1}
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
                        spacing={1}
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
                        spacing={1}
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
