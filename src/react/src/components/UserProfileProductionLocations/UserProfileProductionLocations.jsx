import React from 'react';
import { arrayOf, bool, func, shape, string } from 'prop-types';
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
import InfoOutlined from '@material-ui/icons/InfoOutlined';
import CircularProgress from '@material-ui/core/CircularProgress';
import { fetchMoreProductionLocations } from '../../actions/profile';
import { makeFacilityDetailLink } from '../../util/util';
import PartnershipIcon from '../Icons/Partnership';
import IconComponent from '../Shared/IconComponent/IconComponent';
import LearnMoreLink from '../ProductionLocation/Shared/LearnMoreLink/LearnMoreLink';
import styles from './styles';

const UserProfileProductionLocations = ({
    facilities,
    fetching,
    fetchingMore,
    nextPageUrl,
    error,
    fetchMore,
    classes,
}) => {
    function renderContent() {
        return (
            <div className={classes.detailsContent}>
                <div className={classes.headerRow}>
                    <Typography className={classes.osIdHeader}>
                        OS ID
                    </Typography>
                    <Typography className={classes.nameHeader}>Name</Typography>
                    <Typography className={classes.addressHeader}>
                        Address
                    </Typography>
                    <Typography className={classes.actionHeader}>
                        Action
                    </Typography>
                </div>
                <Divider className={classes.headerDivider} />
                {facilities.map((facility, index) => (
                    <React.Fragment key={facility.id}>
                        <div className={classes.facilityRow}>
                            <Typography className={classes.osIdCell}>
                                <span className={classes.mobileLabel}>
                                    OS ID:{' '}
                                </span>
                                {facility.id}
                            </Typography>
                            <Typography className={classes.nameCell}>
                                <span className={classes.mobileLabel}>
                                    Name:{' '}
                                </span>
                                {facility.properties.name}
                            </Typography>
                            <Typography className={classes.addressCell}>
                                <span className={classes.mobileLabel}>
                                    Address:{' '}
                                </span>
                                {facility.properties.country_code &&
                                    `${facility.properties.country_code}, `}
                                {facility.properties.address}
                            </Typography>
                            <div className={classes.actionCell}>
                                <Button
                                    size="small"
                                    color="primary"
                                    component={Link}
                                    to={makeFacilityDetailLink(facility.id)}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className={classes.viewButton}
                                >
                                    View
                                </Button>
                            </div>
                        </div>
                        {index < facilities.length - 1 && <Divider />}
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
                            data-testid="production-locations-load-more"
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

    if (facilities.length === 0) {
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
                                    <PartnershipIcon
                                        className={classes.icon}
                                        color="#8428FA"
                                    />
                                    Spotlight Locations
                                    <IconComponent
                                        title={
                                            <>
                                                OS Hub Spotlight is the enriched
                                                data layer built into OS Hub
                                                production location profiles. It
                                                aggregates facility-level data
                                                from vetted third-party partner
                                                organizations (Spotlight
                                                Partners) and surfaces it
                                                alongside the core OS Hub
                                                database of millions of
                                                production locations.
                                                <LearnMoreLink href="https://info.opensupplyhub.org/spotlight" />
                                            </>
                                        }
                                        icon={InfoOutlined}
                                        className={classes.infoButton}
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

UserProfileProductionLocations.defaultProps = {
    error: null,
    nextPageUrl: null,
};

UserProfileProductionLocations.propTypes = {
    facilities: arrayOf(
        shape({
            id: string,
            properties: shape({
                name: string,
                address: string,
                country_code: string,
            }),
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
        osIdHeader: string.isRequired,
        nameHeader: string.isRequired,
        addressHeader: string.isRequired,
        actionHeader: string.isRequired,
        headerDivider: string.isRequired,
        facilityRow: string.isRequired,
        osIdCell: string.isRequired,
        mobileLabel: string.isRequired,
        nameCell: string.isRequired,
        addressCell: string.isRequired,
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
        icon: string,
        infoButton: string,
    }).isRequired,
};

function mapStateToProps({
    profile: {
        productionLocations: {
            data,
            fetching,
            fetchingMore,
            nextPageUrl,
            error,
        },
    },
}) {
    return {
        facilities: data,
        fetching,
        fetchingMore,
        nextPageUrl,
        error,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        fetchMore: nextPageUrl =>
            dispatch(fetchMoreProductionLocations(nextPageUrl)),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(styles)(UserProfileProductionLocations));
