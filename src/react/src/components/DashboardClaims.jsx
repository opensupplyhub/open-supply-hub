import React, { useEffect } from 'react';
import { connect } from 'react-redux';
import { arrayOf, bool, func, shape, string } from 'prop-types';
import map from 'lodash/map';
import { withStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

import DashboardClaimsListTable from './DashboardClaimsListTable';
import DashboardDownloadDataButton from './Dashboard/DashboardDownloadDataButton';

import {
    fetchFacilityClaims,
    clearFacilityClaims,
    sortFacilityClaims,
    downloadFacilityClaims,
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
    clearCountryFilter,
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
            width: '100%',
        }),
        dashboardClaimsFilters: Object.freeze({
            padding: '20px',
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
        numberResults: { fontWeight: 800 },
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
    clearCountry,
    countriesData,
    downloadClaims,
    downloadClaimsError,
}) => {
    const { countries, statuses } = getDashboardClaimsListParamsFromQueryString(
        search,
    );

    useEffect(() => {
        fetchCountries();
        fetchClaimStatus();

        // Always keep default PENDING status in the search bar
        if (statuses && statuses.length > 0) {
            const statusesSerialized = map(statuses, status => ({
                label: status,
                value: status,
            }));
            updateClaimStatus(statusesSerialized);
            push(
                makeDashboardClaimListLink({
                    statuses,
                    countries,
                }),
            );
        }
        // If country code is present in URL, it should be set in filter field automatically
        if (countries && countries.length > 0) {
            const countriesSerialized = map(countries, country => ({
                value: country,
                label: country,
            }));
            updateCountry(countriesSerialized);
        }

        return () => {
            clearCountry();
            clearClaims();
        };
    }, []);

    useEffect(() => {
        const finalCountries = map(countriesData, 'value');
        let finalStatuses = statuses;

        if (countriesData.length > 0) {
            if (!statuses && claimStatuses && claimStatuses.length > 0) {
                finalStatuses = map(claimStatuses, 'value');
            }
        } else if (claimStatuses && claimStatuses.length > 0) {
            finalStatuses = map(claimStatuses, 'value');
        }

        push(
            makeDashboardClaimListLink({
                statuses: finalStatuses,
                countries: finalCountries,
            }),
        );
    }, [countriesData]);

    const onClaimStatusUpdate = (s, c) => {
        push(
            makeDashboardClaimListLink({
                countries: map(c, 'value'),
                statuses: map(s, 'value'),
            }),
        );
    };

    if (error) {
        return <Typography>{error}</Typography>;
    }

    const claimsCount = data && data.length;

    return (
        <Paper className={classes.container}>
            <div className={classes.dashboardClaimsContainer}>
                <div className={classes.dashboardClaimsFilters}>
                    <DashboardDownloadDataButton
                        fetching={fetching}
                        downloadPayload={data || []}
                        downloadData={downloadClaims}
                        downloadError={downloadClaimsError}
                    />
                    <ClaimStatusFilter
                        countriesData={countriesData}
                        handleClaimStatusUpdate={onClaimStatusUpdate}
                        isDisabled={fetching}
                    />
                    <CountryNameFilter isDisabled={fetching} />
                    <Grid item className={classes.numberResults}>
                        {claimsCount} results
                    </Grid>
                </div>
                <DashboardClaimsListTable
                    fetching={fetching}
                    data={data}
                    handleSortClaims={sortClaims}
                    handleGetClaims={getClaims}
                    handleGetCountries={fetchCountries}
                    claimStatuses={claimStatuses}
                    countriesData={countriesData}
                    clearClaims={clearClaims}
                />
            </div>
        </Paper>
    );
};

DashboardClaims.defaultProps = {
    data: null,
    error: null,
    countriesData: null,
    downloadClaimsError: null,
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
    clearCountry: func.isRequired,
    downloadClaims: func.isRequired,
    downloadClaimsError: arrayOf(string),
};

function mapStateToProps({
    claimFacilityDashboard: {
        list: { data, fetching, error },
        facilityClaimsDownloadStatus: { error: downloadClaimsError },
    },
    filters: { claimStatuses, countries: countriesData },
}) {
    return {
        data,
        fetching,
        error,
        claimStatuses,
        countriesData,
        downloadClaimsError,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        getClaims: () => dispatch(fetchFacilityClaims()),
        clearClaims: () => dispatch(clearFacilityClaims()),
        sortClaims: sortedData => dispatch(sortFacilityClaims(sortedData)),
        fetchCountries: () => dispatch(fetchCountryOptions()),
        fetchClaimStatus: () => dispatch(fetchClaimStatusOptions()),
        updateClaimStatus: claimStatuses =>
            dispatch(updateClaimStatusFilter(claimStatuses)),
        updateCountry: v => dispatch(updateCountryFilter(v)),
        clearCountry: () => dispatch(clearCountryFilter()),
        downloadClaims: facilityClaims =>
            dispatch(downloadFacilityClaims(facilityClaims)),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(dashboardClaimsStyles)(DashboardClaims));
