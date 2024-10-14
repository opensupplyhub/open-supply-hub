import React, { useEffect } from 'react';
// import React from 'react';
import { connect } from 'react-redux';
// import { arrayOf, bool, func, shape, string } from 'prop-types';
import { func } from 'prop-types';
// import map from 'lodash/map';
import { withStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
// import Grid from '@material-ui/core/Grid';
// import Typography from '@material-ui/core/Typography';

import CountryNameFilter from '../Filters/CountryNameFilter';
import DownloadFacilityClaimsButton from '../DownloadFacilityClaimsButton';
import RecordTypeFilter from '../Filters/RecordTypeFilter';
import MatchStatusFilter from '../Filters/MatchStatusFilter';
import ModerationStatusFilter from '../Filters/ModerationStatusFilter';
// import DashboardClaimsListTable from '../../DashboardClaimsListTable';

// import {
//     fetchFacilityClaims,
//     clearFacilityClaims,
//     sortFacilityClaims,
// } from '../actions/claimFacilityDashboard';

import {
    fetchCountryOptions,
    fetchRecordTypeOptions,
    // fetchClaimStatusOptions,
} from '../../actions/filterOptions';

// import ClaimStatusFilter from './Filters/ClaimStatusFilter';
// import CountryNameFilter from './Filters/CountryNameFilter';
// import {
//     updateClaimStatusFilter,
//     updateCountryFilter,
//     clearCountryFilter,
// } from './../actions/filters';

// import {
//     facilityClaimsListPropType,
//     claimStatusOptionsPropType,
//     countryOptionsPropType,
// } from '../util/propTypes';

// import {
//     makeDashboardClaimListLink,
//     getDashboardClaimsListParamsFromQueryString,
// } from '../util/util';

const dashboardModerationQueueStyles = () =>
    Object.freeze({
        mainContainer: Object.freeze({
            marginBottom: '60px',
            width: '100%',
        }),
        dashboardFilters: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
            padding: '20px',
        }),
        // filterRow: Object.freeze({
        //     padding: '20px',
        //     display: 'flex',
        //     flexDirection: 'column',
        //     gap: '20px',
        // }),
        // filter: Object.freeze({
        //     flex: 1,
        // }),
        // numberResults: { fontWeight: 800 },
    });

