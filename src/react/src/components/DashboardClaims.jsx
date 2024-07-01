/* eslint no-unused-vars: 0 */
import React, { useEffect } from 'react';
import { connect } from 'react-redux';
import { arrayOf, bool, func, shape, string } from 'prop-types';
import map from 'lodash/map';
import { withStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';

import DownloadFacilityClaimsButton from './DownloadFacilityClaimsButton';
import DashboardClaimsListTable from './DashboardClaimsListTable';

import {
    fetchFacilityClaims,
    clearFacilityClaims,
    sortFacilityClaims,
} from '../actions/claimFacilityDashboard';

import ClaimStatusFilter from './Filters/ClaimStatusFilter';

import { facilityClaimsListPropType } from '../util/propTypes';

import { makeDashboardClaimListLink } from '../util/util';

const dashboardClaimsStyles = () =>
    Object.freeze({
        container: Object.freeze({
            marginBottom: '60px',
            width: '100%',
        }),
        dashboardClaimsContainer: Object.freeze({
            marginTop: '24px',
            width: '100%',
        }),
        filterRow: Object.freeze({
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '20px',
        }),
        filter: Object.freeze({
            flex: 1,
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
    history: {
        location: { search },
        push,
        replace,
    },
    claimStatuses,
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

    /*
     TODO: This will come from predefined URL on component mount, omit for now
     */
    const newParams = {
        statuses: claimStatuses,
    };

    const onClaimStatusUpdate = s => {
        replace(
            makeDashboardClaimListLink({
                statuses: map(s, 'value'),
            }),
        );
    };

    return (
        <Paper className={classes.container}>
            <div className={classes.dashboardClaimsContainer}>
                <DownloadFacilityClaimsButton data={data} />
                <ClaimStatusFilter
                    handleClaimStatusUpdate={onClaimStatusUpdate}
                />
                <DashboardClaimsListTable
                    data={data}
                    handleSortClaims={sortClaims}
                />
            </div>
        </Paper>
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
    history: shape({
        replace: func.isRequired,
    }).isRequired,
};

function mapStateToProps({
    claimFacilityDashboard: {
        list: { data, fetching, error },
    },
    filters: { claimStatuses },
}) {
    return {
        data,
        fetching,
        error,
        claimStatuses,
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
