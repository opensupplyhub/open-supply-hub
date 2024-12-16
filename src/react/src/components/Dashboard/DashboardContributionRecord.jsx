import React, { useEffect, useMemo } from 'react';
import { connect } from 'react-redux';
import { string, func, bool, object } from 'prop-types';
import { withStyles, withTheme } from '@material-ui/core/styles';
import isEmpty from 'lodash/isEmpty';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import Paper from '@material-ui/core/Paper';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Divider from '@material-ui/core/Divider';
import CircularProgress from '@material-ui/core/CircularProgress';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';

import { makeDashboardContributionRecordStyles } from '../../util/styles';
import {
    moderationEventsListItemPropType,
    potentialMatchesPropType,
} from '../../util/propTypes';
import {
    fetchSingleModerationEvent,
    fetchPotentialMatches,
    updateSingleModerationEvent,
} from '../../actions/dashboardContributionRecord';
import { makeClaimFacilityLink } from '../../util/util';
import DialogTooltip from './../Contribute/DialogTooltip';

const claimButtonTitle = 'Go to Claim';

const claimButtonDisabled = classes => (
    <span className={`${classes.claimTooltipWrapper}`}>
        <Button
            color="secondary"
            variant="contained"
            className={`${classes.buttonStyles} ${classes.claimButtonStyles}`}
            disabled
        >
            {claimButtonTitle}
        </Button>
    </span>
);

const DashboardContributionRecord = ({
    push,
    singleModerationEventItem,
    matches,
    fetchModerationEventError,
    updateModerationEvent,
    classes,
    fetchModerationEvent,
    fetchMatches,
    moderationEventFetching,
    fetchPotentialMatchError,
}) => {
    const {
        productionLocationName,
        countryCode,
        productionLocationAddress,
    } = useMemo(() => {
        if (!singleModerationEventItem || isEmpty(singleModerationEventItem)) {
            return {};
        }

        const {
            cleaned_data: {
                name: locationName = '',
                country: { alpha_2: code = '' } = {},
                address: locationAddress = '',
            } = {},
        } = singleModerationEventItem || {};

        return {
            productionLocationName: locationName,
            countryCode: code,
            productionLocationAddress: locationAddress,
        };
    }, [singleModerationEventItem]);

    useEffect(() => {
        if (!singleModerationEventItem || isEmpty(singleModerationEventItem)) {
            fetchModerationEvent();
        }
    }, [fetchModerationEvent, updateModerationEvent]);

    useEffect(() => {
        if (
            productionLocationName ||
            countryCode ||
            productionLocationAddress
        ) {
            fetchMatches({
                productionLocationName,
                countryCode,
                productionLocationAddress,
            });
        }
    }, [
        productionLocationName,
        countryCode,
        productionLocationAddress,
        fetchMatches,
    ]);

    if (fetchModerationEventError) {
        return (
            <Typography variant="body2" className={classes.errorStyle}>
                {fetchModerationEventError}
            </Typography>
        );
    }

    const moderationEventStatus = singleModerationEventItem.status || '';
    const jsonResults = JSON.stringify(singleModerationEventItem, null, 2);
    const potentialMatchCount = matches.length || 0;
    const hasClaimID = singleModerationEventItem.claim_id;

    return (
        <>
            <Typography variant="title" className={classes.title}>
                Moderation Event Data
            </Typography>

            <AppBar
                position="static"
                className={`
                        ${classes.moderationEventStatus}
                        ${
                            classes[
                                `moderationEventStatus_${moderationEventStatus.toLowerCase()}`
                            ]
                        }
                        `}
            >
                <Toolbar>
                    <Typography variant="title">
                        {moderationEventStatus}
                    </Typography>
                </Toolbar>
            </AppBar>
            <Paper className={classes.container}>
                <div className={classes.prettyPrint}>
                    {moderationEventFetching ? (
                        <CircularProgress
                            size={25}
                            className={classes.loaderStyles}
                        />
                    ) : (
                        <pre>{jsonResults}</pre>
                    )}
                </div>
            </Paper>

            <Typography variant="title" className={classes.title}>
                Potential Matches ({potentialMatchCount})
            </Typography>

            {fetchPotentialMatchError && (
                <Typography>{fetchPotentialMatchError}</Typography>
            )}
            <div className={classes.potentialMatchesBlock}>
                <Divider className={classes.dividerStyle} />

                <div className={classes.potentialMatchesInternalBlock}>
                    {!potentialMatchCount ? (
                        <div className={classes.emptyBlockStyles}>
                            <Typography
                                className={classes.emptyTextStyle}
                                variant="title"
                            >
                                No potential matches found
                            </Typography>
                        </div>
                    ) : (
                        <List>
                            {matches.map(
                                (
                                    {
                                        os_id: osId,
                                        name,
                                        address,
                                        claim_status: claimStatus,
                                    },
                                    index,
                                ) => (
                                    <React.Fragment key={osId}>
                                        <ListItem
                                            className={classes.listItemStyle}
                                        >
                                            <div>
                                                <ListItemText
                                                    className={
                                                        classes.listItemTextStyle
                                                    }
                                                    primary={`Name: ${name}`}
                                                />
                                                <ListItemText
                                                    className={
                                                        classes.listItemTextStyle
                                                    }
                                                    primary={`Address: ${address}`}
                                                />
                                                <ListItemText
                                                    className={
                                                        classes.listItemTextStyle
                                                    }
                                                    primary={`Claimed Status: ${claimStatus}`}
                                                />
                                            </div>
                                            {/* TODO: PATCH /v1/moderation-events/{moderation_id}/production-locations/ */}
                                            <Button
                                                color="secondary"
                                                variant="contained"
                                                className={
                                                    classes.confirmButtonStyles
                                                }
                                                onClick={() => {}}
                                            >
                                                Confirm
                                            </Button>
                                        </ListItem>

                                        {index < matches.length - 1 && (
                                            <Divider
                                                className={
                                                    classes.innerDividerStyle
                                                }
                                                component="li"
                                            />
                                        )}
                                    </React.Fragment>
                                ),
                            )}
                        </List>
                    )}
                </div>
                <Divider className={classes.dividerStyle} />
            </div>
            <Grid container className={classes.buttonContentStyle}>
                {/* TODO: POST /v1/moderation-events/{moderation_id}/production-locations/ */}
                <Button
                    color="primary"
                    variant="contained"
                    onClick={() => {}}
                    className={classes.buttonStyles}
                    disabled={
                        moderationEventFetching ||
                        moderationEventStatus === 'REJECTED'
                    }
                >
                    Create New Location
                </Button>
                <Button
                    color="secondary"
                    variant="contained"
                    onClick={() => {
                        updateModerationEvent('REJECTED');
                    }}
                    className={classes.buttonStyles}
                    disabled={
                        moderationEventFetching ||
                        moderationEventStatus === 'REJECTED'
                    }
                >
                    Reject Contribution
                </Button>
                <Grid item>
                    {hasClaimID ? (
                        <Button
                            color="secondary"
                            variant="contained"
                            className={`${classes.buttonStyles} ${classes.claimButtonStyles}`}
                            onClick={() => {
                                push(
                                    makeClaimFacilityLink(
                                        singleModerationEventItem.os_id,
                                    ),
                                );
                            }}
                            disabled={moderationEventFetching}
                        >
                            {claimButtonTitle}
                        </Button>
                    ) : (
                        <DialogTooltip
                            text="A production location must be created before it can receive a claim request."
                            aria-label="Claim button tooltip"
                            childComponent={claimButtonDisabled(classes)}
                        />
                    )}
                </Grid>
            </Grid>
        </>
    );
};

