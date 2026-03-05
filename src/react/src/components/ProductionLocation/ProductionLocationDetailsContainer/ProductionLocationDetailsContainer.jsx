import React, { useEffect } from 'react';
import { connect } from 'react-redux';
import { Redirect, withRouter } from 'react-router';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';

import isEmpty from 'lodash/isEmpty';
import isArray from 'lodash/isArray';

import BackToSearch from '../Sidebar/BackToSearch/BackToSearch';
import NavBar from '../Sidebar/NavBar/NavBar';
import SupplyChain from '../Sidebar/SupplyChain/SupplyChain';
import ContributeFields from '../Sidebar/ContributeFields/ContributeFields';
import ProductionLocationDetailsContent from '../ProductionLocationDetailsContent/ProductionLocationDetailsContent';

import {
    getLastPathParameter,
    makeFacilityDetailLinkOnRedirect,
    shouldUseProductionLocationPage,
} from '../../../util/util';
import {
    fetchSingleFacility,
    resetSingleFacility,
} from '../../../actions/facilities';
import { fetchPartnerFieldGroups } from '../../../actions/partnerFieldGroups';

import productionLocationDetailsContainerStyles from './styles';

function ProductionLocationDetailsContainer({
    classes,
    history,
    location,
    match: { params: { osID } = {} } = {},
    data,
    fetching,
    error,
    contributors,
    useProductionLocationPage,
    embed,
    fetchFacility,
    clearFacility,
    getPartnerFieldGroups,
    partnerFieldGroupsData,
}) {
    const normalizedOsID =
        getLastPathParameter(location?.pathname || '') ||
        getLastPathParameter(osID) ||
        osID;

    useEffect(() => {
        fetchFacility(normalizedOsID, contributors);
    }, [normalizedOsID, contributors, fetchFacility]);

    useEffect(() => {
        if (!partnerFieldGroupsData) {
            getPartnerFieldGroups();
        }
    }, [getPartnerFieldGroups, partnerFieldGroupsData]);

    // Run cleanup only on unmount.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(() => () => clearFacility(), []);

    if (fetching) {
        return (
            <div className={classes.loadingRoot}>
                <CircularProgress />
            </div>
        );
    }

    if (error && error.length) {
        return (
            <div className={classes.root}>
                <ul className={classes.errorList}>
                    {error.map(err => (
                        <li key={err} className={classes.errorItem}>
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
        <Grid container className={classes.root}>
            <Grid item xs={12} md={2}>
                <BackToSearch history={history} />
                <Grid className={classes.sidebar}>
                    <NavBar />
                    <ContributeFields osId={osID} />
                    <SupplyChain />
                </Grid>
            </Grid>
            <Grid item xs={12} md={10}>
                <ProductionLocationDetailsContent
                    data={data}
                    embed={!!embed}
                    clearFacility={clearFacility}
                    useProductionLocationPage={useProductionLocationPage}
                    location={location}
                />
            </Grid>
        </Grid>
    );
}

const mapStateToProps = ({
    facilities: {
        singleFacility: { data, fetching, error },
    },
    filters: { contributors },
    featureFlags,
    embeddedMap: { embed },
    partnerFieldGroups: { data: partnerFieldGroupsData },
}) => ({
    data,
    fetching,
    error,
    contributors: contributors || [],
    useProductionLocationPage: shouldUseProductionLocationPage(featureFlags),
    embed,
    partnerFieldGroupsData,
});

const mapDispatchToProps = dispatch => ({
    fetchFacility: (id, contributorId) => {
        const hasContributors =
            isArray(contributorId) && !isEmpty(contributorId);
        const contributors = hasContributors ? contributorId : null;
        return dispatch(fetchSingleFacility(id, 0, contributors, true));
    },
    clearFacility: () => dispatch(resetSingleFacility()),
    getPartnerFieldGroups: () => dispatch(fetchPartnerFieldGroups()),
});

export default withRouter(
    connect(
        mapStateToProps,
        mapDispatchToProps,
    )(
        withStyles(productionLocationDetailsContainerStyles)(
            ProductionLocationDetailsContainer,
        ),
    ),
);
