import React, { useEffect } from 'react';
import { connect } from 'react-redux';
import { arrayOf, bool, func, shape, string } from 'prop-types';
import map from 'lodash/map';
import { withStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';

import DownloadFacilityClaimsButton from './DownloadFacilityClaimsButton';
import DashboardClaimsListTable from './DashboardClaimsListTable';

import {
    fetchFacilityClaims,
    clearFacilityClaims,
    sortFacilityClaims,
} from '../actions/claimFacilityDashboard';

import {
    fetchCountryOptions,
    fetchClaimStatusOptions,
} from '../actions/filterOptions';

import ClaimStatusFilter from './Filters/ClaimStatusFilter';
import CountryNameFilter from './Filters/CountryNameFilter';
import {
    updateClaimStatusFilter,
    updateCountryFilter,
} from './../actions/filters';

import {
    facilityClaimsListPropType,
    claimStatusOptionsPropType,
    countryOptionsPropType,
} from '../util/propTypes';

import {
    makeDashboardClaimListLink,
    getDashboardClaimsListParamsFromQueryString,
} from '../util/util';

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
    claimStatuses,
    fetching,
    error,
    getClaims,
    clearClaims,
    sortClaims,
    classes,
    history: {
        location: { search },
        push,
    },
    fetchClaimStatus,
    fetchCountries,
    updateClaimStatus,
    updateCountry,
    countriesData,
}) => {
    const { countries, statuses } = getDashboardClaimsListParamsFromQueryString(
        search,
    );

    useEffect(() => {
        fetchCountries();
        fetchClaimStatus();

        if (statuses && statuses.length > 0) {
            const statusesSerialized = map(statuses, status => ({
                label: status,
                value: status,
            }));
            updateClaimStatus(statusesSerialized);
            push(
                makeDashboardClaimListLink({
                    statuses,
                    countries: countries || map(countriesData, 'value'),
                }),
            );
        }
        if (countries && countries.length > 0) {
            const countriesSerialized = map(countries, country => ({
                value: country,
                label: country,
            }));
            updateCountry(countriesSerialized);
            push(
                makeDashboardClaimListLink({
                    statuses,
                    countries: map(countriesSerialized, 'value'),
                }),
            );
        }
    }, []);

    useEffect(() => {
        if (countriesData && countriesData.length > 0) {
            push(
                makeDashboardClaimListLink({
                    statuses,
                    countries: map(countriesData, 'value'),
                }),
            );
        }
        if (countries) {
            push(
                makeDashboardClaimListLink({
                    statuses,
                    countries: map(countriesData, 'value'),
                }),
            );
        }
    }, [countriesData]);

    const onClaimStatusUpdate = s => {
        push(
            makeDashboardClaimListLink({
                statuses: map(s, 'value'),
                countries: map(countriesData, 'value'),
            }),
        );
    };

    if (error) {
        return <Typography>{error}</Typography>;
    }

    return (
        <Paper className={classes.container}>
            <div className={classes.dashboardClaimsContainer}>
                <DownloadFacilityClaimsButton
                    fetching={fetching}
                    data={data || []}
                />
                <ClaimStatusFilter
                    handleClaimStatusUpdate={onClaimStatusUpdate}
                />
                <CountryNameFilter />
                <DashboardClaimsListTable
                    fetching={fetching}
                    data={data}
                    handleSortClaims={sortClaims}
                    handleGetClaims={getClaims}
                    handleGetCountries={fetchCountries}
                    claimStatuses={claimStatuses}
                    clearClaims={clearClaims}
                    countriesData={countriesData}
                />
            </div>
        </Paper>
    );
};

DashboardClaims.defaultProps = {
    data: null,
    error: null,
    countriesData: null,
};

DashboardClaims.propTypes = {
    data: facilityClaimsListPropType,
    fetching: bool.isRequired,
    fetchCountries: func.isRequired,
    countriesData: countryOptionsPropType,
    fetchClaimStatus: func.isRequired,
    error: arrayOf(string),
    getClaims: func.isRequired,
    clearClaims: func.isRequired,
    sortClaims: func.isRequired,
    history: shape({
        replace: func.isRequired,
        push: func.isRequired,
    }).isRequired,
    updateClaimStatus: func.isRequired,
    updateCountry: func.isRequired,
    claimStatuses: claimStatusOptionsPropType.isRequired,
};

function mapStateToProps({
    claimFacilityDashboard: {
        list: { data, fetching, error },
    },
    filters: { claimStatuses, countries: countriesData },
}) {
    return {
        data,
        fetching,
        error,
        claimStatuses,
        countriesData,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        getClaims: () => dispatch(fetchFacilityClaims()),
        clearClaims: () => dispatch(clearFacilityClaims()),
        sortClaims: sortedData => dispatch(sortFacilityClaims(sortedData)),
        fetchCountries: () => dispatch(fetchCountryOptions()),
        fetchClaimStatus: () => dispatch(fetchClaimStatusOptions()),
        updateClaimStatus: v => dispatch(updateClaimStatusFilter(v)),
        updateCountry: v => dispatch(updateCountryFilter(v)),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(dashboardClaimsStyles)(DashboardClaims));