const DashboardModerationQueue = ({
    // data,
    // claimStatuses,
    fetching = false,
    // error,
    // getClaims,
    // clearClaims,
    // sortClaims,
    classes,
    // history: {
    //     location: { search },
    //     push,
    // },
    // fetchClaimStatus,
    fetchRecordTypes,
    fetchCountries,
    // updateClaimStatus,
    // updateCountry,
    // clearCountry,
    // countriesData,
}) => {
    // console.log('DashboardModerationQueue');
    const data = null;
    // const { countries, statuses } = getDashboardClaimsListParamsFromQueryString(
    //     search,
    // );

    useEffect(() => {
        fetchRecordTypes();
        fetchCountries();
        // fetchClaimStatus();

        // // Always keep default PENDING status in the search bar
        // if (statuses && statuses.length > 0) {
        //     const statusesSerialized = map(statuses, status => ({
        //         label: status,
        //         value: status,
        //     }));
        //     updateClaimStatus(statusesSerialized);
        //     push(
        //         makeDashboardClaimListLink({
        //             statuses,
        //             countries,
        //         }),
        //     );
        // }
        // // If country code is present in URL, it should be set in filter field automatically
        // if (countries && countries.length > 0) {
        //     const countriesSerialized = map(countries, country => ({
        //         value: country,
        //         label: country,
        //     }));
        //     updateCountry(countriesSerialized);
        // }

        // return () => {
        //     clearCountry();
        //     clearClaims();
        // };
    }, []);

    // useEffect(() => {
    //     const finalCountries = map(countriesData, 'value');
    //     let finalStatuses = statuses;

    //     if (countriesData.length > 0) {
    //         if (!statuses && claimStatuses && claimStatuses.length > 0) {
    //             finalStatuses = map(claimStatuses, 'value');
    //         }
    //     } else if (claimStatuses && claimStatuses.length > 0) {
    //         finalStatuses = map(claimStatuses, 'value');
    //     }

    //     push(
    //         makeDashboardClaimListLink({
    //             statuses: finalStatuses,
    //             countries: finalCountries,
    //         }),
    //     );
    // }, [countriesData]);

    // const onClaimStatusUpdate = (s, c) => {
    //     push(
    //         makeDashboardClaimListLink({
    //             countries: map(c, 'value'),
    //             statuses: map(s, 'value'),
    //         }),
    //     );
    // };

    // if (error) {
    //     return <Typography>{error}</Typography>;
    // }

    // const claimsCount = data && data.length;

    return (
        <Paper className={classes.mainContainer}>
            <div className={classes.dashboardFilters}>
                <DownloadFacilityClaimsButton
                    fetching={fetching}
                    data={data || []}
                />
                {/* <ClaimStatusFilter
                        countriesData={countriesData}
                        handleClaimStatusUpdate={onClaimStatusUpdate}
                        isDisabled={fetching}
                    /> */}
                <RecordTypeFilter />
                <MatchStatusFilter />
                <ModerationStatusFilter />
                <CountryNameFilter isDisabled={fetching} />
                {/* <Grid item className={classes.numberResults}>
                        {claimsCount} results
                    </Grid> */}
            </div>
            {/* <DashboardClaimsListTable
                    fetching={fetching}
                    data={data}
                    handleSortClaims={sortClaims}
                    handleGetClaims={getClaims}
                    handleGetCountries={fetchCountries}
                    claimStatuses={claimStatuses}
                    countriesData={countriesData}
                    clearClaims={clearClaims}
                /> */}
        </Paper>
    );
};

// DashboardModerationQueue.defaultProps = {
//     data: null,
//     error: null,
//     countriesData: null,
// };

DashboardModerationQueue.propTypes = {
    // data: facilityClaimsListPropType,
    // fetching: bool.isRequired,
    fetchRecordTypes: func.isRequired,
    fetchCountries: func.isRequired,
    // countriesData: countryOptionsPropType,
    // fetchClaimStatus: func.isRequired,
    // error: arrayOf(string),
    // getClaims: func.isRequired,
    // clearClaims: func.isRequired,
    // sortClaims: func.isRequired,
    // history: shape({
    //     replace: func.isRequired,
    //     push: func.isRequired,
    // }).isRequired,
    // updateClaimStatus: func.isRequired,
    // updateCountry: func.isRequired,
    // claimStatuses: claimStatusOptionsPropType.isRequired,
    // clearCountry: func.isRequired,
};

// function mapStateToProps({
//     claimFacilityDashboard: {
//         list: { data, fetching, error },
//     },
//     filters: { claimStatuses, countries: countriesData },
// }) {
//     return {
//         // data,
//         // fetching,
//         // error,
//         // claimStatuses,
//         // countriesData,
//     };
// }

const mapStateToProps = () => ({});

const mapDispatchToProps = dispatch => ({
    // getClaims: () => dispatch(fetchFacilityClaims()),
    // clearClaims: () => dispatch(clearFacilityClaims()),
    // sortClaims: sortedData => dispatch(sortFacilityClaims(sortedData)),
    fetchRecordTypes: () => dispatch(fetchRecordTypeOptions()),
    fetchCountries: () => dispatch(fetchCountryOptions()),
    // fetchClaimStatus: () => dispatch(fetchClaimStatusOptions()),
    // updateClaimStatus: claimStatuses =>
    //     dispatch(updateClaimStatusFilter(claimStatuses)),
    // updateCountry: v => dispatch(updateCountryFilter(v)),
    // clearCountry: () => dispatch(clearCountryFilter()),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(dashboardModerationQueueStyles)(DashboardModerationQueue));
