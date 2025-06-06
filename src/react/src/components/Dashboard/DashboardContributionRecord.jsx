import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
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

import RejectModerationEventDialog from './RejectModerationEventDialog';
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
    cleanupContributionRecord,
} from '../../actions/dashboardContributionRecord';
import { makeClaimFacilityLink, makeFacilityDetailLink } from '../../util/util';
import DialogTooltip from './../Contribute/DialogTooltip';
import {
    MODERATION_STATUSES_ENUM,
    MODERATION_ACTIONS_ENUM,
} from '../../util/constants';

const claimButtonTitle = 'Go to Claim';
const confirmPotentialMatchButtonTitle = 'Confirm';
const newLocationTitle = 'New Location';
const matchedTitle = 'Matched';

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

const confirmPotentialMatchButtonDisabled = (classes, osId, matchOsId) => (
    <span className={`${classes.claimTooltipWrapper}`}>
        <Button
            color="secondary"
            variant="contained"
            className={classes.confirmButtonStyles}
            disabled
        >
            {osId === matchOsId ? 'Matched' : confirmPotentialMatchButtonTitle}
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
    handleCleanupContributionRecord,
}) => {
    const prevSingleModerationEventItemRef = useRef();
    const [showBackdrop, setShowBackdrop] = useState(false);
    const [
        rejectModerationEventDialogIsOpen,
        setRejectModerationEventDialogIsOpen,
    ] = useState(false);
    const {
        productionLocationName,
        countryCode,
        productionLocationAddress,
        osId,
    } = useMemo(() => {
        if (isEmpty(singleModerationEventItem)) {
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
        if (fetchPotentialMatchError) {
            toast(fetchPotentialMatchError);
        }
    }, [fetchPotentialMatchError]);

    useEffect(() => {
        if (!isEmpty(singleModerationEventItem) && hasPrefetchedData) {
            if (moderationEventFetching) {
                setShowBackdrop(true);
                toast('Updating moderation event...', {
                    onClose: () => setShowBackdrop(false),
                });
            }
            if (
                fetchModerationEventError &&
                fetchModerationEventError.length > 1
            ) {
                setShowBackdrop(true);
                toast(fetchModerationEventError[0], {
                    onClose: () => setShowBackdrop(false),
                });
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

    useEffect(
        () => () => {
            handleCleanupContributionRecord();
        },
        [],
    );

    const handleRejectContribution = () => {
        setRejectModerationEventDialogIsOpen(true);
    };

    const handleRejectModerationEventDialogClose = () => {
        setRejectModerationEventDialogIsOpen(false);
    };

    if (fetchModerationEventError) {
        return (
            <Typography variant="body2" className={classes.errorStyle}>
                {fetchModerationEventError}
            </Typography>
        );
    }

    const moderationEventStatus = singleModerationEventItem.status || '';
    const moderationActionType = singleModerationEventItem.action_type || null;
    const moderationActionPerformBy =
        singleModerationEventItem.action_perform_by_id || null;
    const jsonResults = JSON.stringify(singleModerationEventItem, null, 2);
    const potentialMatchCount = matches.length || 0;
    // OSDEV-1445: automatic write claim into moderation-events table to be done in Q1
    const hasClaimID = singleModerationEventItem.claim_id;
    const isDisabled =
        moderationEventStatus === MODERATION_STATUSES_ENUM.REJECTED ||
        moderationEventStatus === MODERATION_STATUSES_ENUM.APPROVED;

    return (
        <>
            <Backdrop
                className={
                    showBackdrop
                        ? classes.backdrop_open
                        : classes.backdrop_closed
                }
                open={showBackdrop}
            />
            <Typography variant="title" className={classes.title}>
                Moderation Event Data
            </Typography>
            {moderationActionType &&
            moderationActionType !== MODERATION_ACTIONS_ENUM.REJECTED ? (
                <Typography variant="title" className={classes.actionTypeTitle}>
                    {moderationActionType ===
                    MODERATION_ACTIONS_ENUM.NEW_LOCATION
                        ? newLocationTitle
                        : matchedTitle}
                </Typography>
            ) : null}
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
                    {moderationActionPerformBy === null ? (
                        <Typography variant="title">
                            {moderationEventStatus}
                        </Typography>
                    ) : (
                        <Typography variant="title">
                            {moderationEventStatus} by user ID:{' '}
                            {moderationActionPerformBy}
                        </Typography>
                    )}
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
                                            className={
                                                osId === matchOsId
                                                    ? `${classes.listItemStyle} ${classes.listItemStyle_confirmed}`
                                                    : classes.listItemStyle
                                            }
                                        >
                                            <div>
                                                <ListItemText
                                                    className={
                                                        classes.listItemTextStyle
                                                    }
                                                    primary={
                                                        <Typography>
                                                            OS ID:{' '}
                                                            <Link
                                                                to={makeFacilityDetailLink(
                                                                    matchOsId,
                                                                )}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                            >
                                                                {matchOsId}
                                                            </Link>
                                                        </Typography>
                                                    }
                                                />
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
                                            {!isDisabled ? (
                                                <Button
                                                    color="secondary"
                                                    variant="contained"
                                                    className={
                                                        classes.confirmButtonStyles
                                                    }
                                                    disabled={
                                                        moderationEventFetching
                                                    }
                                                    onClick={() => {
                                                        confirmPotentialMatch(
                                                            matchOsId,
                                                        );
                                                    }}
                                                >
                                                    {
                                                        confirmPotentialMatchButtonTitle
                                                    }
                                                </Button>
                                            ) : (
                                                <DialogTooltip
                                                    text={
                                                        osId === matchOsId
                                                            ? `Moderation event data has been already matched to this production location.`
                                                            : `You can't confirm potential match when moderation event is ${moderationEventStatus.toLowerCase()}.`
                                                    }
                                                    aria-label="Confirm potential match button tooltip"
                                                    childComponent={confirmPotentialMatchButtonDisabled(
                                                        classes,
                                                        osId,
                                                        matchOsId,
                                                    )}
                                                />
                                            )}
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
                    disabled={isDisabled || moderationEventFetching}
                >
                    Create New Location
                </Button>
                <Button
                    color="secondary"
                    variant="contained"
                    onClick={handleRejectContribution}
                    className={classes.buttonStyles}
                    disabled={isDisabled || moderationEventFetching}
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
                        claimButtonDisabled(classes)
                    )}
                </Grid>
            </Grid>
            <RejectModerationEventDialog
                updateModerationEvent={updateModerationEvent}
                isOpenDialog={rejectModerationEventDialogIsOpen}
                closeDialog={handleRejectModerationEventDialogClose}
            />
        </>
    );
};

DashboardContributionRecord.defaultProps = {
    fetchModerationEventError: null,
    fetchPotentialMatchError: null,
};

DashboardContributionRecord.propTypes = {
    push: func.isRequired,
    singleModerationEventItem: moderationEventsListItemPropType.isRequired,
    matches: potentialMatchesPropType.isRequired,
    moderationEventFetching: bool.isRequired,
    fetchModerationEvent: func.isRequired,
    updateModerationEvent: func.isRequired,
    createProductionLocation: func.isRequired,
    confirmPotentialMatch: func.isRequired,
    fetchMatches: func.isRequired,
    classes: object.isRequired,
    fetchModerationEventError: string,
    fetchPotentialMatchError: string,
    handleCleanupContributionRecord: func.isRequired,
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
    updateModerationEvent: (status, textCleaned, textRaw) =>
        dispatch(
            updateSingleModerationEvent(
                moderationID,
                status,
                textCleaned,
                textRaw,
            ),
        ),
    createProductionLocation: () =>
        dispatch(createProductionLocationFromModerationEvent(moderationID)),
    confirmPotentialMatch: osId =>
        dispatch(confirmPotentialMatchFromModerationEvent(moderationID, osId)),
    fetchMatches: data => dispatch(fetchPotentialMatches(data)),
    handleCleanupContributionRecord: () =>
        dispatch(cleanupContributionRecord()),
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
