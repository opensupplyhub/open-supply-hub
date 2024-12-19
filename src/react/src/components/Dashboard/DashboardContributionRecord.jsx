/* eslint no-unused-vars: 0 */
import React, { useEffect, useMemo, useRef, useState } from 'react';
import { connect } from 'react-redux';
import { toast } from 'react-toastify';
import { string, func, bool, object } from 'prop-types';
import { withStyles, withTheme } from '@material-ui/core/styles';
import isEmpty from 'lodash/isEmpty';
import isEqual from 'lodash/isEqual';
import Backdrop from '@material-ui/core/Backdrop';
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
    createProductionLocationFromModerationEvent,
    confirmPotentialMatchFromModerationEvent,
} from '../../actions/dashboardContributionRecord';
import { makeClaimFacilityLink } from '../../util/util';
import DialogTooltip from './../Contribute/DialogTooltip';
import { MODERATION_STATUSES_ENUM } from '../../util/constants';

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

let hasPrefetchedData = false;
const DashboardContributionRecord = ({
    push,
    singleModerationEventItem,
    matches,
    fetchModerationEventError,
    updateModerationEvent,
    createProductionLocation,
    confirmPotentialMatch,
    classes,
    fetchModerationEvent,
    fetchMatches,
    moderationEventFetching,
    fetchPotentialMatchError,
}) => {
    const prevSingleModerationEventItemRef = useRef();
    const [
        shouldDisabledWhileRequest,
        setShouldDisabledWhileRequest,
    ] = useState(false);
    const {
        productionLocationName,
        countryCode,
        productionLocationAddress,
        osId,
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
            os_id: locationOsId = null,
        } = singleModerationEventItem || {};

        return {
            productionLocationName: locationName,
            countryCode: code,
            productionLocationAddress: locationAddress,
            osId: locationOsId,
        };
    }, [singleModerationEventItem]);

    useEffect(() => {
        const prevSingleModerationEventItem =
            prevSingleModerationEventItemRef.current;
        if (
            !isEqual(prevSingleModerationEventItem, singleModerationEventItem)
        ) {
            fetchModerationEvent();
            hasPrefetchedData = true;
        }

        prevSingleModerationEventItemRef.current = singleModerationEventItem;
    }, []);

    useEffect(() => {
        if (!isEmpty(singleModerationEventItem) && hasPrefetchedData) {
            if (moderationEventFetching) {
                setShouldDisabledWhileRequest(true);
                toast('Updating moderation event...');
            }
            if (
                fetchModerationEventError &&
                fetchModerationEventError.length > 1
            ) {
                setShouldDisabledWhileRequest(true);
                toast(fetchModerationEventError[0]);
            }
        }
    }, [moderationEventFetching, fetchModerationEventError]);

    useEffect(() => {
        if (
            productionLocationName ||
            countryCode ||
            productionLocationAddress ||
            osId
        ) {
            fetchMatches({
                productionLocationName,
                countryCode,
                productionLocationAddress,
            });
        }
    }, [productionLocationName, countryCode, productionLocationAddress, osId]);

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
    // TODO: automatic write claim into moderation-events table to be done in Q1
    const hasClaimID = singleModerationEventItem.claim_id;
    const isDisabled =
        moderationEventStatus === MODERATION_STATUSES_ENUM.REJECTED ||
        moderationEventStatus === MODERATION_STATUSES_ENUM.APPROVED;
    let claimButtonTooltipText = '';

    switch (moderationEventStatus) {
        case MODERATION_STATUSES_ENUM.PENDING:
            claimButtonTooltipText =
                'A production location must be created before it can receive a claim request.';
            break;
        case MODERATION_STATUSES_ENUM.APPROVED:
            claimButtonTooltipText =
                "Production location hasn't received a claim yet";
            break;
        case MODERATION_STATUSES_ENUM.REJECTED:
            claimButtonTooltipText =
                'Moderation event has been rejected, no claim request available';
            break;
        default:
            break;
    }

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
                                        os_id: matchOsId,
                                        name,
                                        address,
                                        claim_status: claimStatus,
                                    },
                                    index,
                                ) => (
                                    <React.Fragment key={matchOsId}>
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
                                            <Button
                                                color="secondary"
                                                variant="contained"
                                                className={
                                                    classes.confirmButtonStyles
                                                }
                                                disabled={
                                                    isDisabled ||
                                                    shouldDisabledWhileRequest
                                                }
                                                onClick={() => {
                                                    confirmPotentialMatch(
                                                        matchOsId,
                                                    );
                                                }}
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
                <Button
                    color="primary"
                    variant="contained"
                    onClick={() => {
                        createProductionLocation();
                    }}
                    className={classes.buttonStyles}
                    disabled={isDisabled || shouldDisabledWhileRequest}
                >
                    Create New Location
                </Button>
                <Button
                    color="secondary"
                    variant="contained"
                    onClick={() => {
                        updateModerationEvent(
                            MODERATION_STATUSES_ENUM.REJECTED,
                        );
                    }}
                    className={classes.buttonStyles}
                    disabled={
                        moderationEventFetching ||
                        isDisabled ||
                        shouldDisabledWhileRequest
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
                            text={claimButtonTooltipText}
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
    createProductionLocation: () =>
        dispatch(createProductionLocationFromModerationEvent(moderationID)),
    confirmPotentialMatch: osId =>
        dispatch(confirmPotentialMatchFromModerationEvent(moderationID, osId)),
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
