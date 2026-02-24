import React, { useEffect } from 'react';
import { Redirect, withRouter } from 'react-router';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Divider from '@material-ui/core/Divider';
import get from 'lodash/get';

import ClaimFlag from '../Heading/ClaimFlag';
import LocationTitle from '../Heading/LocationTitle';
import DataSourcesInfo from '../Heading/DataSourcesInfo';
import GeneralFields from '../ProductionLocationDetailsGeneralFields';
import ClaimDataContainer from '../ClaimSection/ClaimDataContainer';
import PartnerDataContainer from '../PartnerSection/PartnerDataContainer';
import DetailsMap from '../ProductionLocationDetailsMap';
import { FACILITIES_REQUEST_PAGE_SIZE } from '../../../util/constants';

import {
    makeFacilityDetailLinkOnRedirect,
    shouldUseProductionLocationPage,
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
    error,
    location,
    match: {
        params: { osID },
    },
    useProductionLocationPage,
    clearFacility,
}) => {
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
    )(withStyles(styles)(ProductionLocationDetailsContent)),
);
