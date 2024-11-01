import React, { useEffect, useState } from 'react';
import { connect } from 'react-redux';
import { string } from 'prop-types';
import { withStyles, withTheme } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Paper from '@material-ui/core/Paper';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Divider from '@material-ui/core/Divider';

import Typography from '@material-ui/core/Typography';
import ShowOnly from '../ShowOnly';

import { makeDashboardContributionRecordStyles } from '../../util/styles';

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
// const potentialMatchesData = [];
const potentialMatchesData = [
    {
        name: 'Test name INC',
        address: '435 Main St, Manhattan, NY - USA',
        claim_status: 'unclaimed',
    },
    // {
    //     name: 'Test name INC',
    //     address: '435 Main St, Manhattan, NY - USA',
    //     claim_status: 'unclaimed',
    // },
    // {
    //     name: 'Test name INC',
    //     address: '435 Main St, Manhattan, NY - USA',
    //     claim_status: 'unclaimed',
    // },
    // {
    //     name: 'Test name INC',
    //     address: '435 Main St, Manhattan, NY - USA',
    //     claim_status: 'unclaimed',
    // },
    // {
    //     name: 'Test name INC',
    //     address: '435 Main St, Manhattan, NY - USA',
    //     claim_status: 'unclaimed',
    // },
    // {
    //     name: 'Test name INC',
    //     address: '435 Main St, Manhattan, NY - USA',
    //     claim_status: 'unclaimed',
    // },
];
const potentialMatchCount = potentialMatchesData.length;
const eventData = {
    moderation_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    created_at: '2024-10-17T11:30:20.287Z',
    updated_at: '2024-10-18T11:30:20.287Z',
    os_id: 'string',
    cleaned_data: {
        name: 'Eco Friendly Plastics',
        address: 'string',
        country: {
            name: 'Germany',
            alpha_2: 'DE',
            alpha_3: 'DEU',
            numeric: '276',
        },
    },
    contributor_id: 0,
    contributor_name: 'Green Solutions Corp',
    request_type: 'CREATE',
    source: 'API',
    moderation_status: 'PENDING',
    moderation_decision_date: null,
    claim_id: 0,
};

const DashboardContributionRecord = ({
    // events,
    // fetching,
    // fetchEvents,
    error,
    theme,
    // downloadEvents,
    // downloadEventsError,
    // fetchCountries,
    classes,
}) => {
    const [results, setResults] = useState(null);
    const fetchPotentialMatches = () => setResults(eventData);
    // apiRequest
    //     .get(makePotentialMatchURL(), {
    //         params: {},
    //     })
    //     .then(({ data }) => {
    //         setResults(potentialMatchesData);
    //     })
    //     .catch(err => setResults(err));

    useEffect(() => {
        fetchPotentialMatches();
    }, []);

    const jsonResults = JSON.stringify(results, null, 2);

    if (error) {
        return <Typography>{error}</Typography>;
    }

    return (
        <>
            <Typography variant="title" className={classes.title}>
                Moderation Event Data
            </Typography>
            <Paper className={classes.container}>
                <div className={classes.prettyPrint}>
                    {results && <pre>{jsonResults}</pre>}
                </div>
            </Paper>
            <Typography variant="title" className={classes.title}>
                Potential Matches ({potentialMatchCount})
            </Typography>
            <div className={classes.potentialMatchesBlock}>
                <List styles={styles.recordList}>
                    <Divider className={classes.dividerStyle} component="li" />
                    <div className={classes.potentialMatchesInternalBlock}>
                        <ShowOnly when={potentialMatchesData.length === 0}>
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
                            when={
                                potentialMatchesData &&
                                potentialMatchesData.length > 0
                            }
                        >
                            {potentialMatchesData &&
                                potentialMatchesData.map(
                                    (potentialMatch, index) => (
                                        <>
                                            {' '}
                                            <ListItem
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
                                                    potentialMatchesData.length >
                                                        1 &&
                                                    potentialMatchesData.length -
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
                >
                    Create New Location
                </Button>{' '}
                <Button
                    color="secondary"
                    variant="contained"
                    onClick={() => {}}
                    className={classes.buttonStyles}
                >
                    Reject Contribution
                </Button>{' '}
                <Button
                    color="secondary"
                    variant="contained"
                    className={classes.buttonStyles}
                    onClick={() => {}}
                    style={{
                        backgroundColor: theme.palette.action.main,
                    }}
                >
                    Go to Claim
                </Button>
            </div>
        </>
    );
};

DashboardContributionRecord.defaultProps = {
    // event: {},
    error: null,
    // downloadEventsError: null,
    // results: null,
    // jsonResults: null,
};

DashboardContributionRecord.propTypes = {
    // event: moderationEventsPropType,
    // fetching: bool.isRequired,
    error: string,
    // downloadEventsError: string,
    // results: object.isRequired,
};

const mapStateToProps = ({
    dashboardModerationQueue: {
        moderationEvents: { event, fetching, error },
        moderationEventsDownloadStatus: { error: downloadEventsError },
    },
}) => ({
    event,
    fetching,
    error,
    downloadEventsError,
});

// const mapDispatchToProps = dispatch => ({
//     fetchPotentialMatches: () => dispatch(fetchPotentialMatches()),
// });

export default connect(
    mapStateToProps,
    // mapDispatchToProps,
)(
    withTheme()(
        withStyles(makeDashboardContributionRecordStyles)(
            DashboardContributionRecord,
        ),
    ),
);
