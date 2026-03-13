import React, { useMemo } from 'react';
import {
    object,
    string,
    oneOfType,
    node,
    instanceOf,
    oneOf,
    func,
    number,
    bool,
} from 'prop-types';
import Typography from '@material-ui/core/Typography';
import Chip from '@material-ui/core/Chip';
import Grid from '@material-ui/core/Grid';
import { withStyles } from '@material-ui/core/styles';

import IconComponent from '../../Shared/IconComponent/IconComponent';
import { getContributionsCount } from '../ContributionsDrawer/utils';
import SourcesButton from './SourcesButton/SourcesButton';
import MetaContributor from './MetaContributor/MetaContributor';
import MetaDate from './MetaDate/MetaDate';
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
    multiline,
}) => {
    const sourcesCount = useMemo(
        () => getContributionsCount(drawerData?.contributions),
        [drawerData?.contributions],
    );
    const showSourcesButton = useMemo(() => sourcesCount > 0 && onOpenDrawer, [
        sourcesCount,
        onOpenDrawer,
    ]);
    const statusChipClass = useMemo(() => {
        if (statusLabel === STATUS_CLAIMED) return classes.claimedChip;
        if (statusLabel === STATUS_CROWDSOURCED)
            return classes.crowdsourcedChip;
        return null;
    }, [statusLabel, classes]);

    const tooltipIcon = tooltipText ? (
        <IconComponent title={tooltipText} className={classes.tooltipIcon} />
    ) : null;

    const dateDot = !multiline && contributorName;
    const sourcesDot = multiline ? date : date || contributorName;

    const statusItem = statusLabel && (
        <Grid item>
            <Chip
                label={statusLabel}
                size="small"
                className={`${classes.statusChip} ${statusChipClass || ''}`}
                data-testid="data-point-status-chip"
            />
        </Grid>
    );
    const contributorItem = contributorName && (
        <Grid item>
            <MetaContributor
                contributorName={contributorName}
                userId={userId}
            />
        </Grid>
    );
    const dateItem = date && (
        <Grid
            item
            className={`${classes.dateItem} ${
                dateDot ? classes.metaDotSeparator : ''
            }`}
        >
            <MetaDate date={date} />
        </Grid>
    );
    const sourcesItem = showSourcesButton && (
        <Grid
            item
            className={`${classes.sourcesButtonItem} ${
                sourcesDot ? classes.metaDotSeparator : ''
            }`}
        >
            <SourcesButton
                sourcesCount={sourcesCount}
                onOpenDrawer={onOpenDrawer}
            />
        </Grid>
    );

    const metaContent = multiline ? (
        <>
            <Grid
                item
                container
                className={classes.metaRow}
                data-testid="data-point-meta-line-1"
            >
                {statusItem}
                {contributorItem}
            </Grid>
            {(date || showSourcesButton) && (
                <Grid
                    item
                    container
                    className={classes.metaRow}
                    data-testid="data-point-meta-line-2"
                >
                    {dateItem}
                    {sourcesItem}
                </Grid>
            )}
        </>
    ) : (
        <Grid item container className={classes.metaRow}>
            {statusItem}
            {contributorItem}
            {dateItem}
            {sourcesItem}
        </Grid>
    );

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
                <Grid
                    item
                    container
                    className={`${classes.metaRowWrapper} ${
                        multiline ? classes.metaRowWrapperMultiline : ''
                    }`}
                >
                    {metaContent}
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
    multiline: bool,
};

DataPoint.defaultProps = {
    tooltipText: null,
    statusLabel: null,
    contributorName: null,
    userId: null,
    date: null,
    drawerData: null,
    onOpenDrawer: null,
    multiline: false,
};

export default withStyles(dataPointStyles)(DataPoint);
