import React, { useEffect } from 'react';
import { arrayOf, bool, func, string } from 'prop-types';
import { connect } from 'react-redux';
import CircularProgress from '@material-ui/core/CircularProgress';
import Grid from '@material-ui/core/Grid';
import { Link, Route } from 'react-router-dom';

import AppGrid from '../components/AppGrid';
import AppOverflow from '../components/AppOverflow';
import ClaimFacilityStepper from '../components/ClaimFacilityStepper';

import {
    fetchClaimFacilityData,
    clearClaimFacilityDataAndForm,
} from '../actions/claimFacility';

import { facilityDetailsPropType } from '../util/propTypes';

import { authLoginFormRoute } from '../util/constants';

import COLOURS from '../util/COLOURS';

const claimFacilityContainerStyles = Object.freeze({
    containerStyles: Object.freeze({
        width: '100%',
        justifyContent: 'center',
    }),
});

const appStyles = Object.freeze({
    gridStyles: Object.freeze({
        backgroundColor: COLOURS.LIGHT_GREY,
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
            <AppGrid title="Claim this production location">
                <Grid container className="margin-bottom-64">
                    <Grid item xs={12}>
                        <Link
                            to={{
                                pathname: authLoginFormRoute,
                                state: { prevPath: pathname },
                            }}
                            href={authLoginFormRoute}
                        >
                            Login to claim a production location on Open Supply
                            Hub
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
        <div style={appStyles.gridStyles}>
            <AppOverflow>
                <AppGrid title="">
                    <div style={claimFacilityContainerStyles.containerStyles}>
                        <Route component={ClaimFacilityStepper} />
                    </div>
                </AppGrid>
            </AppOverflow>
        </div>
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
    auth: {
        user: { user },
        session: { fetching: sessionFetching },
    },
}) => ({
    data,
    fetching: fetching || sessionFetching,
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
    getClaimData: () => dispatch(fetchClaimFacilityData(osID)),
    clearClaimData: () => dispatch(clearClaimFacilityDataAndForm()),
});

export default connect(mapStateToProps, mapDispatchToProps)(ClaimFacility);
