import React, { useEffect } from 'react';
import { Redirect, withRouter } from 'react-router';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import get from 'lodash/get';

import ProductionLocationDetailsClaimFlag from './ProductionLocationDetailsClaimFlag';
import ProductionLocationDetailsTitle from './ProductionLocationDetailsTitle';
import ProductionLocationDetailsDataSourcesInfo from './ProductionLocationDetailsDataSourcesInfo';
import ProductionLocationDetailsGeneralFields from './ProductionLocationDetailsGeneralFields';
import ProductionLocationDetailsMap from './ProductionLocationDetailsMap';
import { FACILITIES_REQUEST_PAGE_SIZE } from '../../util/constants';

import {
    makeFacilityDetailLinkOnRedirect,
    shouldUseProductionLocationPage,
} from '../../util/util';

import {
    fetchSingleFacility,
    resetSingleFacility,
    fetchFacilities,
} from '../../actions/facilities';

const detailsStyles = () =>
    Object.freeze({
        container: Object.freeze({}),
    });

const ProductionLocationDetailsContent = ({
    classes,
    data,
    error,
    location,
    match: {
        params: { osID },
    },
    useProductionLocationPage,
    clearFacility,
}) => {
    // Clears the selected facility when unmounted
    useEffect(() => () => clearFacility(), []);

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
        // When redirecting to a facility alias from a deleted facility,
        // the OS ID in the url will not match the facility data id;
        // redirect to the appropriate facility URL.
        return (
            <Redirect
                to={{
                    pathname: makeFacilityDetailLinkOnRedirect(
                        data.id,
                        location.search,
                        useProductionLocationPage,
                    ),
                }}
            />
        );
    }

    return (
        <div className={classes.container}>
            <Grid item>
                <ProductionLocationDetailsTitle />
            </Grid>
            <Grid item>
                <ProductionLocationDetailsClaimFlag />
            </Grid>
            <Grid item>
                <ProductionLocationDetailsDataSourcesInfo />
            </Grid>
            <Grid container xs={12}>
                <Grid item sm={12} md={7}>
                    <ProductionLocationDetailsGeneralFields />
                </Grid>
                <Grid item sm={12} md={5}>
                    <ProductionLocationDetailsMap />
                </Grid>
            </Grid>
        </div>
    );
};

function mapDispatchToProps(dispatch) {
    return {
        fetchFacility: (id, embed, contributorId) => {
            const contributorValue = get(contributorId, ['0', 'value']);
            const isEmbedded = embed && contributorValue ? embed : 0;
            const contributors = contributorValue ? contributorId : null;

            return dispatch(
                fetchSingleFacility(id, isEmbedded, contributors, true),
            );
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

function mapStateToProps({
    facilities: {
        singleFacility: { data, fetching, error },
    },
    embeddedMap: { embed, config },
    filters: { contributors },
    featureFlags,
}) {
    return {
        data,
        fetching,
        error,
        embed: !!embed,
        embedContributor: config?.contributor_name,
        embedConfig: config,
        contributors,
        hideSectorData: embed ? config.hide_sector_data : false,
        useProductionLocationPage: shouldUseProductionLocationPage(
            featureFlags,
        ),
    };
}

export default withRouter(
    connect(
        mapStateToProps,
        mapDispatchToProps,
    )(withStyles(detailsStyles)(ProductionLocationDetailsContent)),
);
