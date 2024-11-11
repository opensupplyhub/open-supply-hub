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
    moderationEventPropType,
    potentialMatchesPropType,
} from '../../util/propTypes';
import {
    fetchModerationEvent,
    fetchPotentialMatches,
} from '../../actions/dashboardContributionRecord';

const styles = {
    recordList: {
        py: 0,
        width: '100%',
        maxHeight: 360,
        borderRadius: 2,
        border: '3px solid',
        borderColor: 'divider',
        backgroundColor: 'background.paper',
    },
};

const DashboardContributionRecord = ({
    event,
    potentialMatches,
    fetchEventError,
    classes,
    fetchEvent,
    fetchMatches,
    eventFetching,
    fetchPotentialMatchError,
}) => {
    useEffect(() => {
        fetchEvent();
        fetchMatches();
    }, [fetchEvent, fetchMatches]);

    if (fetchEventError) {
        return (
            <Typography variant="body2" style={{ color: 'red' }}>
                {fetchEventError}
            </Typography>
        );
    }

    const jsonResults = JSON.stringify(event, null, 2);
    const potentialMatchCount = potentialMatches?.length || 0;

    return (
        <>
            <Typography variant="title" className={classes.title}>
                Moderation Event Data
            </Typography>

            <Paper className={classes.container}>
                <div className={classes.prettyPrint}>
                    {eventFetching ? (
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
                    {potentialMatches.length === 0 ? (
                        <div className={classes.emptyBlockStyles}>
                            <Typography
                                className={classes.emptyTextStyle}
                                variant="title"
                            >
                                No potential matches found
                            </Typography>
                        </div>
                    ) : (
                        <List styles={styles.recordList}>
                            {potentialMatches.map(
                                (
                                    {
                                        osId,
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

                                        {index <
                                            potentialMatches.length - 1 && (
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
                    disabled={eventFetching}
                >
                    Create New Location
                </Button>
                <Button
                    color="secondary"
                    variant="contained"
                    onClick={() => {}}
                    className={classes.buttonStyles}
                    disabled={eventFetching}
                >
                    Reject Contribution
                </Button>
                <Button
                    color="secondary"
                    variant="contained"
                    className={`${classes.buttonStyles} ${classes.claimButtonStyles}`}
                    onClick={() => {}}
                    disabled={eventFetching}
                >
                    Go to Claim
                </Button>
            </div>
        </>
    );
};

DashboardContributionRecord.defaultProps = {
    event: {},
    potentialMatches: [],
    fetchEventError: null,
    fetchPotentialMatchError: null,
};

DashboardContributionRecord.propTypes = {
    event: moderationEventPropType,
    potentialMatches: potentialMatchesPropType,
    eventFetching: bool.isRequired,
    fetchEvent: func.isRequired,
    fetchMatches: func.isRequired,
    classes: object.isRequired,
    fetchEventError: string,
    fetchPotentialMatchError: string,
};

const mapStateToProps = ({
    dashboardContributionRecord: {
        moderationEvent: {
            event,
            fetching: eventFetching,
            error: fetchEventError,
        },
        potentialMatches: {
            potentialMatches,
            fetching: potentialMatchFetching,
            error: fetchPotentialMatchError,
        },
    },
}) => ({
    event,
    eventFetching,
    potentialMatches,
    potentialMatchFetching,
    fetchEventError,
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
    fetchEvent: () => dispatch(fetchModerationEvent(moderationID)),
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
