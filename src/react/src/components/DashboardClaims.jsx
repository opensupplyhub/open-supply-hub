import React, { useEffect } from 'react';
import { connect } from 'react-redux';
import { arrayOf, bool, func, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';

import DownloadFacilityClaimsButton from './DownloadFacilityClaimsButton';
import DashboardClaimsListTable from './DashboardClaimsListTable';

import {
    fetchFacilityClaims,
    clearFacilityClaims,
    sortFacilityClaims,
} from '../actions/claimFacilityDashboard';

import { facilityClaimsListPropType } from '../util/propTypes';

const dashboardClaimsStyles = () =>
    Object.freeze({
        dashboardClaimsContainer: Object.freeze({
            marginTop: '24px',
            width: '100%',
        }),
    });

const DashboardClaims = ({
    data,
    fetching,
    error,
    getClaims,
    clearClaims,
    sortClaims,
    classes,
}) => {
    useEffect(() => {
        getClaims();

        return clearClaims;
    }, [getClaims, clearClaims]);

    if (fetching) {
        return <CircularProgress />;
    }

    if (error) {
        return <Typography>{error}</Typography>;
    }

    if (!data) {
        return null;
    }

    return (
        <div className={classes.dashboardClaimsContainer}>
            <DownloadFacilityClaimsButton data={data} />
            <DashboardClaimsListTable
                data={data}
                handleSortClaims={sortClaims}
            />
        </div>
    );
};

DashboardClaims.defaultProps = {
    data: null,
    error: null,
};

DashboardClaims.propTypes = {
    data: facilityClaimsListPropType,
    fetching: bool.isRequired,
    error: arrayOf(string),
    getClaims: func.isRequired,
    clearClaims: func.isRequired,
    sortClaims: func.isRequired,
};

function mapStateToProps({
    claimFacilityDashboard: {
        list: { data, fetching, error },
    },
}) {
    return {
        data,
        fetching,
        error,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        getClaims: () => dispatch(fetchFacilityClaims()),
        clearClaims: () => dispatch(clearFacilityClaims()),
        sortClaims: sortedData => dispatch(sortFacilityClaims(sortedData)),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(dashboardClaimsStyles)(DashboardClaims));
