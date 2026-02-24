import React, { useEffect } from 'react';
import { Redirect, withRouter } from 'react-router';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Divider from '@material-ui/core/Divider';
import CircularProgress from '@material-ui/core/CircularProgress';
import get from 'lodash/get';

import ClaimFlag from '../Heading/ClaimFlag/ClaimFlag';
import LocationTitle from '../Heading/LocationTitle/LocationTitle';
import DataSourcesInfo from '../Heading/DataSourcesInfo/DataSourcesInfo';
import GeneralFields from '../ProductionLocationDetailsGeneralFields/ProductionLocationDetailsGeneralFields';
import ClaimDataContainer from '../ClaimSection/ClaimDataContainer/ClaimDataContainer';
import PartnerDataContainer from '../PartnerSection/PartnerDataContainer/PartnerDataContainer';
import DetailsMap from '../ProductionLocationDetailsMap/ProductionLocationDetailsMap';
import { FACILITIES_REQUEST_PAGE_SIZE } from '../../../util/constants';

import {
    makeFacilityDetailLinkOnRedirect,
    shouldUseProductionLocationPage,
    getLastPathParameter,
} from '../../../util/util';

import {
    fetchSingleFacility,
    resetSingleFacility,
    fetchFacilities,
} from '../../../actions/facilities';

import styles from './styles';

const ProductionLocationDetailsContent = ({
    classes,
    data,
    fetching,
    error,
    contributors,
    fetchFacility,
    clearFacility,
    location,
    match: {
        params: { osID },
    },
    useProductionLocationPage,
}) => {
    const normalizedOsID =
        getLastPathParameter(location?.pathname || '') ||
        getLastPathParameter(osID) ||
        osID;

    useEffect(() => {
        fetchFacility(normalizedOsID, 0, contributors);
        /* eslint-disable react-hooks/exhaustive-deps */
    }, [normalizedOsID]);

    // Clears the selected facility when unmounted
    useEffect(() => () => clearFacility(), []);

    if (fetching) {
        return (
            <div className={classes.root}>
                <CircularProgress />
            </div>
        );
    }

    if (error && error.length) {
        return (
            <div className={classes.container}>
                <ul>
                    {error.map(err => (
                        <li key={err} className={classes.error}>
                            {err}
                        </li>
                    ))}
                </ul>
            </div>
        );
    }

    if (data?.id && data?.id !== osID) {
        return (
            <Redirect
                to={makeFacilityDetailLinkOnRedirect(
                    data.id,
                    location.search,
                    useProductionLocationPage,
                )}
            />
        );
    }

    return (
        <div className={classes.container}>
            <LocationTitle />
            <ClaimFlag />
            <DataSourcesInfo className={classes.containerItem} />
            <Grid container xs={12} className={classes.containerItem}>
                <Grid item sm={12} md={7}>
                    <GeneralFields />
                </Grid>
                <Grid item sm={12} md={5}>
                    <DetailsMap />
                </Grid>
            </Grid>
            <ClaimDataContainer className={classes.containerItem} />
            <Divider variant="middle" className={classes.containerItem} />
            <PartnerDataContainer />
        </div>
    );
};

function mapStateToProps({
    facilities: {
        singleFacility: { data, fetching, error },
    },
    filters: { contributors },
    featureFlags,
}) {
    return {
        data,
        fetching,
        error,
        contributors,
        useProductionLocationPage: shouldUseProductionLocationPage(
            featureFlags,
        ),
    };
}

function mapDispatchToProps(dispatch) {
    return {
        fetchFacility: (id, contributorId) => {
            const contributorValue = get(contributorId, ['0', 'value']);
            const contributors = contributorValue ? contributorId : null;

            return dispatch(fetchSingleFacility(id, 0, contributors, true));
        },
        clearFacility: () => dispatch(resetSingleFacility()),
        searchForFacilities: vectorTilesAreActive =>
            dispatch(
                fetchFacilities({
                    pageSize: vectorTilesAreActive
                        ? FACILITIES_REQUEST_PAGE_SIZE
                        : 50,
                }),
            ),
    };
}

export default withRouter(
    connect(
        mapStateToProps,
        mapDispatchToProps,
    )(withStyles(styles)(ProductionLocationDetailsContent)),
);
