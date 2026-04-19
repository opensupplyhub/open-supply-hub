import React from 'react';
import { arrayOf, bool, func, number, shape, string } from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import ExpansionPanel from '@material-ui/core/ExpansionPanel';
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary';
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import CircularProgress from '@material-ui/core/CircularProgress';
import InfoOutlined from '@material-ui/icons/InfoOutlined';
import { fetchMoreFacilityLists } from '../actions/profile';
import COLOURS from '../util/COLOURS';
import IconComponent from './Shared/IconComponent/IconComponent';

const cellHeader = theme =>
    Object.freeze({
        fontWeight: '700',
        padding: `0 ${theme.spacing.unit}px`,
        fontSize: '18px',
    });

const cell = theme =>
    Object.freeze({
        fontSize: '18px',
        padding: `0 ${theme.spacing.unit}px`,
        fontWeight: '500',
    });

const muiStyles = theme =>
    Object.freeze({
        appGridContainer: Object.freeze({
            justifyContent: 'space-between',
            marginBottom: '30px',
            backgroundColor: COLOURS.WHITE,
            padding: '0 24px',
        }),
        container: Object.freeze({
            padding: '10px 0',
            width: '100%',
        }),
        heading: Object.freeze({
            fontWeight: '900',
            fontSize: '28px',
            lineHeight: '28px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
        }),
        panelSummary: Object.freeze({
            paddingLeft: 0,
            paddingRight: 0,
        }),
        expandIcon: Object.freeze({
            padding: 0,
        }),
        panelDetails: Object.freeze({
            padding: 0,
        }),
        detailsContent: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            width: '100%',
        }),
        nameHeader: Object.freeze({
            ...cellHeader(theme),
            flex: 2,
        }),
        descriptionHeader: Object.freeze({
            ...cellHeader(theme),
            flex: 5,
        }),
        actionHeader: Object.freeze({
            ...cellHeader(theme),
            flex: '0 0 80px',
            textAlign: 'right',
            paddingRight: '17px',
        }),
        facilityRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: `${theme.spacing.unit}px 0`,
        }),
        nameCell: Object.freeze({
            flex: 2,
            ...cell(theme),
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
        }),
        descriptionCell: Object.freeze({
            flex: 5,
            ...cell(theme),
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
        }),
        actionCell: Object.freeze({
            flex: '0 0 80px',
            textAlign: 'right',
            ...cell(theme),
        }),
        centeredGrid: Object.freeze({
            marginLeft: 'auto',
            marginRight: 'auto',
        }),
        loadMoreContainer: Object.freeze({
            display: 'flex',
            justifyContent: 'center',
            padding: `${theme.spacing.unit * 2}px 0`,
        }),
        loadMoreButton: Object.freeze({
            minWidth: '100px',
        }),
        loaderContainer: Object.freeze({
            minHeight: '60px',
        }),
        viewButton: Object.freeze({
            fontSize: '14px',
        }),
    });

function UserProfileFacilityLists({
    facilityLists,
    fetching,
    fetchingMore,
    nextPageUrl,
    error,
    fetchMore,
    classes,
}) {
    function renderContent() {
        return (
            <div className={classes.detailsContent}>
                <div className={classes.facilityRow}>
                    <Typography className={classes.nameHeader}>Name</Typography>
                    <Typography className={classes.descriptionHeader}>
                        Description
                    </Typography>
                    <Typography className={classes.actionHeader}>
                        Action
                    </Typography>
                </div>
                <Divider />
                {facilityLists.map((facilityList, index) => (
                    <React.Fragment key={facilityList.id}>
                        <div className={classes.facilityRow}>
                            <Typography className={classes.nameCell}>
                                {facilityList.name}
                            </Typography>
                            <Typography className={classes.descriptionCell}>
                                {facilityList.description || '...'}
                            </Typography>
                            <div className={classes.actionCell}>
                                <Button
                                    size="small"
                                    color="primary"
                                    component={Link}
                                    to={`/?contributors=${facilityList.contributor_id}&lists=${facilityList.id}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className={classes.viewButton}
                                >
                                    View
                                </Button>
                            </div>
                        </div>
                        {index < facilityLists.length - 1 && <Divider />}
                    </React.Fragment>
                ))}
                {nextPageUrl && (
                    <div className={classes.loadMoreContainer}>
                        <Button
                            color="primary"
                            variant="contained"
                            onClick={() => fetchMore(nextPageUrl)}
                            disabled={fetchingMore}
                            className={classes.loadMoreButton}
                        >
                            {fetchingMore ? (
                                <CircularProgress size={24} />
                            ) : (
                                'Load More'
                            )}
                        </Button>
                    </div>
                )}
            </div>
        );
    }

    if (fetching) {
        return (
            <Grid container className={classes.loaderContainer}>
                <Grid item xs={12} sm={9} className={classes.centeredGrid}>
                    <CircularProgress />
                </Grid>
            </Grid>
        );
    }

    if (error) {
        return (
            <Grid container>
                <Grid item xs={12} sm={9} className={classes.centeredGrid}>
                    <Typography color="error">{error}</Typography>
                </Grid>
            </Grid>
        );
    }

    if (facilityLists.length === 0) {
        return null;
    }

    return (
        <Grid container>
            <Grid item xs={12} sm={9} className={classes.centeredGrid}>
                <Grid container className={classes.appGridContainer}>
                    <div className={classes.container}>
                        <ExpansionPanel defaultExpanded elevation={0}>
                            <ExpansionPanelSummary
                                expandIcon={<ExpandMoreIcon />}
                                classes={{
                                    expandIcon: classes.expandIcon,
                                }}
                                className={classes.panelSummary}
                            >
                                <Typography className={classes.heading}>
                                    Facility Lists
                                    <IconComponent
                                        title={
                                            <>
                                                The following lists have been
                                                provided by this contributor.
                                            </>
                                        }
                                        icon={InfoOutlined}
                                    />
                                </Typography>
                            </ExpansionPanelSummary>
                            <ExpansionPanelDetails
                                className={classes.panelDetails}
                            >
                                {renderContent()}
                            </ExpansionPanelDetails>
                        </ExpansionPanel>
                    </div>
                </Grid>
            </Grid>
        </Grid>
    );
}

UserProfileFacilityLists.defaultProps = {
    error: null,
    nextPageUrl: null,
};

UserProfileFacilityLists.propTypes = {
    facilityLists: arrayOf(
        shape({
            id: number,
            name: string,
            description: string,
            contributor_id: number,
        }),
    ).isRequired,
    fetching: bool.isRequired,
    fetchingMore: bool.isRequired,
    nextPageUrl: string,
    error: arrayOf(string),
    fetchMore: func.isRequired,
};

function mapStateToProps({
    profile: {
        facilityLists: { data, fetching, fetchingMore, nextPageUrl, error },
    },
}) {
    return {
        facilityLists: data,
        fetching,
        fetchingMore,
        nextPageUrl,
        error,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        fetchMore: nextPageUrl => dispatch(fetchMoreFacilityLists(nextPageUrl)),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(muiStyles)(UserProfileFacilityLists));
