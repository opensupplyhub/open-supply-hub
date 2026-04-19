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
import { fetchMoreProductionLocations } from '../actions/profile';
import { makeFacilityDetailLink } from '../util/util';
import PartnershipIcon from './Icons/Partnership';
import IconComponent from './Shared/IconComponent/IconComponent';
import LearnMoreLink from './ProductionLocation/Shared/LearnMoreLink/LearnMoreLink';
import COLOURS from '../util/COLOURS';

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
        osIdHeader: Object.freeze({
            ...cellHeader(theme),
            flex: '0 0 160px',
        }),
        nameHeader: Object.freeze({
            ...cellHeader(theme),
            flex: 2,
        }),
        addressHeader: Object.freeze({
            ...cellHeader(theme),
            flex: 3,
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
        osIdCell: Object.freeze({
            flex: '0 0 160px',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            ...cell(theme),
            fontWeight: '600',
        }),
        nameCell: Object.freeze({
            flex: 2,
            ...cell(theme),
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
        }),
        addressCell: Object.freeze({
            flex: 3,
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

function UserProfileProductionLocations({
    facilities,
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
                <Divider />
                {facilities.map((facility, index) => (
                    <React.Fragment key={facility.id}>
                        <div className={classes.facilityRow}>
                            <Typography className={classes.osIdCell}>
                                {facility.id}
                            </Typography>
                            <Typography className={classes.nameCell}>
                                {facility.properties.name}
                            </Typography>
                            <Typography className={classes.addressCell}>
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
                                                Are you a data provider and want
                                                your data listed here? Looking
                                                to access this data for
                                                compliance reporting, risk
                                                analysis, or supplier
                                                monitoring?
                                                <LearnMoreLink href="https://info.opensupplyhub.org/data-integrations" />
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
}

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
)(withStyles(muiStyles)(UserProfileProductionLocations));