DashboardContributionRecord.defaultProps = {
    singleModerationEventItem: {},
    matches: [],
    fetchModerationEventError: null,
    fetchPotentialMatchError: null,
};

DashboardContributionRecord.propTypes = {
    singleModerationEventItem: moderationEventsListItemPropType,
    matches: potentialMatchesPropType,
    moderationEventFetching: bool.isRequired,
    fetchModerationEvent: func.isRequired,
    fetchMatches: func.isRequired,
    classes: object.isRequired,
    fetchModerationEventError: string,
    fetchPotentialMatchError: string,
};

const mapStateToProps = ({
    dashboardContributionRecord: {
        singleModerationEvent: {
            fetching: moderationEventFetching,
            error: fetchModerationEventError,
            data: singleModerationEventItem,
        },
        potentialMatches: {
            matches,
            fetching: potentialMatchFetching,
            error: fetchPotentialMatchError,
        },
    },
}) => ({
    singleModerationEventItem,
    moderationEventFetching,
    matches,
    potentialMatchFetching,
    fetchModerationEventError,
    fetchPotentialMatchError,
});

const mapDispatchToProps = (
    dispatch,
    {
        match: {
            params: { moderationID },
        },
        history: { push },
    },
) => ({
    push,
    fetchModerationEvent: () =>
        dispatch(fetchSingleModerationEvent(moderationID)),
    updateModerationEvent: status =>
        dispatch(updateSingleModerationEvent(moderationID, status)),
    fetchMatches: data => dispatch(fetchPotentialMatches(data)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(
    withTheme()(
        withStyles(makeDashboardContributionRecordStyles)(
            DashboardContributionRecord,
        ),
    ),
);
