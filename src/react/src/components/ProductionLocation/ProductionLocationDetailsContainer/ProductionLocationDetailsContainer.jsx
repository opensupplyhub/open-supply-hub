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

// On an embedded map the page has no side navigation, so "Back to search
// results" sits above the location, which takes the full width.
const embedRootStyle = Object.freeze({
    flexWrap: 'wrap',
    flexDirection: 'row',
    padding: '16px 3% 48px 3%',
});
const embedSidebarStyle = Object.freeze({
    minWidth: 0,
    border: 0,
    margin: 0,
    padding: '0 0 8px 0',
});

function ProductionLocationDetailsContainer({
    classes,
    history,
    location,
    match: { params: { osID } = {} } = {},
    data,
    fetching,
    error,
    requestedOsId,
    contributors,
    useProductionLocationPage,
    embed,
    embedConfig,
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
        fetchFacility(normalizedOsID, contributors, !!embed);
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
    // Sidebar actions (suggest correction, report duplicate/closure,
    // supply chain, section nav) assume a confirmed facility; a
    // satellite-detected candidate gets only the back link (OSDEV-3247).
    const isCandidate = !!data?.properties?.is_candidate;
    const isStaleData =
        requestedId && requestedOsId && requestedOsId !== requestedId;

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

    // When redirecting to a facility alias from a merged/deleted facility, or
    // when URL casing does not match the canonical OS ID, redirect to the
    // appropriate production location URL. Only redirect once the loaded data
    // corresponds to the current URL request (see requestedOsId).
    if (data?.id && requestedOsId === requestedId && requestedId !== loadedId) {
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
        <Grid
            container
            className={classes.root}
            style={embed ? embedRootStyle : undefined}
        >
            <Grid
                item
                xs={12}
                md={embed ? 12 : 2}
                className={classes.sidebarContainer}
                style={embed ? embedSidebarStyle : undefined}
            >
                <div className={classes.backToSearch}>
                    <BackToSearch history={history} />
                </div>
                {/* The page's own navigation and the ways to contribute
                    belong to Open Supply Hub, not to an embedded map. */}
                {!isCandidate && !embed && (
                    <Grid className={classes.sidebar}>
                        <div className={classes.navBar}>
                            <NavBar />
                        </div>
                        <ContributeFields osId={osID} />
                        <SupplyChain />
                    </Grid>
                )}
            </Grid>
            <Grid item xs={12} md={embed ? 12 : 10}>
                <ProductionLocationDetailsContent
                    data={data}
                    embed={!!embed}
                    embedConfig={embed ? embedConfig : null}
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
        singleFacility: { data, fetching, error, requestedOsId },
    },
    filters: { contributors },
    featureFlags,
    embeddedMap: { embed, config: embedConfig },
    partnerFieldGroups: { data: partnerFieldGroupsData },
}) => ({
    embedConfig,
    data,
    fetching,
    error,
    requestedOsId,
    contributors: contributors || [],
    useProductionLocationPage: shouldUseProductionLocationPage(featureFlags),
    embed,
    partnerFieldGroupsData,
});

const mapDispatchToProps = dispatch => ({
    fetchFacility: (id, contributorId, embedded) => {
        const hasContributors =
            isArray(contributorId) && !isEmpty(contributorId);
        const contributors = hasContributors ? contributorId : null;
        // An embedded map asks for the location as its contributor shows
        // it: their own data, and any Spotlight data they have chosen.
        const embed = embedded && hasContributors ? 1 : 0;
        return dispatch(fetchSingleFacility(id, embed, contributors, true));
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
