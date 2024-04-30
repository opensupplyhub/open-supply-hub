import React, { useEffect } from 'react';
import { arrayOf, bool, func, string } from 'prop-types';
import { connect } from 'react-redux';
import CircularProgress from '@material-ui/core/CircularProgress';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import ArrowBackIcon from '@material-ui/icons/ArrowBack';
import { Link, Route } from 'react-router-dom';

import AppGrid from '../components/AppGrid';
import AppOverflow from '../components/AppOverflow';
import ClaimFacilityHeader from '../components/ClaimFacilityHeader';
import ClaimFacilityStepper from '../components/ClaimFacilityStepper';

import {
    fetchClaimFacilityData,
    clearClaimFacilityDataAndForm,
} from '../actions/claimFacility';
import { fetchParentCompanyOptions } from '../actions/filterOptions';

import { facilityDetailsPropType } from '../util/propTypes';

import { authLoginFormRoute } from '../util/constants';

import { makeFacilityDetailLink } from '../util/util';

const claimFacilityContainerStyles = Object.freeze({
    containerStyles: Object.freeze({
        width: '100%',
        display: 'flex',
        justifyContent: 'center',
    }),
    paperStyles: Object.freeze({
        width: '80%',
    }),
});

const ClaimFacility = ({
    history: {
        location: { pathname },
    },
    data,
    fetching,
    error,
    getClaimData,
    clearClaimData,
    userHasSignedIn,
    match: {
        params: { osID },
    },
}) => {
    /* eslint-disable react-hooks/exhaustive-deps */
    useEffect(() => {
        getClaimData();

        return clearClaimData;
    }, []);
    /* eslint-enable react-hooks/exhaustive-deps */

    if (fetching) {
        return <CircularProgress />;
    }

    if (!userHasSignedIn) {
        return (
            <AppGrid title="Claim this facility">
                <Grid container className="margin-bottom-64">
                    <Grid item xs={12}>
                        <Link
                            to={{
                                pathname: authLoginFormRoute,
                                state: { prevPath: pathname },
                            }}
                            href={authLoginFormRoute}
                        >
                            Log in to claim a facility on Open Supply Hub
                        </Link>
                    </Grid>
                </Grid>
            </AppGrid>
        );
    }

    if (error) {
        return (
            <div>An error prevented fetching details about that facility.</div>
        );
    }

    if (!data) {
        return null;
    }

    return (
        <AppOverflow>
            <AppGrid
                title="Claim this facility"
                backButtonComponent={
                    <Link
                        to={makeFacilityDetailLink(osID)}
                        href={makeFacilityDetailLink(osID)}
                        style={{ color: 'black' }}
                    >
                        <ArrowBackIcon fill="black" />
                    </Link>
                }
            >
                <div style={claimFacilityContainerStyles.containerStyles}>
                    <Paper style={claimFacilityContainerStyles.paperStyles}>
                        <ClaimFacilityHeader data={data} />
                        <Route component={ClaimFacilityStepper} />
                    </Paper>
                </div>
            </AppGrid>
        </AppOverflow>
    );
};

ClaimFacility.defaultProps = {
    data: null,
    error: null,
};

ClaimFacility.propTypes = {
    data: facilityDetailsPropType,
    fetching: bool.isRequired,
    error: arrayOf(string),
    getClaimData: func.isRequired,
    clearClaimData: func.isRequired,
    userHasSignedIn: bool.isRequired,
};

const mapStateToProps = ({
    claimFacility: {
        facilityData: { data, fetching, error },
    },
    filterOptions: {
        parentCompanies: { fetching: fetchingParentCompanyOptions },
    },
    auth: {
        user: { user },
        session: { fetching: sessionFetching },
    },
}) => ({
    data,
    fetching: fetching || sessionFetching || fetchingParentCompanyOptions,
    userHasSignedIn: !user.isAnon,
    error,
});

const mapDispatchToProps = (
    dispatch,
    {
        match: {
            params: { osID },
        },
    },
) => ({
    getClaimData: () => {
        dispatch(fetchParentCompanyOptions());
        return dispatch(fetchClaimFacilityData(osID));
    },
    clearClaimData: () => dispatch(clearClaimFacilityDataAndForm()),
});

export default connect(mapStateToProps, mapDispatchToProps)(ClaimFacility);
