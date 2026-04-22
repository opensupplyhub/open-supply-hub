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
import { fetchMoreFacilityLists } from '../../actions/profile';
import { facilitiesRoute } from '../../util/constants';
import IconComponent from '../Shared/IconComponent/IconComponent';
import styles from './styles';

const UserProfileFacilityLists = ({
    facilityLists,
    fetching,
    fetchingMore,
    nextPageUrl,
    error,
    fetchMore,
    classes,
}) => {
    const renderContent = () => (
        <div className={classes.detailsContent}>
            <div className={classes.headerRow}>
                <Typography className={classes.nameHeader}>Name</Typography>
                <Typography className={classes.descriptionHeader}>
                    Description
                </Typography>
                <Typography className={classes.actionHeader}>Action</Typography>
            </div>
            <Divider className={classes.headerDivider} />
            {facilityLists.map((facilityList, index) => (
                <React.Fragment key={facilityList.id}>
                    <div className={classes.facilityRow}>
                        <Typography className={classes.nameCell}>
                            <span className={classes.mobileLabel}>Name: </span>
                            {facilityList.name}
                        </Typography>
                        <Typography className={classes.descriptionCell}>
                            <span className={classes.mobileLabel}>
                                Description:{' '}
                            </span>
                            {facilityList.description || '...'}
                        </Typography>
                        <div className={classes.actionCell}>
                            <Button
                                size="small"
                                color="primary"
                                component={Link}
                                to={`${facilitiesRoute}?contributors=${facilityList.contributor_id}&lists=${facilityList.id}`}
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
                        data-testid="facility-lists-load-more"
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
                                    Production Location Lists
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
};

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
    classes: shape({
        detailsContent: string.isRequired,
        headerRow: string.isRequired,
        nameHeader: string.isRequired,
        descriptionHeader: string.isRequired,
        actionHeader: string.isRequired,
        headerDivider: string.isRequired,
        facilityRow: string.isRequired,
        nameCell: string.isRequired,
        mobileLabel: string.isRequired,
        descriptionCell: string.isRequired,
        actionCell: string.isRequired,
        loadMoreContainer: string.isRequired,
        loadMoreButton: string.isRequired,
        viewButton: string.isRequired,
        loaderContainer: string.isRequired,
        centeredGrid: string.isRequired,
        appGridContainer: string.isRequired,
        container: string.isRequired,
        expandIcon: string.isRequired,
        panelSummary: string.isRequired,
        heading: string.isRequired,
        panelDetails: string.isRequired,
    }).isRequired,
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
)(withStyles(styles)(UserProfileFacilityLists));
