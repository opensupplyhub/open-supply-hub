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

import styles from './styles';

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
    fetchFacility,
    clearFacility,
}) {
    const normalizedOsID =
        getLastPathParameter(location?.pathname || '') ||
        getLastPathParameter(osID) ||
        osID;

    useEffect(() => {
        fetchFacility(normalizedOsID, contributors);
    }, [normalizedOsID, contributors, fetchFacility]);

    // Run cleanup only on unmount
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
        <Grid container className={classes.root} spacing={8} xs={12}>
            <Grid item xs={12} md={2}>
                <BackToSearch history={history} />
                <NavBar />
                <ContributeFields osId={osID} />
                <SupplyChain />
            </Grid>
            <Grid item xs={12} md={10}>
                <ProductionLocationDetailsContent />
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
}) => ({
    data,
    fetching,
    error,
    contributors: contributors || [],
    useProductionLocationPage: shouldUseProductionLocationPage(featureFlags),
});

const mapDispatchToProps = dispatch => ({
    fetchFacility: (id, contributorId) => {
        const hasContributors =
            isArray(contributorId) && !isEmpty(contributorId);
        const contributors = hasContributors ? contributorId : null;
        return dispatch(fetchSingleFacility(id, 0, contributors, true));
    },
    clearFacility: () => dispatch(resetSingleFacility()),
});

export default withRouter(
    connect(
        mapStateToProps,
        mapDispatchToProps,
    )(withStyles(styles)(ProductionLocationDetailsContainer)),
);
