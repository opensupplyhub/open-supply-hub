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
import ShowOnly from '../ShowOnly';

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
    error,
    classes,
    fetchEvent,
    fetchMatches,
    fetching,
    fetchPotentialMatchError,
}) => {
    useEffect(() => {
        fetchEvent();
        fetchMatches();
    }, [fetchEvent, fetchMatches]);

    if (error) {
        return <Typography>{error}</Typography>;
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
                    {fetching ? (
                        <CircularProgress
                            size={25}
                            className={classes.loaderStyles}
                        />
                    ) : (
                        <>{event && <pre>{jsonResults}</pre>}</>
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
                <List styles={styles.recordList}>
                    <Divider className={classes.dividerStyle} component="li" />
                    <div className={classes.potentialMatchesInternalBlock}>
                        <ShowOnly
                            key="title"
                            when={potentialMatches.length === 0}
                        >
                            <div className={classes.emptyBlockStyles}>
                                <Typography
                                    className={classes.emptyTextStyle}
                                    variant="title"
                                >
                                    No potential matches found
                                </Typography>
                            </div>
                        </ShowOnly>
                        <ShowOnly
                            key="section"
                            when={
                                potentialMatches && potentialMatches.length > 0
                            }
                        >
                            {potentialMatches &&
                                potentialMatches.map(
                                    (potentialMatch, index) => (
                                        <>
                                            {' '}
                                            <ListItem
                                                key={potentialMatch.os_id}
                                                className={
                                                    classes.listItemStyle
                                                }
                                            >
                                                <div>
                                                    <ListItemText
                                                        className={
                                                            classes.listItemTextStyle
                                                        }
                                                        primary={`Name: ${potentialMatch.name}}`}
                                                    />
                                                    <ListItemText
                                                        className={
                                                            classes.listItemTextStyle
                                                        }
                                                        primary={`Address: ${potentialMatch.address}}`}
                                                    />
                                                    <ListItemText
                                                        className={
                                                            classes.listItemTextStyle
                                                        }
                                                        primary={`Claimed Status: ${potentialMatch.claim_status}}`}
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
                                            <ShowOnly
                                                when={
                                                    potentialMatches.length >
                                                        1 &&
                                                    potentialMatches.length -
                                                        1 !==
                                                        index
                                                }
                                            >
                                                <Divider
                                                    className={
                                                        classes.innerDividerStyle
                                                    }
                                                    component="li"
                                                />
                                            </ShowOnly>
                                        </>
                                    ),
                                )}
                        </ShowOnly>
                    </div>
                    <Divider className={classes.dividerStyle} component="li" />
                </List>
            </div>
            <div className={classes.buttonsContainerStyles}>
                <Button
                    color="primary"
                    variant="contained"
                    onClick={() => {}}
                    className={classes.buttonStyles}
                    isDisabled={fetching}
                >
                    Create New Location
                </Button>{' '}
                <Button
                    color="secondary"
                    variant="contained"
                    onClick={() => {}}
                    className={classes.buttonStyles}
                    isDisabled={fetching}
                >
                    Reject Contribution
                </Button>{' '}
                <Button
                    color="secondary"
                    variant="contained"
                    className={`${classes.buttonStyles} ${classes.claimButtonStyles}`}
                    onClick={() => {}}
                    isDisabled={fetching}
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
    error: null,
    fetchPotentialMatchError: null,
};

DashboardContributionRecord.propTypes = {
    event: moderationEventPropType,
    potentialMatches: potentialMatchesPropType,
    fetching: bool.isRequired,
    fetchEvent: func.isRequired,
    fetchMatches: func.isRequired,
    classes: object.isRequired,
    error: string,
    fetchPotentialMatchError: string,
};

const mapStateToProps = ({
    dashboardContributionRecord: {
        moderationEvent: { event, fetching, error },
        potentialMatches: {
            potentialMatches,
            fetching: potentialMatchFetching,
            error: fetchPotentialMatchError,
        },
    },
}) => ({
    event,
    fetching,
    potentialMatches,
    potentialMatchFetching,
    error,
    fetchPotentialMatchError,
});

const mapDispatchToProps = dispatch => ({
    fetchEvent: () => dispatch(fetchModerationEvent()),
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
