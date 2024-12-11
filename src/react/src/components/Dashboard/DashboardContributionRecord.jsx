import React, { useEffect } from 'react';
import { connect } from 'react-redux';
import { string, func, bool, object } from 'prop-types';
import { withStyles, withTheme } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Paper from '@material-ui/core/Paper';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Divider from '@material-ui/core/Divider';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';

import { makeDashboardContributionRecordStyles } from '../../util/styles';
import {
    moderationEventsListItemPropType,
    potentialMatchesPropType,
} from '../../util/propTypes';
import {
    fetchSingleModerationEvent,
    fetchPotentialMatches,
} from '../../actions/dashboardContributionRecord';

const DashboardContributionRecord = ({
    moderationEventsListItem,
    matches,
    fetchModerationEventError,
    classes,
    fetchModerationEvent,
    fetchMatches,
    moderationEventFetching,
    fetchPotentialMatchError,
}) => {
    useEffect(() => {
        fetchModerationEvent();
        fetchMatches();
    }, [fetchModerationEvent, fetchMatches]);

    if (fetchModerationEventError) {
        return (
            <Typography variant="body2" className={classes.errorStyle}>
                {fetchModerationEventError}
            </Typography>
        );
    }

    const jsonResults = JSON.stringify(moderationEventsListItem, null, 2);
    const potentialMatchCount = matches?.length || 0;

    return (
        <>
            <Typography variant="title" className={classes.title}>
                Moderation Event Data
            </Typography>

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
                    {matches.length === 0 ? (
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

            <div className={classes.buttonsContainerStyles}>
                <Button
                    color="primary"
                    variant="contained"
                    onClick={() => {}}
                    className={classes.buttonStyles}
                    disabled={moderationEventFetching}
                >
                    Create New Location
                </Button>
                <Button
                    color="secondary"
                    variant="contained"
                    onClick={() => {}}
                    className={classes.buttonStyles}
                    disabled={moderationEventFetching}
                >
                    Reject Contribution
                </Button>
                <Button
                    color="secondary"
                    variant="contained"
                    className={`${classes.buttonStyles} ${classes.claimButtonStyles}`}
                    onClick={() => {}}
                    disabled={moderationEventFetching}
                >
                    Go to Claim
                </Button>
            </div>
        </>
    );
};

DashboardContributionRecord.defaultProps = {
    moderationEventsListItem: {},
    matches: [],
    fetchModerationEventError: null,
    fetchPotentialMatchError: null,
};

DashboardContributionRecord.propTypes = {
    moderationEventsListItem: moderationEventsListItemPropType,
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
            moderationEventsListItem,
            fetching: moderationEventFetching,
            error: fetchModerationEventError,
        },
        potentialMatches: {
            matches,
            fetching: potentialMatchFetching,
            error: fetchPotentialMatchError,
        },
    },
}) => ({
    moderationEventsListItem,
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
    },
) => ({
    fetchModerationEvent: () =>
        dispatch(fetchSingleModerationEvent(moderationID)),
    fetchMatches: () => dispatch(fetchPotentialMatches()),
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
