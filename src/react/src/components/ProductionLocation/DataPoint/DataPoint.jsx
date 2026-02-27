import React from 'react';
import PropTypes from 'prop-types';
import Typography from '@material-ui/core/Typography';
import Tooltip from '@material-ui/core/Tooltip';
import Chip from '@material-ui/core/Chip';
import Button from '@material-ui/core/Button';
import Icon from '@material-ui/core/Icon';
import InfoIcon from '@material-ui/icons/Info';
import { withStyles } from '@material-ui/core/styles';

import ScheduleIcon from '@material-ui/icons/Schedule';
import PersonIcon from '@material-ui/icons/Person';

import { formatDataPointDate, getSourcesCount } from './utils';
import styles from './styles';

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
        <div className={classes.root} role="group">
            <Typography className={classes.label} variant="body2">
                {label}
            </Typography>
            <div className={classes.valueColumn}>
                <div className={classes.valueRow}>
                    <div className={classes.valueWithTooltip}>
                        {tooltipIcon}
                        <Typography className={classes.value} variant="body1">
                            {value}
                        </Typography>
                    </div>
                    {statusLabel ? (
                        <Chip
                            label={statusLabel}
                            size="small"
                            className={`${classes.statusChip} ${
                                getStatusChipClass() || ''
                            }`}
                        />
                    ) : null}
                </div>
                {(contributorName || date || showSourcesButton) && (
                    <div className={classes.metaRow}>
                        {contributorName ? (
                            <span className={classes.contributor}>
                                <PersonIcon
                                    fontSize="small"
                                    className={classes.personIcon}
                                />
                                <Typography variant="body2" component="span">
                                    {contributorName}
                                </Typography>
                            </span>
                        ) : null}
                        {date ? (
                            <span className={classes.dateBlock}>
                                <ScheduleIcon
                                    fontSize="small"
                                    className={classes.dateIcon}
                                />
                                <Typography variant="body2" component="span">
                                    {formatDataPointDate(date)}
                                </Typography>
                            </span>
                        ) : null}
                        {date && showSourcesButton ? (
                            <span
                                className={classes.metaSeparator}
                                aria-hidden="true"
                            >
                                ·
                            </span>
                        ) : null}
                        {showSourcesButton && (
                            <Button
                                className={classes.sourcesButton}
                                onClick={onOpenDrawer}
                                aria-label={`View ${sourcesCount} sources`}
                                data-testid="data-point-sources-button"
                            >
                                +{sourcesCount} sources
                            </Button>
                        )}
                    </div>
                )}
            </div>
            {renderDrawer && typeof renderDrawer === 'function'
                ? renderDrawer()
                : null}
        </div>
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

export default withStyles(styles)(DataPoint);
export { STATUS_CLAIMED, STATUS_CROWDSOURCED };
