import React, { useEffect } from 'react';
import { connect } from 'react-redux';
import { Redirect, withRouter } from 'react-router';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';

import isEmpty from 'lodash/isEmpty';
import isArray from 'lodash/isArray';
import noop from 'lodash/noop';

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
    fetchFacilities,
    resetSingleFacility,
} from '../../../actions/facilities';
import { fetchPartnerFieldGroups } from '../../../actions/partnerFieldGroups';
import {
    setFiltersFromQueryString,
    resetAllFilters,
} from '../../../actions/filters';
import { resetSectionNavigation } from '../../../actions/sectionNavigation';

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
    hydrateFiltersFromQueryString,
    resetFilters,
    fetchFacilitiesForMap,
    resetNavigation,
}) {
    const normalizedOsID =
        getLastPathParameter(location?.pathname || '') ||
        getLastPathParameter(osID) ||
        osID;

    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(() => {
        fetchFacility(normalizedOsID, contributors);
    }, [normalizedOsID]);

    useEffect(() => {
        if (!partnerFieldGroupsData) {
            getPartnerFieldGroups();
        }
    }, [partnerFieldGroupsData, getPartnerFieldGroups]);

    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(() => {
        const search = location?.search || '';
        if (search) {
            hydrateFiltersFromQueryString(search);
        } else {
            resetFilters();
        }
        fetchFacilitiesForMap();
    }, [location?.search]);

    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(
        () => () => {
            clearFacility();
            resetNavigation();
        },
        [],
    );

    const requestedId = normalizedOsID || '';
    const loadedId = data?.id || '';
    const isStaleData =
        requestedId &&
        loadedId &&
        requestedId.toLowerCase() !== loadedId.toLowerCase();

    if (fetching || (isStaleData && !error?.length)) {
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

    const isSameFacility = requestedId.toLowerCase() === loadedId.toLowerCase();
    const needsCanonicalRedirect = isSameFacility && requestedId !== loadedId;
    if (data?.id && needsCanonicalRedirect) {
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
    resetNavigation: () => dispatch(resetSectionNavigation()),
    getPartnerFieldGroups: () => dispatch(fetchPartnerFieldGroups()),
    hydrateFiltersFromQueryString: qs =>
        dispatch(setFiltersFromQueryString(qs)),
    resetFilters: () => dispatch(resetAllFilters()),
    fetchFacilitiesForMap: () =>
        dispatch(
            fetchFacilities({
                pushNewRoute: noop,
                activateFacilitiesTab: false,
            }),
        ),
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
